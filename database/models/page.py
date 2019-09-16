from flask_wtf import FlaskForm
from wtforms.validators import (
	DataRequired
)
from wtforms import (
	HiddenField, StringField, SelectField
)
from flask import (
	Blueprint, render_template, redirect, url_for, session, flash, send_from_directory, request
)
from database.sqldb import db as db
import auth.auth as authentication
import datetime
from database.models.user import UserAction

class PageForm(FlaskForm):
	title	= StringField("Title", validators=[DataRequired()])
	access	= SelectField(
		'User Access',
		choices		= [(authentication.PUBLIC, 'Public'), (authentication.ADMIN, 'Private')],
		validators	= [DataRequired()]
	)
	delta	= HiddenField('delta', validators=[DataRequired()])

class PageEditForm(FlaskForm):
	delta = HiddenField('delta')

class CalendarForm(FlaskForm):
	html = StringField("HTML")

class Page(db.Model):
	id				= db.Column(db.Integer, primary_key=True)
	title			= db.Column(db.String(), nullable=False)
	access			= db.Column(db.String(), nullable=False)
	content			= db.Column(db.String(), nullable=False)
	hidden_fields 	= ['id', 'content']

	def __init__(self, title, access, content):
		self.access 	= access
		self.content	= content
		self.title		= title

	@staticmethod
	def __dir__():
		return ['id', 'title', 'access', 'content']

	@staticmethod
	def exists_id(id):
		return Page.query.filter_by(id=id).first()
	
	@staticmethod
	def getAllRoute():
		return url_for('page.pages_get')

	@staticmethod
	def getNewRoute():
		return url_for('page.page_new')

	def getEditRoute(self):
		return url_for('page.page_edit', page_id=self.id)

	def getDeleteRoute(self):
		return url_for('page.page_delete', page_id=self.id)

	def getGetRoute(self):
		return url_for('page.page_get', page_id=self.id)

blueprint = Blueprint('page', __name__, url_prefix='/page')

@blueprint.route('/new', methods=['GET', 'POST'])
@authentication.can_write(Page.__name__)
def page_new():
	pageForm = PageForm()
	if request.method == 'POST':
		if pageForm.validate_on_submit():
			user		= authentication.getCurrentUser()
			title		= pageForm.title.data
			contents	= pageForm.delta.data
			access		= pageForm.access.data
			
			newPage = Page(title=title, access=access, content=contents)
			db.session.add(newPage)
			user.actions.append(UserAction(model_type=Page.__name__, model_title=title, action='Created', when=datetime.datetime.now()))
			db.session.commit()
			flash('Page Created', 'success')
			return redirect(newPage.getEditRoute())
	
	return authentication.auth_render_template('admin/model.html', form=pageForm, type='new', model=Page, breadcrumbTitle='New Page')

@blueprint.route('/<int:page_id>/edit', methods=['GET', 'POST'])
@authentication.can_read(Page.__name__)
def page_edit(page_id):
	editingPage = Page.exists_id(page_id)
	if editingPage == None:
		flash('Page does not exist', 'danger')
		return redirect(Page.getAllRoute())
	
	pageForm = PageForm()
	if request.method == 'POST':
		if pageForm.validate_on_submit():
			user		= authentication.getCurrentUser()
			title		= pageForm.title.data
			contents	= pageForm.delta.data
			access		= pageForm.access.data

			editingPage.title	= title
			editingPage.content	= contents
			editingPage.access	= access

			user.actions.append(UserAction(model_type=Page.__name__, model_title=title, action='Edited', when=datetime.datetime.now()))
			db.session.commit()
			flash('Page Edited', 'success')

	pageForm.title.data		= editingPage.title
	pageForm.delta.data		= editingPage.content
	pageForm.access.data	= editingPage.access
	return authentication.auth_render_template('admin/model.html', form=pageForm, type='edit', model=Page, breadcrumbTitle=editingPage.title, data=editingPage)

@blueprint.route('/<int:page_id>/delete', methods=['POST'])
@authentication.can_write(Page.__name__)
def page_delete(page_id):
	editingPage = Page.exists_id(page_id)
	if editingPage == None:
		flash('Page does not exist', 'danger')
	else:
		user = authentication.getCurrentUser()
		user.actions.append(UserAction(model_type=Page.__name__, model_title=editingPage.title, action='Deleted', when=datetime.datetime.now()))
		db.session.delete(editingPage)
		db.session.commit()
		flash('Page Deleted', 'success')

	return redirect(Page.getAllRoute())

@blueprint.route('pages')
@authentication.can_read(Page.__name__)
def pages_get():
	pages = Page.query.all()
	return authentication.auth_render_template('admin/getAllBase.html', data=pages, model=Page, hidden_fields=Page.hidden_fields)

@blueprint.route('/<int:page_id>/', methods=['GET', 'POST'])
def page_get(page_id):
	user = authentication.getCurrentUser()
	getting_page = Page.exists_id(page_id)
	if getting_page == None:
		flash('Page does not exist', 'warning')
		return redirect(url_for('main.events'))

	form = PageEditForm()

	if request.method == 'POST' and user != None and user.canWrite(Page.__name__) and form.validate_on_submit():
		getting_page.content = form.delta.data
		user.actions.append(UserAction(model_type=Page.__name__, model_title=getting_page.title, action='Edited', when=datetime.datetime.now()))
		db.session.commit()
		flash('Page Edited', 'success')
	elif getting_page.access == authentication.ADMIN:
		if user == None or not user.canRead(Page.__name__):
			flash('You do not have permission', 'danger')
			return redirect(url_for('main.events'))

	form.delta.data = getting_page.content

	return authentication.auth_render_template('main/page.html', page=getting_page, form=form)

def getPagesByUserType(type):
	if type == authentication.ADMIN and authentication.getCurrentUser().canRead(Page.__name__):
		return Page.query.all()
	return Page.query.filter_by(access=authentication.PUBLIC).all()