# Memory optimization to-do: make it so unsorted text isn't always passed
# around

# Goal: order the words in a patent's text field by tf-idf (descending)

# python treats dictionaries as unordered, and it's awkward to reorder
# MongoDB's BSON objects, so I use a python array of dicts to hold the text
# while I shuffle it around

from pymongo  import MongoClient
from operator import attrgetter
import randPat
from time import time
from datetime import datetime
from parallelMap import parallelMap
import csv_module
import multiprocessing
import os


# for operations where a document's order is important,
# we want to store mongo objects as SON and not python
# dicts (which do not preserve order)


patDB = MongoClient().patents
patns = patDB.patns
just_cites = patDB.just_cites


# copies {key1: v1, key2: v2} into [{key: key1, v1}, {key: key2, v2}]
# (so there is some flattening, convenient for our use)
def dictToArray(D, keylabel = "key"):
	arr = []
	for elem in D:
		# just copies the dict entry in an array
		newElem = D[elem]
		newElem[keylabel] = elem
		arr.append(newElem)
	return arr

# For a patent, produces an array of the words in that patent's text
# in descending tf-idf order
def createSortedText(patn, verbose = False):
	textArray = dictToArray(patn['text'], keylabel='word')
	if verbose: print patn['pno']
	sortedTextArray = sorted(textArray, key=lambda w: w['tf-idf'], reverse = True)
	return sortedTextArray

def has_tf_idfs(pat):
	if 'text' not in pat: return False
	for word in pat['text']:
		if 'tf-idf' in pat['text'][word]: return True
		else: return False


def perLineArrayDisplay(arr):
	for elem in arr:
		print elem

# pretty prints a word and its tf-idf from a patent's sorted_text
def displaySortedWord(word):
	# makes all words width-20
	pstring = '{0: <15}'.format(word['word']) + ' tf-idf: ' + "%.3f" % word['tf-idf']
	print pstring


def topNTerms(patn, n, patCol_to_update = False, display=False):
	if 'sorted_text' not in patn:
		patn['sorted_text'] = createSortedText(patn)
		# if the optional patCol_to_update arg is used, and the patent's text has never
		# been sorted before, save the sorted text in the patent collection
		if patCol_to_update:
			patCol_to_update.update({'pno': patn['pno']},{'$set': {'sorted_text': patn['sorted_text']}})
	if display:
		print '\n'
		print 'Patent ' + str(pat['pno']) + ': ' + pat['title']
		for word in patn['sorted_text'][:n]:
			displaySortedWord(word)
	return patn['sorted_text'][:n]

def orderOneText(patn):
	return {'$set': {'sorted_text': createSortedText(patn)} }


def orderAllTexts(coll):
	parallelMap(orderOneText,
				in_collection = coll,
				out_collection= coll,
				findArgs = {'spec': {'sorted_text': {'$exists': False}, 'text': {'$exists': True}}, 'fields': {'text': 1}},
				updateFreq = 5000,
				bSize = 5000)

# returns a vector of (s_1,...,s_n) where s_i is the number of terms
# shared by the top n words between the two pats
def shared_n_vector(p1, p2, n):
	words1, words2 = topNTerms(p1, n), topNTerms(p2, n)
		
	shCount = 0
	out_vect = []
	# the max n for which both pats have an nth word we care abt
	word_lim = min(n, len(words1), len(words2))
	# dicts for lookup
	w1s, w2s = {}, {}

	for i in range(word_lim):
		# each ith word
		w1 = words1[i]['word']
		w2 = words2[i]['word']

		# add words to lookup dicts
		w1s[w1] = True
		w2s[w2] = True

		# checks for overlap
		if w1 in w2s: shCount += 1
		if w2 in w1s: shCount += 1

		#updates out_vect
		out_vect.append(shCount)

	# in case len(words2) < n, len(words1)
	for i in range(word_lim, min(len(words1), n) ):
		w1 = words1[i]['word']
		if w1 in w2s: shCount += 1
		#updates out_vect
		out_vect.append(shCount)
	# like above, switching 1 and 2
	for i in range(word_lim, min(len(words2), n) ):
		w2 = words2[i]['word']
		if w2 in w1s: shCount += 1
		#updates out_vect
		out_vect.append(shCount)

	# now accounts for when both words1 and words2 are shorter than n
	# in which case the final (n - max(length of each words)) spots of
	# outvect must be filled (e.g. if two patents each have 5 words, then
	# the number of terms they share among their top 8 words is the
	# same as among their top 5.)
	for i in range( len(out_vect), n ):
		if (len(out_vect) != 0):
			out_vect.append(out_vect[-1])
		else:
			out_vect.append(0)

	return out_vect

def add_sh_vector(v1, v2):
	out_v = [v1[i] + v2[i] for i in range(len(v1))]
	return out_v

# calls shared_n_vector m different times, summing the result, for shared
# or unshared patents
def shared_n_vectors(n, m, cite_pairs=True, texts_already_ordered=False):
	selector = get_selector(texts_already_ordered)

	fname = 'shared_n_vectors(%d, %d)'
	if cite_pairs: fname += 'cite_pair'
	else:          fname += 'rand_pair'

	pat1, pat2 = selector.get_pair(cite_pairs)

	out = shared_n_vector(pat1, pat2, n)

	for i in range(1,m):
		pat1, pat2 = selector.get_pair(cite_pairs)
		# add output to running total (a reduce function)
		out = add_sh_vector(out, shared_n_vector(pat1, pat2, n))
	return out

# Returns the number of words shared by the top n words in each patent
# if returnWords is true, returns a list of the shared words. Otherwise
# just returns the number of shared words.

# After running some rudimentary speed tests, I figured that the fastest
# comparison was to transform pat1's top terms into a dict for fast word-
# indexed lookup
def sharedTopN(pat1, pat2, n, returnWords=False, patCol_to_update = False, verbose = False):
	words1, words2 = topNTerms(pat1, n, patCol_to_update), topNTerms(pat2, n, patCol_to_update)
	shCount = 0
	shWords = []
	compare_dict = { word1['word']: True for word1 in words1 }
	for word2 in words2:
		if word2['word'] in compare_dict:
			if returnWords or verbose:
				shWords.append(word2['word'])
			shCount += 1
	if verbose and shCount > 0:
		print '%d and %d share top term(s): %s' % (pat1['pno'], pat2['pno'], ', '.join(shWords))
	
	if returnWords: return shWords
	else: return shCount

# spits out an array of {wordSharedByBothPats, source_tf-idf, cite_tf-idf}
# so that we can find avg tf_idfs of shared terms
def compareTopN(sourceP, citeP, n, patCol_to_update = False, verbose = False):
	if not (has_tf_idfs(sourceP) and has_tf_idfs(citeP)):
		return 'error: no tf_idfs to compare between patns %d and %d.' % (sourceP['pno'],citeP['pno'])
	words1, words2 = topNTerms(sourceP, n, patCol_to_update), topNTerms(citeP, n, patCol_to_update)
	shCount = 0
	shWords = []
	# below line will break if words1 doesn't have tf_idfs
	compare_dict = { word1['word']: word1['tf-idf'] for word1 in words1 }
	for word2 in words2:
		if word2['word'] in compare_dict:
			res = { 'word': word2['word'], 'src_tf-idf': compare_dict[word2['word']], 'ctd_tf-idf': word2['tf-idf'] }
			shCount += 1
	if verbose and shCount > 0:
		print '%d and %d share top term(s): %s' % (pat1['pno'], pat2['pno'], ', '.join(shWords))
	
	return shWords



# If texts are already sorted, we save a lot of memory by
# not retrieving the unsorted texts. Otherwise, those are retrieved
# so that they can be sorted
def get_selector(texts_already_ordered = False):
	if texts_already_ordered:
		return randPat.Selector(patns, projection={'pno':1, 'title': 1, 'sorted_text': 1, '_id': 0})
	else:
		return randPat.Selector(patns, projection={'pno':1, 'title': 1, 'text': 1, 'sorted_text': 1, '_id': 0})


# if citations = True, returns the avg shared terms among patents where
# one cites the other. if False, returns avg shared terms among two randomly
# chosen patents
def avg_shared_terms(numTrials, n, citations = False, texts_already_ordered = False, verbose = False):
	totSharedTerms = 0
	selector = get_selector(texts_already_ordered)
	
	for i in range(numTrials):
			# get_pair will returns either a cite pair or a random pair
			# depending on 'citations'
		pat1, pat2 = selector.get_pair(citations)
		shares = sharedTopN(pat1, pat2, n, returnWords = False, patCol_to_update=patns, verbose = verbose)
		if shares > 0:
			#print '%d shared terms between patns %d and %d' % (shares, pat1['pno'], pat2['pno'])
			totSharedTerms += shares
	return float(totSharedTerms)/numTrials


# simply a script for calling the above func on a parameter sweep of n and 'citations' and
# saving the output in .csv.
# There's obviously a much faster way of doing this, but there's free compute time right now
# and this code is easy to write (i.e. collect shared terms considering top1..n for each pair,
# not collecting only the shared terms considering top i incrementally
# dname suffix goes on the end of the folder name where the output is saved
def sweep_shared_terms(numTrials, max_n, min_n=1, texts_already_ordered=True, verbose=True, fname_suffix=None):
	
	# makes an output folder
	fname = 'sh_term_sweep_%d_trials_upto_%d' % (numTrials, max_n)
	if fname_suffix:
		fname += ('_'+fname_suffix)
	
	if verbose: print 'fname is ' + fname
	
	# this is the format of each row of the .csv
	header = ['top n', 'sst(n,rand)', 'sst(n,rand)/n', 'sst(n,cite)', 'sst(n,cite)/n']
 
	csv_module.save_csv(header, fname, trail_endl=True)

	if verbose:
		strHead = ', '.join(header)
		print 'saved header as ' + strHead

	for i in range(min_n, max_n+1):
		# cite_stat=citation status of the pairs being examined (True means cite pairs, False means random pairs)
		
		if verbose: print 'gathering data for top n = %d' % i
		
		# I figure I'll silence 'verbose' down the line regardless
		rand_sh, cite_sh = (avg_shared_terms(numTrials, i, citations=CITE_STAT, texts_already_ordered=texts_already_ordered, verbose=False) for CITE_STAT in [False, True])
		
		if verbose: print 'rand_sh = %f; cite_sh = %f' % (rand_sh, cite_sh)

		rand_norm, cite_norm = rand_sh/i, cite_sh/i
		if verbose: print 'rand_nm = %f; cite_nm = %f' % (rand_norm, cite_norm)
		out_arr = [i, rand_sh, rand_norm, cite_sh, cite_norm]

		# This could be better formatted
		if verbose:
			if i % 5 == 1:
				print '[top n, rand pair avg shared terms, rand pair ratio ast/n, cite pair ast, cite pair ast/n]'
			print '%s: %s' % (str(datetime.now()), str(out_arr))
		
		# saving: successive values of i will be new lines in the cite_stat .csv file
		csv_module.save_csv(out_arr, fname, trail_endl=True)




'''
# returns a tuple of lists, ([all tf-idfs of words shared in p1, p2's top n],[all tf-idfs of words which appear in exactly one of p1 and p2's top n])
# if uptoN == True, returns a list of 'n' tuples, for the top 1 terms, top 2 terms, ... , top n terms.
def tf_idf_by_shared(pat0, pat1, n, uptoN = False):
	words = [topNTerms(pat1, n), topNTerms(pat2, n)]
	# speeds up "is this word in that list" lookup
	lookup_dicts = [{}, {}]
	# in case either patent has less than n total words
	upper_limits = [len(pat0['sorted_text'] ), len(pat1['sorted_text'] ) ]
	current_words
	shared_tf_idfs = []
	unshared_tf_idfs = []
	for i in range(n):
		# make sure we don't search out of bounds in either patent's sorted_text
		idxes = [ max(i, uplim) for uplim in upper_limits ]
		# contains each nth word
		this_words = [ words[j][ idxes[j] ] for j in [0,1] ]
		for j in [0,1]:
			# update the two lookup dicts
			lookup_dicts[j][ this_words[j]['word'] ] = this_words[j]['tf-idf']
			
		for j in [0,1]:
			# if the nth word of this pat is in the lookup dict of that pat
			if this_words[j]['word'] in lookup_dicts[1-j]:
				# add the tf-idfs from this patn to the list of shared
				shared_tf_idfs.append(this_words[j]['tf-idf'])
				# the tf-idf of the same word in the other patn is in
				# the lookup dict
				shared_tf_idfs.append(lookup_dicts[1-j][ this_words[j]['word'] ] )
			else:
'''

# Given two patents, returns a tuple of lists:
# ([tf-idfs of words shared by both patn's top n],
#  [tf-idfs of words in only one patn's top n])
def tf_idfs_by_shared(pat0, pat1, n):
	
	list_of_shares = sharedTopN(pat0, pat1, n, returnWords = True)
	dict_of_shares = {word: True for word in list_of_shares}
	pats = (pat0, pat1)
	shared_tf_idfs = []
	unshared_tf_idfs = []

	for i in [0,1]:
		iwords = topNTerms(pats[i], n)
		for word in iwords:
			if word['word'] in dict_of_shares:
				shared_tf_idfs.append(word['tf-idf'])
			else:
				unshared_tf_idfs.append(word['tf-idf'])

	return (shared_tf_idfs, unshared_tf_idfs)

# returns the combined output of num_pairs calls of tf_idfs_by_shared,
# each call being on a pair of patents whose relation is described by
# is_citepair
def bulk_tf_idfs_by_shared(num_pairs, top_n, is_citepair=True, enforce_cite_buf_size = None):
	sel = get_selector()
	if enforce_cite_buf_size:
		sel.cite_buf_size = enforce_cite_buf_size
	shared_tf_idfs = []
	unshared_tf_idfs = []

	for i in range(num_pairs):
		p0, p1 = sel.get_pair(is_citepair)
		thisShare, thisUnShare = tf_idfs_by_shared(p0, p1, top_n)
		shared_tf_idfs += thisShare
		unshared_tf_idfs += thisUnShare

	return (shared_tf_idfs, unshared_tf_idfs)


# Calls the above functions repeatedly, writing the cumulative output to
# .csv. If append=True, two output files (shared, notshared) will be
# continuously added to, else new versions will be continually rewritten

# A NOTE ON RANDOM CITATION SUBSETS: the selector's cite_buf_size (CBS for now)
# decides how many patent-citation pairs are chosen at a time without replacement.
# After CBS pairs are chosen, a new batch of CBS pairs are chosen. There
# might be overlap ('replacement' in random-selection-from-a-set lingo)
# between the pairs chosen in separate batches, but never within one batch.

def write_bulk_tf_idfs_by_shared(tot_pairs, pairs_per_batch, top_n, out_name, is_citepair=True, append=True, verbose = False):
	
	num_batches = tot_pairs/pairs_per_batch
	remainder = tot_pairs % pairs_per_batch

	for i in range(num_batches):
		this_out = bulk_tf_idfs_by_shared(pairs_per_batch, top_n, is_citepair, enforce_cite_buf_size = pairs_per_batch)
		outn = out_name
		if not append: outn += '.%d' % i
		csv_module.save_csv(this_out[0], 'shared_'+outn)
		csv_module.save_csv(this_out[1], 'unshared_'+outn)
		if verbose: print str(datetime.now()) + ': saved batch %d / %d' % (i+1, num_batches)

# BROKEN at least wrt randomization ( I think each processor gets the same random
# seed, somewhere in randPat)
# literally just executes p instances of the above func, where p = num processors
def write_parallel_bulk_tf_idfs_by_shared(tot_pairs_per_proc, pairs_per_batch, top_n, out_name, is_citepair=True, append=True, verbose = False):

	if not os.path.exists(out_name):
		os.makedirs(out_name)

	workerProcesses = []
	for i in range(0, multiprocessing.cpu_count()):
		p = multiprocessing.Process(target = write_bulk_tf_idfs_by_shared,
									args = (tot_pairs_per_proc, pairs_per_batch,
											top_n, out_name+'/proc%d'%i,
											is_citepair, append, verbose)
									)
		p.daemon = True
		p.start()
		workerProcesses.append(p)
	
	for p in workerProcesses:
		p.join()



def timeFunc(func, input):
	t0 = time()
	output = func(input)
	print 'took %f seconds' % (time() - t0)
	return output

#curried avg_shared_terms for easy, kludgey timing
def ast10tc(numTrials):
	return avg_shared_terms(numTrials,10,citations=True)

def avg_tf_idf_shared_terms(numTrials, n, citations = True, texts_already_ordered = False, verbose = False):

	sh_terms = []
	selector = get_selector(texts_already_ordered)

	for i in range(numTrials):
		pat1, pat2 = selector.get_pair(citations)
		sh_terms += compareTopN(pat1, pat2, n)

	num_terms = len(sh_terms)
	if num_terms == 0:
		if verbose: print 'no shared terms found'
		return (0, 0)

	tot_src_tf_idf = sum(word['src_tf-idf'] for word in sh_terms)
	tot_ctd_tf_idf = sum(word['ctd_tf-idf'] for word in sh_terms)

	avg_src_tf_idf = tot_src_tf_idf / num_terms
	avg_ctd_tf_idf = tot_ctd_tf_idf / num_terms

	if verbose:
		print str(datetime.now())+': From %d cite pairs, %d shared terms were found in the top %d terms between parent and child. The average tf_idf of these shared terms in the cited patents (parents) was %f. The average tf_idf of these shared terms in the source patents (children) was %f.' %(num_terms, n, avg_ctd_tf_idf, avg_src_tf_idf)

	print 'sh_terms'
	return (avg_src_tf_idf, avg_ctd_tf_idf)


# saves a .csv of
# pno1 pno2 rank1 rank2
# for each term which is shared between a pair of patents
# if citations = True, pno1 signifies the child patent.
# rankI signifies the rank (1 - n) of the term in that patent's
# top-n tf-idf terms.
def shared_term_ranks(num_sh_terms, top_n, citations = True, texts_already_ordered = False, verbose = False, fname_suffix='', patCol_to_update=patns, write_freq = 1000):

	selector = get_selector(texts_already_ordered)
	sh_term_count = 0
	
	fname = 'sh_term_ranks_%s_topn=%d_num=%d%s' % (
												'cite-pairs' if citations else 'rand-pairs',
												top_n,
												num_sh_terms,
												fname_suffix
												)
	outf = open(fname + '.csv', 'a')
	def write_out(array, out):
		out.write(','.join( map(str, array) ) + '\n')
	
	# saves the header
	write_out(['pno1','pno2','rank1','rank2'], outf)


	while (sh_term_count < num_sh_terms):
		# if citations, p1 is the child, p2 the parent
		p1, p2 = selector.get_pair(citations)
		# each patent's top terms
		tts1, tts2 = topNTerms(p1, top_n, patCol_to_update), topNTerms(p2, top_n, patCol_to_update)

		# it's faster to see if a word is in a dict than an array
		tts1_lookup = { tts1[i]['word']: i for i in range(len(tts1)) }

		for i in range(len(tts2)):
			if tts2[i]['word'] in tts1_lookup:
				
				pno1 = p1['pno']
				pno2 = p2['pno']
				rank1 = tts1_lookup[tts2[i]['word']] + 1
				rank2 = i + 1
				
				write_out([pno1, pno2, rank1, rank2], outf)
				
				sh_term_count += 1
				if sh_term_count % write_freq == 0:
				# save the output by closing, reopening file
					outf.close()
					outf = open(fname + '.csv', 'a')
	outf.close()


# at Mark's request, returns an array of the number of terms which are
# the ith most important term for i from 1-n, for num samples patents.
# If from_cites, the patents will be chosen as following: a citation-link
# (parent/child pair) will be chosen from all citation-links
# in the database with equal probability, and those will be two of the
# patents sampled, repeatedly. Otherwise each patent sampled is chosen
# from all patents with equal probability
def top_n_rank_dist(n, num_samples, from_cites, patCol_to_update = False, texts_already_ordered=False, plot=True):

	# maybe an odd way of doing it, but allows for use of pyplot.hist
	# this code will only run once anyway
	# nth ranks is a list of all of the ranks that appear in a patent
	# it'll look like [1,2,...,n,1,2,...,n-1,1,2,...,n-3,1,2,...,n,1,2...]
	nth_ranks = []
	selector = get_selector(texts_already_ordered)

	def count_pat(p, nth_ranks):
		# the number, from 1-n, of terms in p's top n
		p_len = min(len(p['sorted_text']), n)
		nth_ranks += [i+1 for i in range(p_len)]
		return nth_ranks

	# patents are chosen two-at-a-time because that code's already
	# written. the %2 makes sure odd numbers are overshot, not under
	for i in range(num_samples/2 + num_samples%2):
		p1, p2 = selector.get_pair(from_cites)
		nth_ranks = count_pat(p1, nth_ranks)
		nth_ranks = count_pat(p2, nth_ranks)
	
	ranknums = [nth_ranks.count(i) for i in range(1,n+1)]
	cite_label = 'cite-pair' if from_cites else 'random'

	csv_module.save_csv(ranknums, 'rank_dist_%s_pats_topn=%d_num=%d' % (cite_label,n,num_samples))

	if plot:
		from matplotlib import pyplot as plt
		plt.hist(nth_ranks,n)
		plt.title('terms of rank i in the top %d terms of %d %s patents' % (n, num_samples, cite_label))
		plt.savefig('%_topn=%d_term_rank_dist.png')





