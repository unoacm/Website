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
from utils.forms import RedirectForm
from database.sqldb import db as db
import database.sqldb as sqldb
import auth.auth as authentication
import database.models.user as user_models
import database.models.suggestion as suggestion_models
import database.models.member as member_models
import database.models.document as document_models
import utils.utils as utils

class AdminLoginForm(RedirectForm):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Login")

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@blueprint.route('/')
@authentication.login_required('admin')
def index():
	users = user_models.User.query.all()
	members = member_models.Member.query.all()
	suggestions = suggestion_models.Suggestion.query.all()
	documents = document_models.Document.query.all()
	data = [
		["Users", user_models.User, ['password'], users],
		["Members", member_models.Member, [], members],
		["Suggestions", suggestion_models.Suggestion, ['description'], suggestions],
		["Documents", document_models.Document, ['description'], documents]
	]
	return render_template('admin/index.html', data=data)

@blueprint.route('/members')
@authentication.login_required(authentication.ADMIN)
def members():
	members = member_models.Member.query.all()
	return render_template('admin/members.html', classType=member_models.Member, disabled_fields=[], data=members)

@blueprint.route('/suggestions')
@authentication.login_required(authentication.ADMIN)
def suggestions():
	suggestions = suggestion_models.Suggestion.query.all()
	return render_template('admin/suggestions.html', data=suggestions)

@blueprint.route('/suggestions/<int:suggestion_id>')
@authentication.login_required(authentication.ADMIN)
def suggestion(suggestion_id):
	currentSuggestion = suggestion_models.Suggestion.exists_id(suggestion_id)
	if currentSuggestion == None:
		return redirect(url_for('admin.suggestions'))
	
	return render_template('admin/suggestion.html', data=currentSuggestion)

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
	if authentication.isLoggedIn(authentication.ADMIN):
		return redirect(url_for('admin.index'))

	loginForm = AdminLoginForm()
	if loginForm.validate_on_submit():
		username = loginForm.username.data
		password = loginForm.password.data
		if authentication.login(username, password, authentication.ADMIN):
			return redirect(url_for('admin.index'))
		flash('Invalid Credentials', 'danger')
	
	return render_template('admin/login.html', form=loginForm)

@blueprint.route('/logout', methods=['GET'])
@authentication.login_required(authentication.ADMIN)
def logout():
	session[authentication.SESSION_USER] = (authentication.PUBLIC, None)
	return redirect(url_for('admin.login'))