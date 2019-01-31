var options = document.getElementById('options');
var editOptionTemplate = document.getElementById('editOption')
var otherOptionsTemplate = document.getElementById('otherOptions')
var fields = document.getElementsByClassName('field');
var type = document.getElementById('type');
var originalData = [];
for(var i = 0; i < fields.length; i++) {
	if(fields[i].type =='radio') {
		originalData.push(fields[i].checked);
	}
	else {
		originalData.push(fields[i].value);
	}
}
var editMode = true;

function edit() {
	var clone = null;
	if(editMode) {
		type.innerHTML = 'View ';
		clone = editOptionTemplate.content.cloneNode(true);
		editMode = false;
	}
	else {
		type.innerHTML = 'Edit ';
		clone = otherOptionsTemplate.content.cloneNode(true);
		editMode = true;
	}
	options.innerHTML = '';
	options.appendChild(clone);
	for(var i = 0; i < fields.length; i++) {
		fields[i].disabled = !editMode;
		if(!editMode) {
			if(fields[i].type == 'radio') {
				fields[i].checked = originalData[i];
			}
			else {
				fields[i].value = originalData[i];
			}
		}
	}
}

edit();