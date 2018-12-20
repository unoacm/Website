from flask import (
	Blueprint, render_template, redirect, url_for, session, flash
)
from wtforms import (
	StringField, SubmitField, PasswordField
)
from wtforms.validators import (
	DataRequired
)
from werkzeug.security import (
	generate_password_hash
)
from flask_wtf import FlaskForm
from database.sqldb import db as db
import auth.auth as authentication
import database.admin as admin_models
import database.main as main_models

class AdminLoginForm(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Login")

class AdminCreateForm(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Create")

class AdminEditForm(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ")
	submit = SubmitField("Create")

class MemberCreateForm(FlaskForm):
	first_name = StringField("First Name: ", validators=[DataRequired()])
	last_name = StringField("Last Name: ", validators=[DataRequired()])
	email = StringField("Email: ")
	submit = SubmitField("Create")

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@blueprint.route('/')
def index():
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	admins = admin_models.User.query.all()
	members = main_models.Member.query.all()
	suggestions = main_models.Suggestion.query.all()
	return render_template('admin/index.html', admins=admins, members=members, suggestions=suggestions)

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
	if authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.index'))

	loginForm = AdminLoginForm()
	if loginForm.validate_on_submit():
		username = loginForm.username.data
		password = loginForm.password.data
		if authentication.login(username, password, admin_models.User, 'admin'):
			return redirect(url_for('admin.index'))
		flash('Invalid Credentials', 'danger')
	
	return render_template('admin/login.html', form=loginForm)

@blueprint.route('/logout', methods=['GET'])
def logout():
	session.clear()
	return redirect(url_for('admin.login'))

@blueprint.route('/new', methods=['GET', 'POST'])
def admin_new():
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	
	createForm = AdminCreateForm()
	if createForm.validate_on_submit():
		username = createForm.username.data
		password = createForm.password.data
		if admin_models.User.exists(username, password) != None:
			flash('Admin user already exists', 'danger')
			return redirect(url_for('admin.admin_new'))

		newAdmin = admin_models.User(username=username, password=password)
		db.session.add(newAdmin)
		db.session.commit()
		return redirect(url_for('admin.index'))
	
	return render_template('admin/admin-form.html', form=createForm, type='new')

@blueprint.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def admin_edit(user_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingUser = admin_models.User.exists_id(user_id)
	if editingUser == None:
		return redirect(url_for('admin.index'))

	createForm = AdminEditForm()
	if createForm.validate_on_submit():
		username = createForm.username.data
		password = createForm.password.data
		findingUser = admin_models.User.exists(username, password)
		if findingUser != None and findingUser.id != user_id:
			flash('Admin user already exists', 'danger')
			return redirect(url_for('admin.admin_edit', user_id=user_id))
		editingUser.username = username
		if password != "":
			editingUser.password = generate_password_hash(password)
		db.session.commit()
		return redirect(url_for('admin.index'))

	createForm.username.data = editingUser.username
	return render_template('admin/admin-form.html', form=createForm, type='edit')

@blueprint.route('/<int:user_id>/delete', methods=['POST'])
def admin_delete(user_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingUser = admin_models.User.exists_id(user_id)
	if editingUser == None:
		return redirect(url_for('admin.index'))
	admin_models.User.query.filter_by(id=user_id).delete()
	db.session.commit()
	return redirect(url_for('admin.index'))

@blueprint.route('/member/new', methods=['GET', 'POST'])
def member_new():
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	
	memberForm = MemberCreateForm()
	if memberForm.validate_on_submit():
		first_name = memberForm.first_name.data
		last_name = memberForm.last_name.data
		if memberForm.email.data == "":
			email = None
		else:
			email = memberForm.email.data

		newMember = main_models.Member(first_name=first_name, last_name=last_name, email=email)
		db.session.add(newMember)
		db.session.commit()
		return redirect(url_for('admin.index'))
	
	return render_template('admin/member-form.html', form=memberForm, type='new')

@blueprint.route('/member/<int:member_id>/edit', methods=['GET', 'POST'])
def member_edit(member_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingMember = main_models.Member.exists_id(member_id)
	if editingMember == None:
		return redirect(url_for('admin.index'))

	memberForm = MemberCreateForm()
	if memberForm.validate_on_submit():
		first_name = memberForm.first_name.data
		last_name = memberForm.last_name.data
		if memberForm.email.data == "":
			email = None
		else:
			email = memberForm.email.data
		editingMember.first_name = first_name
		editingMember.last_name = last_name
		editingMember.email = email
		db.session.commit()
		return redirect(url_for('admin.index'))

	memberForm.first_name.data = editingMember.first_name
	memberForm.last_name.data = editingMember.last_name
	memberForm.email.data = editingMember.email
	return render_template('admin/member-form.html', form=memberForm, type='edit')

@blueprint.route('/member/<int:member_id>/delete', methods=['POST'])
def member_delete(member_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingMember = main_models.Member.exists_id(member_id)
	if editingMember == None:
		return redirect(url_for('admin.index'))
	main_models.Member.query.filter_by(id=member_id).delete()
	db.session.commit()
	return redirect(url_for('admin.index'))