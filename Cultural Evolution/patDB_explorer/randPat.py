
# a random patent selector. 'projection' is a mongodb projection
# which describes which fields to return; if left {} the entire
# patent will be returned.

# buf_size is the number of citation links {src: pno, cte: pno} are
# stored by the selector at a time (to reduce calls to the cite db)

from pymongo  import MongoClient, ASCENDING, DESCENDING
from bson.code import Code
import random
from randomizeCollection import rand_doc, n_rand_docs
from time import time


patDB = MongoClient().patents
patns = patDB.patns
just_cites = patDB.just_cites

patns.ensure_index('pno')


#	def rand_cite_pair(self):

def return_true(input): return True

# kludgey; work-around for the bizarre fact that some patents in the db
# don't have tf-idfs stored

def has_tf_idfs(pat):
	if 'text' not in pat: return False
	for word in pat['text']:
		if 'tf-idf' in pat['text'][word]: return True
		else: return False

def has_sorted_text(pat):
	if 'sorted_text' not in pat: return False
	else: return True



# a random patent selector. 'projection' is a mongodb projection
# which describes which fields to return; if left {} the entire
# patent will be returned.

# buf_size is the number of citation links {src: pno, cte: pno} are
# stored by the selector at a time (to reduce calls to the cite db)
class Selector(object):
	
	def __init__(self, patCol = patns, projection = {'_id':0}, rand_seed = time(), db = patDB, verbose = False, buf_size = 10000):
		
		if not db.pat_metadata.find_one({'_id': 'max_pno'}):
			import maxmin
			maxmin.storeMaxMinPno(db)
		
		self.max_pno = db.pat_metadata.find_one({'_id': 'max_pno'})['val']
		self.min_pno = db.pat_metadata.find_one({'_id': 'min_pno'})['val']
		self.verbose = verbose
		
		patCol.ensure_index('pno')
		
		
		# default randSeed is system time
		random.seed(rand_seed)
		
		self.col = patCol
		self.proj = projection
		self.cite_buf_size = buf_size
			
		self.rand_cites = n_rand_docs( buf_size, just_cites )

	
	
	# randomly chooses a patent number in the pno range covered by
	# the patent collection
	# Set retryIfAbsent to False if the collection contains relatively
	# few pnos between min_pno and max_pno; this results in a non-uniform
	# random distribution
	# enforce_func is a boolean function which must eval to tr
	def rand_pat(self, retryIfAbsent=True, enforce_func=has_sorted_text):
		rand_pno = random.randint(self.min_pno, self.max_pno)
		if self.verbose: print 'rand pno is ' + str(rand_pno)
		randy = self.col.find_one( {'pno' : rand_pno}, self.proj)
		if retryIfAbsent:
			while not randy or not enforce_func(randy):
				rand_pno = random.randint(self.min_pno, self.max_pno)
				if self.verbose: print 'rand pno is ' + str(rand_pno)
				randy = self.col.find_one( {'pno' : rand_pno}, self.proj)
				if self.verbose and randy: print str(enforce_func(randy))
		return randy
	
	# Allows you to choose two different patents at random, checking that
	# you don't accidentally choose the same one twice
	def rand_pair(self):
		pat1 = self.rand_pat()
		pat2 = self.rand_pat()
		while pat1['pno'] == pat2['pno']:
			pat2 = self.rand_pat()
		return pat1, pat2
	
	# given a just_cite doc of the form {src: pno, cte: pno},
	# returns both patents
	def just_cite_to_patns(self, cite):
		source = patns.find_one({'pno':cite['src']}, self.proj)
		cited  = patns.find_one({'pno':cite['ctd']}, self.proj)
		return (source, cited)
	
	def stock_n_cite_pairs(self, n):
		self.rand_cites = n_rand_docs( n, just_cites )
	
	# depending on the input arg, returns rand_pair or rand_cite
	def get_pair(self, is_citepair):
		if is_citepair:
			return self.get_rand_cite()
		else:
			return self.rand_pair()

	# enforce_func is a boolean test each patent must pass to be
	# returned
	def get_rand_cite(self, enforce_func = has_sorted_text):
		if not self.rand_cites.alive:
			self.stock_n_cite_pairs(self.cite_buf_size)

		# I don't get it--I'm getting an empty cursor error on the
		# following line, but the above line should prevent that
		citation = self.rand_cites.next()
		p1, p2 = self.just_cite_to_patns(citation)
		
		if enforce_func(p1) and enforce_func(p2): return (p1,p2)
		# Try again if one of the patents fails the required test
		else:
			if self.verbose: print 'retry'
			return self.get_rand_cite(enforce_func)

	def rand_pnos(self, n, sort = False):
		pnos = random.sample( range( self.min_pno, self.max_pno ), n )
		if sort: pnos = sorted(pnos)
		return pnos



