import matplotlib.pyplot as plt
import csv_module

execfile('comber.py')
# all_tfidfs = tf_idf_comb(1000)

# A not-really-necessary wrapper for pyplot.hist
# includes just a few of the args from pyplot.hist
# Checkvals is for some data-cleaning that's only necessary on
# data from my early-version bulk .csv writer
def histogram(vals, title=None, xlabel=None, drawMean=True, binsCode=100, rangeCode = None, logCode=False, colorCode='r',checkVals=False, normCode=False):
	
	# If vals is a string, it's assumed to be the name of a csv file that
	# can be opened
	if type(vals) == str:
		vals = csv_module.open_csv(vals, fixVals=checkVals)
	
	plt.hist(vals, bins=binsCode,range=rangeCode, log=logCode, color=colorCode, normed=normCode)
	if title: plt.title(title)
	if xlabel: plt.xlabel(xlabel)
	if drawMean:
		plt.axvline(mean(vals), color='k', linestyle='dashed', linewidth=2)
	plt.show()

def mean(vals):
	sum = 0.0
	for val in vals:
		sum += val
	return sum/len(vals)
