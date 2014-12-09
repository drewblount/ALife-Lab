EMPIRICAL NEUTRAL MODEL
=======================

.js files are scripts which were run on the mongo server to clean data.
arraymaker.py was used to transpose the empirical data from the mongo
db to a numpy array, which was saved as emp_neut_2darray.npy. The
heatmapper functions are the scripts that generated the images.

The goal here is to find two statistics for each citation in the patent network:

	1. The age of the parent at the time of citation
	2. The number of prior cites to the parent at the time of citation

This will inform a neutral model, where new patents cite old ones based purely on the empirical distribution of those two values across cite-space. This will let us account for aging and preferential attachment in a way consistent with empirical data.