from flask import (
	redirect, url_for, session
)
from functools import wraps

ADMIN = 'admin'
PUBLIC = 'public'
SESSION_USER = 'user'

import database.models.user as user_models

def login(username, password, userType):
	users = user_models.User.query.filter_by(username=username).all()
	user = None
	for u in users:
		if u.check_password(password):
			user = u
			break
	if user is None:
		return False
	session[SESSION_USER] = (userType, user.id)
	return True

def isLoggedIn(userType):
	return getCurrentUserType() == userType

def getCurrentUserType():
	s = session.get(SESSION_USER)
	return PUBLIC if s is None else s[0]

def power(userType):
	p = 0
	if userType == ADMIN:
		p = 1
	return p

def login_required(type):
	def outer_decorator(f):
		@wraps(f)
		def decorator(*args, **kwargs):
			if type == ADMIN:
				if not isLoggedIn(ADMIN):
					return redirect(url_for('admin.login'))
				else:
					return f(*args, **kwargs)
			else:
				return redirect(url_for('/'))
		return decorator
	return outer_decorator