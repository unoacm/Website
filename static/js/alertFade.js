function fade(element) {
	var op = 1;
	var timer = setInterval(function() {
		if(op <= 0.05) {
			clearInterval(timer);
			element.setAttribute('style', 'display: none !important');
		}
		element.style.opacity = op;
		op -= op * 0.1;
	}, 50);
}

var flashes = document.getElementById('flashes');
if(flashes != null) {
	setTimeout(function() {
		fade(flashes);
	}, 3000);
}