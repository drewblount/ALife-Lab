xcxcfrom pymongo import MongoClient()
c = MongoClient()
c.patents.eval('''db.runCommand({ touch: "patns", data: true, index: true })''')
