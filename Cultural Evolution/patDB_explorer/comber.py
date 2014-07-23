

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
import os
import csv_module as csv
from datetime import datetime

patDB = MongoClient().patents
patns = patDB.patns
just_cites = patDB.just_cites
metadata = patDB.pat_metadata

glob_max = metadata.find_one({'_id':'max_pno'})['val']
glob_min = metadata.find_one({'_id':'min_pno'})['val']


'''	  for (obj in lists) {
	merged = merged.concat(obj['vals']);
	}
'''

# You can't have the second half of the 'emit' tuple be an array in mongodb,
# hence the awkwardness with {'vals':out_arr} instead of just out_arr
def top_n_map(n):
	return Code('''
	function() {
	  var to_return = Math.min(%d, this.sorted_text.length);
	  var out_arr = [];
	  for (var i = 0; i < to_return; i++) {
	    out_arr[i] = this.sorted_text[i]['tf-idf']
	  };
	  emit("tf-idf", {'vals':out_arr})
	};''' % n)
	return out

# concatenates arrays stored in dictionaries (navigating necessary messiness described
# above). The input arg lists is of the form
# { key: {vals: [list]}, key: {vals: [list]}, ... }
top_n_reduce = Code('''
	function(key, lists) {
	  var merged = [];
	  for (var i = 0; i < lists.length; i++) {
	    merged = merged.concat(lists[i]['vals'])
	  }
	  return {'vals':merged}
	}
	''')



def top_upto_n_map(n):
	# makes and emits the singleton list of the 'top1' term,
	# then recursively makes and emits the 'topN' terms as
	# the top(N-1)::(Nth term)
	return Code('''
	function() {
	  var max_return = this.sorted_text.length;
	  var out_arr = {};
	  tops = []
	  for (var i = 0; i < %d; i++) {
		if (i < max_return) {
	      tops.push(this.sorted_text[i]['tf-idf'])
		}
	    emit('top' + i.toString(), {'vals':tops})
	  };
	};''' % n)
	# I'll admit I have no idea why I have n+1 as to_return here instead of n
	# as in top_n_map, but empirically it's what works

# Returns a list of every top_n tf-idf value (but none of the words)
# min_pno is an inclusive bound and max_pno is exclusive
# pno_subset, if included, is a list of pnos to be combed
# if up_to_n, will return n arrays of the tf-idfs of top1 terms, top2,..., topN
# lim limits the number of documents looked at
def tf_idf_comb(top_n, up_to_n = False, min_pno=None, max_pno=None, pno_subset=None, lim=None):
	
	query_arg = {'sorted_text': {'$exists': True} }

	# Adds pno restrictions to the query_arg if those arguments were
	# included in the function call
	if min_pno != None:
		query_arg.update( { 'pno': {'$gte': min_pno} } )
	
	if max_pno != None:
		up_bound = {'$lt': max_pno}
		# check if query_arg already has a 'pno' dict
		# (dict.update overwrites any existing fields)
		if min_pno != None:
			query_arg['pno'].update( up_bound )
		else:
			query_arg.update( {'pno': up_bound} )
				
	if pno_subset:
		in_check = {'$in': pno_subset}
		if min_pno!= None or max_pno!= None: query_arg['pno'].update( in_check )
		else: query_arg.update( {'pno' : in_check } )


	# Use map_reduce
	def map_sel(n, upto):
		if upto: return top_upto_n_map(n)
		else:    return top_n_map(n)
				
	map = map_sel(top_n, up_to_n)
	reduce = top_n_reduce

	out = (patns.inline_map_reduce(map, reduce, query=query_arg) )

	# now clean up 'out' depending on which reduce we used
	if up_to_n: return [ ith['value']['vals'] for ith in out ]
	else: return out[0]['value']['vals']








# The following two funcs are not for deployment, but interpreter-level
# debugging
def arrEq(a1, a2):
	for thing in a1:
		if thing not in a2: return False
	for thing in a2:
		if thing not in a1: return False
	return True

def printLens(a):
	for i in range(len(a)):
		print 'len %d: %d' % (i, len(a[i]))

'''
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
	else: query_arg.update( {'pno' : in_check } ) '''
