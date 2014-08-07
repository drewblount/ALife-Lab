execfile('topWords.py')

nruns = 100000

n = 100


outC = shared_n_vectors(n, nruns, cite_pairs=True, texts_already_ordered=False)

csv_module.save_csv(outC, 'cited_shared_vects_%d_pairs_n=%d' % (nruns,n) )

outR = shared_n_vectors(n, nruns, cite_pairs=False, texts_already_ordered=False)
	
csv_module.save_csv(outR, 'rand_shared_vects_%d_pairs_n=%d' % (nruns,n) )

