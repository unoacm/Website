from flask import (
	Blueprint, render_template, session, url_for, redirect
)
from database.sqldb import db as db
import database.models.document as document_models
import database.models.event as event_models
import auth.auth as authentication
import math, datetime

blueprint = Blueprint('main', __name__, url_prefix='/')

@blueprint.route('/')
def index():
	return render_template('main/index.html')

@blueprint.route('about')
def about():
	return render_template('main/about.html')

@blueprint.route('events')
def events():
	today = datetime.date.today()
	events = event_models.Event.query.filter(event_models.Event.end_date >= today).order_by(event_models.Event.end_date.desc()).all()
	return render_template('main/events.html', events=events, type='current')

@blueprint.route('events/past')
def events_past():
	today = datetime.date.today()
	events = event_models.Event.query.filter(event_models.Event.end_date < today).order_by(event_models.Event.end_date.desc()).all()
	return render_template('main/events.html', events=events, type='past')

@blueprint.route('documents')
def documents():
	return redirect(url_for('main.documents_page', page=1))

@blueprint.route('documents/<int:page>')
def documents_page(page):
	DOCUMENTS_PER_ROW = 3
	MAX_DOCUMENT_PER_PAGE  = 9
	if page <= 0:
		return redirect(url_for('main.documents_page', page=1))
	docs = document_models.getDocumentsByUserType(authentication.getCurrentUserType())
	
	if len(docs) == 0 and page != 1 or max(1, math.ceil(len(docs) / MAX_DOCUMENT_PER_PAGE)) < page:
		return redirect(url_for('main.documents_page', page=1))
	return render_template(
		'main/documents.html',
		docs=docs[((page - 1) * MAX_DOCUMENT_PER_PAGE):MAX_DOCUMENT_PER_PAGE * page],
		page=page,
		maxPages= max(math.ceil(len(docs)/MAX_DOCUMENT_PER_PAGE), 1),
		per_row=DOCUMENTS_PER_ROW,
		per_page=MAX_DOCUMENT_PER_PAGE
	)