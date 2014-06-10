import xmltodict
from pymongo import MongoClient
import json


testFile = open("samPat.xml", "r")
testRead = testFile.read()

testDict = xmltodict.parse(testRead)

json.dump(testDict, open('test.json', 'wb'))
