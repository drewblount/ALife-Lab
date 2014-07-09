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

addToSetUntil = 4400000

patents.ensure_index('pno')

# Load only the pno and rawcites from each patent, sort by pno so progress reports are possible
# limiting batch_size to keep memory down, reduce timeouts
for citingPatn in patents.find( {}, {'rawcites':1, 'pno':1} ).sort( [ ('pno' , 1) ] ).batch_size(100000):
	citingNo = citingPatn['pno']
	if citingNo >= landmarkPno:
		print 'drawing back-citations for patn ' + str (landmarkPno)
		landmarkPno += 100000
		bulk.execute()
		bulk = client[dbname]['patns'].initialize_unordered_bulk_op()

	if citingNo < addToSetUntil:
		for citedNo in citingPatn['rawcites'] :
			# addToSet makes sure not to add duplicates
			bulk.find( {'pno' : citedNo} ).update_one( {'$addToSet' : {'citedby': citingNo} } )
	else:
		for citedPNo in citingPatn['rawcites'] :
			# 'bulk' will (in theory) execute all of these update_ones in parallel, in nondeterministic order
			bulk.find( {'pno' : citedNo} ).update_one( {'$push' : {'citedby': citingNo} } )

	bulk.find( {'pno' : citingNo} ).update_one( {'$set': {'backCitesDrawn' = True} })

bulk.execute()
