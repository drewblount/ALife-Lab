from parallelMapInsert import parallelMapInsert
from pymongo import MongoClient

## adds all the patents in new_patns into the cite_net, along with their rawcites and a blank citedby field


citeDB    = MongoClient().patents
cite_net  = citeDB.cite_net
new_patns = citeDB.new_patns

def new_cite_net_entry(patn):
    if ('rawcites') in patn:
        return {'_id': patn['pno'], 'rawcites': pat['rawcites'], 'citedby': []}
    else:
        return {'_id': patn['pno'], 'rawcites': [], 'citedby': []}
        
def update_cite_net(from_collection = new_patns, a_cite_net = cite_net):
    parallelMapInsert(
        func = new_cite_entry,
        in_collection = from_collection,
        out_collection = a_cite_net,
	    updateFreq = 10000,
        bSize = 10000)
        

def test_this_file():
    test_cite_net = citeDB.test_cite_net
    update_cite_net(new_patns, test_cite_net)
        
                    
        
        
        
