from pymongo import MongoClient
from populateNewCiteDB import drawBackCites
from makeCiteDB import storeAllCites
from datetime import datetime


patDB = MongoClient().patents
cite_net = patDB.cite_net
just_cites = patDB.just_cites
patns = patDB.patns


# copies cite_net into just_cites, 1 document for each citation
# (rather than 1 document for each source patent)
print str(datetime.now()) + ' COPYING cite_net TO just_cites'
storeAllCites(cite_net, just_cites)

import randomizeCollection
print str(datetime.now()) + ' CREATING RAND IDS'
randomizeCollection.create_rand_ids(just_cites)
print str(datetime.now()) + ' INDEXING RAND IDS'
randomizeCollection.index_rand_ids(just_cites)








