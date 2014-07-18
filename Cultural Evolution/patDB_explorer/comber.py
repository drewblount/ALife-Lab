

# Need to write combers, which go through the db and get a list
# of whichever attribute (e.g. list of all top 10 tf-idfs)

# Is this an appropriate case for map-reduce??

# map(patn) = list(attr)

# reduce(key, vals) -> val
# reduce(all, lists_of_attributes) -> concatenaded lists


# very big lists? : if we get every single top-ten-tf-idf, that's
# 40 million terms. Is that a problem? If each term is a float, then
# that's 40 mb * (float size / byte)

# if this is done mongod-side (it should be), then gotta check if
# JS lists have a max size
from pymongo  import MongoClient
from bson.code import Code
import randPat
import topWords

patDB = MongoClient().patents
patns = patDB.patns
just_cites = patDB.just_cites

# concatenates arrays stored in dictionaries. The input arg lists
# is of the form { key: {vals: [list]}, key: {vals: [list]}, ... }
concat_list_reduce = Code('''
	function(key, lists) {
	  var merged = []
	  for (var i = 0; i < lists.length; i++) {
		merged = merged.concat(lists[i]['vals'])
	  }
	  return {'vals':merged};
	}
	''')

'''	  for (obj in lists) {
	merged = merged.concat(obj['vals']);
	}
'''

# Returns a list of every top_n tf-idf value (but none of the words)
# min_pno is an inclusive bound and max_pno is exclusive
# pno_subset, if included, is a list of pnos to be combed
def tf_idf_comb(top_n, min_pno=None, max_pno=None, pno_subset=None):
	
	query_arg = {'sorted_text': {'$exists': True}}

	# Adds pno restrictions to the query_arg if those arguments were
	# included in the function call
	if min_pno:
		query_arg.update( { 'pno': {'$gte': min_pno} } )
	
	if max_pno:
		up_bound = {'$lt': max_pno}
		# check if query_arg already has a 'pno' dict
		# (dict.update overwrites any existing fields)
		if min_pno:
			query_arg['pno'].update( up_bound )
		else:
			query_arg.update( {'pno': up_bound} )
				
	if pno_subset:
		in_check = {'$in': pno_subset}
		if min_pno or max_pno: query_arg['pno'].update( in_check )
		else: query_arg.update( {'pno' : in_check } )


	# Use map_reduce
	map = Code('''
		function() {
		var to_return = Math.min(%d, this.sorted_text.length);
		var out_arr = [];
		for (var i = 0; i < to_return; i++) {
		out_arr[i] = this.sorted_text[i]['tf-idf']
		};
		emit("tf-idf", {'vals':out_arr})
		};
		
		''' % top_n )

	# all the business at the end gets the single result array from
	# concat_list_reduce
	return (patns.inline_map_reduce(map, concat_list_reduce,
									query = query_arg ) )[0]['value']['vals']

def save_csv(value_array, out_file_name):
	outf = open(out_file_name, "w")
	outf.write(','.join( map(str,value_array) ) )
	outf.close()

def rand_tf_idf_comb(top_n, num_pats, max_pno: None, min_pno: None):
	
	sel = randPat.Selector()
	if min_pno: sel.min_pno = min_pno
	if max_pno: sel.max_pno = max_pno

	sel.rand_pnos(num_pats)




# Goal here is to comb a bunch of random citations and return
# two lists: one of the tf-idfs of non-shared words between
# parent and child, and one of tf-idfs of shared words
def cited_tf_idfs(n_pairs, top_m):

	sel = randPat.Selector()
	
	for i in range(n_pairs):




