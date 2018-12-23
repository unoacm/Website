var deleteLinks = document.getElementsByClassName('delete-confirm')
for(var i = 0; i < deleteLinks.length; i++) {
	deleteLinks[i].onclick = function() {
		return confirm("Are you sure you want to delete?")
	}
}