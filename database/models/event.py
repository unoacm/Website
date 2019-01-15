from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
from utils.forms import RedirectForm
import auth.auth as authentication
import database.models.document as document_models
import utils.utils as utils
import datetime, os, zipfile
import time
from io import BytesIO
from wtforms import (
	StringField, SubmitField, FileField, TextAreaField, BooleanField, SelectMultipleField
)
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import (
	DataRequired, ValidationError
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash, send_from_directory, request, send_file
)

ALLOWED_PICTURE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

def validate_file_ext(form, field):
	if field.data:
		ext = field.data.filename[field.data.filename.rfind('.') + 1:]
		if ext.lower() not in ALLOWED_PICTURE_EXTENSIONS:
			raise ValidationError('Invalid file type')


class EventForm(RedirectForm):
	title = StringField("Title: ", validators=[DataRequired()])
	description = TextAreaField("Description: ", validators=[DataRequired()])
	start_date = DateField('Start Date: ', validators=[DataRequired()])
	end_date = DateField('End Date: ', validators=[DataRequired()])
	start_time = TimeField('Start Time: ', validators=[DataRequired()])
	end_time = TimeField('End Time: ', validators=[DataRequired()])
	location = StringField('Location: ', validators=[DataRequired()])
	picture = FileField("Choose Cover Picture...", validators=[DataRequired(), validate_file_ext])
	files = SelectMultipleField("Select Documents...")
	submit = SubmitField("Submit")

	def __init__(self, *args, **kwargs):
		super(EventForm, self).__init__(*args, **kwargs)
		self.files.choices = [('', '')]

class EventEditForm(EventForm):
	picture = FileField("Choose Cover Picture...", validators=[validate_file_ext])
	submit = SubmitField("Submit")

class Event(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(), nullable=False)
	description = db.Column(db.String(), nullable=False)
	start_time = db.Column(db.Time(), nullable=False)
	end_time = db.Column(db.Time(), nullable=False)
	start_date = db.Column(db.Date(), nullable=False)
	end_date = db.Column(db.Date(), nullable=False)
	location = db.Column(db.String(), nullable=False)
	picture_type = db.Column(db.String(), nullable=False)
	documents = db.relationship('Document', backref='event', lazy='dynamic')
	
	def __init__(self, title, description, location, start_time, end_time, start_date, end_date, picture_type, documents):
		self.title = title
		self.description = description
		self.start_time = start_time
		self.end_time = end_time
		self.start_date = start_date
		self.end_date = end_date
		self.location = location
		self.picture_type = picture_type
		self.documents = documents

	@staticmethod
	def __dir__():
		return ['id', 'title', 'description', 'start_date', 'end_date', 'start_time', 'end_time', 'location', 'picture_type']

	@staticmethod
	def exists_id(id):
		return Event.query.filter_by(id=id).first()

	@staticmethod
	def getNewRoute():
		return url_for('event.event_new')

	def getEditRoute(self):
		return url_for('event.event_edit', event_id=self.id)
	
	def getDeleteRoute(self):
		return url_for('event.event_delete', event_id=self.id)

	def getPicture(self):
		return url_for('event.event_get_picture', event_id=self.id)
	
	def getDocuments(self):
		return url_for('event.event_get_documents', event_id=self.id)

blueprint = Blueprint('event', __name__, url_prefix='/event')

@blueprint.route('/new', methods=['GET', 'POST'])
@authentication.login_required(authentication.ADMIN)
def event_new():
	eventForm = EventForm()
	docs = document_models.getDocumentsByUserType(authentication.PUBLIC)
	choices = [(str(doc.id), doc.title) for doc in docs]
	eventForm.files.choices = choices
	if eventForm.validate_on_submit():
		title = eventForm.title.data
		description = eventForm.description.data
		start_date = eventForm.start_date.data
		end_date = eventForm.end_date.data
		start_time = eventForm.start_time.data
		end_time = eventForm.end_time.data
		location = eventForm.location.data
		pictureData = eventForm.picture.data
		picture_type = pictureData.filename[pictureData.filename.rfind('.') + 1:]
		
		list_of_docs = []
		for d in eventForm.files.data:
			for doc in docs:
				if int(d) == doc.id:
					list_of_docs.append(doc)

		newEvent = Event(title=title, description=description, location=location, start_time=start_time, end_time=end_time, start_date=start_date, end_date=end_date, picture_type=picture_type, documents=list_of_docs)
		db.session.add(newEvent)
		db.session.commit()
		uploadFile(pictureData, str(newEvent.id) + '.' + picture_type)

		flash('Event Created', 'success')
		return eventForm.redirect(url_for('admin.index'))

	return render_template('models/event-form.html', form=eventForm, type='new')

@blueprint.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@authentication.login_required(authentication.ADMIN)
def event_edit(event_id):
	editingEvent = Event.exists_id(event_id)
	if editingEvent == None:
		return redirect(url_for('admin.index'))
	
	eventForm = EventEditForm()
	docs = document_models.getDocumentsByUserType(authentication.PUBLIC)
	choices = [(str(doc.id), doc.title) for doc in docs]
	eventForm.files.choices = choices
	if eventForm.validate_on_submit():
		title = eventForm.title.data
		description = eventForm.description.data
		start_date = eventForm.start_date.data
		end_date = eventForm.end_date.data
		start_time = eventForm.start_time.data
		end_time = eventForm.end_time.data
		location = eventForm.location.data
		pictureData = eventForm.picture.data

		if pictureData:
			deleteFile(str(event_id) + '.' + editingEvent.picture_type)
			picture_type = pictureData.filename[pictureData.filename.rfind('.') + 1:]
			editingEvent.picture_type = picture_type
			uploadFile(pictureData, str(event_id) + '.' + picture_type)
			

		editingEvent.title = title
		editingEvent.description = description
		editingEvent.location = location
		editingEvent.start_date = start_date
		editingEvent.end_date = end_date
		editingEvent.start_time = start_time
		editingEvent.end_time = end_time

		list_of_docs = []
		for d in eventForm.files.data:
			for doc in docs:
				if int(d) == doc.id:
					list_of_docs.append(doc)

		editingEvent.documents = list_of_docs

		db.session.commit()
		flash('Event Edited', 'success')
		return redirect(url_for('admin.index'))

	eventDocsIds = [str(doc.id) for doc in editingEvent.documents.all()]
	eventForm.files.default = eventDocsIds
	eventForm.process()
	eventForm.title.data = editingEvent.title
	eventForm.description.data = editingEvent.description
	eventForm.start_date.data = editingEvent.start_date
	eventForm.end_date.data = editingEvent.end_date
	eventForm.start_time.data = editingEvent.start_time
	eventForm.end_time.data = editingEvent.end_time
	eventForm.location.data = editingEvent.location
	
	return render_template('/models/event-form.html', form=eventForm, type='edit')

@blueprint.route('/<int:event_id>/delete', methods=['POST'])
@authentication.login_required(authentication.ADMIN)
def event_delete(event_id):
	editingEvent = Event.exists_id(event_id)
	if editingEvent == None:
		return redirect(url_for('admin.index'))

	deleteFile(str(event_id) + '.' + editingEvent.picture_type)
	db.session.delete(editingEvent)
	db.session.commit()
	flash('Event Deleted', 'success')
	return redirect(utils.get_redirect_url() or url_for('admin.index'))

@blueprint.route('/<int:event_id>')
def event_get(event_id):
	currentEvent = Event.exists_id(event_id)
	if currentEvent == None:
		return redirect(url_for('main.events'))
	return render_template('main/event.html', data=currentEvent)

@blueprint.route('/getpicture/<int:event_id>')
def event_get_picture(event_id):
	from flask import current_app as app
	currentEvent = Event.exists_id(event_id)
	if currentEvent == None:
		abort(404)
	return send_from_directory(os.path.join(app.config['EVENT_PATH'], 'documents'), str(event_id) + '.' + currentEvent.picture_type)

@blueprint.route('/getdocuments/<int:event_id>')
def event_get_documents(event_id):
	from flask import current_app as app
	currentEvent = Event.exists_id(event_id)
	if currentEvent == None:
		abort(404)
	doc_ids = [(doc.id, doc) for doc in currentEvent.documents.all()]
	files = [os.path.join(app.config['DOCUMENT_PATH'], str(doc_id[0])) for doc_id in doc_ids]
	zipFile = BytesIO()
	with zipfile.ZipFile(zipFile, 'w') as zf:
		for i,fileName in enumerate(files):
			zf.write(fileName, doc_ids[i][1].title + '.' + doc_ids[i][1].file_type)
	zipFile.seek(0)
	return send_file(zipFile, attachment_filename=currentEvent.title + '.zip', as_attachment=True)

def uploadFile(fileData, id):
	from flask import current_app as app
	path = os.path.join(app.config['EVENT_PATH'], 'documents', str(id))
	fileData.save(path)

def deleteFile(id):
	from flask import current_app as app
	path = os.path.join(app.config['EVENT_PATH'], 'documents', str(id))
	try:
		os.remove(path)
	except:
		pass