function deleteModel(formId) {
	var form = document.getElementById(formId);
	if(form != null) {
		if(confirm('Are you sure you want to delete this?')) {
			form.submit();
		}
	}
}