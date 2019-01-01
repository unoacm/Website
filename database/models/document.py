from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
from utils.forms import RedirectForm
import auth.auth as authentication
import utils.utils as utils
import os
from wtforms import (
	StringField, SubmitField, PasswordField, SelectField, FileField
)
from wtforms.validators import (
	DataRequired
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash, 
)

class DocumentForm(RedirectForm):
	title = StringField("Title: ", validators=[DataRequired()])
	description = StringField("Description: ", validators=[DataRequired()])
	document_access = SelectField(
		'User Access',
		choices = [(authentication.PUBLIC, 'Public'), (authentication.ADMIN, 'Admin')],
		validators = [DataRequired()]
	)
	file = FileField(validators=[DataRequired()])
	submit = SubmitField("Submit")

class DocumentEditForm(DocumentForm):
	file = FileField()
	submit = SubmitField("Submit")

class Document(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(30), nullable=False)
	description = db.Column(db.String(200), nullable=False)
	document_access = db.Column(db.String(20), nullable=False)
	file_type = db.Column(db.String(10), nullable=False)
	
	def __init__(self, title, description, file_type, document_access='public'):
		self.title = title
		self.description = description
		self.document_access = document_access
		self.file_type = file_type

	@staticmethod
	def __dir__():
		return ['id', 'title', 'description', 'document_access', 'file_type']

	@staticmethod
	def exists_id(id):
		return Document.query.filter_by(id=id).first()

	@staticmethod
	def getNewRoute():
		return url_for('document.document_new')

	def getEditRoute(self):
		return url_for('document.document_edit', document_id=self.id)
	
	def getDeleteRoute(self):
		return url_for('document.document_delete', document_id=self.id)

blueprint = Blueprint('document', __name__, url_prefix='/document')

@blueprint.route('/new', methods=['GET', 'POST'])
def document_new():
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))

	documentForm = DocumentForm()
	if documentForm.validate_on_submit():
		fileData = documentForm.file.data
		title = documentForm.title.data
		description = documentForm.description.data
		document_access = documentForm.document_access.data
		file_type = fileData.filename[fileData.filename.index('.'):]

		newDocument = Document(title=title, description=description, document_access=document_access, file_type=file_type)
		db.session.add(newDocument)
		db.session.commit()
		uploadFile(fileData, newDocument.id)

		flash('Document Created', 'success')
		return documentForm.redirect(url_for('admin.index'))

	return render_template('models/document-form.html', form=documentForm, type='new')

@blueprint.route('/<int:document_id>/edit', methods=['GET', 'POST'])
def document_edit(document_id):
	if not authentication.isLoggedIn(authentication.ADMIN):
		return redirect(url_for('admin.login'))
	editingDocument = Document.exists_id(document_id)
	if editingDocument == None:
		return redirect(url_for('admin.index'))
	
	documentForm = DocumentEditForm()
	if documentForm.validate_on_submit():
		fileData = documentForm.file.data
		title = documentForm.title.data
		description = documentForm.description.data
		document_access = documentForm.document_access.data
		
		if fileData:
			file_type = fileData.filename[fileData.filename.index('.'):]
			editingDocument.file_type = file_type
			uploadFile(fileData, document_id)

		editingDocument.title = title
		editingDocument.description = description
		editingDocument.document_access = document_access

		db.session.commit()
		flash('Document Edited', 'success')
		return documentForm.redirect(url_for('admin.index'))

	documentForm.title.data = editingDocument.title
	documentForm.description.data = editingDocument.description
	documentForm.document_access.data = editingDocument.document_access
	return render_template('models/document-form.html', form=documentForm, type='edit')

@blueprint.route('/<int:document_id>/delete', methods=['POST'])
def document_delete(document_id):
	if not authentication.isLoggedIn(authentication.ADMIN):
		return redirect(url_for('admin.login'))
	editingDocument = Document.exists_id(document_id)
	if editingDocument == None:
		return redirect(url_for('admin.index'))

	deleteFile(document_id)
	Document.query.filter_by(id=document_id).delete()
	db.session.commit()
	flash('Document Deleted', 'success')
	return redirect(utils.get_redirect_url() or url_for('admin.index'))

def uploadFile(fileData, id):
	from flask import current_app as app
	path = os.path.join(app.config['DOCUMENT_PATH'], str(id))
	fileData.save(path)

def deleteFile(id):
	from flask import current_app as app
	path = os.path.join(app.config['DOCUMENT_PATH'], str(id))
	try:
		os.remove(path)
	except:
		pass