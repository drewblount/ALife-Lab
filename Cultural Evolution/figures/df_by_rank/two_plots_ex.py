import numpy as np
import matplotlib.pyplot as plt


top_n = 13
num_terms = 100000
bins = [i for i in range(1, top_n+2)]


fig, ax1 = plt.subplots(figsize=(11, 8.5))

scaled_rps = [ [val/1000.0 for val in row] for row in rps]

ax1.boxplot(scaled_rps, positions = [i+0.5 for i in range(1,14)])
ax1.axis([1,15,0,250])
ax1.set_xlabel('per-patent tf-idf rank of shared term')
# Make the y-axis label and tick labels match the line color.
ax1.set_ylabel('document frequency of shared term, x1,000 \n(median/quartile box-and-whisker plots)')

ax2 = ax1.twinx()
ax2.hist(rphs, alpha=0.1, bins=bins, normed=True)
ax2.set_ylabel('normed number of shared terms per rank')

plt.title('doc-freq distribution and number of shared terms per tf-idf rank\nrand pairs of patents, p1 and p2 data combined')

plt.show()
