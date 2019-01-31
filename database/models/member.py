from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
from flask_wtf import FlaskForm
import auth.auth as authentication
from database.models.user import UserAction
import datetime
from wtforms import (
	StringField, SubmitField, PasswordField
)
from wtforms.validators import (
	DataRequired
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash, 
)

class MemberCreateForm(FlaskForm):
	first_name = StringField("First Name", validators=[DataRequired()])
	last_name = StringField("Last Name", validators=[DataRequired()])
	email = StringField("Email")

class Member(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(), nullable=False)
	last_name = db.Column(db.String(), nullable=False)
	email = db.Column(db.String())

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
	
	@staticmethod
	def getAllRoute():
		return url_for('member.members_get')
	
	def getEditRoute(self):
		return url_for('member.member_edit', member_id=self.id)

	def getDeleteRoute(self):
		return url_for('member.member_delete', member_id=self.id)

blueprint = Blueprint('member', __name__, url_prefix='/member')

@authentication.can_write(Member.__name__)
@blueprint.route('/new', methods=['GET', 'POST'])
def member_new():
	memberForm = MemberCreateForm()
	if memberForm.validate_on_submit():
		user = authentication.getCurrentUser()
		first_name = memberForm.first_name.data
		last_name = memberForm.last_name.data
		if memberForm.email.data == "":
			email = None
		else:
			email = memberForm.email.data

		newMember = Member(first_name=first_name, last_name=last_name, email=email)
		db.session.add(newMember)
		user.actions.append(UserAction(model_type=Member.__name__, model_title=first_name+' '+last_name, action='Created', when=datetime.datetime.now()))
		db.session.commit()
		flash('Member Created', 'success')
		return redirect(url_for('member.member_edit', member_id=newMember.id))
	
	return authentication.auth_render_template('admin/model.html', form=memberForm, type='new', model=Member, breadcrumbTitle='New Member')

@authentication.can_read(Member.__name__)
@blueprint.route('<int:member_id>/edit', methods=['GET', 'POST'])
def member_edit(member_id):
	editingMember = Member.exists_id(member_id)
	if editingMember == None:
		flash('Member does not exist', 'danger')
		return redirect(url_for('member.members_get'))

	memberForm = MemberCreateForm()
	if authentication.getCurrentUser().canWrite(Member.__name__) and memberForm.validate_on_submit():
		user = authentication.getCurrentUser()
		first_name = memberForm.first_name.data
		last_name = memberForm.last_name.data
		if memberForm.email.data == "":
			email = None
		else:
			email = memberForm.email.data
		editingMember.first_name = first_name
		editingMember.last_name = last_name
		editingMember.email = email
		user.actions.append(UserAction(model_type=Member.__name__, model_title=first_name+' '+last_name, action='Edited', when=datetime.datetime.now()))
		db.session.commit()
		flash('Member edited', 'success')
		return redirect(url_for('member.member_edit', member_id=editingMember.id))

	memberForm.first_name.data = editingMember.first_name
	memberForm.last_name.data = editingMember.last_name
	memberForm.email.data = editingMember.email
	return authentication.auth_render_template('admin/model.html', form=memberForm, type='edit', model=Member, breadcrumbTitle=memberForm.first_name.data, data=editingMember)

@authentication.can_write(Member.__name__)
@blueprint.route('<int:member_id>/delete', methods=['POST'])
def member_delete(member_id):
	editingMember = Member.exists_id(member_id)
	if editingMember == None:
		flash('Member does not exist', 'danger')
		return redirect(url_for('member.members_get'))
	user = authentication.getCurrentUser()
	user.actions.append(UserAction(model_type=Member.__name__, model_title=editingMember.first_name+' '+editingMember.last_name, action='Deleted', when=datetime.datetime.now()))
	Member.query.filter_by(id=member_id).delete()
	db.session.commit()
	flash('Member Deleted', 'success')
	return redirect(url_for('member.members_get'))

@authentication.can_read(Member.__name__)
@blueprint.route('members')
def members_get():
	members = Member.query.all()
	hidden_fields = ['id']
	return authentication.auth_render_template('admin/getAllBase.html', data=members, model=Member, hidden_fields=hidden_fields)