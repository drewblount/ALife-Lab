import multiprocessing
from pymongo import MongoClient
from parallelMap import parallelMap
from tokeAndClean import tokeAndClean

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
		text = tokeAndClean(text)
		text = countWords(text)
		text = normalizeWordFreq(text)
		
		return( {'$set': {'text' : text} } )
	
    # I updated findArgs so that only fresh patents are grabbed
	parallelMap(initText, patDB.new_patns, patDB.new_patns
				findArgs = {'spec': {}, 'fields': {'title':1, 'abstract':1} },
				# sends bulk updates to the db every updateFreq patents
				updateFreq = 10000,
				bSize = 10000)

initFreshTexts(MongoClient.patns)

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


