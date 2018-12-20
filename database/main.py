from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db

class Document(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(30), nullable=False)
	description = db.Column(db.String(200), nullable=False)
	file_location = db.Column(db.String(100), nullable=False)
	
	def __init__(self, title, description, file_location):
		self.title = title
		self.description = description
		self.file_location = file_location

	@staticmethod
	def exists_id(id):
		return Document.query.filter_by(id=id).first()

# class Event(db.Model):
# 	pass

class Member(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(30), nullable=False)
	last_name = db.Column(db.String(30), nullable=False)
	email = db.Column(db.String(30))

	def __init__(self, first_name, last_name, email=None):
		self.first_name = first_name
		self.last_name = last_name
		self.email = email

	@staticmethod
	def exists_id(id):
		return Member.query.filter_by(id=id).first()

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

	@staticmethod
	def exists_id(id):
		return Suggestion.query.filter_by(id=id).first()
