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

def get_rank_dist(top_n, num_trials, is_cite):
	pair_tag = 'cite' if is_cite else 'rand'
	out = []
	with open('%s-pairs_topn=%d_num=%d.csv' % (pair_tag, top_n, num_trials), 'rb') as csvf:
		reader = csv.reader(csvf, delimiter=',')
		for row in reader:
			out.append(row)

	p1s = [int(out[i][2]) for i in range(1,len(out))]
	p2s = [int(out[i][3]) for i in range(1,len(out))]

	return (p1s, p2s)


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

rphs = get_rank_dist(13, 100000, False)
# combine the p1 and p2 data
rphs_both = rphs[0] + rphs[1]

# overlays a box-n-whisker of df of shared terms by rank
# with a histogram of number of shared terms by rank
# for random pairs, combining the data for p1 and p2 of
# each pair (because there is no meaningful difference
# between the first and second randomly-selected patents
# in each pair, as supported by comparative p1 and p2 stats)
def compare_rand_data(combine_pair=True):
	
	top_n = 13
	num_terms = 100000
	bins = [i for i in range(1, top_n+2)]
	
	fig, ax1 = plt.subplots(figsize=(11, 8.5))

	scaled_rps = [ [val/1000.0 for val in row] for row in rps]

	ax1.boxplot(scaled_rps, positions = [i+0.5 for i in range(1,14)])
	ax1.axis([1,15,0,250])
	ax1.set_xlabel('per-patent tf-idf rank of shared term')
	# Make the y-axis label and tick labels match the line color.
	ax1.set_ylabel('document frequency of shared term, x1,000 \n(median/quartile box-and-whisker plots)')

	hist_data = rphs_both if combine_pair else rphs
	combined_tag = ' p1 and p2 data combined' if combine_pair else ''

	ax2 = ax1.twinx()
	ax2.hist(rphs, alpha=0.1, bins=bins, normed=True)
	ax2.set_ylabel('normed number of shared terms per rank')

	plt.title('doc-freq distribution and number of shared terms per tf-idf rank\nrand pairs of patents%s' % combined_tag)

	plt.show()

def compare_cite_data():

	top_n = 13
	num_terms = 100000
	bins = [i for i in range(1, top_n+2)]

	fig, ax1 = plt.subplots(figsize=(11, 8.5))

	scaled_rps = [ [val/1000.0 for val in row] for row in rps]

	ax1.boxplot(scaled_rps, positions = [i+0.5 for i in range(1,14)])
	ax1.axis([1,15,0,250])
	ax1.set_xlabel('per-patent tf-idf rank of shared term')
	# Make the y-axis label and tick labels match the line color.
	ax1.set_ylabel('document frequency of shared term, x1,000 \n(median/quartile box-and-whisker plots)')

	hist_data = rphs_both if combine_pair else rphs
	combined_tag = ' p1 and p2 data combined' if combine_pair else ''

	ax2 = ax1.twinx()
	ax2.hist(rphs, alpha=0.1, bins=bins, normed=True)
	ax2.set_ylabel('normed number of shared terms per rank')

	plt.title('doc-freq distribution and number of shared terms per tf-idf rank\nrand pairs of patents%s' % combined_tag)

	plt.show()


