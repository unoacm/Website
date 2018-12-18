from flask import (
	Blueprint, render_template, redirect, url_for
)
from flask_wtf import FlaskForm
from wtforms import (
	StringField, SubmitField, PasswordField
)
from wtforms.validators import (
	DataRequired
)
from database.sqldb import db as db

class AdminLoginForm(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Login")

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@blueprint.route('/')
def index():
	return render_template('admin/index.html')

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
	loginForm = AdminLoginForm()
	if loginForm.validate_on_submit():
		if loginForm.username.data == 'admin' and loginForm.password.data == 'pass':
			return redirect(url_for('admin.index'))
	
	return render_template('admin/login.html', form=loginForm)