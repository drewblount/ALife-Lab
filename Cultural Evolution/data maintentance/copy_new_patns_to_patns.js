// this is a mongo shell script, saved for longevity
// from http://stackoverflow.com/questions/5681851/mongodb-combine-data-from-multiple-collections-into-one-how
db.new_patns.find().forEach(function(doc){db.patns.save(doc)})