// to be applied to each object in cite_net:

function clean(entry) {
	var clean_citedby = entry.citedby.filter(function(item, pos) {
		return entry.citedby.indexOf(item) == pos;
	});
	db.cite_net.update( {_id : entry._id}, {$set: {citedby: clean_citedby, cleaned: true} } );
	db.patns.update( {pno : entry._id}, {$set: {citedby: clean_citedby} } );
}

// in db = patents
// limiting batch size because of recurring cursor timeout
db.cite_net.find({cleaned:{$exists: false}},{cleaned:1,citedby:1}).batchSize(1000).forEach(clean)