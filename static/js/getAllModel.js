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

	var amountVisible = currentRowsVisible()
	maxAmount.innerText = amountVisible;
	amount.innerHTML = amountVisible;
	var modelAmountTagString = amount.getAttribute('tag')
	if(amountVisible != 1) {
		modelAmountTagString += 's'
	}
	amountTag.innerHTML = modelAmountTagString;
	changeSelectedNumber();
}

function resetSearch(inputID) {
	document.getElementById(inputID).value = '';
	search('search');
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

function sendAction() {
	if(actionSelect.selectedIndex == 0) {
		return;
	}

	var ids = [];
	for(var i = 1; i < checkboxes.length; i++) {
		if(checkboxes[i].parentElement.parentElement.parentElement.style.display === ""
				&& checkboxes[i].checked) {
			ids.push(Number(checkboxes[i].parentElement.parentElement.parentElement.getAttribute('unique')))
		}
	}
	var request = new XMLHttpRequest();
	request.open("POST", document.URL, true);
	request.onreadystatechange = function() {
		if(request.readyState === 4 && request.status === 200) {
			if(request.getResponseHeader('Download') === 'yes') {
				var matchContentType = /(.*)?;.*/.exec(request.getResponseHeader('Content-Type'))
				var matchFileName = /attachment;filename=(.*)/.exec(request.getResponseHeader('Content-Disposition'))
				if(matchFileName != null && matchFileName.length > 1 && matchContentType != null && matchContentType.length > 1) {
					var blob = new Blob([request.response], {type: matchContentType[1]});
					var link = document.createElement('a');
					link.hidden = true;
					link.href = window.URL.createObjectURL(blob); 
					link.download = matchFileName[1];
					document.body.appendChild(link);
					link.click();
					document.body.removeChild(link);
				}
			}
			else {
				window.lcation.href = document.URL;
			}
		}
	};
	request.setRequestHeader('Content-Type', 'application/json');
	request.send(JSON.stringify({
		ids: ids,
		action: actionSelect.options[actionSelect.selectedIndex].text
	}));
}

var inputs = document.getElementsByTagName("input");
var selectedAmount = document.getElementById("selectedAmount");
var maxAmount = document.getElementById("maxAmount");
var amount = document.getElementById("amount")
var amountTag = document.getElementById("model-amount-tag")
var actionSelect = document.getElementById("action-select")
var tableRows = document.getElementById('model-table').rows;
var checkboxes = [];
for(var i = 0; i < inputs.length; i++) {
	if(inputs[i].type === "checkbox") {
		checkboxes.push(inputs[i]);
	}
}
changeSelectedNumber();

window.onload = function() {
	document.getElementById('search').value = '';
}