from pymongo  import MongoClient, ASCENDING, DESCENDING
from bson.code import Code
import random

patDB = MongoClient().patents
patns = patDB.patns

patns.ensure_index('pno')

minPno = patDB

# a random patent selector. 'projection' is a mongodb projection
# which describes which fields to return; if left {} the entire
# patent will be returned.
class Selector(object):
	
	def __init__(self, patCol, projection = {'_id':0}, randSeed = None, db = patDB):
	
		print 'gettin max'
		self.maxPno = patCol.find({},{'pno': 1, '_id': 0}).sort('pno',DESCENDING)[0]['pno']
		print 'max is ' + str(self.maxPno)

		print 'gettin min'
		self.minPno = patCol.find({},{'pno': 1, '_id': 0}).sort('pno',ASCENDING)[0]['pno']


		print 'min is ' + str(self.minPno)


		patCol.ensure_index('pno', ASCENDING)
		
		
		# default randSeed is system time
		random.seed(randSeed)

		self.col = patCol
		self.proj = projection


	# randomly chooses a patent number in the pno range covered by
	# the patent collection
	# Set retryIfAbsent to False if the collection contains relatively
	# few pnos between minPno and maxPno; this results in a non-uniform
	# random distribution
	def randPat(self, retryIfAbsent=True):
		randPno = random.randint(self.minPno, self.maxPno)
		print 'rand pno is ' + str(randPno)
		if retryIfAbsent:
			while not self.col.find_one( {'pno' : randPno}, {'pno': 1, '_id': 0}):
				randPno = random.randint(self.minPno, self.maxPno)
			return self.col.find_one( {'pno' : randPno}, self.proj )
		else:
			return self.col.find_one( {'pno' : {'$gte': randPno} }, self.proj )

	# in case that patent num is not in the collection, this finds
	# the number that is closest above it

	# randomly chooses a patent, then a patent that it cited (or, if backwardbias=True,
	# randomly chooses a cited patent, then one that cited it)
	# Note that this does not sample all citation links uniformly, as the citations of
	# a patent with few total citations are more likely to be chosen than those of
	# patents with many total citations
	def naiveRandomCitePair():
		p1 = self.randPat()
		while not rawcites in p1:
			p1 = self.randPat()
		
		
'''
	# starting in a random place in the cite list, finds a random citation
	def randomCitation(patn):
		citelen = len(patn['rawcites'])
		if citelen == 0:
			print 'error, no citations available for patn %d', patn['pno']
		
		offset = random.randint(0,len(patn['rawcites']))
		for cite in range(citelen):
			out = self.col.find_one( {'pno' : patn['rawcites'][(patn + cite) % citelen]

'''

