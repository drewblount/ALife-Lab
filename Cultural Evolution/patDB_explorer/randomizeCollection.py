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

from pymongo import MongoClient, GEO2D

# 'coll' is a collection
def create_random_index(coll):

	coll.ensure_index([('rand_id' , GEO2D)])
	
	# done in mongo's JS so the collection doesn't have to be
	# passed from mongod to python and back; this uses mongo's
	# random number generator, not python's
	
	
	code = '''
		var bulk = db.%(name)s.initializeUnorderedBulkOp()
		bulk.find({}).update( {$set: {rand_id: Math.random() } } )
		bulk.execute()
		''' % {'name': coll.name}

	code2 = '''
		db.%(name)s.update({}, {$set: {rand_id: Math.random() } }, {multi: true})
		''' % {'name': coll.name}

	code3 = '''
		%(full_name)s.find().forEach(function (obj) {
        obj.rand_id = Math.random();
        collection.save(obj);
		});
		}''' % {'name': coll.name}


		
