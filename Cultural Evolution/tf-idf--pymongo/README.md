TF-IDF with pymongo
------------------------
------------------------

The purpose of these files is to compute tf-idf scores for each word in each patent in a MongoDB database, in parallel. The words in each patent with the highest tf-idf scores "say the most" "about" the patent, so semantics is completely reduced to statistics.

The tf-idf process takes a few steps, some or all of each must be completed before the next:
1.  For each patent, count the frequency of each word in its text.
2.  Normalize these frequencies, generating a "term frequency" or tf value for each word in each patent
3.  For each word that appears in the corpus (the body of patents), count how many patents contain that word, generating a "document frequency" for each word in the corpus's dictionary.
4.  Take the logarithm of the (total number of patents) / (document frequency) for each word in the corpus dictionary, producing the "inverse document frequency" or idf.
5.  For each patent, for each word in that patent, multiply that word's term frequency (in that patent) by its document frequency (across the corpus) to get its tf-idf score. 

I parallelized the above steps using two methods:

"parallelMap" : steps 1, 2, and 5
----------------------------------
I did steps 1, 2, and 5 in parallel, in Python, and in a kind-of-crude way. In each case, an update function is mapped across a collection, using a useful li'l generic map generator I made called "parallelMap". 
I say that parallelMap is kind-of-crude because it just partitions the input collection into P equal-sized chunks, where P is the number of processors available to python.multiprocessing. Each processor works on its own partition, and doesn't help the others if it finishes early. Nonetheless, it runs way faster than if it was single-threaded, and I kind of like how simple and easy it is.


Map-Reduce: steps 3 & 4
------------------------------
At first, seduced by the buzzword, I wanted to use map/reduce for everything. I too-slowly realized that step 3 above is the only one I could easily mapreduce, which is (I now know) a tool for getting aggregated statistics, not for finding and updating field values throughout a collection. My solution to 3) in tf_idf.generateDocFreq is in fact Baby's First Map/Reduce. The advantage is that with pymongo.map_reduce() the mongod server does all of the hard work (not stupid slow idiot Python), and automatically parallelizes reallyfast.

Step 4 is snuck into an optional "finalize" argument to map_reduce, and so is also done "server-side," "in-parallel."

I looked into just using a mongoDB map function for 1, 2, and 5, but it didn't work well with pymongo. Now that I've learned JavaScript for the map and reduce functions, maybe I could go back and write JS functions to do 1, 2, and 5 over on mongod, if it ever makes sense to spend that much time to make something go faster.