from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
import auth.auth as authentication
from flask_wtf import FlaskForm
from database.models.user import UserAction
import datetime
import os
from wtforms import (
	StringField, SubmitField, SelectField, FileField
)
from wtforms.validators import (
	DataRequired
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash, send_from_directory, request
)

class DocumentForm(FlaskForm):
	title 			= StringField("Title", validators=[DataRequired()])
	description 	= StringField("Description", validators=[DataRequired()])
	document_access = SelectField(
		'User Access',
		choices 	= [(authentication.PUBLIC, 'Public'), (authentication.ADMIN, 'Private')],
		validators 	= [DataRequired()]
	)
	file = FileField("File", validators=[DataRequired()])

class DocumentEditForm(DocumentForm):
	file = FileField("File", description='If you leave this field blank, it will use the previously saved file.')

class Document(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	title 			= db.Column(db.String(), nullable=False)
	description 	= db.Column(db.String(), nullable=False)
	document_access = db.Column(db.String(), nullable=False)
	file_type 		= db.Column(db.String(), nullable=False)
	hidden_fields 	= ['id', 'description']
	
	def __init__(self, title, description, file_type, document_access='public'):
		self.title 				= title
		self.description 		= description
		self.document_access	= document_access
		self.file_type 			= file_type

	@staticmethod
	def __dir__():
		return ['id', 'title', 'description', 'document_access', 'file_type']

	@staticmethod
	def exists_id(id):
		return Document.query.filter_by(id=id).first()

	@staticmethod
	def getAllRoute():
		return url_for('document.documents_get')

	@staticmethod
	def getNewRoute():
		return url_for('document.document_new')

	def getEditRoute(self):
		return url_for('document.document_edit', document_id=self.id)
	
	def getDeleteRoute(self):
		return url_for('document.document_delete', document_id=self.id)
	
	def getGetRoute(self):
		return url_for('document.document_get', document_id=self.id)

blueprint = Blueprint('document', __name__, url_prefix='/document')

@blueprint.route('/new', methods=['GET', 'POST'])
@authentication.can_write(Document.__name__)
def document_new():
	documentForm = DocumentForm()
	if request.method == 'POST':
		if documentForm.validate_on_submit():
			user 			= authentication.getCurrentUser()
			fileData 		= documentForm.file.data
			title 			= documentForm.title.data
			description 	= documentForm.description.data
			document_access = documentForm.document_access.data
			file_type 		= os.path.splitext(fileData.filename)[1][1:]

			newDocument = Document(title=title, description=description, document_access=document_access, file_type=file_type)
			db.session.add(newDocument)
			user.actions.append(UserAction(model_type=Document.__name__, model_title=title+'.'+file_type, action='Created', when=datetime.datetime.now()))
			db.session.commit()
			uploadFile(fileData, newDocument.id)

			flash('Document Created', 'success')
			return redirect(newDocument.getEditRoute())

	return authentication.auth_render_template('admin/model.html', form=documentForm, type='new', model=Document, breadcrumbTitle='New Document')

@blueprint.route('/<int:document_id>/edit', methods=['GET', 'POST'])
@authentication.can_read(Document.__name__)
def document_edit(document_id):
	editingDocument = Document.exists_id(document_id)
	if editingDocument == None:
		return redirect(Document.getAllRoute())
	
	documentForm = DocumentEditForm()
	if request.method == 'POST':
		if authentication.getCurrentUser().canWrite(Document.__name__) and documentForm.validate_on_submit():
			user 			= authentication.getCurrentUser()
			fileData 		= documentForm.file.data
			title 			= documentForm.title.data
			description 	= documentForm.description.data
			document_access = documentForm.document_access.data
			
			if fileData:
				editingDocument.file_type = os.path.splitext(fileData.filename)[1][1:]
				uploadFile(fileData, document_id)

			editingDocument.title 			= title
			editingDocument.description 	= description
			editingDocument.document_access = document_access

			user.actions.append(UserAction(model_type=Document.__name__, model_title=title+'.'+editingDocument.file_type, action='Edited', when=datetime.datetime.now()))
			db.session.commit()
			flash('Document Edited', 'success')

	documentForm.title.data 			= editingDocument.title
	documentForm.description.data 		= editingDocument.description
	documentForm.document_access.data 	= editingDocument.document_access
	return authentication.auth_render_template('admin/model.html', form=documentForm, type='edit', model=Document, breadcrumbTitle=documentForm.title.data, data=editingDocument)

@blueprint.route('/<int:document_id>/delete', methods=['POST'])
@authentication.can_write(Document.__name__)
def document_delete(document_id):
	editingDocument = Document.exists_id(document_id)
	if editingDocument == None:
		flash('Document does not exist', 'danger')
	else:
		user = authentication.getCurrentUser()
		deleteFile(document_id)
		user.actions.append(UserAction(model_type=Document.__name__, model_title=editingDocument.title+'.'+editingDocument.file_type, action='Deleted', when=datetime.datetime.now()))
		db.session.delete(editingDocument)
		db.session.commit()
		flash('Document Deleted', 'success')
		
	return redirect(Document.getAllRoute())

@blueprint.route('/<int:document_id>/')
def document_get(document_id):
	from flask import current_app as app
	user = authentication.getCurrentUser()
	gettingDocument = Document.query.filter_by(id=document_id).first()
	if gettingDocument == None:
		flash('Document does not exist')
		return redirect(url_for('main.documents'))
	if gettingDocument.document_access == authentication.ADMIN:
		if user == None or not user.canRead(Document.__name__):
			flash('You do not have permission', 'danger')
			return redirect(url_for('main.documents'))

	return send_from_directory(app.config['DOCUMENT_PATH'], str(document_id),
			as_attachment = True,
			attachment_filename=gettingDocument.title + "." + gettingDocument.file_type)

@blueprint.route('documents')
@authentication.can_read(Document.__name__)
def documents_get():
	documents = Document.query.all()
	return authentication.auth_render_template('admin/getAllBase.html', data=documents, model=Document, hidden_fields=Document.hidden_fields)

def getDocumentsByUserType(type):
	if type == authentication.ADMIN and authentication.getCurrentUser().canRead(Document.__name__):
		return Document.query.order_by(Document.title).all()
	return Document.query.order_by(Document.title).filter_by(document_access=authentication.PUBLIC).all()

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