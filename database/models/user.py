from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
import auth.auth as authentication
from utils.forms import RedirectForm
import utils.utils as utils
from werkzeug.security import (
	check_password_hash, generate_password_hash
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash
)
from wtforms import (
	StringField, SubmitField, PasswordField, SelectField
)
from wtforms.validators import (
	DataRequired
)

class UserCreateForm(RedirectForm):
	import auth.auth as authentication
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	user_type = SelectField(
		'User Type',
		choices = [(authentication.ADMIN, 'Admin')],
		validators=[DataRequired()])
	submit = SubmitField("Submit")

class UserEditForm(UserCreateForm):
	password = PasswordField("Password: ")
	submit = SubmitField("Submit")

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(64), nullable=False) # String 64 for SHA-256 hashing
	user_type = db.Column(db.String(30), nullable=False)

	def __init__(self, username, password, user_type):
		self.username = username
		self.password = generate_password_hash(password)
		self.user_type = user_type

	def check_password(self, password):
		return check_password_hash(self.password, password)

	@staticmethod
	def __dir__():
		return ['id', 'username', 'password', 'user_type']

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
	def getNewRoute():
		return url_for('user.user_new')
	
	def getEditRoute(self):
		return url_for('user.user_edit', user_id=self.id)
	
	def getDeleteRoute(self):
		return url_for('user.user_delete', user_id=self.id)

blueprint = Blueprint('user', __name__, url_prefix='/user')

@blueprint.route('/new', methods=['GET', 'POST'])
def user_new():
	if not authentication.isLoggedIn(authentication.ADMIN):
		return redirect(url_for('admin.login'))
	
	createForm = UserCreateForm()
	if createForm.validate_on_submit():
		username = createForm.username.data
		password = createForm.password.data
		user_type = createForm.user_type.data
		if User.exists(username, password) != None:
			flash('Admin user already exists', 'danger')
			return createForm.redirect(url_for('user.user_new'))

		newUser = User(username=username, password=password, user_type=user_type)
		db.session.add(newUser)
		db.session.commit()
		flash('User Created', 'success')
		return redirect(url_for('admin.index'))
	
	return render_template('models/user-form.html', form=createForm, type='new')

@blueprint.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def user_edit(user_id):
	if not authentication.isLoggedIn(authentication.ADMIN):
		return redirect(url_for('admin.login'))
	editingUser = User.exists_id(user_id)
	if editingUser == None:
		return redirect(url_for('admin.index'))

	createForm = UserEditForm()
	if createForm.validate_on_submit():
		username = createForm.username.data
		password = createForm.password.data
		findingUser = User.exists(username, password)
		if findingUser != None and findingUser.id != user_id:
			flash('User already exists', 'danger')
			return redirect(url_for('user.user_edit', user_id=user_id))
		editingUser.username = username
		if password != "":
			editingUser.password = generate_password_hash(password)
		db.session.commit()
		flash('User Edited', 'success')
		return createForm.redirect(url_for('admin.index'))

	createForm.username.data = editingUser.username
	return render_template('models/user-form.html', form=createForm, type='edit')

@blueprint.route('/<int:user_id>/delete', methods=['POST'])
def user_delete(user_id):
	if not authentication.isLoggedIn(authentication.ADMIN):
		return redirect(url_for('admin.login'))
	editingUser = User.exists_id(user_id)
	if editingUser == None:
		return redirect(url_for('admin.index'))
	User.query.filter_by(id=user_id).delete()
	db.session.commit()
	flash('User Deleted', 'success')
	return redirect(utils.get_redirect_url() or url_for('admin.index'))