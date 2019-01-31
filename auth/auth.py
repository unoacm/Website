from flask import (
	redirect, url_for, session, render_template, flash
)
from functools import wraps

SESSION_USER = 'user'

ADMIN = 'admin'
PUBLIC = 'public'

def can_read(model):
	def outer_decorator(f):
		@wraps(f)
		def decorator(*args, **kwargs):
			user = getCurrentUserType()
			if user == None or not user.canRead(model):
				flash('You do not have access', 'danger')
				return redirect(url_for('admin.login'))
			else:
				return f(*args, **kwargs)
		return decorator
	return outer_decorator

def can_write(model):
	def outer_decorator(f):
		@wraps(f)
		def decorator(*args, **kwargs):
			user = getCurrentUserType()
			if user == None or not user.canWrite(model):
				flash('You do not have access', 'danger')
				return redirect(url_for('admin.login'))
			else:
				return f(*args, **kwargs)
		return decorator
	return outer_decorator

from database.models.user import User

def getCurrentUser():
	s = session.get(SESSION_USER)
	if s == None or type(s) != int:
		return None
	return User.query.filter_by(id=s).first()

def isLoggedIn():
	return getCurrentUser() != None

def getCurrentUserType():
	return ADMIN if isLoggedIn() else PUBLIC

def auth_render_template(*args, **kwargs):
	user = getCurrentUser()
	return render_template(*args, **kwargs, user=user, isLoggedIn=isLoggedIn)

def login_required():
	def outer_decorator(f):
		@wraps(f)
		def decorator(*args, **kwargs):
			if isLoggedIn() == None:
				flash('Access Denied', 'danger')
				return redirect(url_for('admin.login'))
			else:
				return f(*args, **kwargs)
		return decorator
	return outer_decorator

import database.models.user as user_models

def login(username, password):
	users = user_models.User.query.filter_by(username=username).all()
	user = None
	for u in users:
		if u.check_password(password):
			user = u
			break
	if user is None:
		return False
	session[SESSION_USER] = user.id
	return True