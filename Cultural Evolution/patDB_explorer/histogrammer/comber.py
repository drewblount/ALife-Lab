

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
def tf_idf_comb(top_n):
	map = Code('''
		function() {
		  var to_return = Math.min(%d, this.sorted_text.length);
		  var out_arr = [];
		  for (var i = 0; i < to_return; i++) {
		    out_arr[i] = this.sorted_text[i]['tf-idf']
		  };
		  emit("tf-idf", {'vals':out_arr})
		}
		''' % top_n )

	return (patns.inline_map_reduce(map, concat_list_reduce, query = {'sorted_text': {'$exists': True} } ) )[0]['value']['vals']

def save_csv(value_array, out_file_name):
	outf = open(out_file_name, "w")
	outf.write(','.join( map(str,value_array) ) )
	outf.close()


