
def runScript():
	execfile('topWords.py')

	df_by_rank(100000, 13, cite_pairs = True, save_freq = 1000)
	df_by_rank(100000, 13, cite_pairs = False, save_freq= 1000)

	# just incase somethin's weird with save_freq
	df_by_rank(100000, 13, cite_pairs = True, fname_suffix='backup')
	df_by_rank(100000, 13, cite_pairs = False, fname_suffix='backup')


import csv
def fixup(fname):
	out = []
	with open(fname, 'rb') as fin:
		rdr = csv.reader(fin, delimiter=',')
		for row in rdr:
			out.append(row)
	data = [out[j] for j in range(1300,1313)]
	return data