from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import bigrams, trigrams
from nltk.stem.snowball import SnowballStemmer

# Defaults to using nltk's english stopwords and SnowBallStemmer
# ngramMinFreq is the minimum number of times an n-gram must appear
# for it to be included in the database
def tokeAndClean(str, bgrams = False, tgrams = False, stopwords = stopwords.words('english'), ngramMinFreq = 2, stemming = True, stemmer = SnowballStemmer('english')):
	tokenizer = RegexpTokenizer("[\w']+")

	tokens = tokenizer.tokenize(str)
	# lower-cases everything, removes words < 2 letters
	tokens = [token.lower() for token in tokens if len(token) > 2]
	
	if stemming:
		try:
			tokens = [stemmer.stem(token) for token in tokens if len(token) > 2]
	# sometimes get a weird error from snowball because these tokens have length longer than 3 where the tokens are too short and snowball
		except:
			tokens = [stemmer.stem(token) for token in tokens if len(token) > 3]

	def cleanNGram(ngrams):
		out = [' '.join(token) for token in ngrams]
		# includes only those ngrams which occur at least ngramMinFreq times
		out = [ngram for ngram in out if out.count(ngram) >= ngramMinFreq]
		return out
	
	# adds cleaned bigrams and trigrams if necessary
	if(bgrams): tokens.extend(cleanNGram(bigrams(tokens)))
	if(tgrams): tokens.extend(cleanNGram(trigrams(tokens)))
		
	
	return tokens
