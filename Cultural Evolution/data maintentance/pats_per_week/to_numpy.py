from pymongo import MongoClient
from bson.code import Code
import numpy as np


week_data = MongoClient().patents.week_counter

numweeks = 2003
outarr = np.empty(numweeks)

for week in week_data:
    age = -int(week['_id'])
    outarr[age]=week['value']
    
np.save('raw_MR_out.npy', outarr)
