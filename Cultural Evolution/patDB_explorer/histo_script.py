import matplotlib.pyplot as plt

execfile('comber.py')
all_tfidfs = tf_idf_comb(1000)

plt.hist(all_tfidfs, 75,range=(0,0.75),color='r')
plt.title("tf-idfs of all terms from the week of 4/15/2014")
plt.xlabel("tf-idf of stemmed word (stop words not removed)")
plt.show()
