from pymongo import MongoClient
from populateNewCiteDB import drawBackCites
from makeCiteDB import storeAllCites
from datetime import datetime
from randomizeCollection import create_rand_ids, index_rand_ids


patDB = MongoClient().patents
cite_net = patDB.cite_net
just_cites = patDB.just_cites
patns = patDB.patns


# copies cite_net into just_cites, 1 document for each citation
# (rather than 1 document for each source patent)
# print str(datetime.now()) + ' COPYING cite_net TO just_cites'
# storeAllCites(cite_net, just_cites)

import randomizeCollection
print str(datetime.now()) + ' CREATING RAND IDS'
create_rand_ids(just_cites)
print str(datetime.now()) + ' INDEXING RAND IDS'
index_rand_ids(just_cites)








