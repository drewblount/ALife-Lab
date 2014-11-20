// Map, Reduce, and Finalize functions for the mongoDB generation of the
// empirical neutral model

// as it's a little awkward to sum 2d arrays of variable size with mapreduce,
// the objects being reduced will look like this:
// key: ctd_age_in_days, value: assoc. array of {# prior cites : count}
// so each age value will be an array of # prior cites counts.


var map = function() {
	if ('ctd_age_in_days' in this && 'prev_cites_to_ctd' in this) {
		var prevs = this.prev_cites_to_ctd;
		emit(this.ctd_age_in_days, {prevs:1});
	}
}

// value is constructed weirdly so that its key is an integer, this.prev_cites_to_ctd
var map = function() {
	var value = {}
	value[this.prev_cites_to_ctd]=1
	emit(this.ctd_age_in_days, value);

}

var mapFunction2 = function() {
                           var key = this.ctd_age_in_days;
                           var value = {
                                         count: 1,
                                         qty: this.items[idx].qty
                                       };
                           emit(key, value);
                    };

//function reduce(ageKey, prev_count_dicts) {
var reduce = function(ageKey, prev_count_dicts) {
	reduced = {}
	for (var i = 0; i < prev_count_dicts.length; i++) {
		for (var count_num in prev_count_dicts[i]) {
			if (count_num in reduced) {
				reduced[count_num]+=prev_count_dicts[i][count_num]
			}
			else {
				reduced[count_num]=prev_count_dicts[i][count_num]
			}
		}
	}
	return reduced
}

db.just_cites.mapReduce(map, reduce, {out: 'emp_neut_data', query: {prev_cites_to_ctd: {$exists: true}, ctd_age_in_days: {$exists: true}},limit:1000})
/*
function finalize(ageKey, prev_count_dicts) {
	var max_prev_count=0;
	for (var dict in prev_count_dicts) {
		for (var value in dict) {
			if (value > max_prev_count) max_prev_count=value;
		}
	}
	// ALL AGES CONVERTED DAYS->WEEKS!
	var max_age_diff = Math.floor(Math.max.apply(Object.keys(prev_count_dicts), null)/7);
	var output_arr = []
	
	
}