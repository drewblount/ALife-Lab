import csv
from pymongo import MongoClient

patDB = MongoClient().patents
patns = patDB.patns
just_cites = patDB.just_cites
metadata = patDB.pat_metadata

glob_max = metadata.find_one({'_id':'max_pno'})['val']
glob_min = metadata.find_one({'_id':'min_pno'})['val']


def save_csv(value_array, out_name):
	# using the 'a' tag means that if the file already exists, it is appended to
	outf = open(out_name + '.csv', 'a')
	outf.write(','.join( map(str,value_array) ) )
	outf.close()

def save_csvs(list_of_value_arrays, out_name):
	for i in range( len(list_of_value_arrays) ):
		outf = open(out_name + '.' + str(i+1) + '.csv', 'a')
		outf.write(','.join( map(str, list_of_value_arrays[i]) ) )
		outf.close()

# kwargs is a dict of func's arguments. func is assumed to take min_pno and max_pno args,
# which will be chosen as sub-intervals of glob_min and glob_max.
# save_func is assumed to take as args (output of func, output_name)
# the output of this function is a folder of name out_name with a bunch of incremental
# saved files. If onefile, keeps appending to one outfile with a consistent name.
# else, writes incremental indexed files (out_name1, out_name2, ...)
def incremental_saves(func, kwargs, inc_size, save_func, out_name, onefile = False, glob_min_pno = glob_min, glob_max_pno = glob_max, verbose = False):
	
	pno_range = glob_max_pno - glob_min_pno
	num_incs = pno_range / inc_size
	remainder = pno_range % inc_size
	if remainder != 0: num_incs += 1
	
	bounds = [ glob_min_pno + i*inc_size for i in range(num_incs+1) ]
	bounds[num_incs] = max(bounds[num_incs], glob_max_pno)
	
	if not onefile:
		os.makedirs(out_name)
	
	# for when onefile = true
	fname = out_name
	
	for i in range(num_incs):
		# file = out_name/startpno-endpno.csv
		kwargs['min_pno'] = bounds[i]
		kwargs['max_pno'] = bounds[i+1]
		out = func(**kwargs)
		if not onefile:
			fname = '%s/%d-%d' % (out_name, bounds[i], bounds[i+1])
		save_func(out, fname)
		if verbose:
			print str(datetime.now()) + ': saved file %d / %d' % (i+1, num_incs)

def open_csv(fname):
	out = []
	with open(fname, 'rb') as inF:
		reader = csv.reader(inF)
		for row in reader:
			out.append(row)

	if len(out) == 1:	return out[0]
	else: return out


