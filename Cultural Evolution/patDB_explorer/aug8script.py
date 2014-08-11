execfile('topWords.py')

nruns = 100000

n = 100


outC = shared_n_vectors(n, nruns, cite_pairs=True, texts_already_ordered=False)

csv_module.save_csv(outC, 'cited_shared_vects_%d_pairs_n=%d' % (nruns,n) )

outR = shared_n_vectors(n, nruns, cite_pairs=False, texts_already_ordered=False)
	
csv_module.save_csv(outR, 'rand_shared_vects_%d_pairs_n=%d' % (nruns,n) )



import csv
out = []
with open('sh_term_ranks_rand-pairs_topn=13_num=10000.csv', 'rb') as csvf:
	reader = csv.reader(csvf, delimiter=',')
	for row in reader:
		out.append(row)

p1s = [int(out[i][2]) for i in range(1,10001)]
p2s = [int(out[i][3]) for i in range(1,10001)]

from numpy import mean, std
p1m, p1std, p2m, p2std = mean(p1s), std(p1s), mean(p2s), std(p2s)

from matplotlib import pyplot as plt
plt.hist(p1s, alpha=0.5,bins=13, label = 'patent 1 in rand pair')
plt.hist(p2s, alpha=0.5,bins=13, label = 'parent 2 in rand pair')
plt.legend(loc='upper left')
plt.title('rand pairs, tf-idf ranks of shared terms; 10,000 shared terms')
plt.show()


import csv
out = []
num_trials = 1000
with open('sh_term_ranks_cite-pairs_topn=13_num=%d.csv' % num_trials, 'rb') as csvf:
	reader = csv.reader(csvf, delimiter=',')
	for row in reader:
		out.append(row)

p1s = [int(out[i][2]) for i in range(1,num_trials+1)]
p2s = [int(out[i][3]) for i in range(1,num_trials+1)]

cite_pairs = True

from numpy import mean, std
p1m, p1std, p2m, p2std = mean(p1s), std(p1s), mean(p2s), std(p2s)
p1label, p2label, pairlabel = (('children','parents','cite')
							   if cite_pairs else
							   ('pat 1', 'pat 2', 'rand'))


from matplotlib import pyplot as plt
plt.hist(p1s, alpha=0.5,bins=13, label=p1label, normed=True)
plt.hist(p2s, alpha=0.5,bins=13, label=p2label, normed=True)
plt.legend(loc='upper right')
plt.title('%s pairs, tf-idf ranks of %d shared terms' % (pairlabel, num_trials))
plt.show()
