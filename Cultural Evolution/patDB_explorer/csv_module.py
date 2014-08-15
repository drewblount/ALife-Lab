import csv
from pymongo import MongoClient
import os

patDB = MongoClient().patents
patns = patDB.patns
just_cites = patDB.just_cites
metadata = patDB.pat_metadata

glob_max = metadata.find_one({'_id':'max_pno'})['val']
glob_min = metadata.find_one({'_id':'min_pno'})['val']


def save_csv(value_array, out_name, trail_endl=True, overwrite=False):
	if overwrite:
	try: os.remove(out_name)
	except OSError: pass

	# using the 'a' tag means that if the file already exists, it is appended to
	outf = open(out_name + '.csv', 'a')
	# the comma at the end is important for bulk writes
	outf.write(','.join( map(str,value_array) )+',' )
	if trail_endl:
		outf.write('\n')
	outf.close()

def save_csvs(list_of_value_arrays, out_name, overwrite=False):
	if overwrite:
	try: os.remove(out_name)
	except OSError: pass

	for i in range( len(list_of_value_arrays) ):
		outf = open(out_name + '.' + str(i+1) + '.csv', 'a+')
		outf.write(','.join( map(str, list_of_value_arrays[i]) )+',' )
		outf.close()

def save_multi_csv(array_of_val_arrays, out_name, overwrite=False)
	if overwrite:
		try: os.remove(out_name)
		except OSError: pass
	for val_array in array_of_val_arrays:
		save_csv(val_array, out_name)


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

# With my initial bulk-write protocol, successive bulk-writes
# weren't comma-separated, so at the end of each write/beginning of next,
# there is a value which looks like '0.123450.12345', which can't
# be cast back into a float. This replaces those troublesome vals with
# a default value, which is bad data-practice but shouldn't make a big dif
# over a million data points, and allows us to use the large-but-slightly-broken
# files already made
def tryFloat(val, default_float=0.12):
	try: return float(val)
	except ValueError: return(default_float)

# simple helper for the function below
def mapTyp(func):
	def mapper(arg):
		return map(func, arg)
	return mapper

def open_csv(fname, arrTyp=float, fixVals=False):
	out = []
	with open(fname, 'rb') as inF:
		reader = csv.reader(inF)
		for row in reader:
			out.append(row)
	# out is currently an array of arrays of strings
	if fixVals: arrTyp = tryFloat
	out = map(mapTyp(arrTyp), out)
	# now out is an array of arrays of arrTyp
	if len(out) == 1: out = out[0]

	return out







