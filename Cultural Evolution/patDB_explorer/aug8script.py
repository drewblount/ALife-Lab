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
with open('sh_term_ranks_cite-pairs_topn=13_num=100000.csv', 'rb') as csvf:
	reader = csv.reader(csvf, delimiter=',')
	for row in reader:
		out.append(row)

p1s = [int(out[i][2]) for i in range(1,100001)]
p2s = [int(out[i][3]) for i in range(1,100001)]

from numpy import mean, std
p1m, p1std, p2m, p2std = mean(p1s), std(p1s), mean(p2s), std(p2s)

from matplotlib import pyplot as plt
plt.hist(p1s, alpha=0.5,bins=13, label = 'children')
plt.hist(p2s, alpha=0.5,bins=13, label = 'parents')
plt.legend(loc='upper right')
plt.title('cite pairs, tf-idf ranks of shared terms; 100,000 shared terms')
plt.show()
