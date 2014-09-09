from pymongo import MongoClient

patDB = MongoClient().patents
patns = patDB.patns
cite_net = patDB.cite_net
from parallelMap import parallelMap

# current goal: procure an empirical distribution of
# (# of prior cites to parent, age of parent at citation)
# across cite-space
# the above tuple will be stored for entries in just_cites,

def citestat_tuple(child, parent):
	# input args can be patent numbers or patents themselves
	if type(child) == int:
		# projection--which fields to return from db
		proj = {'isd'}
		child = patDB

# returns the age difference, in days, between child and parent
# -1 if there is a database error (lazy simply)
def age_diff(child, parent):
	# input args can be patent numbers or patents themselves (from patDB.patns)
	if type(child) == int:
		child = patns.find_one({'pno':child},{'isd':1})
		parent = patns.find_one({'pno':parent},{'isd':1})
	# makes sure both patents are in the db, have the right fields
	if (child and 'isd' in child and parent and 'isd' in parent):
		a_diff = (child['isd']-parent['isd']).days
		return a_diff
	else:
		# lazy simple error handling
		return -1

def prior_cites_to_parent(child, parent, pat_coll=cite_net):
	
	# captures idiosyncrasies of cite_net vs. patns
	pno_field = '_id' if pat_coll == cite_net else 'pno'
	
	# we only need the child's pno
	if type(child) != int:
		child = child[pno_field]

	# we need the parent's 'cited_by' field, though the parent arg can be a pno
	if type(parent) == int:
		parent = pat_coll.find_one({pno_field: parent},{'citedby':1})
		
	# input args can be patent numbers or patents themselves (from patDB.patns)
	if type(child) == int:
		child = pat_coll.find_one({'pno':child},{'pno':1})
		parent = pat_coll.find_one({'pno':parent},{'isd':1})

	if 'citedby' in parent:
		# takes advantage of chronologicality of patent nums
		older_than_child = [pno for pno in parent['citedby'] if pno < child]
		return len(older_than_child)
	# should this be a -1?
	else:
		return 0

# the below function is easier described in code than english; its type is
# tupleize :: (type(T) -> type(U)), (type(T) -> type(V)) -> (type(T) -> (type(U),type(V)) )
def tupleize(f1, f2):
	def tuple_func(arg):
		return (f1(arg), f2(arg))
	return tuple_func

# returns update arg to set 'age_diff' and 'n_older_sibs' (= parents_prior_cites) fields
def set_cite_stats(cite, samecoll=False):
	child_pno = cite['src']
	parent_pno = cite['ctd']
	
	if samecoll:
		child = patns.find_one({'pno':child_pno},{'isd':1,'pno':1,'_id':0})
		parent = patns.find_one({'pno':parent_pno},{'isd':1,'pno':1,'cited_by':1,'_id':0})
		return {'$set':{'age_diff': age_diff(child, parent), 'n_older_sibs': prior_cites_to_parent(child, parent, patns) } }
	
	else:
		return {'$set': {'age_diff': age_diff(child_pno, parent_pno), 'n_older_sibs':prior_cites_to_parent(child_pno, parent_pno) } }

# uses parallelMapInsert to store this data for all citations
def all_cite_stats(samecoll=False):
	def curried_citestats(cite):
		return set_cite_stats(cite, samecoll)
	parallelMap(curried_citestats,
				in_collection = just_cites,
				out_collection = just_cites,
				findArgs = {'spec': {}, 'fields': {'_id':0}},
				updateFreq=5000,
				bSize=5000)

