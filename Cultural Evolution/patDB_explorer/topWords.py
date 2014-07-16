# Memory optimization to-do: make it so unsorted text isn't always passed
# around

# Goal: order the words in a patent's text field by tf-idf (descending)

# python treats dictionaries as unordered, and it's awkward to reorder
# MongoDB's BSON objects, so I use a python array of dicts to hold the text
# while I shuffle it around

from pymongo  import MongoClient
from operator import attrgetter
import randPat
import time


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


def orderAllTexts(disp= False, showN= 10):
	pats = patns.find({}, {'pno':1, 'title': 1, 'text': 1, 'sorted_text': 1})
	for pat in pats:
		topNTerms(pat, showN, display=disp, patCol_to_update=patns)


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
def avg_shared_terms(numTrials, n, citations = False, texts_already_ordered = False, verbose = False, enforce_fields = []):
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













