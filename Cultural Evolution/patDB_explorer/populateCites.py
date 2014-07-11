# Populates the patents' "citedby" lists


# CAREFUL: offset skips that many patents on each processor. Use with caution; check logs to make sure first few batches were empty (we only want to skip empty batches)
offset = 100000

from pymongo import MongoClient
import multiprocessing
import time
from datetime import datetime
import logging


# For logging: copied from Andy's readPatnsFromFiles.py
fnLog = 'backCites.log'
frOutputData = 'html/data/'
logFormat = "%(asctime)s %(levelname)s %(processName)s\t%(message)s"
logging.basicConfig(filename=fnLog, level=logging.NOTSET, format = logFormat)



# These are all just the parameters I'm currently using on my
# local machine
client = MongoClient(host='127.0.0.1', port=27017)
dbname = 'patents'
patDB = client[dbname]
patents = patDB['patns']
client[dbname]['patns'].ensure_index( [ ('pno', 1) ] )


# This might force mongod into only keeping what we need in memory
initialCursor = patents.find({},{'rawcites':1, 'pno':1, 'backCitesDrawn':1, 'citedby':1, '_id': 0})

bulkExecuteFreq = 10000


patents.ensure_index('pno')

# if pat_metadata (max and min pno) isn't stored, store it
if not patDB.pat_metadata.find_one({'_id': 'max_pno'}):
	import maxmin
	maxmin.storeMaxMinPno(patDB)
	
max_pno = patDB.pat_metadata.find_one({'_id': 'max_pno'})['val'] + 1
# + 1 because I treat upper pno bounds as exclusive, but lower inclusive
min_pno = patDB.pat_metadata.find_one({'_id': 'min_pno'})['val']

pnos = max_pno - min_pno
# add one to the result so cpu_count * pnosPerProc is never < pnos
pnosPerProc = pnos / multiprocessing.cpu_count() + 1

addToSetUntil = 4600000


def backCiteNoBulk(thesePats):
	count = 0
	lastTime = time.time()
	for citingPatn in thesePats:
		# makes sure not to redraw citations
		if 'backCitesDrawn' not in citingPatn or citingPatn['backCitesDrawn'] == False:
			count += 1
			citingNo = citingPatn['pno']
			if count == bulkExecuteFreq:
				thisTime = time.time()
				print 'db-dumping the ' + str(bulkExecuteFreq) + ' patents until ' + str (citingNo)
				print 'took about ' + str(thisTime - lastTime) + ' seconds'
				lastTime = thisTime
				count = 0

			if citingNo < addToSetUntil:
				patents.update( {'pno' : {'$in' : citingPatn['rawcites'] } } ,{'$addToSet' : {'citedby': citingNo} } , multi = True )
			else:
				patents.update( {'pno' : {'$in' : citingPatn['rawcites'] } } ,{'$push' : {'citedby': citingNo} }, multi = True )
			patents.update( {'pno' : citingNo}, {'$set': {'backCitesDrawn' : True} })

	''' Seems like the above option would be faster, but I'm not sure
			if citingNo < addToSetUntil:
				for citedNo in citingPatn['rawcites'] :
					# addToSet makes sure not to add duplicates
					bulk.find( {'pno' : {'$in' : citingPatn['rawcites']} ).update_one( {'$addToSet' : {'citedby': citingNo} } )
			else:
				for citedPNo in citingPatn['rawcites'] :
					# 'bulk' will (in theory) execute all of these update_ones in parallel, in nondeterministic order
					bulk.find( {'pno' : citedNo} ).update_one( {'$push' : {'citedby': citingNo} } )
					'''
# covers patents for which startPno <= pno < endPno
# coreNum is used for logging
def backCite(startPno, endPno, coreNum=0):
	

	startPno = startPno + offset
	
	totalBulkExecs = (endPno - startPno) / bulkExecuteFreq + 1
	thisCollection = MongoClient()[dbname]['patns']
	lastTime = time.time()
	
	logging.info("%d: Drawing undrawn back-citations for patns %d-%d, using %d ordered bulk op executions, each back-citing %d patents.", coreNum, startPno, endPno, totalBulkExecs, bulkExecuteFreq)


	for i in range(totalBulkExecs):

		start = startPno + i * bulkExecuteFreq
		end = min(endPno, startPno + (i+1) * bulkExecuteFreq)
		logging.info("%d: STARTING BATCH %d; PATNS %d-%d", coreNum, i, start, end)
		# hopefully including 'citedby' will prevent mongod from digging through the HD to do each citedby update'
		# need to generate a new cursor for each bulk execution because cursors time out during bulk execs
		logging.info("%d: Requesting cursor.", coreNum)
		thesePats = thisCollection.find({'pno' : {'$gte' : start, '$lt': end} },
										{'rawcites':1, 'pno':1, 'backCitesDrawn':1, 'citedby':1} ) #.batch_size(100000)
		logging.info("%d: Cursor retrieved; initializing ordered bulk op", coreNum)
		bulk = thisCollection.initialize_ordered_bulk_op()
		count = 0
		logging.info("%d: Bulk op retrieved; searching through cursor for patns with undrawn back-cites", coreNum)
		anyToAdd = False
		for citingPatn in thesePats:
			# makes sure not to redraw citations
			if 'backCitesDrawn' not in citingPatn or citingPatn['backCitesDrawn'] == False:
				count += 1
				citingNo = citingPatn['pno']
				
				bulk.find( {'pno' : {'$in' : citingPatn['rawcites'] } } ).update( {'$push' : {'citedby': citingNo} } )
				bulk.find( {'pno' : citingNo} ).update_one( {'$set': {'backCitesDrawn' : True} })

		if count > 1:
			logging.info("%d: %d patns with undrawn back-cites found; sending bulk.execute()", coreNum, count)
			bulk.execute()
			logging.info("%d: Execution complete", coreNum)

		else:
			logging.info("%d: No undrawn back-cites found", coreNum)



workerProcesses = []
for i in range(0, multiprocessing.cpu_count()):
	# Load only the pno and rawcites from each patent, sort by pno so progress reports are possible
	# limiting batch_size to keep memory down, reduce timeouts
	curs = patents.find({'pno' : {'$gte' : min_pno + i * pnosPerProc, '$lt': min_pno + (i+1) * pnosPerProc} },
						{'rawcites':1, 'pno':1, 'backCitesDrawn':1} ).batch_size(100000)
	p = multiprocessing.Process(target = backCite, args = (min_pno + i * pnosPerProc, min_pno + (i+1) * pnosPerProc, i+1) )
	p.daemon = True
	p.start()
	workerProcesses.append(p)

for p in workerProcesses:
	p.join()
