# goal here: produce a folder containing a text file for each patent.
# each file is  <pno>.txt and looks like
# title: <title text as a string>
# abstract: <abstract text as a string>

# each call of write_pats has an optional argument enforce_func,
# which is a function: patent -> boolean that determines which
# patents from the database are of interest

from pymongo import MongoClient
from randPat import Selector
import os

# the names below are pretty consistent across all my code
client = MongoClient()
patDB  = client.patents
patns  = patDB.patns


# example enforce functions
def has_title_abs(pat):
	return ('title' in pat and 'abstract' in pat)

def pno_in_range(pat, min, max):
	return (pat['pno'] in range(min, max))

def pno_range_plus_titabs(pat, min, max):
	return has_title_abs(pat) and pno_in_range(pat, min, max)


# writes dir/<pno>.txt in the format described at the top of this file
def write_pat(pat, dir):
	fname = '%s/%d.txt' % (dir, pat['pno'])
	with open(fname, 'w') as f:
		f.write('title:\n')
		f.write(pat['title']+'\n\n')
		f.write('abstract:\n')
		f.write(pat['abstract'])
		f.close()


# the meat of it all
# extra_proj is an optional pymongo projection argument in case fields
# beyond pno, title, and abstract need to be used by the enforce_func
def write_pats(n, out_name, enforce_func=has_title_abs, extra_proj=None):
	# makes output file if it's not there already
	if not os.path.exists(out_name):
		os.makedirs(out_name)

	proj = {'_id':0, 'pno':1, 'title':1, 'abstract':1}
	# combine proj with extra_proj
	if extra_proj: proj = dict(proj.items() + extra_proj.items())

	# get a random patent selector which returns patents and the fields
	# described by proj
	selector = Selector(patns, projection=proj)

	for i in range(n):
		pat = selector.rand_pat(enforce_func=enforce_func)
		write_pat(pat, out_name)

