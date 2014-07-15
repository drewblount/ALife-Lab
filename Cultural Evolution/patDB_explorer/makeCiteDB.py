# The goal here is to store all citations in their own database
# which contains only {source: pnum, cited: pnum}, where 'source'
# cites 'cited'

# This is useful because with an index for each citation link, we can
# choose a random citatino from cite-space with (pseudo) uniform random
# probability

# This is done by combing through each 'citedby' field, rather than
# 'rawcites', because we don't want to include citations where one
# patent isn't in the database (likely because it is older than '76)

from parallelMapInsert import parallelMapInsert
from pymongo import MongoClient

patDB = MongoClient().patents
patns = patDB.patns
cite_net = patDB.cite_net
just_cites = patDB.just_cites

# returns an array of {source: pno, cited: pno} for every citation
# whose source is 'pat'
def storeCites(pat):
	outCites = []
	if 'citedby' in pat and '_id' in pat:
		citedNum = pat['_id']
		for citer in pat['citedby']:
			outCites.append({'src': citer, 'ctd': citedNum})
	return outCites

def storeAllCites(in_coll = cite_net, out_coll = just_cites):
	parallelMapInsert(func = storeCites,
					  in_collection  = in_coll,
					  out_collection = out_coll,
					  findArgs = {'spec': {}, 'fields': {'citedby' : 1, '_id': 1} },
					  updateFreq = 1,
					  bSize = 10000)
