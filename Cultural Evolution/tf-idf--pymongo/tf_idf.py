import multiprocessing
from pymongo import MongoClient
from parallelMap import parallelMap
from tokeAndClean import tokeAndClean
import math
from nltk.tokenize import RegexpTokenizer
from bson.code import Code

# returns a dict of elements like (word: {freq: wordFreq})
def countWords(tokens):
	dict = {}
	for word in tokens:
		if word in dict: dict[word]['freq'] += 1
		else: dict[word] = {'freq': 1}
	return dict

# takes a dictionary with entries (word: {freq: wordFreq}) and returns
# one with entries (word: {freq: wordFreq, tf: normalizedWordFreq})
def normalizeWordFreq(freqDict):
	totalWords = sum([freqDict[word]['freq'] for word in freqDict])
	for word in freqDict:
		freqDict[word]['tf'] = float(freqDict[word]['freq'])/totalWords
	return freqDict


def initTexts(patDB):

	# The func that, once passed to parallelMap, will populate
	# the 'text' field for each patent
	# returns a pymongo update dict setting the patent's text
	# field to a dictionary of elements like
	# (word: {freq: wordFreq, tf: normalizedWordFreq})
	
	def initText(patn):

		text = ''
		if  'title' in patn: text += patn['title']
		else :
			logging.warning('No title for patent %d.',    patn['pno'])
	
		if 'abstract' in patn: text += (' ' + patn['abstract'])
		else :
			logging.warning('No abstract for patent %d.', patn['pno'])

		# faster, for testing:
		text = tokeAndClean(text, stemming = False, stopwords = [])
		# text = tokeAndClean(text)
		text = countWords(text)
		text = normalizeWordFreq(text)
		
		return( {'$set': {'text' : text} } )

	parallelMap(initText, patDB.patns,
				findArgs = {'spec': {}, 'fields': {'title':1, 'abstract':1} },
				# sends bulk updates to the db every updateFreq patents
				updateFreq = 5000)


# uses map/reduce to get the number of documents containing each word
def generateDocFreq(patDB, outColName = 'corpusDict'):

	map = Code(open('docFreqMap.js').read())
	reduce = Code(open('docFreqReduce.js').read())

	# finIDF will calculate IDF scores, so I have to pass it
	# the number of total docs in a crafty way.
	size = patDB.patns.count()
	# replace all instances of TOTALDOCS with size in docFreqFinalize.js
	finIDF = open('docFreqFinalize.js').read()
	finIDF = finIDF.replace('TOTALDOCS', str(size))
	
	patDB.patns.map_reduce(map, reduce, outColName, finalize=finIDF)


# assumes all the other stuff has been done
def tf_idf(patDB):

	def tf_idf_onePat(patn):

		for word in patn['text']:
			# getting the arguments of this find_one right was weirdly difficult
			idf = patDB.corpusDict.find_one({'_id': word})['value']['idf']
			patn['text'][word]['tf-idf'] = patn['text'][word]['tf'] * idf
		return( {'$set': {'text' : patn['text'] } } )

	parallelMap(tf_idf_onePat, patDB.patns,
				findArgs = {'spec': {}, 'fields': {'text': 1} },
				updateFreq = 5000)



def main():
	c = MongoClient()
	patDB = c.patents
	
	initTexts(patDB)
	generateDocFreq(patDB)

	tf_idf(patDB)



# Makes main() run on typing 'python tf-idf.py' in terminal
if __name__ == '__main__':
	main()








