import csv
from matplotlib import pyplot as plt

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

# from numpy import mean, std
# p1m, p1std, p2m, p2std = mean(p1s), std(p1s), mean(p2s), std(p2s)

def plot(top_n, num_trials, is_cite):
	
	def labelmaker(i, cite):
		if cite and i == 1: return 'child in cite pair'
		if cite: return 'parent in cite pair'
		return 'patent %d in rand pair' % i
	
	p1s, p2s = get_rank_dist(top_n, num_trials, is_cite)
	plt.hist(p1s, alpha=0.5,bins=13, label = labelmaker(1, is_cite))
	plt.hist(p2s, alpha=0.5,bins=13, label = labelmaker(2, is_cite))
	plt.legend(loc='upper left' if not is_cite else 'upper right')
	plt.title('%s pairs, tf-idf ranks of shared terms among %d pairs' % ('cite' if is_cite else 'rand', num_trials))
	plt.show()



def plot_both(top_n, num_trials):

	rp1, rp2 = get_rank_dist(top_n, num_trials, False)
	rps = rp1 + rp2

	cp1, cp2 = get_rank_dist(top_n, num_trials, True)
	cps = cp1 + cp2

	plt.hist(rps, alpha=0.5, bins=top_n, label='among %d random pairs' % num_trials)
	plt.hist(cps, alpha=0.5, bins=top_n, label='among %d citation pairs' % num_trials)
	plt.legend(loc='upper right')
	plt.title('tf-idf rank distribution of shared terms')
	plt.show()
