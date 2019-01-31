from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
import auth.auth as authentication
import database.models.document as document_models
from flask_wtf import FlaskForm
import datetime, os, zipfile
from database.models.user import UserAction
import datetime
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


class EventForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	description = TextAreaField("Description", validators=[DataRequired()])
	start_date = DateField('Start Date', validators=[DataRequired()])
	end_date = DateField('End Date', validators=[DataRequired()])
	start_time = TimeField('Start Time', validators=[DataRequired()])
	end_time = TimeField('End Time', validators=[DataRequired()])
	location = StringField('Location', validators=[DataRequired()])
	picture = FileField("Cover Picture", validators=[DataRequired(), validate_file_ext])
	files = SelectMultipleField("Select Documents")

	def __init__(self, *args, **kwargs):
		super(EventForm, self).__init__(*args, **kwargs)
		self.files.choices = [('', '')]

class EventEditForm(EventForm):
	picture = FileField("Cover Picture", validators=[validate_file_ext], description='If you leave this field blank, it will use the previously saved picture.')

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
		return ['id', 'title', 'description', 'start_date', 'end_date', 'start_time', 'end_time', 'location', 'picture_type', 'documents']

	@staticmethod
	def exists_id(id):
		return Event.query.filter_by(id=id).first()

	@staticmethod
	def getAllRoute():
		return url_for('event.events_get')

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
@authentication.can_write(Event.__name__)
def event_new():
	eventForm = EventForm()
	docs = document_models.getDocumentsByUserType(authentication.PUBLIC)
	choices = [(str(doc.id), doc.title) for doc in docs]
	eventForm.files.choices = choices
	if eventForm.validate_on_submit():
		user = authentication.getCurrentUser()
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
		user.actions.append(UserAction(model_type=Event.__name__, model_title=title, action='Created', when=datetime.datetime.now()))
		db.session.commit()
		uploadFile(pictureData, str(newEvent.id) + '.' + picture_type)

		flash('Event Created', 'success')
		return eventForm.redirect(url_for('event.event_edit', event_id=newEvent.id))

	return authentication.auth_render_template('admin/model.html', form=eventForm, type='new', model=Event, breadcrumbTitle='New Event')

@blueprint.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@authentication.can_read(Event.__name__)
def event_edit(event_id):
	editingEvent = Event.exists_id(event_id)
	if editingEvent == None:
		flash('Event does not exist', 'danger')
		return redirect(url_for('event.events_get'))
	
	eventForm = EventEditForm()
	docs = document_models.getDocumentsByUserType(authentication.PUBLIC)
	choices = [(str(doc.id), doc.title) for doc in docs]
	eventForm.files.choices = choices
	if authentication.getCurrentUser().canWrite(Event.__name__) and eventForm.validate_on_submit():
		user = authentication.getCurrentUser()
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
		user.actions.append(UserAction(model_type=Event.__name__, model_title=title, action='Edited', when=datetime.datetime.now()))
		db.session.commit()
		flash('Event Edited', 'success')
		return redirect(url_for('event.event_edit', event_id=editingEvent.id))

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
	
	return authentication.auth_render_template('admin/model.html', form=eventForm, type='edit', model=Event, breadcrumbTitle=eventForm.title.data, data=editingEvent)

@blueprint.route('/<int:event_id>/delete', methods=['POST'])
@authentication.can_write(Event.__name__)
def event_delete(event_id):
	editingEvent = Event.exists_id(event_id)
	if editingEvent == None:
		flash('Event does not exist', 'danger')
		return redirect(url_for('event.events_get'))
	
	user = authentication.getCurrentUser()
	deleteFile(str(event_id) + '.' + editingEvent.picture_type)
	user.actions.append(UserAction(model_type=Event.__name__, model_title=editingEvent.title, action='Deleted', when=datetime.datetime.now()))
	db.session.delete(editingEvent)
	db.session.commit()
	flash('Event Deleted', 'success')
	return redirect(url_for('event.events_get'))

@blueprint.route('/<int:event_id>')
def event_get(event_id):
	currentEvent = Event.exists_id(event_id)
	if currentEvent == None:
		return redirect(url_for('main.events'))
	return render_template('main/event.html', data=currentEvent)

@blueprint.route('events')
@authentication.can_read(Event.__name__)
def events_get():
	events = Event.query.all()
	hidden_fields = ['id', 'description', 'picture_type', 'documents']
	return authentication.auth_render_template('admin/getAllBase.html', data=events, model=Event, hidden_fields=hidden_fields)

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