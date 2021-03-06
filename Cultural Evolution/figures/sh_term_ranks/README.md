The histogram 'histogram_n=13.png' is incredible to me. 
It shows the tf-idf ranks of 100,000 terms shared across a citation-link, considering each patent's top 13 terms. 
Note there are two semi-transparent histograms atop eachother--one for parent-side ranks and one for child-side ranks. And note that these two histograms are nearly identical! 
Looking at the raw data, a shared term almost always has a different rank parent-side than child-side, yet in aggragate both parent- and child-side ranks follow almost exactly the same distribution.
I spot-checked this data in about ~20 places, confirming that it reflects what is actually in our database. I trust this incredible histogram to be correct.

RANDOM PAIRS: only 10,000 shared terms were measured, just because it is much harder computationally to find a shared term among a random pair of patents. A bigger sample can be measured any time, it'll just take a little bit.



AGGREGATE DATA (from the same data that made 'histogram_n=13.png', 100,000 shared terms):
  * avg tf-idf rank of a shared term, parent-side : 5.478
  * st dev of tf-idf rank of sh term, parent-side : 3.664
  * avg	tf-idf rank of a shared term, child-side  : 5.468
  * st dev of tf-idf rank of sh term, child-side  : 3.665

AGGREGATE DATA (from the rand-pair histogram data, 10,000 shared terms)
  * avg tf-idf of a shared term, either patent: 7.320
  * st dev of tf-idf of a shared term, either : 3.600