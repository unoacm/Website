from flask import (
	Flask, render_template
)
from werkzeug.security import (
	check_password_hash, generate_password_hash
)
from flask_sqlalchemy import SQLAlchemy

from database.sqldb import db as db
import main.main as main
import blog.blog as blog
import admin.admin as admin

app = Flask(__name__)
app.app_context().push()
app.config['SQLACHEMY_DATABASE_URI'] = 'sqlite:////database/test.db'
app.config['SECRET_KEY'] = "Gotta make sure this key is super dang long, yeehaw!"

db.init_app(app)
db.create_all()

app.register_blueprint(main.blueprint)
app.register_blueprint(blog.blueprint)
app.register_blueprint(admin.blueprint)

if __name__ == "__main__":
	app.run()