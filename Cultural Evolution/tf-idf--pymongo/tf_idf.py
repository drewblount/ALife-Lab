import multiprocessing
from pymongo import MongoClient
from parallelMap import parallelMap
from math import log
from nltk.tokenize import RegexpTokenizer


def tokeAndClean(str):
	tokenizer = RegexpTokenizer("[\w']+")
	tokens = tokenizer.tokenize(str)
	tokens = [token.lower() for token in tokens]
	
	# TODO: remove stop words
	# TODO: stemming
	
	return tokens

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

		text = tokeAndClean(text)
		text = countWords(text)
		text = normalizeWordFreq(text)
		
		return( {'$set': {'text' : text} } )

	parallelMap(initText, patDB.patns,
				findArgs = {'spec': {}, 'fields': {'title':1, 'abstract':1} },
				# sends bulk updates to the db every updateFreq patents
				updateFreq = 5000)


def main():
	c = MongoClient()
	patDB = c.patents
	initTexts(patDB)


# Makes main() run on typing 'python tf-idf.py' in terminal
if __name__ == '__main__':
	main()
















