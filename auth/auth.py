from flask import (
	render_template, redirect, url_for, session
)

def login(username, password, model, userType):
	users = model.query.filter_by(username=username).all()
	user = None
	for u in users:
		if u.check_password(password):
			user = u
			break
	if user is None:
		return False
	session[userType] = user.id
	return True

def isLoggedIn(userType):
	return session.get(userType) != None