# MongoDB doesn't automatically allow for random selection from
# a database collection. This file adds a random index to each
# document in a collection, then indexes the collection by those
# numbers. To select a random doc, a new random number is chosen,
# and the database finds the document whose random index is closest.
# This also allows for random groups of docs to be easily chosen.

# Based closely on the StackOverflow question, "Random record from
# MongoDB," asked by user Will M. I implement user Michael's solution,
# but in pymongo and using bulk updates
# http://stackoverflow.com/questions/2824157/random-record-from-mongodb

# each doc in col is given a rand index

from pymongo import MongoClient, GEO2D
import random
from time import time

# 'coll' is a collection
def create_rand_ids(coll):

	# done in mongo's JS so the collection doesn't have to be
	# passed from mongod to python and back; this uses mongo's
	# random number generator, not python's
	
	code = '''
		var bulk = db.%(name)s.initializeUnorderedBulkOp()
		bulk.find({}).update( {$set: {rand_id: Math.random() } } )
		bulk.execute()
		''' % {'name': coll.name}



def index_rand_ids(coll):
	coll.ensure_index( 'rand_id' )

# Only performs well if coll is indexed by rand_id
def doc_near(coll, num, proj):
	if proj == {}:
		ret = coll.find_one( { 'rand_id' : {'$gte' : num} } )
		if not ret:
			return coll.find_one( { 'rand_id' : {'$lt' : num} } )
		else:
			return ret
	else:
		ret = coll.find_one( { 'rand_id' : {'$gte' : rand} }, num )
		if not ret:
			return coll.find_one( { 'rand_id' : {'$lt' : rand} }, num )
		else:
			return ret


def rand_doc(coll, proj = {}, randseed = time() % 10000):
	print 'seeding w ' + str(randseed % 10000)
	random.seed(randseed % 10000)
	rno = random.random()
	print 'rno is ' + str(rno)
	return doc_near(coll, rno, proj)

# Only performs well if coll is indexed by rand_id
def n_docs_near(n, coll, num):
	if proj == {}:
		ret = coll.find( { 'rand_id' : {'$gte' : num} } ).limit(n)
		if not ret:
			return coll.find( { 'rand_id' : {'$lt' : num} } ).limit(n)
		else:
			return ret
	else:
		ret = coll.find( { 'rand_id' : {'$gte' : rand} }, num ).limit(n)
		if not ret:
			return coll.find( { 'rand_id' : {'$lt' : rand} }, num ).limit(n)
		else:
			return ret

def n_rand_docs(n, coll, proj ={}, randseed = time()):
	random.seed(randseed)
	return n_docs_near(coll, random.rand(), proj)















