# The purpose of this file is to quickly grab certain fields from patents
# for use in visualization and reporting


from pymongo import MongoClient
from topWords import topNTerms

patDB = MongoClient().patents
patns = patDB.patns

def get_text(pno):
    p = patns.find_one({'pno':pno},{'title':1, 'abstract':1})
    if not p:
        return 'Patent #%d not in database' % pno
    
    text = ''
    if 'title' in p:
        text += str(p['title']) + '\n'
    if 'abstract' in p:
        text += str(p['abstract'])
    
    if text == '':
        return 'Patent #%d has no text in DB' % pno

    return text

# return's the top n tf-idf terms
def get_top_n(pno, n, pretty=False):
    p = patns.find_one({'pno':pno},{'sorted_text':1,'text':1})
    if not p:
        return 'Patent #%d not in database' % pno

    terms = topNTerms(p, n)
    clean_terms = [(str(entry['word']),entry['tf-idf']) for entry in terms]
    
    if pretty:
        extra_clean = '\n'
        for term in clean_terms:
            # tf-idf is width-6, precision to 4 places
            extra_clean += '{:6.4f}'.format(term[1])
            extra_clean += '  %s\n' % term[0]
        print extra_clean

    else: return clean_terms
        
