function mainCheckboxChange(checkbox) {
	for(var i = 1; i < checkboxes.length; i++) {
		if(checkboxes[i].parentElement.parentElement.parentElement.style.display === "") {
			checkboxes[i].checked = checkbox.checked;
		}
	}
	changeSelectedNumber();
}

function checkboxChange(checkbox) {
	checkbox.checked = checkbox.checked;
	changeSelectedNumber();
}

function changeSelectedNumber() {
	var count = 0;
	for(var i = 1; i < checkboxes.length; i++) {
		if(checkboxes[i].parentElement.parentElement.parentElement.style.display === ""
				&& checkboxes[i].checked) {
			count++;
		}
	}
	selectedAmount.innerText = count;
	document.getElementById('checkbox-main').checked = count === parseInt(maxAmount.innerText);
}

function search(inputID) {
	var inputText = document.getElementById(inputID).value.toLowerCase();
	if(inputText === "") {
		for(var i = 1; i < tableRows.length; i++) {
			tableRows[i].style.display = "";
		}
	}
	else
	{
		for(var i = 1; i < tableRows.length; i++) {
			var matchFound = false;
			var cells = tableRows[i].cells;
			for(var j = 1; j < cells.length; j++) {
				if(cells[j].innerText.toLowerCase().includes(inputText)) {
					matchFound = true;
					break;
				}
			}
			if(matchFound) {
				tableRows[i].style.display = "";
			}
			else {
				tableRows[i].style.display = "none";
			}
		}
	}

	maxAmount.innerText = currentRowsVisible();
	changeSelectedNumber();
}

function currentRowsVisible() {
	var count = 0;
	for(var i = 1; i < tableRows.length; i++) {
		if(tableRows[i].style.display === "") {
			count++;
		}
	}

	return count;
}

document.getElementById('search').addEventListener('keypress', function(event) {
	if(event.keyCode === 13) {
		search('search');
	}
});
var inputs = document.getElementsByTagName("input");
var selectedAmount = document.getElementById("selectedAmount");
var maxAmount = document.getElementById("maxAmount");
var tableRows = document.getElementById('model-table').rows;
var checkboxes = [];
for(var i = 0; i < inputs.length; i++) {
	if(inputs[i].type === "checkbox") {
		checkboxes.push(inputs[i]);
	}
}
changeSelectedNumber();