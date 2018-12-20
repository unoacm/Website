from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db

class Document(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(30), nullable=False)
	description = db.Column(db.String(200), nullable=False)
	file_location = db.Column(db.String(100), nullable=False)

# class Event(db.Model):
# 	pass

class Member(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(30), nullable=False)
	last_name = db.Column(db.String(30), nullable=False)
	email = db.Column(db.String(30))

class Suggestion(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(30))
	last_name = db.Column(db.String(30))
	title = db.Column(db.String(30), nullable=False)
	description = db.Column(db.String(500), nullable=False)

	def __init__(self, title, description, first_name=None, last_name=None):
		self.first_name = first_name
		self.last_name = last_name
		self.title = title
		self.description = description

