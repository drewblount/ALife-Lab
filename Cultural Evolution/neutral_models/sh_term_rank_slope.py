import random
from matplotlib import pyplot as plt
import csv_module

# If p1's term-rank and p2's term rank are random uniformly
# from 1-top_n inclusive
def uniform(top_n, num_samples=100000, normed=True, print=False):
	slopes = []
	for i in range(num_samples):
		a,b = random.randint(1,top_n), random.randint(1,top_n)
		slope = a-b
		slopes.append(slope)

	csv_module.save_csv(slope, 'slopes_from_uniform_rank_dist_n=%d_num=%d' % (top_n,num_samples))

	# makes sure there's one bin per val
	bins = [i for i in range(1-top_n, top_n+1)]
	plt.hist(slopes, bins, normed=normed)

	if print:
		norm_label = '(output normed)' if normed else ''
		plt.title('slope distribution\neach patent\'s term rank chosen from 1-%d with uniform probability\n%d sample pairs %s\n' % (top_n, num_samples, norm_label))
		plt.show()

