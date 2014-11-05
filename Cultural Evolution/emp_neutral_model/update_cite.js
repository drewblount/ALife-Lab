
// This function adds a 'prev_cites_to_src' and 'src_age_in_days' field to each
// cite object in patents.just_cites.
// The prev_cites_to_src field relies on the info in the collection cite_net,
// and src_age_in_days relies on the collection patns
function add_prior_stats(cite) {
	
	var parent_pno = cite['ctd'];
	var child_pno = cite['src'];
	
	var parent_cite = db.just_cites.findOne(
		{'_id': parent_pno},
		{'citedby': 1}
	);
	
	var set_arg = {};
	
	if (parent_cite) {
		prev_cites_to_parent = parent_cite.citedby.filter(
			function(pno) { return pno < child_pno } 
		);
		set_art['prev_cites_to_src'] = prev_cites_to_parent.length;
	}
	
	var parent_pat = db.patns.findOne(
		{'pno': parent_pno},
		{'isd': 1}
	);
	
	var child_pat = db.patns.findOne(
		{'pno': child_pno},
		{'isd': 1}
	);
	
	if (parent_pat && child_pat) {
		var diff = (parent_pat.isd - child_pat.isd);
		var day_in_milliseconds = 24*60*60*1000;
		var diff_in_days = Math.round(diff / day_in_milliseconds);
		set_arg['src_age_in_days'] = diff_in_days;
	}
	
	if (set_arg != {}) {
		db.just_cites.update( {_id: cite._id}, {$set: set_arg} )
	}
	
}

