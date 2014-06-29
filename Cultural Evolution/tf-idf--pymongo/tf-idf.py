
import re
import nltk
from pymongo import MongoClient
from nltk.tokenize import RegexpTokenizer
from nltk import bigrams, trigrams
import math
import logging

import multiprocessing

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


def tf_idf(patDB) :
	 
	print 'Begininning tf_idf'
	 
	# TODO: pick up preexisting docFreq (type: dict) if one is already in DB
	# should be a parallel-accessible dictionary
	docFreq = multiprocessing.Manager().dict()

	patents = patDB.patns.find({},{"title":1,"abstract":1})
	# defining __len__ allows the map function to be used with multiprocessing
	# (map requires that an iterable has a length, and will load
	# the whole db to measure its length if cursor.__len__ is
	# not defined)
	patents.__len__ = patents.count()

	# pool of processors
	procPool = multiprocessing.Pool(multiprocessing.cpu_count())
	
	
	
	# in parallel, calculate the tf for each word in each patent's text,
	# store it in the database, and simultaneously update the document
	# frequency dictionary
	def tf_updateDB(patn) :
		text = tf(patn, docFreq)
		# Adds text field to patDB.patns[patn]
		patDB.patns.update({'_id': patn['_id']},
						   {'$set': {'text': text}})

	print 'Calculating term and document frequencies...'
	procPool.map(tf_updateDB, patents)
	print 'term and document frequencies calculated.'
		
		
		
	# Now docFreq should be completely up-to-date
	# so idf can be computed.

	totalWordCount = float(sum([docFreq[word] for word in docFreq]))
	idf = docFreq.copy()
	# docFreq is later saved on db, so idf can be updated without
	# re-counting word frequencies across the corpus when a single
	# document is inserted. Thus idf = docFreq.copy()
		
	# In parallel, calculate the idf for each word in the dictionary
	def df_to_idf(word):
		idf[word] = math.log(totalWordCount/idf[word])
	print 'Converting document frequencies to idf...'
	procPool.map(df_to_idf, idf)
	print 'idf dictionary calculated'
		


	# In parallel, add the idf score to each word in each patent.
	patents = patDB.patns.find({},{"title":1,"abstract":1,"text":1})

	def add_tfidf_to_patn(patn):
		for word in patn['text']:
			patn['text'][word]['tf-idf'] = patn['text'][word]['tf'] * idf[word]
		patDB.patns.update({'_id': patn['_id']},
						   {'$set': {'text': patn['text']}})

	print 'Calculating tf-idf for each word in each patent...'
	procPool.map(add_tfidf_to_patn, patents)
	print 'tf-idf saved for each patent'



	print 'Saving document frequency dict as collection \'corpusDict\'...'
	# overwrites corpusDict with docFreq
	patDB.corpusDict.drop()
	patDB.corpusDict.insert(docFreq)
	print 'Doc freq dict saved as collection \'corpusDict\'.'
	print 'tf-idf done!'



def main():
	
	c = MongoClient()
	patDB = c.patents
	
		
	# load the patents, but only their titles and abstracts
	# (_id is automatically loaded, too, and is used later for
	# patDB.save)
	
	
	tf_idf(patDB)
	
	# now save the dict of word document frequencies
	#patDB.corpusDict.insert(corpusDict)

# Makes main() run on typing 'python tf-idf.py' in terminal
if __name__ == '__main__':
    main()







