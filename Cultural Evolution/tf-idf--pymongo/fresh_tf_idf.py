## The goal of this file is to go through the database after fresh patents
## have been added (those with field 'fresh': True), and update all tf-idf
## related stats db-wide

## my batch tf_idf writer
import tf_idf
from pymongo import MongoClient
from bson.code import Code
from math import log
from parallelMap import parallelMap




## Idea: Have all newly-added patents contain the field {fresh: True}
## so that they can easily be grabbed


def initFreshTexts(patDB):

	# The func that, once passed to parallelMap, will populate
	# the 'text' field for each patent
	# returns a pymongo update dict setting the patent's text
	# field to a dictionary of elements like
	# (word: {freq: wordFreq, tf: normalizedWordFreq})
	
	def initText(patn):

		text = ''
		if  'title' in patn: text += patn['title']
		else :
			#logging.warning('No title for patent %d.',    patn['pno'])
			pass # oh well, so it goes
		if 'abstract' in patn: text += (' ' + patn['abstract'])
		else :
			#logging.warning('No abstract for patent %d.', patn['pno'])
			pass # what could we do about it?
		
		# faster, for testing:
		# text = tokeAndClean(text, stemming = False, stopwords = [])
		text = tf_idf.tokeAndClean(text)
		text = tf_idf.countWords(text)
		text = tf_idf.normalizeWordFreq(text)
		
		return( {'$set': {'text' : text} } )

    # I updated findArgs so that only fresh patents are grabbed
	parallelMap(initText, patDB.patns,
				findArgs = {'spec': {'fresh': {'$exists':True}}, 'fields': {'fresh':1,'title':1, 'abstract':1} },
				# sends bulk updates to the db every updateFreq patents
				updateFreq = 10000,
				bSize = 10000)

# uses map/reduce to get the number of fresh documents containing each word,
# and should send that to the corpusDict database additively (not replacing)
def updateDocFreq(patDB, outColName = 'corpusDict'):

	map    = Code(open('fresh_docFreqMap.js').read())
	reduce = Code(open('fresh_docFreqReduce.js').read())

	# finIDF will calculate IDF scores, so I have to pass it
	# the number of total docs in a crafty way.
	size = patDB.patns.count()
	# replace all instances of TOTALDOCS with size in docFreqFinalize.js
	finIDF = open('docFreqFinalize.js').read()
	finIDF = finIDF.replace('TOTALDOCS', str(size))
	
	# patDB.patns.map_reduce(map, reduce, outColName, finalize=finIDF)
	# can either reduce into outColName or replace it. I like replace for now
    ## I changed 'out' from 'replace' to 'reduce', that should combine the results
    ## uh-oh, I'm not sure if that works, because of the way docFreqFinalize works
	patDB.patns.map_reduce(map, reduce, out = {'reduce':outColName}, finalize=finIDF)
    
## because of wonky pymongo handling of foreach, this takes a mongo client
## After running updateDocFreq, all IDFs in corpusDict are incorrect and must be
## fixed
def updateIDF(patDB):
    total_docs = patDB.patns.count()
    def find_idf(word_entry):
        idf = log(total_docs*1.0/word_entry['df'])
        return( {'$set': {'idf': idf} } )
    parallelMap(find_idf, padDB.corpusDict, findArgs = {'spec':{'df':{'$exists':True}}}, updateFreq=10000)
        
    
# assumes fresh patents have had their docFreqs added to corpusDict, and the idf
# values
def freshen_tf_idf(patDB):

	def tf_idf_onePat(patn):

		for word in patn['text']:
			# getting the arguments of this find_one right was weirdly difficult
			# making it so the db doesn't have to be called each time a patent
			# has word w would be a big improvement, I think
			idf = patDB.corpusDict.find_one({'_id': word})['value']['idf']
			patn['text'][word]['tf-idf'] = patn['text'][word]['tf'] * idf
		return( {'$set': {'text' : patn['text'] } } )

	parallelMap(tf_idf_onePat, patDB.patns,
				findArgs = {'spec': {}, 'fields': {'text': 1} },
				updateFreq = 15000,
				bSize = 15000)


def main():
    patDB = MongoClient().patents.patDB
    initFreshTexts(patDB)
    updateDocFreq(patDB)
    updateIDF(patDB)
    # now every idf value must be updated
    
    