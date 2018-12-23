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
import auth.auth as authentication

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

@blueprint.route('documents')
def documents():
	return render_template('main/documents.html')