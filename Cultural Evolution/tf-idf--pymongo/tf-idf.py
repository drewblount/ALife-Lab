
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
def updateDict(words, dict):
	for word in words:
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

def freq(s)

def tokeAndClean(str):
	tokenizer = RegexpTokenizer("[\w’]+")
	tokens = tokenizer.tokenize(str)
	tokens = [token.lower() for token in tokens]
	return tokens


# adds a field to a patent object for that patent's text,
# which is stored as a bag-of-words dictionary where each
# word might know its frequency, normalized frequency, tf-idf
def makePatentTextDict(patn):
	str = ''
	if  patn.get('title'):
		str += patn['title']
	else:
		logging.warning('No title for patent %d.', patn['pno'])
	if patn.get('abstract'):
		str += (' ' + patn['abstract'])
	else:
		logging.warning('No abstract for patent %d.', patn['pno'])

	tokens = tokeAndClean


def tf(patent):
	# We want to combine titles and abstracts, right?
