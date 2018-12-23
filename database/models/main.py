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
	def __dir__():
		return ['id', 'title', 'description', 'file_location']

	@staticmethod
	def exists_id(id):
		return Document.query.filter_by(id=id).first()

# class Event(db.Model):
# 	pass
