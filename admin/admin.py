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
import database.sqldb as sqldb
import auth.auth as authentication
import database.models.admin as admin_models
import database.models.suggestion as suggestion_models
import database.models.member as member_models

class AdminLoginForm(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Login")

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@blueprint.route('/')
def index():
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	admins = admin_models.User.query.all()
	members = member_models.Member.query.all()
	suggestions = suggestion_models.Suggestion.query.all()
	data = [
		["Admins", admin_models.User, ['password'], admins],
		["Members", member_models.Member, [], members],
		["Suggestions", suggestion_models.Suggestion, ['description'], suggestions]
	]
	return render_template('admin/index.html', data=data)

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