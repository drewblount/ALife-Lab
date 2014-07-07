# Goal: order the words in a patent's text field by tf-idf (descending)

# python treats dictionaries as unordered, and it's awkward to reorder
# MongoDB's BSON objects, so I use a python array of dicts to hold the text
# while I shuffle it around

from pymongo  import MongoClient
from operator import attrgetter
import randPat


# for operations where a document's order is important,
# we want to store mongo objects as SON and not python
# dicts (which do not preserve order)


patDB = MongoClient().patents
patns = patDB.patns


# copies {key1: v1, key2: v2} into [{key: key1, v1}, {key: key2, v2}]
# (so there is some flattening, convenient for our use)
def dictToArray(D, keylabel = "key"):
	arr = []
	for elem in D:
		# just copies the dict entry in an array
		newElem = D[elem]
		newElem[keylabel] = elem
		arr.append(newElem)
	return arr

# For a patent, produces an array of the words in that patent's text
# in descending tf-idf order
def createSortedText(patn):
	textArray = dictToArray(patn['text'], keylabel='word')
	sortedTextArray = sorted(textArray, key=lambda w: w['tf-idf'], reverse = True)
	return sortedTextArray


def perLineArrayDisplay(arr):
	for elem in arr:
		print elem

# pretty prints a word and its tf-idf from a patent's sorted_text
def displaySortedWord(word):
	# makes all words width-20
	pstring = '{0: <15}'.format(word['word']) + ' tf-idf: ' + "%.3f" % word['tf-idf']
	print pstring


def topNTerms(patn, n, patCol_to_update = False, display=False):
	if 'sorted_text' not in patn:
		patn['sorted_text'] = createSortedText(patn)
		# if the optional patCol_to_update arg is used, and the patent's text has never
		# been sorted before, save the sorted text in the patent collection
		if patCol_to_update:
			patCol_to_update.update({'pno': patn['pno']},{'$set': {'sorted_text': patn['sorted_text']}})
	if display:
		print '\n'
		print 'Patent ' + str(pat['pno']) + ': ' + pat['title']
		for word in patn['sorted_text'][:n]:
			displaySortedWord(word)
	return patn['sorted_text'][:n]


def orderAllTexts(disp= False, showN= 10):
	pats = patns.find({}, {'pno':1, 'title': 1, 'text': 1, 'sorted_text': 1})
	for pat in pats:
		topNTerms(pat, showN, display=disp, patCol_to_update=patns)


# Returns the number of words shared by the top n words in each patent
# if returnWords is true, returns a list of the shared words. Otherwise
# just returns the number of shared words.
def sharedTopN(pat1, pat2, n, returnWords=False, patCol_to_update = False):
	words1, words2 = topNTerms(pat1, n, patCol_to_update), topNTerms(pat2, n, patCol_to_update)
	shCount = 0
	shWords = []
	for word1 in words1:
		for word2 in words2:
			if word1['word'] == word2['word']:
				if returnWords: shWords.append(word1['word'])
				else: shCount += 1
				break
	if returnWords: return shWords
	else: return shCount

# for randomly selected pairs
def aveSharedTopN(numTrials, n):
	totSharedTerms = 0
	selector = randPat.Selector(patns, projection={'pno':1, 'title': 1, 'text': 1, 'sorted_text': 1})

	for i in range(numTrials):
		pat1, pat2 = selector.randPat(), selector.randPat()
		totSharedTerms += sharedTopN(pat1, pat2, n, patCol_to_update=patns)
	return float(totSharedTerms)/numTrials













