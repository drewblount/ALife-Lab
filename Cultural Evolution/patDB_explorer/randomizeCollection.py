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
from datetime import datetime
from parallelMap import parallelMap

# 'coll' is a collection
def create_rand_ids(coll, db = MongoClient().patents):
	
	# done in mongo's JS so the collection doesn't have to be
	# passed from mongod to python and back; this uses mongo's
	# random number generator, not python's
	
	code = '''
		db.%(name)s.find({},{_id:1}).forEach( function(doc) { db.cite_net.update({_id:doc._id},{$set : {"rand_id":Math.random()}}) })
		''' % {'name': coll.name}

	db.eval(code)

def return_rand_id(doc):
	return {'$set': {'rand_id' : random.random() } }

def parallel_rand_ids(coll, verbose = False):
	t0 = time()
	parallelMap(return_rand_id,
				in_collection = coll,
				out_collection= coll,
				findArgs = {'spec': {}, 'fields': {'_id': 1}},
				updateFreq = 100)
	t1 = time()
	dt = t1 - t0
	
	if verbose: print ('took %f seconds; if the db was of size 40 mil, translates to %f minutes') % (dt, dt*40000000/coll.count()/60 )

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
def n_docs_near(n, coll, num, proj, verbose = False):
	
	
	if proj == {}:
		ret = coll.find( { 'rand_id' : {'$gte' : num} } ).limit(n)
		if not ret:
			if verbose: print ret.count()
			return coll.find( { 'rand_id' : {'$lt' : num} } ).limit(n)
		else:
			if verbose: print ret.count()
			return ret
	else:
		ret = coll.find( { 'rand_id' : {'$gte' : rand} }, num ).limit(n)
		if not ret:
			if verbose: print ret.count()
			return coll.find( { 'rand_id' : {'$lt' : rand} }, num ).limit(n)
		else:
			if verbose: print ret.count()
			return ret

def n_rand_docs(n, coll, randseed = time(), proj = {}, verbose = True):
	random.seed(randseed)
	return n_docs_near(n, coll, random.random(), proj)






