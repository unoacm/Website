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
import database.models.event as event_models
import datetime, collections

class UserLoginForm(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Login")

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@authentication.login_required()
@blueprint.route('/')
def index():
	data = collections.OrderedDict()
	data["AUTHENICATION AND AUTHORIZATION"] = [["Users", user_models.User]]
	data["OTHER"] = [["Members", member_models.Member],
					 ["Suggestions", suggestion_models.Suggestion],
					 ["Documents", document_models.Document],
					 ["Events", event_models.Event]
					]
	
	user = authentication.getCurrentUser()
	weekAgo = datetime.datetime.now() - datetime.timedelta(days=7)
	recentActions = user.actions.filter(UserAction.when > weekAgo)
	return authentication.auth_render_template('admin/index.html', data=data, recentActions=recentActions)

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

@authentication.login_required()
@blueprint.route('/logout', methods=['GET'])
def logout():
	session.clear()
	return redirect(url_for('admin.login'))