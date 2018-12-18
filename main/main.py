from flask import (
	Blueprint, render_template
)

blueprint = Blueprint('main', __name__, url_prefix='/')

@blueprint.route('/')
def index():
	return render_template('main/index.html')

@blueprint.route('/about')
def about():
	return render_template('main/about.html')

@blueprint.route('events')
def events():
	return render_template('main/events.html')

@blueprint.route('suggestions')
def suggestions():
	return render_template('main/suggestions.html')

@blueprint.route('documents')
def documents():
	return render_template('main/documents.html')