## I'm writing this without an internet connection, so I've left a comment
## starting with '#note:' wherever there's something I'd like to look up

## The goal of this file is to take the data in the emp_neut_model collection
## and collate it into a big 2d histogram-style array

## accomplishing that goal will be as simple as using some (presumably)
## pre-existing library to save the np.array output of make_data_array
## as a .csv


from pymongo import MongoClient, ASCENDING
import numpy as np
from operator import add

patDB = MongoClient().patents

#note: what exactly is the name of this collection?
raw_data = patDB.emp_neut_data


# takes a dictionary of {nonnegative integer key: value} pairs 
# and turns it into an array
def dict_to_arr(D, arr_len=None):
    
    # can enforce arr_len, else chooses the largest key in dict
    if not arr_len:
        # translate keys to integers (mongodb uses unicode)
        keys = map(int,D.keys())
        arr_len = max(keys)
        
    # note that since mongodb has unicode keys we have to switch from int/unicode
    arr = np.array([int(D[unicode(n)]) if unicode(n) in D.keys() else 0 for n in range(arr_len)])
    return arr

# say you have the output of the above, then want t

def make_data_array(lim=None):
    
    #note: the below should get a cursor sorted ascending by agediff
    curs = raw_data.find({'_id':{'$gte':0}}).sort('_id',1)
    if lim:
        curs
    
    # weeknum makes sure that any holes in the data get fixed, i.e.,
    # if no empirical citation has a given agediff, there is no
    # entry for that agediff in the database, and we want to copy a zero
    # value instead of a null one
    # outarr isn't numpy bc i don't know how to construct a numpy array in a loop as below
    outarr = []
    weeknum = 0
    for row_dict in curs:
        #note: make sure current data is in days, double checking the below conversion
        #note: make sure _id contains the agediff field
        thisweek = row['_id']//7
        
        # if thisweek < rownum, that means there are multiple agediffs in days
        # that amount to the same agediff in weeks
        if thisweek < weeknum:
            #note: below line should element-wise add the two arrays
            outarr[weeknum] = elementwise_add(outarr[weeknum],dict_to_arr(row_dict['value']))
        
        else:
            # fills holes in the data with empty arrays
            while weeknum < thisweek:
                # not sure how to append to numpy arrays
                outarr.append([0])
                weeknum += 1
            #note: same as above
            outarr.append(dict_to_arr(row_dict['value']))
            weeknum += 1
            
    # now out_arr should be a misshapen 2d array whose i,jth entry is the number of
    # citations where the parent was age i, with j prior citations to it. Each row
    # is only as long as its nonzero values (hence misshapenness)
    
    #note: below line should make each row in outarr the same length by padding
    # short rows with 0
    out_arr = pad_with_zeroes(outarr)
    
    #note: make sure return type is how we want (numpy array)
    np.save('emp_neut_2darray.npy',out_arr)
    return outarr
      
# elementwise addition of two arrays, where one might be longer than the other
def elementwise_add(a1, a2):
    # l = overlapping length of arrays
    l = min(len(a1), len(a2))
    out_arr = map(add,a1[:l],a2[:l])
    if len(a1)>len(a2): out_arr = np.append(out_arr, a1[l:])
    else: out_arr = np.append(out_arr, a2[l:])
    return out_arr
    
# takes a lumpy 2d array (rows are of different lengths)
# and expands each row to be the same length by adding zeroes
def pad_with_zeroes(arr2d, row_len=None):
    if not row_len:
        row_len = max([len(row) for row in arr2d])
    for row_num in range(len(arr2d)):
        l = len(arr2d[row_num])
        if (l < row_len):
            # pads with zeroes
            arr2d[row_num] = np.lib.pad(arr2d[row_num],(0,row_len-l),'constant')
        elif (l > row_len):
            # trim the end
            arr2d[row_num] = arr2d[row_num][:l]
    return np.array(arr2d)
            
        
    
    
    