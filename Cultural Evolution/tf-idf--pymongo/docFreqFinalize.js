// Python will later replace all occurances of TOTALDOCS
// with the number of total documents, for computing idf.

function docFreqReduce(key, reducedVal){
	var calcIDF = Math.log( TOTALDOCS / reducedVal )
	
	return( {idf: calcIDF, df: reducedVal} )
	
	
}