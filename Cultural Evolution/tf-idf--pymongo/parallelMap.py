import multiprocessing
from pymongo import MongoClient

# # # # PARALLEL MAP # # # #
# In need of an easy and parallel way to apply a function to each
# document in the database, I'll just make a simplistic one myself.
# collection is partitioned into #processor equal-sized chunks,
# each processor applies func across that partition

# ASSUMED: one processor adding fields to a document in collection
# won't change the document index from 0 to (collection.count() - 1)

# INPUT ARGUMENTS: The goal is to map func over collection and update the results into collection
# func: a function which takes an item in the collection and returns an update arg (labeled, like findArgs)
# collection: that to be mapped over
# findArgs: a dict for pymongo.collection.find's argument containing keys 'spec' and 'fields'
# bSize: if set above zero, determines the batch size of each find(), else bsize unlimited
# waitToFinish: if true, the function returns when all workers have joined after
#				completing their tasks, else returns after sending workers
# updateFreq: if more than one, loads all updates into a pymongo bulk_op
# bulkOrdered: if using a bulk_op, determines if that op should be ordered


def parallelMap(func, collection, findArgs = {'spec':{},'fields':{}}, bSize = -1, waitToFinish = True, updateFreq = 1, bulkOrdered = False):

	# if updateFreq > 1, my 'update' function adds an update to the idNum element to a bulk updater,
	# and tells that updater to execute its bulk updates every
	# updateFreq calls of the function.
		
		
	if updateFreq > 1:
		if bulkOrdered: bulk = collection.initialize_ordered_bulk_op()
		else:           bulk = collection.initialize_unordered_bulk_op()
		def bulkUpdate(idNum, param, commit):
			
			updateNum += 1
			if commit:
				bulk.execute()

	# Otherwise, my 'update' function simply calls collection.update
	else:
		def update(idNum, param):
			collection.update({'_id': idNum}, param, {'multi': False})

	# This will be applied to everything in the collection

	if updateFreq > 1:
		# use a bulk updater
		def partFunc(cursor):
			
			if bulkOrdered: bulk = collection.initialize_ordered_bulk_op()
			else:           bulk = collection.initialize_unordered_bulk_op()
			
			updateNum = 0
			realNum = 0
			for item in cursor:
				updateNum += 1
				realNum += 1
				# update item in the db, adding a field for the output of func(item)
				bulk.find({'_id': item['_id']}).update_one(func(item))
				if updateNum == updateFreq:
					# every updateFreq number of updates, sends a batch to the db.
					bulk.execute()
					updateNum = 0
			# make sure a final execute is done
			bulk.execute()
			print 'This processor\'s partFunc was called ' + str(realNum) + ' times.'

	else:
		def partFunc(cursor):
			for item in cursor:
				out = func(item)
				collection.update({'_id': item['_id']}, func(item))


	# Adapted from Andy Buchanan's readPatnsFromFiles.py
	workerProcesses = []
	# add one to the result so cpu_count * partSize is never < collection.count()
	partSize = collection.count()/multiprocessing.cpu_count() + 1
	print 'partSize = ' + str(partSize)
	for i in range(0, multiprocessing.cpu_count()):
		# [a : b] partitions the result of find into the closed-open interval [a, b)
		# if batch size hasn't been set, don't limit it
		print 'ith part should be entries ' + str(i*partSize) + '-' + str((i+1)*partSize)
		if bSize < 0:
			partCursor = collection.find(findArgs['spec'], findArgs['fields'])[i*partSize : (i+1)*partSize]
			'partCursor size = ' + str(partCursor.count())
		
		else:
			partCursor = collection.find(findArgs['spec'], findArgs['fields'])[i*partSize : (i+1)*partSize].batch_size(bSize)
			'partCursor size = ' + str(partCursor.count())
		print 'partCursor size = ' + str(partCursor.count())
		
		p = multiprocessing.Process(target=partFunc, args=(partCursor,))
		#p = multiprocessing.Process(target=testFun, args=(i, ))
		p.daemon = True
		p.start()
		workerProcesses.append(p)

	if waitToFinish :
		for p in workerProcesses:
			p.join()

	return
