var fileInput = document.getElementById('validatedCustomFile');
var label = document.getElementsByClassName('custom-file-label')[0]
fileInput.addEventListener('change', function(){
	label.innerHTML = fileInput.files[0].name
});