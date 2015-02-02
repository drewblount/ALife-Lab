// goal: sum the contents of each dictionary in values
function docFreqReduce(word,values){
	var result = {};
	for(var i=0; i<values.length; i++){
		var item=values[i];
		for(var j=0; j<Object.keys(item).length; j++){
			var key = Object.keys(item)[j]
			if(!result[key]){
				result[key] = item[key];
			} else {
				result[key] += item[key];
			}
		}
	}
}