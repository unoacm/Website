from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
import auth.auth as authentication
from flask_wtf import FlaskForm
from werkzeug.security import (
	check_password_hash, generate_password_hash
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash
)
from wtforms import (
	StringField, SubmitField, PasswordField
)
from wtforms.validators import (
	DataRequired
)

class AdminCreateForm(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Create")

class AdminEditForm(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ")
	submit = SubmitField("Create")

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(64), nullable=False) # String 64 for SHA-256 hashing

	def __init__(self, username, password):
		self.username = username
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	@staticmethod
	def __dir__():
		return ['id', 'username', 'password']

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
		return url_for('user.admin_new')
	
	def getEditRoute(self):
		return url_for('user.admin_edit', user_id=self.id)
	
	def getDeleteRoute(self):
		return url_for('user.admin_delete', user_id=self.id)

blueprint = Blueprint('user', __name__, url_prefix='/user')

@blueprint.route('/new', methods=['GET', 'POST'])
def admin_new():
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	
	createForm = AdminCreateForm()
	if createForm.validate_on_submit():
		username = createForm.username.data
		password = createForm.password.data
		if User.exists(username, password) != None:
			flash('Admin user already exists', 'danger')
			return redirect(url_for('admin.admin_new'))

		newAdmin = User(username=username, password=password)
		db.session.add(newAdmin)
		db.session.commit()
		return redirect(url_for('admin.index'))
	
	return render_template('models/admin-form.html', form=createForm, type='new')

@blueprint.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def admin_edit(user_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingUser = User.exists_id(user_id)
	if editingUser == None:
		return redirect(url_for('admin.index'))

	createForm = AdminEditForm()
	if createForm.validate_on_submit():
		username = createForm.username.data
		password = createForm.password.data
		findingUser = User.exists(username, password)
		if findingUser != None and findingUser.id != user_id:
			flash('Admin user already exists', 'danger')
			return redirect(url_for('admin.admin_edit', user_id=user_id))
		editingUser.username = username
		if password != "":
			editingUser.password = generate_password_hash(password)
		db.session.commit()
		return redirect(url_for('admin.index'))

	createForm.username.data = editingUser.username
	return render_template('models/admin-form.html', form=createForm, type='edit')

@blueprint.route('/<int:user_id>/delete', methods=['POST'])
def admin_delete(user_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingUser = User.exists_id(user_id)
	if editingUser == None:
		return redirect(url_for('admin.index'))
	User.query.filter_by(id=user_id).delete()
	db.session.commit()
	return redirect(url_for('admin.index'))