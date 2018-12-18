from flask_sqlalchemy import SQLAlchemy
from sqldb import db as db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password = db.Column(db.String(64), unique=True, nullable=False) # String 64 for SHA-256 hashing