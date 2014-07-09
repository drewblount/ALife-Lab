from pymongo  import MongoClient, ASCENDING, DESCENDING

def storeMaxMinPno(patDB, saveOnDB = True, verbose = False, ret = False):
	maxPno = patDB.patns.find({},{'pno': 1, '_id': 0}).sort('pno',DESCENDING)[0]['pno']
	minPno = patDB.patns.find({},{'pno': 1, '_id': 0}).sort('pno',ASCENDING)[0]['pno']

	if saveOnDB:
		patDB.pat_metadata.insert( {'_id': 'max_pno', 'val': maxPno} )
		patDB.pat_metadata.insert( {'_id': 'min_pno', 'val': minPno} )


	if verbose:
		print 'Max, min pnos are (' + str(minPno) + ', ' + str(maxPno) + ').'

	if ret:
		return (minPno, maxPno)