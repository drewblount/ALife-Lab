# Populates the patents' "citedby" lists


# CAREFUL: offset skips that many patents on each processor. Use with caution; check logs to make sure first few batches were empty (we only want to skip empty batches)
offset = 0

from pymongo import MongoClient, ASCENDING
import multiprocessing
import time
from datetime import datetime
import logging
from parallelMapInsert import parallelMapInsert

# These are all just the parameters I'm currently using on my
# local machine
client = MongoClient(host='127.0.0.1', port=27017)
dbname = 'patents'
patDB = client[dbname]
patents = patDB['patns']
client[dbname]['patns'].ensure_index( [ ('pno', 1) ] )
citeNetwork = patDB['cite_net']



# if pat_metadata (max and min pno) isn't stored, store it
if not patDB.pat_metadata.find_one({'_id': 'max_pno'}):
	import maxmin
	maxmin.storeMaxMinPno(patDB)

max_pno = patDB.pat_metadata.find_one({'_id': 'max_pno'})['val'] + 1
# + 1 because I treat upper pno bounds as exclusive, but lower inclusive
min_pno = patDB.pat_metadata.find_one({'_id': 'min_pno'})['val']


# For logging: copied from Andy's readPatnsFromFiles.py
fnLog = 'backCiteswNewCol.log'
frOutputData = 'html/data/'
logFormat = "%(asctime)s %(levelname)s %(processName)s\t%(message)s"
logging.basicConfig(filename=fnLog, level=logging.NOTSET, format = logFormat)

# First builds a new patent collection containing only the bare minimum info,
# so the whole thing can fit on memory


def storeCiteInfo(pat):
	# the last check should solve for duplicate errors
	if 'rawcites' in pat and 'pno' in pat and not citeNetwork.find_one( {'_id': pat['pno']} ):
		return( {'_id': pat['pno'], 'rawcites': pat['rawcites'], 'citedby': [] } )

def storeCiteNetwork():
	logging.info("Building the citation network")
	parallelMapInsert(func = storeCiteInfo,
					  in_collection  = patents,
					  out_collection = citeNetwork,
					  findArgs = {'spec': {}, 'fields': {'pno': 1, 'rawcites' : 1, '_id': 0} },
					  updateFreq = 1,
					  bSize = 10000)
	logging.info("Citation network built with parallelMapInsert")



bulkExecuteFreq = 10000


patents.ensure_index('pno')


pnos = max_pno - min_pno
# add one to the result so cpu_count * pnosPerProc is never < pnos
pnosPerProc = pnos / multiprocessing.cpu_count() + 1

# covers patents for which startPno <= pno < endPno
# coreNum is used for logging
def backCite(startPno, endPno, coreNum=0):
	

	startPno = startPno + offset
	
	totalBulkExecs = (endPno - startPno) / bulkExecuteFreq + 1
	thisCollection = MongoClient()[dbname]['cite_net']
	
	logging.info("%d: Drawing undrawn back-citations for patns %d-%d, using %d ordered bulk op executions, each back-citing %d patents.", coreNum, startPno, endPno, totalBulkExecs, bulkExecuteFreq)


	for i in range(totalBulkExecs):

		start = startPno + i * bulkExecuteFreq
		end = min(endPno, startPno + (i+1) * bulkExecuteFreq)
		logging.info("%d: STARTING BATCH %d; PATNS %d-%d", coreNum, i, start, end)
		# hopefully including 'citedby' will prevent mongod from digging through the HD to do each citedby update'
		# need to generate a new cursor for each bulk execution because cursors time out during bulk execs
		logging.info("%d: Requesting cursor.", coreNum)
		# bCited: null selects only those citatinos that haven't been back-cited yet, and have no defined bCited field
		thesePats = thisCollection.find({'_id' : {'$gte' : start, '$lt': end}, 'bCited': None },
										{'rawcites':1, '_id':1} ) #.batch_size(100000)
		logging.info("%d: Cursor retrieved; initializing ordered bulk op", coreNum)
		bulk = thisCollection.initialize_ordered_bulk_op()
		count = 0
		logging.info("%d: Bulk op retrieved; searching through cursor for patns with undrawn back-cites", coreNum)
		anyToAdd = False
		for citingPatn in thesePats:
			# makes sure not to redraw citations
			if 'bCited' not in citingPatn or citingPatn['bCited'] != True:
				count += 1
				citingNo = citingPatn['_id']
				
				bulk.find( {'_id' : {'$in' : citingPatn['rawcites'] } } ).update( {'$push' : {'citedby': citingNo} } )
				#
				bulk.find( {'_id' : citingNo} ).update_one( {'$set': {'bCited' : True} })

		if count > 1:
			logging.info("%d: %d patns with undrawn back-cites found; sending bulk.execute()", coreNum, count)
			bulk.execute()
			logging.info("%d: Execution complete", coreNum)

		else:
			logging.info("%d: No undrawn back-cites found", coreNum)

	logging.info("%d: DONE DRAWING BACK-CITES **********", coreNum)


def drawBackCites(patCol):
	workerProcesses = []
	for i in range(0, multiprocessing.cpu_count()):
			# Load only the pno and rawcites from each patent, sort by pno so progress reports are possible
		# limiting batch_size to keep memory down, reduce timeouts
		p = multiprocessing.Process(target = backCite, args = (min_pno + i * pnosPerProc, min_pno + (i+1) * pnosPerProc, i+1) )
		p.daemon = True
		p.start()
		workerProcesses.append(p)

	for p in workerProcesses:
		p.join()


def main():
	# patDB.eval('''db.runCommand({ touch: "cite_net", data: true, index: true })''')
	
	storeCiteNetwork()
	print "loading cite_network into memory with mongo db.touch."
	logging.info("loading cite_network into memory with mongo db.touch.")
	patDB.eval('''db.runCommand({ touch: "cite_net", data: true, index: true })''')
	print "cite_net in memory"
	logging.info("cite_net in memory")
	drawBackCites(citeNetwork)
	print "back_cites drawn" #; copying to main db"
	logging.info("back_cites drawn") #; copying to main db")


if __name__ == '__main__':
	main()









