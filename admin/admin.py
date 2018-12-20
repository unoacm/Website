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

class AdminLoginForm(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Login")

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@blueprint.route('/')
def index():
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	return render_template('admin/index.html')

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

@blueprint.route('/admin/logout', methods=['GET'])
def logout():
	session.clear()
	return redirect(url_for('admin.login'))