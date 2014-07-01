import multiprocessing
from pymongo import MongoClient
import random

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
# staggerThreads: a helpful kludge. A thread gets into a rhythm of calling mongod to
#	do something while twiddling its thumbs, then working really hard while mongod twiddles.
#	if staggerThreads, each thread will start this cycle at a random time in its period, avoiding
#	bank-rush type scenarios but maybe not making much of a difference runtime-wise

def parallelMap(func, collection, findArgs = {'spec':{},'fields':{}}, bSize = -1, waitToFinish = True, updateFreq = 1, bulkOrdered = False, staggerThreads = True):

	# partFunc will be applied to each subset of the collection

	if updateFreq > 1:
		# use a bulk updater (rseed lets me pass a random seed optionally)
		
		def partFunc(cursor):

			# generates an appropriate bulk updater
			def assignBulk():
				if bulkOrdered: outBulk = collection.initialize_ordered_bulk_op()
				else:           outBulk = collection.initialize_unordered_bulk_op()
				return outBulk
			
			bulk = assignBulk()

			updateNum = 0
			if staggerThreads:
				updateNum += random.randint(0, updateFreq - 1)

			for item in cursor:
				updateNum += 1
				# update item in the db, adding a field for the output of func(item)
				bulk.find({'_id': item['_id']}).update_one(func(item))
				if updateNum == updateFreq:
					# every updateFreq number of updates, sends a batch to the db.
					bulk.execute()
					# I was getting errors that 'Bulk options can only be executed once'
					bulk = assignBulk()
					updateNum = 0
			# make sure a final execute is done
			bulk.execute()

	else:
		def partFunc(cursor):
			for item in cursor:
				out = func(item)
				collection.update({'_id': item['_id']}, func(item))


	# Adapted from Andy Buchanan's readPatnsFromFiles.py
	workerProcesses = []
	# add one to the result so cpu_count * partSize is never < collection.count()
	partSize = collection.count()/multiprocessing.cpu_count() + 1
	for i in range(0, multiprocessing.cpu_count()):
		# [a : b] partitions the result of find into the closed-open interval [a, b)
		# if batch size hasn't been set, don't limit it
		# print 'ith part should be entries ' + str(i*partSize) + '-' + str((i+1)*partSize)
		if bSize < 0:
			partCursor = collection.find(findArgs['spec'], findArgs['fields'])[i*partSize : (i+1)*partSize]
			'partCursor size = ' + str(partCursor.count())
		
		else:
			partCursor = collection.find(findArgs['spec'], findArgs['fields'])[i*partSize : (i+1)*partSize].batch_size(bSize)
			'partCursor size = ' + str(partCursor.count())
		# print 'partCursor size = ' + str(partCursor.count())
		
		p = multiprocessing.Process(target=partFunc, args=(partCursor,))
		#p = multiprocessing.Process(target=testFun, args=(i, ))
		p.daemon = True
		p.start()
		workerProcesses.append(p)

	if waitToFinish :
		for p in workerProcesses:
			p.join()

	return
