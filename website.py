from flask import (
	Flask, render_template, session
)
from flask_sqlalchemy import SQLAlchemy

from database.sqldb import db as db
import os, sys
import main.main as main
import blog.blog as blog
import admin.admin as admin
import database.models.user as user_models
import database.models.member as member_models
import database.models.suggestion as suggestion_models
import database.models.document as document_models
import auth.auth as authentication

app = Flask(__name__)
app.app_context().push()
app.instance_path = app.root_path

DEFAULT_SECRET_KEY			= 'Gotta make sure this key is super dang long, yeehaw!'
ACM_FLASK_ADMIN_USERNAME	= os.environ['ACM_FLASK_ADMIN_USERNAME']
ACM_FLASK_ADMIN_PASSWORD	= os.environ['ACM_FLASK_ADMIN_PASSWORD']
ACM_FLASK_SECRET_KEY		= os.environ.get('ACM_FLASK_SECRET_KEY', DEFAULT_SECRET_KEY)

if app.env == 'development':
	databaseURL = 'sqlite:///database/test.db'
elif app.env == 'production':
	if ACM_FLASK_SECRET_KEY == DEFAULT_SECRET_KEY:
		raise ValueError('ACM_FLASK_SECRET_KEY cannot be the default in production')
		
	databaseURL = 'sqlite:///database/production.db'
else:
	raise ValueError(f'Invalid environment: {app.env}. Must be either "development" or "production".')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']	= False
app.config['SQLALCHEMY_DATABASE_URI'] 			= databaseURL
app.config['SECRET_KEY'] 						= ACM_FLASK_SECRET_KEY
app.config['DOCUMENT_PATH'] 					= os.path.join(app.instance_path, 'documents')
app.config['EVENT_PATH'] 						= os.path.join(app.instance_path, 'events')

db.init_app(app)
db.create_all()

app.register_blueprint(main.blueprint)
app.register_blueprint(blog.blueprint)
app.register_blueprint(admin.blueprint)

app.register_blueprint(user_models.blueprint)
app.register_blueprint(member_models.blueprint)
app.register_blueprint(suggestion_models.blueprint)
app.register_blueprint(document_models.blueprint)

default_admin = user_models.User.query.filter_by(username=ACM_FLASK_ADMIN_USERNAME).first()

if not default_admin:
	admin = user_models.User(username=ACM_FLASK_ADMIN_USERNAME, password=ACM_FLASK_ADMIN_PASSWORD, write_access='all')
	db.session.add(admin)
	db.session.commit()

if __name__ == "__main__":
	if app.env == 'development':
		app.run()
	elif app.env == 'production':
		print('Please use gunicorn and a wsgi file to run production')
		sys.exit(1)
	else:
		print(f'Invalid FLASK_ENV: {app.env}')
		sys.exit(1)