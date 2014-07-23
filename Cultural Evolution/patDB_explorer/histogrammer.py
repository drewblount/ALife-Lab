import matplotlib.pyplot as plt
import csv_module

execfile('comber.py')
# all_tfidfs = tf_idf_comb(1000)

# A not-really-necessary wrapper for pyplot.hist
# includes just a few of the args from pyplot.hist
# if saveName is entered, it is presumed to be a string choosing the
# output imagename. Else, the histogram is displayed in a new window.
# Checkvals is for some data-cleaning that's only necessary on
# data from my early-version bulk .csv writer
def histogram(vals, saveName=None, title=None, xlabel=None, drawMean=True, binsCode=100, rangeCode = None, logCode=False, colorCode='r',checkVals=False, normCode=False):
	
	# If vals is a string, it's assumed to be the name of a csv file that
	# can be opened
	if type(vals) == str:
		vals = csv_module.open_csv(vals, fixVals=checkVals)
	
	plt.hist(vals, bins=binsCode,range=rangeCode, log=logCode, color=colorCode, normed=normCode)
	if title: plt.title(title)
	if xlabel: plt.xlabel(xlabel)
	if drawMean:
		plt.axvline(mean(vals), color='k', linestyle='dashed', linewidth=2)

	if saveName:
		plt.savefig(saveName)
	else:
		plt.show()

def mean(vals):
	sum = 0.0
	for val in vals:
		sum += val
	return sum/len(vals)


## SOME SCRIPTS ####

# simply a helper function for finding some of the data I've saved
def data_top(n):
	return 'data/fulldb.firstgo.top_n_tfidf/fulldb.firstgo.top_n_tfidf.%d.csv' % n

def name_top(n, opt=None):
	ret = 'top_%d_terms_all_pats' % n

	if opt:
		ret += opt

def title_top(n):
	# so the title doesn't have a weird plural when n = 1
	instring = ''
	if n == 1:
		instring = ' '
	else:
		instring = '-%d-' % n
	'histogram of all patents\' top%sterms\' tf-idfs' % instring


def plot_top(n, range=None):
	histogram(data_top(n), name_top(n), title_top(n), checkVals = True)


