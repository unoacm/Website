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
		last_name = suggestionForm.last_name.data
		title = suggestionForm.title.data
		description = suggestionForm.description.data
		suggestion = main_models.Suggestion(first_name=first_name, last_name=last_name, title=title, description=description)
		db.session.add(suggestion)
		db.session.commit()
		flash('Successfully submitted', 'success')
		return redirect(url_for('main.suggestions'))
	return render_template('main/suggestion-new.html', form=suggestionForm)

@blueprint.route('documents')
def documents():
	return render_template('main/documents.html')