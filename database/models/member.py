from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
from utils.forms import RedirectForm
import auth.auth as authentication
import utils.utils as utils
from wtforms import (
	StringField, SubmitField, PasswordField
)
from wtforms.validators import (
	DataRequired
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash, 
)

class MemberCreateForm(RedirectForm):
	first_name = StringField("First Name: ", validators=[DataRequired()])
	last_name = StringField("Last Name: ", validators=[DataRequired()])
	email = StringField("Email: ")
	submit = SubmitField("Create")

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
	def __dir__():
		return ['id', 'first_name', 'last_name', 'email']

	@staticmethod
	def exists_id(id):
		return Member.query.filter_by(id=id).first()

	@staticmethod
	def getNewRoute():
		return url_for('member.member_new')
	
	def getEditRoute(self):
		return url_for('member.member_edit', member_id=self.id)

	def getDeleteRoute(self):
		return url_for('member.member_delete', member_id=self.id)

blueprint = Blueprint('member', __name__, url_prefix='/member')

@blueprint.route('/new', methods=['GET', 'POST'])
def member_new():
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	
	memberForm = MemberCreateForm()
	if memberForm.validate_on_submit():
		first_name = memberForm.first_name.data
		last_name = memberForm.last_name.data
		if memberForm.email.data == "":
			email = None
		else:
			email = memberForm.email.data

		newMember = Member(first_name=first_name, last_name=last_name, email=email)
		db.session.add(newMember)
		db.session.commit()
		return memberForm.redirect(url_for('admin.index'))
	
	return render_template('models/member-form.html', form=memberForm, type='new')

@blueprint.route('<int:member_id>/edit', methods=['GET', 'POST'])
def member_edit(member_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingMember = Member.exists_id(member_id)
	if editingMember == None:
		return redirect(url_for('admin.index'))

	memberForm = MemberCreateForm()
	if memberForm.validate_on_submit():
		first_name = memberForm.first_name.data
		last_name = memberForm.last_name.data
		if memberForm.email.data == "":
			email = None
		else:
			email = memberForm.email.data
		editingMember.first_name = first_name
		editingMember.last_name = last_name
		editingMember.email = email
		db.session.commit()
		return memberForm.redirect('admin.index')

	memberForm.first_name.data = editingMember.first_name
	memberForm.last_name.data = editingMember.last_name
	memberForm.email.data = editingMember.email
	return render_template('models/member-form.html', form=memberForm, type='edit')

@blueprint.route('<int:member_id>/delete', methods=['POST'])
def member_delete(member_id):
	if not authentication.isLoggedIn('admin'):
		return redirect(url_for('admin.login'))
	editingMember = Member.exists_id(member_id)
	if editingMember == None:
		return redirect(url_for('admin.index'))
	Member.query.filter_by(id=member_id).delete()
	db.session.commit()
	return redirect(url_for('admin.index'))