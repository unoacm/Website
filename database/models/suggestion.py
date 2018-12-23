from flask import (
	Blueprint, render_template, flash, redirect, url_for
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

class SuggestionForm(FlaskForm):
	first_name = StringField("First Name: ")
	last_name = StringField("Last Name: ")
	title = StringField("Title: ", validators=[DataRequired()])
	description = TextAreaField("Suggestion: ", validators=[DataRequired()])
	submit = SubmitField("Submit")

class Suggestion(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(30))
	last_name = db.Column(db.String(30))
	title = db.Column(db.String(30), nullable=False)
	description = db.Column(db.String(500), nullable=False)

	def __init__(self, title, description, first_name=None, last_name=None):
		self.first_name = first_name
		self.last_name = last_name
		self.title = title
		self.description = description

	@staticmethod
	def __dir__():
		return ['id', 'first_name', 'last_name', 'title', 'description']

	@staticmethod
	def exists_id(id):
		return Suggestion.query.filter_by(id=id).first()

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
	if suggestionForm.validate_on_submit():
		first_name = suggestionForm.first_name.data
		if first_name == '':
			first_name = None
		last_name = suggestionForm.last_name.data
		if last_name == '':
			last_name = None
		title = suggestionForm.title.data
		description = suggestionForm.description.data
		suggestion = Suggestion(first_name=first_name, last_name=last_name, title=title, description=description)
		db.session.add(suggestion)
		db.session.commit()
		flash('Successfully submitted', 'success')
		return redirect(url_for('suggestion.suggestion_new'))
	return render_template('models/suggestion-form.html', form=suggestionForm, type='new')

@blueprint.route('<int:suggestion_id>/edit', methods=['GET', 'POST'])
def suggestion_edit(suggestion_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingSuggestion = Suggestion.exists_id(suggestion_id)
	if editingSuggestion == None:
		return redirect(url_for('admin.index'))
	
	suggestionForm = SuggestionForm()
	if suggestionForm.validate_on_submit():
		editingSuggestion.first_name = None if suggestionForm.first_name.data == '' else suggestionForm.first_name.data
		editingSuggestion.last_name = None if suggestionForm.last_name.data == '' else suggestionForm.last_name.data
		editingSuggestion.title = suggestionForm.title.data
		editingSuggestion.description = suggestionForm.description.data
		db.session.commit()
		return redirect(url_for('admin.index'))
	
	suggestionForm.first_name.data = editingSuggestion.first_name
	suggestionForm.last_name.data = editingSuggestion.last_name
	suggestionForm.title.data = editingSuggestion.title
	suggestionForm.description.data = editingSuggestion.description
	return render_template('models/suggestion-form.html', form=suggestionForm)

@blueprint.route('<int:suggestion_id>/delete', methods=['POST'])
def suggestion_delete(suggestion_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingSuggestion = Suggestion.exists_id(suggestion_id)
	if editingSuggestion == None:
		return redirect(url_for('admin.index'))
	Suggestion.query.filter_by(id=suggestion_id).delete()
	db.session.commit()
	return redirect(url_for('admin.index'))