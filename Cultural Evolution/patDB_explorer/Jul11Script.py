from pymongo import MongoClient()
import logging

# For logging: copied from Andy's readPatnsFromFiles.py
fnLog = 'backCiteswNewCol.log'
frOutputData = 'html/data/'
logFormat = "%(asctime)s %(levelname)s %(processName)s\t%(message)s"
logging.basicConfig(filename=fnLog, level=logging.NOTSET, format = logFormat)



c = MongoClient()
patDB = c.patents
patns = patDB.patns
cite_net = patDB.cite_net


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
	execfile("makeCiteDB.py")
	
	#updateMainDB(cite_net, patns)

if __name__ == '__main__':
	main()


