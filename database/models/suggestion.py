from flask import (
	Blueprint, render_template, flash, redirect, url_for, request
)
from wtforms import (
	StringField, SubmitField, TextAreaField
)
from wtforms.validators import (
	DataRequired
)
import auth.auth as authentication
from database.sqldb import db as db
from flask_wtf import FlaskForm
from database.models.user import UserAction
import datetime

class SuggestionForm(FlaskForm):
	first_name 	= StringField("First Name: ")
	last_name 	= StringField("Last Name: ")
	title 		= StringField("Title: ", validators=[DataRequired()])
	description = TextAreaField("Suggestion: ", validators=[DataRequired()])
	submit 		= SubmitField("Submit")

class EditSuggestionForm(FlaskForm):
	first_name 	= StringField("First Name")
	last_name 	= StringField("Last Name")
	title 		= StringField("Title", validators=[DataRequired()])
	description = TextAreaField("Suggestion", validators=[DataRequired()])

class Suggestion(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	first_name 		= db.Column(db.String())
	last_name 		= db.Column(db.String())
	title 			= db.Column(db.String(), nullable=False)
	description 	= db.Column(db.String(), nullable=False)
	date 			= db.Column(db.Date(), nullable=False)

	hidden_fields 	= ['id', 'description']

	def __init__(self, title, description, first_name=None, last_name=None):
		self.first_name 	= first_name
		self.last_name 		= last_name
		self.title 			= title
		self.description	= description
		self.date 			= datetime.datetime.today()

	@staticmethod
	def __dir__():
		return ['id', 'first_name', 'last_name', 'title', 'description', 'date']

	@staticmethod
	def exists_id(id):
		return Suggestion.query.filter_by(id=id).first()

	@staticmethod
	def getAllRoute():
		return url_for('suggestion.suggestions_get')

	@staticmethod
	def getNewRoute():
		return url_for('suggestion.suggestion_new')
	
	def getEditRoute(self):
		return url_for('suggestion.suggestion_edit', suggestion_id=self.id)

	def getDeleteRoute(self):
		return url_for('suggestion.suggestion_delete', suggestion_id=self.id)

blueprint = Blueprint('suggestion', __name__, url_prefix='/suggestion')

@blueprint.route('new', methods=['GET', 'POST'])
def suggestion_new():
	suggestionForm = SuggestionForm()
	if request.method == 'POST':
		if suggestionForm.validate_on_submit():
			user 		= authentication.getCurrentUser()
			first_name 	= suggestionForm.first_name.data
			last_name 	= suggestionForm.last_name.data
			title 		= suggestionForm.title.data
			description = suggestionForm.description.data
			suggestion 	= Suggestion(first_name=first_name, last_name=last_name, title=title, description=description)

			if user != None:
				user.actions.append(UserAction(model_type=Suggestion.__name__, model_title=title, action='Created', when=datetime.datetime.now()))
			db.session.add(suggestion)
			db.session.commit()
			flash('Suggestion Submitted', 'success')

	return render_template('models/suggestion-form.html', form=suggestionForm, type='new')

@blueprint.route('<int:suggestion_id>/edit', methods=['GET', 'POST'])
@authentication.can_read(Suggestion.__name__)
def suggestion_edit(suggestion_id):
	editingSuggestion = Suggestion.exists_id(suggestion_id)
	if editingSuggestion == None:
		flash('Suggestion does not exist', 'danger')
		return redirect(Suggestion.getAllRoute())
	
	suggestionForm = EditSuggestionForm()
	if request.method == 'POST':
		if authentication.getCurrentUser().canWrite(Suggestion.__name__) and suggestionForm.validate_on_submit():
			user = authentication.getCurrentUser()

			editingSuggestion.first_name 	= suggestionForm.first_name.data
			editingSuggestion.last_name 	= suggestionForm.last_name.data
			editingSuggestion.title 		= suggestionForm.title.data
			editingSuggestion.description 	= suggestionForm.description.data

			user.actions.append(UserAction(model_type=Suggestion.__name__, model_title=editingSuggestion.title, action='Edited', when=datetime.datetime.now()))
			db.session.commit()
			flash('Suggestion Edited', 'success')
	
	suggestionForm.first_name.data 	= editingSuggestion.first_name
	suggestionForm.last_name.data 	= editingSuggestion.last_name
	suggestionForm.title.data 		= editingSuggestion.title
	suggestionForm.description.data = editingSuggestion.description

	return authentication.auth_render_template('admin/model.html', form=suggestionForm, type='edit', model=Suggestion, breadcrumbTitle=suggestionForm.title.data, data=editingSuggestion, uneditable_fields=[('Date', editingSuggestion.date)])

@blueprint.route('<int:suggestion_id>/delete', methods=['POST'])
@authentication.can_write(Suggestion.__name__)
def suggestion_delete(suggestion_id):
	editingSuggestion = Suggestion.exists_id(suggestion_id)
	if editingSuggestion == None:
		flash('Suggestion does not exist', 'danger')
	else:
		user = authentication.getCurrentUser()
		user.actions.append(UserAction(model_type=Suggestion.__name__, model_title=editingSuggestion.title, action='Deleted', when=datetime.datetime.now()))
		db.session.delete(editingSuggestion)
		db.session.commit()
		flash('Suggestion Deleted', 'success')

	return redirect(Suggestion.getAllRoute())

@blueprint.route('suggestions')
@authentication.can_read(Suggestion.__name__)
def suggestions_get():
	suggestions = Suggestion.query.all()
	return authentication.auth_render_template('admin/getAllBase.html', data=suggestions, model=Suggestion, hidden_fields=Suggestion.hidden_fields)