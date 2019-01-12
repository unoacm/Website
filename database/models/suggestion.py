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
from utils.forms import RedirectForm
import utils.utils as utils
import datetime

class SuggestionForm(RedirectForm):
	first_name = StringField("First Name: ")
	last_name = StringField("Last Name: ")
	title = StringField("Title: ", validators=[DataRequired()])
	description = TextAreaField("Suggestion: ", validators=[DataRequired()])
	submit = SubmitField("Submit")

class Suggestion(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String())
	last_name = db.Column(db.String())
	title = db.Column(db.String(), nullable=False)
	description = db.Column(db.String(), nullable=False)
	date = db.Column(db.Date(), nullable=False)

	def __init__(self, title, description, first_name=None, last_name=None):
		self.first_name = first_name
		self.last_name = last_name
		self.title = title
		self.description = description
		self.date = datetime.datetime.today()

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

	def getGetRoute(self):
		return url_for('suggestion.suggestion_get', suggestion_id=self.id)

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
		flash('Suggestion Submitted', 'success')
		if authentication.isLoggedIn('admin'):
			return suggestionForm.redirect(url_for('suggestion.suggestion_new'))
		return redirect(url_for("suggestion.suggestion_new"))
	return render_template('models/suggestion-form.html', form=suggestionForm, type='new')

@blueprint.route('<int:suggestion_id>/edit', methods=['GET', 'POST'])
@authentication.login_required(authentication.ADMIN)
def suggestion_edit(suggestion_id):
	editingSuggestion = Suggestion.exists_id(suggestion_id)
	if editingSuggestion == None:
		return utils.redirect('admin.index')
	
	suggestionForm = SuggestionForm()
	if suggestionForm.validate_on_submit():
		editingSuggestion.first_name = None if suggestionForm.first_name.data == '' else suggestionForm.first_name.data
		editingSuggestion.last_name = None if suggestionForm.last_name.data == '' else suggestionForm.last_name.data
		editingSuggestion.title = suggestionForm.title.data
		editingSuggestion.description = suggestionForm.description.data
		db.session.commit()
		flash('Suggestion Edited', 'success')
		return suggestionForm.redirect(url_for('admin.index'))
	
	suggestionForm.first_name.data = editingSuggestion.first_name
	suggestionForm.last_name.data = editingSuggestion.last_name
	suggestionForm.title.data = editingSuggestion.title
	suggestionForm.description.data = editingSuggestion.description
	return render_template('models/suggestion-form.html', form=suggestionForm)

@blueprint.route('<int:suggestion_id>/delete', methods=['POST'])
@authentication.login_required(authentication.ADMIN)
def suggestion_delete(suggestion_id):
	editingSuggestion = Suggestion.exists_id(suggestion_id)
	if editingSuggestion == None:
		return redirect(url_for('admin.index'))
	Suggestion.query.filter_by(id=suggestion_id).delete()
	db.session.commit()
	flash('Suggestion Deleted', 'success')
	return redirect(utils.get_redirect_url() or url_for('admin.index'))

@blueprint.route('/<int:suggestion_id>')
@authentication.login_required(authentication.ADMIN)
def suggestion_get(suggestion_id):
	currentSuggestion = Suggestion.exists_id(suggestion_id)
	if currentSuggestion == None:
		return redirect(url_for('admin.suggestions'))
	
	return render_template('admin/suggestion.html', data=currentSuggestion)