import csv
from numpy import mean, std
from pylab import *

def to_int_2d(arr2d):
	return [ [int(entry) for entry in arr if entry != ''] for arr in arr2d]

def openup(fname):
	out = []
	with open(fname, 'rb') as fin:
		rdr = csv.reader(fin, delimiter=',')
		for row in rdr:
			out.append(row)
	return to_int_2d(out)

def stats(array2d):
	return [{
			'mean': mean(arr),
			'standard dev': std(arr),
			'length': len(arr),
			'min': min(arr),
			'max': max(arr)} for arr in array2d ]

def pretprint(arr2d):
	for row in arr2d:
		print row

fnames=('rand-pairs_topn=13_num=100000p1.csv',
		'rand-pairs_topn=13_num=100000p2.csv',
		'cite-pairs_topn=13_num=100000p1.csv',
		'cite-pairs_topn=13_num=100000p2.csv',)


(rp1, rp2, cp1, cp2) = (openup(fn) for fn in fnames)

rps = [rp1[i]+rp2[i] for i in range(len(rp1))]

titles=('rand pairs, n=13, 100,000 shared terms, pat1',
		'rand pairs, n=13, 100,000 shared terms, pat2',
		'cite pairs, n=13, 100,000 shared terms, children',
		'cite pairs, n=13, 100,000 shared terms, parents')

rand_title = 'rand pairs, n=13, 100,000 shared terms, both pats'

