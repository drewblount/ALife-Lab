# topWords.py has been good to me, and has produced a lot of the
# interesting results we've seen this summer

# but it's become long and disorganized

# this is an attempt to provide a lot of the functionality
# of topWords.py, but in a functionalish, modular, and so
# easily extensible package

# it's all about the class pair_data (couldn't think
# of a good name)
#
# which has two functional parts:
#
#	get_pair  (pair selector): a function which, when called,
#	returns a list (pat1, pat2) tuples. This list can be of
#	any length, but it must be a LIST of TUPLES (pairs).
#
#	proc_pair (pair processor): takes a pair of patents (as they
#	are returned from the db) and returns a list of dictionaries,
#	e.g. [{pno1: x, pno2: y, sh_rank1: n, sh_rank2: m}]
#
#	an object of type pair_data has a get(n) method that gets an
#	n-length array of outputs of proc_pair called on the output
#	of get_pair
#	write(n) will call get(n) and write the output to .csv
#	with column names derived from the dict keys (assumed to
#	be the same for each output of proc_pair)

from pymongo import MongoClient
import csv_module
from topWords import get_selector, topNTerms

patDB = MongoClient().patents
patns = patDB.patns


class Pair_data(object):

	def __init__(self, get_pair, proc_pair, fname=''):
				
		# a function that returns a list of patent-pair tuples
		self.get_pair  = get_pair
		# a function that turns a pat-pair tuple into a dict of output data
		self.proc_pair = proc_pair

		self.pair_stack = self.get_pair()
		self.output = []
		self.fname = fname


	def clear_output(self):
		self.output = []
		
	def get(self, n, refresh=False):
		if refresh: self.clear_output()
		
		# below equivalent to "while len(self.output) < n"
		outl = len(self.output)
		while outl < n:
			p1, p2 = self.get_pair()
			out    = self.proc_pair(p1, p2)
			if out != []: self.output += out
			outl += len(out)

	def write(self, n, refresh=False, write_freq=None, reset_fname=None):
		
		if reset_fname:
			self.fname = reset_fname
		
		outfname = self.fname + '_pdata_n=%d' % n

		self.get(n, refresh)
		out_arr = []
		# out_arr[0] is set to the column names
		# every elt in out_arr is assumed to have the same
		# keys
		keys = self.output[0].keys()
		out_arr.append(keys)

		for i in range(1, n):
			out_arr.append([self.output[i][key] for key in keys])

			if write_freq and i % write_freq == 0:
				csv_module.save_multi_csv(out_arr,outfname)
				out_arr=[]
				
		csv_module.save_multi_csv(out_arr,outfname,overwrite=False)


# as a proof of this framework, here's a refactoring of
# topWords.shared_term_ranks
def sh_term_ranks(top_n, cites, fname=''):

	# from randPat.py via topWords.get_selector()
	rand_pat_sel  = get_selector()

	def get_pair():
		return rand_pat_sel.get_pair(cites)
		

	def proc_pair(p1, p2):
		# gets top terms from topWords.topNTerms
		tts1, tts2 = topNTerms(p1, top_n), topNTerms(p2, top_n)

		# it's faster to see if a word is in a dict than an array
		tts1_lookup = { tts1[i]['word']: i for i in range(len(tts1)) }

		p1_labl = 'child'  if cites else 'pno1'
		p2_labl = 'parent' if cites else 'pno2'
		r1_labl, r2_labl = p1_labl+'-rank', p2_labl+'-rank'

		out_arr=[]
		for i in range(len(tts2)):
			if tts2[i]['word'] in tts1_lookup:
				pno1 = p1['pno']
				pno2 = p2['pno']
				rank1 = tts1_lookup[tts2[i]['word']] + 1
				rank2 = i + 1
				out_arr.append({p1_labl: pno1, p2_labl: pno2, r1_labl:rank1, r2_labl:rank2})
		return out_arr

	return Pair_data(get_pair, proc_pair, fname)


















