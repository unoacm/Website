var listItems = document.getElementsByClassName('list-group-item')
for(var i = 0; i < listItems.length; i++) {
	listItems[i].onmouseover = function() {
		this.classList.add("active")
	}
	listItems[i].onmouseout = function() {
		this.classList.remove("active")
	}
}