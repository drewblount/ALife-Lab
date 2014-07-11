from pymongo import MongoClient
import logging
import populateNewCiteDB
from datetime import datetime

# For logging: copied from Andy's readPatnsFromFiles.py
fnLog = 'backCiteswNewCol.log'
frOutputData = 'html/data/'
logFormat = "%(asctime)s %(levelname)s %(processName)s\t%(message)s"
logging.basicConfig(filename=fnLog, level=logging.NOTSET, format = logFormat)



c = MongoClient()
patDB = c.patents
patns = patDB.patns
cite_net = patDB.cite_net
just_cites = patDB.just_cites


# After drawing back-cites in the lightweight cite_net collection,
# transfers them to the main collections
# note that in auxCol, patent numbers have key '_id', whereas in
# mainCol the key is 'pno'.
def updateMainDB(aux_col, main_col):

# For each patn in aux_col, copy its citedby field into the patn in main_col

    copy_cites_js ='''
db.%(aux_name)s.find( {}, {_id: 1, citedby: 1} ).forEach(function (obj) {
db.%(main_name)s.update( {pno: obj['_id'] }, {$set: {citedby: obj['citedby'] } } )
} );
''' % {'aux_name': aux_col.name, 'main_name' : main_col.name}

    patDB.eval(copy_cites_js)




def main():
	
	print str(datetime.now()) + ' POPULATING NEW CITE NET DB'
	
	populateNewCiteDB.storeCiteNetwork()
	print "loading cite_network into memory with mongo db.touch."
	logging.info("loading cite_network into memory with mongo db.touch.")
	patDB.eval('''db.runCommand({ touch: "cite_net", data: true, index: true })''')
	print "cite_net in memory"
	logging.info("cite_net in memory")
	populateNewCiteDB.drawBackCites(citeNetwork)
	print "back_cites drawn" #; copying to main db"
	logging.info("back_cites drawn") #; copying to main db")



	print str(datetime.now()) + ' MAKING PURE CITE DB (FOR RANDOMIZATION)'
	execfile("makeCiteDB.py")
	
	
	
	print str(datetime.now()) + ' RANDOMIZING PURE CITE DB'
	execfile("randomizeCollection.py")
	print str(datetime.now()) + ' CREATING RAND IDS'
	create_rand_ids(just_cites)
	print str(datetime.now()) + ' INDEXING RAND IDS'
	index_rand_ids(just_cites)



	print str(datetime.now()) + ' ~~~~~CHANGING~GEARS~~~~~'
	print str(datetime.now()) + ' SORTING EACH PATENT\'S TEXT'
	execfile("topWords.py")
	sort_all_texts(patns)
	


    #updateMainDB(cite_net, patns)

if __name__ == '__main__':
    main()

