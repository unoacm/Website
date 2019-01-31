from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DATABASE_MODELS = [
	'Suggestion',
	'User',
	'UserAction',
	'Member',
	'Event',
	'Document'
	]

EDITABLE_DATABASE_MODELS = [
	'User',
	'Document',
	'Event',
	'Member',
	'Suggestion'
	]

def getTitleNames(model):
	return [attr.replace('_', ' ').strip().title() for attr in model.__dir__()]

def getAttributeNames(model):
	return [attr for attr in model.__dir__()]

def getTitlesWithAttributes(model):
	return [(attr.replace('_', ' ').strip().title(), attr) for attr in model.__dir__()]