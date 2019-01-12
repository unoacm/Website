from flask import (
	Flask, render_template, session
)
from flask_sqlalchemy import SQLAlchemy

from database.sqldb import db as db
import os
import main.main as main
import blog.blog as blog
import admin.admin as admin
import database.models.user as user_models
import database.models.member as member_models
import database.models.suggestion as suggestion_models
import database.models.document as document_models
import database.models.event as event_models
import auth.auth as authentication

app = Flask(__name__)
app.app_context().push()
app.instance_path = app.root_path

databaseURL = ''
if app.env == 'development':
	databaseURL = 'sqlite:///database/test.db'
elif app.env == 'production':
	databaseURL = os.environ['DATABASE_URL']
else:
	raise ValueError(f'Invalid environment: {app.env}')

app.config['SQLALCHEMY_DATABASE_URI'] = databaseURL
app.config['SECRET_KEY'] = "Gotta make sure this key is super dang long, yeehaw!"
app.config['DOCUMENT_PATH'] = os.path.join(app.instance_path, 'documents')
app.config['EVENT_PATH'] = os.path.join(app.instance_path, 'events')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db.create_all()

app.register_blueprint(main.blueprint)
app.register_blueprint(blog.blueprint)
app.register_blueprint(admin.blueprint)

app.register_blueprint(user_models.blueprint)
app.register_blueprint(member_models.blueprint)
app.register_blueprint(suggestion_models.blueprint)
app.register_blueprint(document_models.blueprint)
app.register_blueprint(event_models.blueprint)

if __name__ == "__main__":
	if not os.environ.get('FLASK_ADMIN_USERNAME'):
		raise ValueError('FLASK_ADMIN_USERNAME not set')
	if not os.environ.get('FLASK_ADMIN_PASSWORD'):
		raise ValueError('FLASK_ADMIN_PASSWORD not set')
	default_admin = user_models.User.query.filter_by(user_type=authentication.ADMIN, username=os.environ['FLASK_ADMIN_USERNAME']).first()
	if not default_admin:
		admin = user_models.User(username=os.environ['FLASK_ADMIN_USERNAME'], password=os.environ['FLASK_ADMIN_PASSWORD'], user_type=authentication.ADMIN)
		db.session.add(admin)
		db.session.commit()
	app.run()