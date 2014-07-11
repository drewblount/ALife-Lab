

bulkExecuteFreq = 10000


# This makes some convenient assumptions: fromCol is of format {'_id': patentNumber, 'citedby': blah}
def copyBackCite(startPno, endPno, coreNum=0):
	totalBulkExecs = (endPno - startPno) / bulkExecuteFreq + 1
	
	for i in range(totalBulkExecs):
	
	start = startPno + i * bulkExecuteFreq
	end = min(endPno, startPno + (i+1) * bulkExecuteFreq)
	logging.info("%d: STARTING BATCH %d; PATNS %d-%d", coreNum, i, start, end)
	
	totalBulkExecs = (endPno - startPno) / bulkExecuteFreq + 1
	thisCollection = MongoClient()[dbname]['cite_net']
	
	logging.info("%d: Copying back-citations for patns %d-%d, using %d ordered bulk op executions, each back-citing %d patents.", coreNum, startPno, endPno, totalBulkExecs, bulkExecuteFreq)

	for i in range(totalBulkExecs):

def copyBackCites(fromCol, toCol):
