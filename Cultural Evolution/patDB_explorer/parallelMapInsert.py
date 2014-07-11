import multiprocessing
from pymongo import MongoClient
import random

# # # # PARALLEL MAP + INSERT # # # #
# Just like my tf-idf--pymongo/parallelMap.py, but takes the output of func
# and inserts it into out_collection rather than updating in_collection
def parallelMapInsert(func, in_collection, out_collection, findArgs = {'spec':{},'fields':{}}, bSize = -1, waitToFinish = True, updateFreq = 1, bulkOrdered = False, staggerThreads = True):

	# partFunc will be applied to each subset of the in_collection

	if updateFreq > 1:
		# use a bulk updater (rseed lets me pass a random seed optionally)
		
		def partFunc(cursor):

			# generates an appropriate bulk updater
			def assignBulk():
				if bulkOrdered:
					outBulk = out_collection.initialize_ordered_bulk_op()
				else:
					outBulk = out_collection.initialize_unordered_bulk_op()
				return outBulk
			
			bulk = assignBulk()

			updateNum = 0
			if staggerThreads:
				updateNum += random.randint(0, updateFreq - 1)

			for item in cursor:
				updateNum += 1
				# update item in the db, adding a field for the output of func(item)
				out = func(item)
				if out: bulk.insert(out, continue_on_error=True)
				if updateNum == updateFreq:
					# every updateFreq number of updates, sends a batch to the db.
					try: bulk.execute()
					# if for some reason bulk is empty we get an InvalidOperation
					except TypeError: pass
					else: pass
					# I was getting errors that 'Bulk options can only be executed once'
					bulk = assignBulk()
					updateNum = 0
			# make sure a final execute is done
			try: bulk.execute()
			except TypeError: pass
			except BulkWriteError: pass
			else: pass
	else:
		def partFunc(cursor):
			for item in cursor:
				out = func(item)
				if out: out_collection.insert(out)


	# Adapted from Andy Buchanan's readPatnsFromFiles.py
	workerProcesses = []
	# add one to the result so cpu_count * partSize is never < in_collection.count()
	partSize = in_collection.count()/multiprocessing.cpu_count() + 1
	for i in range(0, multiprocessing.cpu_count()):
		# [a : b] partitions the result of find into the closed-open interval [a, b)
		# if batch size hasn't been set, don't limit it
		# print 'ith part should be entries ' + str(i*partSize) + '-' + str((i+1)*partSize)
		if bSize < 0:
			partCursor = in_collection.find(findArgs['spec'], findArgs['fields'])[i*partSize : (i+1)*partSize]
			'partCursor size = ' + str(partCursor.count())
		
		else:
			partCursor = in_collection.find(findArgs['spec'], findArgs['fields'])[i*partSize : (i+1)*partSize].batch_size(bSize)
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
