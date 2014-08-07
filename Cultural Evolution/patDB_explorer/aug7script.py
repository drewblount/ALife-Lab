execfile('topWords.py')

maxruns = 100000

dumpfreq = maxruns / 100

n = 25


# sum all of the columns in output to get final result
for i in range(100):

	outC = shared_n_vectors(n, maxruns, cite_pairs=True, texts_already_ordered=False)

	csv_module.save_csv(outC, 'cited_shared_vects_%d_trials_%d_perrow' % (maxruns,dumpfreq) )

	outR = shared_n_vectors(n, maxruns, cite_pairs=False, texts_already_ordered=False)
	
	csv_module.save_csv(outC, 'rand_shared_vects_%d_trials_%d_perrow' % (maxruns,dumpfreq) )

