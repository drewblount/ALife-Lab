# Populates the patents' "citedby" lists

from pymongo import MongoClient

# These are all just the parameters I'm currently using on my
# local machine
client = MongoClient(host='127.0.0.1', port=27017)
dbname = 'patents'
patents = client[dbname]['patns']
client[dbname]['patns'].ensure_index( [ ('pno', 1) ] )

# Below doesn't work, not sure why, but I just made the index in the mongo shell
# TODO: ensure that the following ensure ensures the index

# for printing progress reports
landmarkPno = 4000000

# hopefully allows parallelization
bulk = client[dbname]['patns'].initialize_unordered_bulk_op()


# Load only the pno and rawcites from each patent, sort by pno so progress reports are possible
for citingPatn in patents.find( {}, {'rawcites':1, 'pno':1} ).sort( [ ('pno' , 1) ] ):
	if citingPatn['pno'] >= landmarkPno:
		print 'drawing back-citations for patn ' + str (landmarkPno)
		landmarkPno += 100000
		bulk.execute()
		bulk = client[dbname]['patns'].initialize_unordered_bulk_op()
	citingNo = citingPatn['pno']
	for citedPNo in citingPatn['rawcites'] :
		# 'bulk' will (in theory) execute all of these update_ones in parallel, in nondeterministic order
		bulk.find( {'pno' : citedPNo} ).update_one( {'$push' : {'citedby': citingNo} } )
bulk.execute()
