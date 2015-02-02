## The goal of this script is to save a numpy array of the number
## of patents per week in each week of the database.

from pymongo import MongoClient
import numpy as np

patns = MongoClient().patents.patns

map_fun = Code('''
    function map() {
    	var d = new Date(1976, 1, 6, 0, 0, 0, 0);
    	age_weeks = ((d.getTime() - this['isd'].getTime()) / (1000 * 3600 * 24 * 7.0)).toFixed();
    	emit(age_weeks, 1)
    }'''
)

red_fun = Code('''
    function reduce(key,values){
    	return Array.sum(values);
    }'''
)
    

result = patns.map_reduce(map_fun, red_fun, query={"isd": {"$exists": True}} )
np.save('raw_MR_out.npy',np.array(result))