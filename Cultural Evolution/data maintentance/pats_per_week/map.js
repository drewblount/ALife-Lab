// map each patent to the number of weeks from Jan 06, 1976 and its own ISD

function map() {
	var d = new Date(1976, 1, 6, 0, 0, 0, 0);
	// float divide by ms/s, s/h, h/d, d/wk, and then round to int
	age_weeks = ((d.getTime() - this['isd'].getTime()) / (1000 * 3600 * 24 * 7.0)).toFixed();
	emit(age_weeks, 1)
}