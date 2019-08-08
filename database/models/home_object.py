from flask_wtf import FlaskForm
from wtforms.validators import (
	DataRequired
)
from wtforms import (
	HiddenField, StringField, SelectField
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash, send_from_directory, request
)
from database.sqldb import db as db
import auth.auth as authentication
import datetime
from database.models.user import UserAction

class HomeObjectForm(FlaskForm):
	category	= StringField("Category", validators=[DataRequired()])
	title		= StringField("Title", validators=[DataRequired()])
	delta		= HiddenField('delta', validators=[DataRequired()])

class Home_Object(db.Model):
	id				= db.Column(db.Integer, primary_key=True)
	category		= db.Column(db.String(), nullable=False)
	title			= db.Column(db.String(), nullable=False)
	content			= db.Column(db.String(), nullable=False)
	hidden_fields	= ['id', 'content']

	def __init__(self, category, title, content):
		self.category	= category
		self.title		= title
		self.content	= content

	@staticmethod
	def __dir__():
		return ['id', 'category', 'title', 'content']

	@staticmethod
	def exists_id(id):
		return Home_Object.query.filter_by(id=id).first()

	@staticmethod
	def getAllRoute():
		return url_for('Home Object.home_objects_get')

	@staticmethod
	def getNewRoute():
		return url_for("Home Object.home_object_new")

	def getEditRoute(self):
		return url_for("Home Object.home_object_edit", home_object_id=self.id)

	def getDeleteRoute(self):
		return url_for("Home Object.home_object_delete", home_object_id=self.id)

blueprint = Blueprint('Home Object', __name__, url_prefix='/home_object')

@blueprint.route('/new', methods=['GET', 'POST'])
@authentication.can_write(Home_Object.__name__)
def home_object_new():
	homeObjectForm = HomeObjectForm()
	if request.method == 'POST':
		if homeObjectForm.validate_on_submit():
			user		= authentication.getCurrentUser()
			category	= homeObjectForm.category.data
			title		= homeObjectForm.title.data
			contents	= homeObjectForm.delta.data

			newHomeObject = Home_Object(category=category, title=title, content=contents)
			db.session.add(newHomeObject)
			user.actions.append(UserAction(model_type=Home_Object.__name__, model_title=title, action='Created', when=datetime.datetime.now()))
			db.session.commit()
			flash('Home Object Created', 'success')
			return redirect(newHomeObject.getEditRoute())

	return authentication.auth_render_template('admin/model.html', form=homeObjectForm, type='new', model=Home_Object, breadcrumbTitle='New Home Object')

@blueprint.route('/<int:home_object_id>/edit', methods=['GET', 'POST'])
@authentication.can_read(Home_Object.__name__)
def home_object_edit(home_object_id):
	editingHomeObject = Home_Object.exists_id(home_object_id)
	if editingHomeObject == None:
		flash('Home Object does not exist', 'danger')
		return redirect(Home_Object.getAllRoute())

	homeObjectForm = HomeObjectForm()
	if request.method == 'POST':
		if homeObjectForm.validate_on_submit():
			user		= authentication.getCurrentUser()
			category	= homeObjectForm.category.data
			title		= homeObjectForm.title.data
			contents	= homeObjectForm.delta.data

			editingHomeObject.category	= category
			editingHomeObject.title		= title
			editingHomeObject.content	= contents

			user.actions.append(UserAction(model_type=Home_Object.__name__, model_title=title, action='Edited', when=datetime.datetime.now()))
			db.session.commit()
			flash('Home Object Edited', 'success')

	homeObjectForm.category.data	= editingHomeObject.category
	homeObjectForm.title.data		= editingHomeObject.title
	homeObjectForm.delta.data		= editingHomeObject.content
	return authentication.auth_render_template('admin/model.html', form=homeObjectForm, type='edit', model=Home_Object, breadcrumbTitle=editingHomeObject.title, data=editingHomeObject)

@blueprint.route('/<int:home_object_id>/delete', methods=['POST'])
@authentication.can_write(Home_Object.__name__)
def home_object_delete(home_object_id):
	editingHomeObject = Home_Object.exists_id(home_object_id)
	if editingHomeObject == None:
		flash('Home Ojbect does not exist', 'danger')
	else:
		user = authentication.getCurrentUser()
		user.actions.append(UserAction(model_type=Home_Object.__name__, model_title=editingHomeObject.title, action='Deleted', when=datetime.datetime.now()))
		db.session.delete(editingHomeObject)
		db.session.commit()
		flash('Page Deleted', 'success')

	return redirect(Home_Object.getAllRoute())

@blueprint.route('home_objects')
@authentication.can_read(Home_Object.__name__)
def home_objects_get():
	home_objects = Home_Object.query.all()
	return authentication.auth_render_template('admin/getAllBase.html', data=home_objects, model=Home_Object, hidden_fields=Home_Object.hidden_fields)