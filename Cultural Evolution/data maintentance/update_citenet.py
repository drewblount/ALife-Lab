## The goal of this file is to update the citation network (which contains forward and backward citations only) to reflect the citations in a new batch of patents

from parallelMapInsert import parallelMapInsert
from pymongo import MongoClient

patDB = MongoClient().patents
patns = patDB.patns
cite_net = patDB.cite_net
just_cites = patDB.just_cites


## This could be done faster if we avoided the find_one below, and instead used something like a parallelMapUpsert that would take care of '_id' field collisions
def make_cite_object(pat):
    ## could be done faster, because each patent leads to a find_one in cite_net
    ## runs fastest if cite_net is in memory
    if ('rawcites' in pat and not cite_net.find_one( {'_id': pat['pno']} )):
        return({'_id': pat['pno'], 'rawcites': pat['rawcites'], 'citedby': [] })
    else:
        return({'_id': pat['pno'], 'rawcites': [], 'citedby': [] })
        
def storeCiteNetwork(col_name='new_patns'):
	logging.info("Copying db."+col_name+'\'s citations into cite_net with parallelMapInsert')
	parallelMapInsert(func = storeCiteInfo,
					  in_collection  = patDB.col_name,
					  out_collection = cite_net,
					  findArgs = {'spec': {'pno':{'$exists':True}}, 'fields': {'pno': 1, 'rawcites' : 1, '_id': 0} },
					  updateFreq = 1,
					  bSize = 10000)
	logging.info("Done copying db."+col_name+'\'s citations into cite_net with parallelMapInsert')

## The below performs the same task as the above, but with parallelMapUpsert (should be faster, but as yet untested)
def make_cite_object1(pat):
    ## could be done faster, because each patent leads to a find_one in cite_net
    ## runs fastest if cite_net is in memory
    if ('rawcites' in pat):
        return({'_id': pat['pno'], 'rawcites': pat['rawcites'], 'citedby': [] })
    else:
        return({'_id': pat['pno'], 'rawcites': [], 'citedby': [] })
        
def storeCiteNetwork1(col_name='new_patns'):
	logging.info("Copying db."+col_name+'\'s citations into cite_net with parallelMapInsert')
	parallelMapUpsert(func = storeCiteInfo,
					  in_collection  = patDB.col_name,
					  out_collection = cite_net,
					  findArgs = {'spec': {'pno':{'$exists':True}}, 'fields': {'pno': 1, 'rawcites' : 1, '_id': 0} },
					  updateFreq = 1,
					  bSize = 10000)
	logging.info("Done copying db."+col_name+'\'s citations into cite_net with parallelMapInsert')
