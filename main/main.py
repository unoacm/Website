from flask import (
	Blueprint, render_template, session, url_for, redirect
)
from database.sqldb import db as db
import database.models.document as document_models
import auth.auth as authentication
import math, datetime

blueprint = Blueprint('main', __name__, url_prefix='/')

DOCUMENTS_PER_ROW		= 3
MAX_DOCUMENT_PER_PAGE 	= 9

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
	return redirect(url_for('main.documents_page', page=1))

@blueprint.route('documents/<int:page>')
def documents_page(page):
	if page <= 0:
		page = 1
	docs = document_models.getDocumentsByUserType(authentication.getCurrentUserType())
	
	if len(docs) == 0 and page != 1 or max(1, math.ceil(len(docs) / MAX_DOCUMENT_PER_PAGE)) < page:
		page = 1
		
	return authentication.auth_render_template(
		'main/documents.html',
		docs=docs[(page - 1) * MAX_DOCUMENT_PER_PAGE:MAX_DOCUMENT_PER_PAGE * page],
		page=page,
		maxPages=max(math.ceil(len(docs)/MAX_DOCUMENT_PER_PAGE), 1),
		per_row=DOCUMENTS_PER_ROW,
		per_page=MAX_DOCUMENT_PER_PAGE,
	)