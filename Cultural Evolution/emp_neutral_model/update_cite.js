
// This function adds a 'prev_cites_to_src' and 'src_age_in_days' field to each
// cite object in patents.just_cites.
		 
// assumed: all relevant fields are in the patns collection, i.e., 
// the function in clean_citedby.js has been applied to each document
// in cite_net
function add_prior_stats(cite) {
	// gets the parent, child, and their related fields
        // in just_cites, ctd = cited = parent, src = source = child
	var parent = db.patns.findOne( { pno:cite['ctd'] }, {pno:1,citedby:1,isd:1,_id:0} );
	var child  = db.patns.findOne( { pno:cite['src'] }, {pno:1,isd:1,_id:0} );
	var set_arg = {priord:true}
	
	// if-checks avoid dirty (incomplete) data
	if (parent.citedby) {
		prev_cites_to_parent = parent.citedby.filter(
			function(pno) { return pno < child.pno } 
		);
		set_arg['prev_cites_to_ctd'] = prev_cites_to_parent.length;
	}
	
	if (parent.isd && child.isd) {
		var diff = (child.isd - parent.isd);
		var day_in_milliseconds = 24*60*60*1000;
		var diff_in_days = Math.round(diff / day_in_milliseconds);
		set_arg['ctd_age_in_days'] = diff_in_days;
	}
	
	if (set_arg != {}) {
		db.just_cites.update( {_id: cite._id}, {$set: set_arg} )
	}
}

function add_prior_stats(cite) {
    var parent = db.patns.findOne( { pno:cite['ctd'] }, {pno:1,citedby:1,isd:1,_id:0} );
    var child  = db.patns.findOne( { pno:cite['src'] }, {pno:1,isd:1,_id:0} );
    var set_arg = {priord:true}
    if (parent.citedby) {
	prev_cites_to_parent = parent.citedby.filter(
						     function(pno) { return pno < child.pno }
						     );
	set_arg['prev_cites_to_ctd'] = prev_cites_to_parent.length;
    }
    if (parent.isd && child.isd) {
	var diff = (child.isd - parent.isd);
	var day_in_milliseconds = 24*60*60*1000;
	var diff_in_days = Math.round(diff / day_in_milliseconds);
	set_arg['ctd_age_in_days'] = diff_in_days;
    }
    if (set_arg != {}) {
	db.just_cites.update( {_id: cite._id}, {$set: set_arg} )
    }
}
