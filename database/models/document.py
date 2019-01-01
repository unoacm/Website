from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
from utils.forms import RedirectForm
import auth.auth as authentication
import utils.utils as utils
from wtforms import (
	StringField, SubmitField, PasswordField
)
from wtforms.validators import (
	DataRequired
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash, 
)

class DocumentForm(RedirectForm):
	title = StringField("Title: ", validators=[DataRequired()])
	description = StringField("Description: ", validators=[DataRequired()])
	

class Document(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(30), nullable=False)
	description = db.Column(db.String(200), nullable=False)
	file_location = db.Column(db.String(100), nullable=False)
	document_access = db.Column(db.String(20), nullable=False)
	
	def __init__(self, title, description, file_location, document_access='public'):
		self.title = title
		self.description = description
		self.file_location = file_location
		self.document_access = document_access

	@staticmethod
	def __dir__():
		return ['id', 'title', 'description', 'file_location', 'document_access']

	@staticmethod
	def exists_id(id):
		return Document.query.filter_by(id=id).first()

	@staticmethod
	def getNewRoute():
		return url_for('document.document_new')

blueprint = Blueprint('document', __name__, url_prefix='/document')

@blueprint.route('/new', methods=['GET', 'POST'])
def document_new():
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))

	documentForm = DocumentForm()
	if documentForm.validate_on_submit():
		title = documentForm.title.data
		description = documentForm.description.data

