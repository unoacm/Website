from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def getTitleNames(model):
	return [attr.replace('_', ' ').strip().title() for attr in model.__dir__()]

def getAttributeNames(model):
	return [attr for attr in model.__dir__()]

def getTitlesWithAttributes(model):
	return [(attr.replace('_', ' ').strip().title(), attr) for attr in model.__dir__()]

