
from pymongo import MongoClient
from parallelMap import parallelMap

patDB = MongoClient().patents
patns = patDB.patns


def has_tf_idfs(pat):
	if 'text' not in pat: return False
	for word in pat['text']:
		if 'tf-idf' in word: return True
		else: return False

def return_updated_text(patn):
	if has_tf_idfs(patn):
		return
	else:
		for word in patn['text']:
			idf = patDB.corpusDict.find_one({'_id': word})['value']['idf']
			patn['text'][word]['tf-idf'] = patn['text'][word]['tf'] * idf
	return( {'$set': {'text' : patn['text'] } } )

def check_tf_idfs(pats):
	parallelMap(return_updated_text, pats, pats,
				findArgs = {'spec': {}, 'fields': {'text': 1} },
				updateFreq = 5000,
				bSize = 5000)

