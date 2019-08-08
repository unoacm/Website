from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
from database.sqldb import EDITABLE_DATABASE_MODELS as EDITABLE_DATABASE_MODELS
import auth.auth as authentication
from flask_wtf import FlaskForm
import datetime
from database.sqldb import EDITABLE_DATABASE_MODELS
from werkzeug.security import (
	check_password_hash, generate_password_hash
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash, request
)
from wtforms import (
	StringField, SubmitField, PasswordField, RadioField
)
from wtforms.validators import (
	DataRequired, Required
)

class UserCreateForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])

class UserEditForm(UserCreateForm):
	password = PasswordField("Password", description='This value is hashed, so it is not visible. To keep the old password, leave this blank.')

for model in EDITABLE_DATABASE_MODELS: # Dynamically creating fields for each editable model in the database
	model_name = model.replace('_', ' ').title()
	field = RadioField(f'{model_name} Access', choices=[('read', 'Read'), ('write', 'Write'), ('none', 'None')], validators=[Required()], default='read')
	setattr(UserCreateForm, f'{model.lower()}Access', field)
	setattr(UserEditForm, f'{model.lower()}Access', field)

class User(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	username 		= db.Column(db.String(), nullable=False)
	password 		= db.Column(db.String(), nullable=False)
	actions 		= db.relationship('UserAction', backref='user', lazy='dynamic')
	write_access 	= db.Column(db.String(), nullable=False)
	read_access 	= db.Column(db.String(), nullable=False)

	hidden_fields 	= ['actions', 'write_access', 'read_access', 'password', 'id']

	def __init__(self, username, password, write_access=[], read_access=[]):
		self.username 		= username
		self.password 		= generate_password_hash(password)
		self.write_access 	= ''
		self.read_access 	= ''
		if type(write_access) == str and write_access.lower() == 'all':
			self.addWrite(EDITABLE_DATABASE_MODELS)
		else:
			self.addWrite(write_access)
		if type(read_access) == str and read_access.lower() == 'all':
			self.addRead(EDITABLE_DATABASE_MODELS)
		else:
			self.addRead(read_access)
		
	def check_password(self, password):
		return check_password_hash(self.password, password)

	@staticmethod
	def __dir__():
		return ['id', 'username', 'password', 'actions', 'write_access', 'read_access']

	@staticmethod
	def exists(username, password):
		allUsers = User.query.filter_by(username=username).all()
		for user in allUsers:
			if user.check_password(password):
				return user
		return None
	
	@staticmethod
	def exists_id(id):
		return User.query.filter_by(id=id).first()

	@staticmethod
	def getAllRoute():
		return url_for('user.users_get')
	
	@staticmethod
	def getNewRoute():
		return url_for('user.user_new')
	
	def getEditRoute(self):
		return url_for('user.user_edit', user_id=self.id)
	
	def getDeleteRoute(self):
		return url_for('user.user_delete', user_id=self.id)

	def canWrite(self, models):
		data = self.write_access.split('/')
		if type(models) != list:
			models = [models]
		for model in models:
			if not model in data:
				return False
		return True

	def canRead(self, models):
		data = self.read_access.split('/')
		if type(models) != list:
			models = [models]
		for model in models:
			if not model in data:
				return False
		return True

	def addWrite(self, models):
		if not self.canWrite(models):
			data = self.write_access.split('/')
			if type(models) != list:
				models = [models]
			data += models
			self.write_access = '/'.join(data)
			self.addRead(models)

	def addRead(self, models):
		if not self.canRead(models):
			data = self.read_access.split('/')
			if type(models) != list:
				models = [models]
			data += models
			self.read_access = '/'.join(data)

	def removeWrite(self, models):
		if self.canWrite(models):
			data = self.write_access.split('/')
			if type(models) != list:
				models = [models]
			for model in models:
				data.remove(model)
			self.write_access = '/'.join(data)

	def removeRead(self, models):
		if self.canRead(models):
			data = self.read_access.split('/')
			if type(models) != list:
				models = [models]
			for model in models:
				data.remove(model)
			self.read_access = '/'.join(data)
			self.removeWrite(models)

class UserAction(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	model_type 		= db.Column(db.String(), nullable=False)
	model_title 	= db.Column(db.String(), nullable=False)
	action 			= db.Column(db.String(), nullable=False)
	when 			= db.Column(db.DateTime(), nullable=False)
	user_id 		= db.Column(db.Integer, db.ForeignKey('user.id'))

	hidden_fields 	= ['id', 'user_id']

	@staticmethod
	def __dir__():
		return ['id', 'model_type', 'model_title', 'action', 'when', 'user_id']

blueprint = Blueprint('user', __name__, url_prefix='/user')

@blueprint.route('/new', methods=['GET', 'POST'])
@authentication.can_write(User.__name__)
def user_new():
	createForm = UserCreateForm()

	if request.method == 'POST':
		if createForm.validate_on_submit():
			user 		= authentication.getCurrentUser()
			username 	= createForm.username.data
			password 	= createForm.password.data
			if User.exists(username, password) == None:
				newUser = User(username=username, password=password)
				db.session.add(newUser)
				user.actions.append(UserAction(model_type=User.__name__, model_title=username, action='Created', when=datetime.datetime.now()))
				db.session.commit()
				flash('User Created', 'success')
				return redirect(newUser.getEditRoute())
			else:
				flash('User already exists', 'danger')
	
	return authentication.auth_render_template('admin/model.html', form=createForm, type='new', model=User, breadcrumbTitle='New User')

@blueprint.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@authentication.can_read(User.__name__)
def user_edit(user_id):
	editingUser = User.exists_id(user_id)
	if editingUser == None:
		flash('User does not exist', 'danger')
		return redirect(User.getAllRoute())

	editForm = UserEditForm()
	if request.method == 'POST':
		if authentication.getCurrentUser().canWrite(User.__name__) and editForm.validate_on_submit():
			user 	= authentication.getCurrentUser()
			reads 	= []
			writes 	= []

			for model in EDITABLE_DATABASE_MODELS:
				access = editForm.__getattribute__(f'{model.lower()}Access').data
				if access == 'read':
					reads.append(model)
				elif access == 'write':
					writes.append(model)

			username 	= editForm.username.data
			password 	= editForm.password.data
			findingUser = User.exists(username, password)

			if findingUser == None or findingUser.id == user_id:
				editingUser.username 		= username
				editingUser.read_access 	= ''
				editingUser.write_access	= ''
				editingUser.addRead(reads)
				editingUser.addWrite(writes)
				if password != "":
					editingUser.password = generate_password_hash(password)
				user.actions.append(UserAction(model_type=User.__name__, model_title=username, action='Edited', when=datetime.datetime.now()))
				db.session.commit()
				flash('User Edited', 'success')
			else:
				flash('User already exists', 'danger')

	for model in EDITABLE_DATABASE_MODELS:
		accessField 		= editForm.__getattribute__(f'{model.lower()}Access')
		accessField.default = 'write' if editingUser.canWrite(model) else 'read' if editingUser.canRead(model) else 'none'
	
	editForm.process()
	editForm.username.data = editingUser.username
	return authentication.auth_render_template('admin/model.html', form=editForm, type='edit', model=User, breadcrumbTitle=editForm.username.data, data=editingUser, uneditable_data=[('Actions', editingUser.actions, UserAction, UserAction.hidden_fields)])

@blueprint.route('/<int:user_id>/delete', methods=['POST'])
@authentication.can_write(User.__name__)
def user_delete(user_id):
	editingUser = User.exists_id(user_id)
	if editingUser != None:
		user = authentication.getCurrentUser()
		user.actions.append(UserAction(model_type=User.__name__, model_title=editingUser.username, action='Deleted', when=datetime.datetime.now()))
		db.session.delete(editingUser)
		db.session.commit()
		flash('User Deleted', 'success')
	else:
		flash('User does not exist', 'danger')

	return redirect(User.getAllRoute())

@blueprint.route('users')
@authentication.can_read(User.__name__)
def users_get():
	users = User.query.all()
	return authentication.auth_render_template('admin/getAllBase.html', data=users, model=User, hidden_fields=User.hidden_fields)