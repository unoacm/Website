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
from database.models.user import UserAction
import database.sqldb as sqldb
import auth.auth as authentication
import database.models.user as user_models
import database.models.suggestion as suggestion_models
import database.models.member as member_models
import database.models.document as document_models
import database.models.blog as blog_models
import database.models.page as page_models
import database.models.home_object as home_object_models
import datetime, collections

class UserLoginForm(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Login")

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

model_data = collections.OrderedDict()

model_data["AUTHENTICATION AND AUTHORIZATION"] = \
[
	["Users", user_models.User]
]

model_data["INTERAL"] = \
[
	["Members", member_models.Member]
]

model_data["EXTERNAL"] = \
[
	["Suggestions", suggestion_models.Suggestion],
	["Documents", document_models.Document],
	["Blog Posts", blog_models.Blog_Post],
	["Pages", page_models.Page],
	['Home Objects', home_object_models.Home_Object]
]

@blueprint.route('/')
@authentication.login_required()
def index():
	user = authentication.getCurrentUser()
	if user == None:
		flash('Access Denied', 'danger')
		return redirect(url_for('admin.login'))
		
	weekAgo = datetime.datetime.now() - datetime.timedelta(days=7)
	recentActions = user.actions.filter(UserAction.when > weekAgo)
	return authentication.auth_render_template('admin/index.html', data=model_data, recentActions=recentActions)

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
	if authentication.isLoggedIn():
		return redirect(url_for('admin.index'))

	loginForm = UserLoginForm()
	if loginForm.validate_on_submit():
		username = loginForm.username.data
		password = loginForm.password.data
		if authentication.login(username, password):
			return redirect(url_for('admin.index'))
		flash('Invalid Credentials', 'danger')
	
	return render_template('admin/login.html', form=loginForm)

@blueprint.route('/logout', methods=['GET'])
@authentication.login_required()
def logout():
	session.clear()
	return redirect(url_for('admin.login'))