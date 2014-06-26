
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



# returns a cleaned dict of {word: wordFreq} for patn's text,
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
	text = {}

	# Create entry for each word in patn['text'] and fill frequency field
	for token in tokens:
		if token not in text:
			# patn['text'][token]['freq'] = tokens.count(token)
			text[token] = {'freq': tokens.count(token)}


	for word in text:
		if word not in docFreq:
			docFreq[word]  = text[word]['freq']
		else :
			docFreq[word] += text[word]['freq']

	return text

# returns a dict 'text' with the freq and normalized freq 'tf' of each word from the patent.
def tf(patn, docFreq):
	text = initPatentText(patn, docFreq)

	wordCount = float(sum([text[word]['freq'] for word in text]))

	# term frequency = normalized frequency
	# how can I do this functionally in Python?
	for word in text:
		text[word]['tf'] = text[word]['freq']/wordCount
	return text


def tf_idf(patents, docFreq) :
	print 'tf-idf called'
	
	for patn in patents:
		text = tf(patn, docFreq)
	# HERE: insert (bulk insert)/update (bulk update?) patn in mongodb
	
	# after the above loop, docFreqDict should be completely up-to-date
	# so idf can be computed.

	totalWordCount = float(sum([docFreqDict[word] for word in docFreqDict]))
	idf = docFreqDict.copy()
	for word in idf:
		# TODO: What's the standard log base to use here?
		# (the choice of base is just a multiplicative factor in the end)
		idf[word] = math.log(totalWordCount/idf[word])

	# idf is now a dictionary with an entry for each word in the corpus

	# is there a cleaner way of writing this?
	print 'end of tf_idf'
	for patn in patents:
		for word in patn['text']:
			patn['text'][word]['tf-idf'] = patn['text'][word][tf] * idf[word]
		print patn['text']

def main():
	
	c = MongoClient()
	patDB = c.patents
	
	
	corpusDict = {}
	
	# load the patents, but only their titles and abstracts
	patents = patDB.patns.find({},{"title":1,"abstract":1})
	print 'patents loaded'
	
	tf_idf(patents, corpusDict)
	
	# now save the dict of word document frequencies
	patDB.corpusDict.insert(corpusDict)

	print 'patents:'
	print patents
	print '/patents'

	# just a test to see if the patents have their stuff
	patDB.tf_idf_patns.insert(patents)

# Makes main() run on typing 'python tf-idf.py' in terminal
if __name__ == '__main__':
    main()







