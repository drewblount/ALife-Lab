function docFreqMap() {
	if (!this.text) {
		return;
	}
	
	for (word in this.text) {
		emit(word, 1);
	}
	
	
	
}