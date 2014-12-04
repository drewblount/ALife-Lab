function count_raw(entry) {
	db.cite_net.update( {pno : entry._id}, {$set: {n_citedby: entry.citedby.length} } );
}
