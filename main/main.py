from flask import (
	Blueprint, render_template, flash, redirect, url_for
)
from wtforms import (
	StringField, SubmitField, TextAreaField
)
from wtforms.validators import (
	DataRequired
)

from database.sqldb import db as db
from flask_wtf import FlaskForm
import database.main as main_models
import database.admin as admin_models
import auth.auth as authentication

class SuggestionForm(FlaskForm):
	first_name = StringField("First Name: ")
	last_name = StringField("Last Name: ")
	title = StringField("Title: ", validators=[DataRequired()])
	description = TextAreaField("Suggestion: ", validators=[DataRequired()])
	submit = SubmitField("Submit")

blueprint = Blueprint('main', __name__, url_prefix='/')

@blueprint.route('/')
def index():
	return render_template('main/index.html')

@blueprint.route('about')
def about():
	return render_template('main/about.html')

@blueprint.route('events')
def events():
	return render_template('main/events.html')

@blueprint.route('suggestions/new', methods=['GET', 'POST'])
def suggestions():
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
		suggestion = main_models.Suggestion(first_name=first_name, last_name=last_name, title=title, description=description)
		db.session.add(suggestion)
		db.session.commit()
		flash('Successfully submitted', 'success')
		return redirect(url_for('main.suggestions'))
	return render_template('main/suggestion-form.html', form=suggestionForm, type='new')

@blueprint.route('suggestions/<int:suggestion_id>/edit', methods=['GET', 'POST'])
def suggestions_edit(suggestion_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingSuggestion = main_models.Suggestion.exists_id(suggestion_id)
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
	return render_template('main/suggestion-form.html', form=suggestionForm)

@blueprint.route('suggestions/<int:suggestion_id>/delete', methods=['POST'])
def suggestions_delete(suggestion_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingSuggestion = main_models.Suggestion.exists_id(suggestion_id)
	if editingSuggestion == None:
		return redirect(url_for('admin.index'))
	main_models.Suggestion.query.filter_by(id=suggestion_id).delete()
	db.session.commit()
	return redirect(url_for('admin.index'))

@blueprint.route('documents')
def documents():
	return render_template('main/documents.html')