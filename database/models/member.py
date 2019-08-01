from flask_sqlalchemy import SQLAlchemy
from database.sqldb import db as db
from flask_wtf import FlaskForm
import auth.auth as authentication
from database.models.user import UserAction
import datetime
import csv
import io
from wtforms import (
	StringField, SubmitField, PasswordField
)
from wtforms.validators import (
	DataRequired
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash, request, Response
)

class MemberCreateForm(FlaskForm):
	first_name 	= StringField("First Name", validators=[DataRequired()])
	last_name 	= StringField("Last Name", validators=[DataRequired()])
	email 		= StringField("Email")

class Member(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	first_name 		= db.Column(db.String(), nullable=False)
	last_name 		= db.Column(db.String(), nullable=False)
	email 			= db.Column(db.String())

	hidden_fields 	= ['id']

	def __init__(self, first_name, last_name, email=None):
		self.first_name = first_name
		self.last_name 	= last_name
		self.email 		= email

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

actions = ['Export to CSV']

@blueprint.route('/new', methods=['GET', 'POST'])
@authentication.can_write(Member.__name__)
def member_new():
	memberForm = MemberCreateForm()
	if request.method == 'POST':
		if memberForm.validate_on_submit():
			user 		= authentication.getCurrentUser()
			first_name 	= memberForm.first_name.data
			last_name 	= memberForm.last_name.data
			email 		= memberForm.email.data

			newMember = Member(first_name=first_name, last_name=last_name, email=email)
			db.session.add(newMember)
			user.actions.append(UserAction(model_type=Member.__name__, model_title=first_name+' '+last_name, action='Created', when=datetime.datetime.now()))
			db.session.commit()
			flash('Member Created', 'success')
			return redirect(newMember.getEditRoute())
	
	return authentication.auth_render_template('admin/model.html', form=memberForm, type='new', model=Member, breadcrumbTitle='New Member')

@blueprint.route('<int:member_id>/edit', methods=['GET', 'POST'])
@authentication.can_read(Member.__name__)
def member_edit(member_id):
	editingMember = Member.exists_id(member_id)
	if editingMember == None:
		flash('Member does not exist', 'danger')
		return redirect(Member.getAllRoute())

	memberForm = MemberCreateForm()
	if request.method == 'POST':
		if authentication.getCurrentUser().canWrite(Member.__name__) and memberForm.validate_on_submit():
			user 		= authentication.getCurrentUser()
			first_name 	= memberForm.first_name.data
			last_name 	= memberForm.last_name.data
			email 		= memberForm.email.data

			editingMember.first_name	= first_name
			editingMember.last_name 	= last_name
			editingMember.email 		= email
			user.actions.append(UserAction(model_type=Member.__name__, model_title=first_name+' '+last_name, action='Edited', when=datetime.datetime.now()))
			db.session.commit()
			flash('Member edited', 'success')

	memberForm.first_name.data 	= editingMember.first_name
	memberForm.last_name.data 	= editingMember.last_name
	memberForm.email.data 		= editingMember.email
	
	return authentication.auth_render_template('admin/model.html', form=memberForm, type='edit', model=Member, breadcrumbTitle=memberForm.first_name.data, data=editingMember)

@blueprint.route('<int:member_id>/delete', methods=['POST'])
@authentication.can_write(Member.__name__)
def member_delete(member_id):
	editingMember = Member.exists_id(member_id)
	if editingMember == None:
		flash('Member does not exist', 'danger')
	else:
		user = authentication.getCurrentUser()
		user.actions.append(UserAction(model_type=Member.__name__, model_title=editingMember.first_name+' '+editingMember.last_name, action='Deleted', when=datetime.datetime.now()))
		db.session.delete(editingMember)
		db.session.commit()
		flash('Member Deleted', 'success')

	return redirect(Member.getAllRoute())

@blueprint.route('members', methods=['GET', 'POST'])
@authentication.can_read(Member.__name__)
def members_get():
	if request.method == 'POST':
		data = request.get_json()
		if data != None:
			members = [Member.exists_id(id) for id in data['ids']]
			if all((member != None for member in members)):
				if data['action'] == 'Export to CSV':
					with io.StringIO() as csvfile:
						csvwriter = csv.writer(csvfile, delimiter=",", quotechar="'")
						csvwriter.writerow(['First Name', 'Last Name', 'Email'])
						for member in members:
							csvwriter.writerow([member.first_name, member.last_name, member.email])
						return Response(csvfile.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=members.csv", "Download": "yes"})
			else:
				flash('Not all members that were selected exist anymore', 'warning')


	members = Member.query.all()
	return authentication.auth_render_template('admin/getAllBase.html', data=members, model=Member, hidden_fields=Member.hidden_fields, actions=actions)