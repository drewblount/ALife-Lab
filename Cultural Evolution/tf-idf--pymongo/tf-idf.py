
import re
import nltk
from pymongo import MongoClient
from nltk.tokenize import RegexpTokenizer
from nltk import bigrams, trigrams
import math
import logging

# for logging
fnLog = 'tf-idf.log'
logFormat = "%(asctime)s %(levelname)s %(processName)s\t%(message)s"
logging.basicConfig(filename=fnLog, level=logging.NOTSET, format = logFormat)

def main():

	c = MongoClient()
	patDB = c.patents

	corpusDict = {}

	# load the patents, but only their titles and abstracts
	patents = patDB.patns.find({},{"title":1,"abstract":1})

	tf_idf(patents, corpusDict)

	# now save the dict of word document frequencies
	patDB.corpusDict.insert(corpusDict)


# dict stores the frequency of each word
def updateFreqDict(word, dict):
	if word not in dict:
		dict[word] = 1
	else:
		dict[word] += 1

def combineDicts(toBeCombined, corpus):
	for word in toBeCombined:
		if word not in corpus:
			corpus[word] = toBeCombined[word]
		else:
			corpus[word] += toBeCombined[word]

def cleanTokens(tokens):
	tokens = [token.lower() for token in tokens]

def tokeAndClean(str):
	tokenizer = RegexpTokenizer("[\w']+")
	tokens = tokenizer.tokenize(str)
	tokens = [token.lower() for token in tokens]

	# TODO: remove stop words
	# TODO: stemming

	return tokens



# adds a field to a patent object for that patent's text,
# which is stored as a bag-of-words dictionary where each
# word has a frequency field (other fields are added later)
# Simultaneously updates a document frequency dict
def initPatentText(patn, docFreq):

	# We want to combine titles and abstracts, right?
	str = ''
	if  'title' in patn: str += patn['title']
	else :
		logging.warning('No title for patent %d.',    patn['pno'])

	if 'abstract' in patn: str += (' ' + patn['abstract'])
	else :
		logging.warning('No abstract for patent %d.', patn['pno'])


	tokens = tokeAndClean(str)
	patn['text'] = {}

	# Create entry for each word in patn['text'] and fill frequency field
	for token in tokens:
		if token not in patn['text']:
			patn['text'][token]['freq'] = tokens.count(token)

	for word in patn['text']:
		if word not in docFreq:
			docFreq[word]  = patn['text'][word]['freq']
		else :
			docFreq[word] += patn['text'][word]['freq']

# stores term frequency for each word in a patent's text
def tf(patn):
	if not 'text' in patn: initPatentTextDict(patn)

	wordCount = float(sum([patn['text'][word]['freq'] for word in patn['text']]))

	# term frequency = normalized frequency
	for word in patn['text']:
		patn['text'][word]['tf'] = patn['text'][word]['freq']/wordCount

def tf_idf(patents, docFreqDict) :
	for patn in patents: initPatentText(patn, docFreqDict)
	# after the above loop, docFreqDict should be completely updated

	totalWordCount = float(sum([docFreqDict[word] for word in docFreqDict]))
	idf = docFreqDict.copy
	for word in idf:
		# TODO: What's the standard log base to use here?
		# (the choice of base is just a multiplicative factor in the end)
		idf[word] = math.log(totalWordCount/idf[word])

	# idf is now a dictionary with an entry for each word in the corpus

	# is there a cleaner way of writing this?
	for patn in patents:
		for word in patn['text']:
			patn['text'][word]['tf-idf'] = patn['text'][word][tf] * idf[word]





