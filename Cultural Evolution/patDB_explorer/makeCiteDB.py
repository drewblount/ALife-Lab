# The goal here is to store all citations in their own database
# which contains only {source: pnum, cited: pnum}, where 'source'
# cites 'cited'

# This is done by combing through each 'citedby' field, rather than
# 'rawcites', because we don't want to include citations where one
# patent isn't in the database (likely because it is older than '76)

from parallelMapInsert import parallelMapInsert
from pymongo import MongoClient

patDB = MongoClient().patents
patns = patDB.patns
cites = patDB.cites

# returns an array of {source: pno, cited: pno} for every citation
# whose source is 'pat'
def storeCites(pat):
	outCites = []
	if 'citedby' in pat and 'pno' in pat:
		citedNum = pat['pno']
		for citer in pat['citedby']:
			outCites.append({'source': citer, 'cited': citedNum})
	return outCites

def storeAllCites():
	parallelMapInsert(func = storeCites,
					  in_collection  = patns,
					  out_collection = cites,
					  findArgs = {'spec': {}, 'fields': {'pno': 1, 'citedby' : 1, '_id': 0} },
					  updateFreq = 100000,
					  bSize = 100000)

def main():
	storeAllCites()

# Makes main() run on typing 'python tf-idf.py' in terminal
if __name__ == '__main__':
	main()