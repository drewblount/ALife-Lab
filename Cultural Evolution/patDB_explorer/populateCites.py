# Populates the patents' "citedby" lists

from pymongo import MongoClient
import multiprocessing

# These are all just the parameters I'm currently using on my
# local machine
client = MongoClient(host='127.0.0.1', port=27017)
dbname = 'patents'
patDB = client[dbname]
patents = patDB['patns']
client[dbname]['patns'].ensure_index( [ ('pno', 1) ] )


bulkExecuteFreq = 10000


patents.ensure_index('pno')

# if pat_metadata (max and min pno) isn't stored, store it
if not patDB.pat_metadata.find_one({'_id': 'max_pno'}):
	import maxmin
	maxmin.storeMaxMinPno(PatDB)
	
max_pno = patDB.pat_metadata.find_one({'_id': 'max_pno'})['val']
min_pno = patDB.pat_metadata.find_one({'_id': 'min_pno'})['val']

pnos = max_pno - min_pno + 1
# add one to the result so cpu_count * pnosPerProc is never < pnos
pnosPerProc = pnos / multiprocessing.cpu_count() + 1


workerProcesses = []


def backCite(thesePats)
	bulk = client[dbname]['patns'].initialize_unordered_bulk_op()
	count = 0
	for citingPatn in thesePats:
		count += 1
		citingNo = citingPatn['pno']
		if count == bulkExecuteFreq:
			print 'db-dumping the ' + str(bulkExecuteFreq) ' patents until ' + str (citingNo)
			bulk.execute()
			bulk = client[dbname]['patns'].initialize_unordered_bulk_op()
			count = 0
		
		if citingNo < addToSetUntil:
			for citedNo in citingPatn['rawcites'] :
				# addToSet makes sure not to add duplicates
				bulk.find( {'pno' : citedNo} ).update_one( {'$addToSet' : {'citedby': citingNo} } )
		else:
			for citedPNo in citingPatn['rawcites'] :
				# 'bulk' will (in theory) execute all of these update_ones in parallel, in nondeterministic order
				bulk.find( {'pno' : citedNo} ).update_one( {'$push' : {'citedby': citingNo} } )
		
		bulk.find( {'pno' : citingNo} ).update_one( {'$set': {'backCitesDrawn' : True} })
			
	bulk.execute()



for i in range(0, multiprocessing.cpu_count()):
	# Load only the pno and rawcites from each patent, sort by pno so progress reports are possible
	# limiting batch_size to keep memory down, reduce timeouts
	curs = patents.find({'pno' : {'$gte' : min_pno + i * pnosPerProc, '$lt': min_pno + (i+1) * pnosPerProc} },
						{'rawcites':1, 'pno':1} ).batch_size(10000)

for p in workerProcesses:
	p.join()
