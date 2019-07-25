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

class BlogPostForm(FlaskForm):
	title	= StringField("Title", validators=[DataRequired()])
	access	= SelectField(
		'User Access',
		choices		= [(authentication.PUBLIC, 'Public'), (authentication.ADMIN, 'Private')],
		validators	= [DataRequired()]
	)
	delta 	= HiddenField('delta', validators=[DataRequired()])

class Blog_Post(db.Model):
	id				= db.Column(db.Integer, primary_key=True)
	title			= db.Column(db.String(), nullable=False)
	content			= db.Column(db.String(), nullable=False)
	author			= db.Column(db.String(), nullable=False)
	access			= db.Column(db.String(), nullable=False)
	created			= db.Column(db.DateTime(), nullable=False)
	hidden_fields	= ['id', 'content']

	def __init__(self, title, author, access, content, created):
		self.title 		= title
		self.author		= author
		self.access		= access
		self.content	= content
		self.created	= created

	@staticmethod
	def __dir__():
		return ['id', 'title', 'content', 'author', 'access', 'created']
	
	@staticmethod
	def exists_id(id):
		return Blog_Post.query.filter_by(id=id).first()
	
	@staticmethod
	def getAllRoute():
		return url_for('blog_post.blog_posts_get')

	@staticmethod
	def getNewRoute():
		return url_for('blog_post.blog_post_new')
	
	def getEditRoute(self):
		return url_for('blog_post.blog_post_edit', blog_post_id=self.id)

	def getDeleteRoute(self):
		return url_for('blog_post.blog_post_delete', blog_post_id=self.id)

	def getGetRoute(self):
		return url_for('blog_post.blog_post_get', blog_post_id=self.id)

blueprint = Blueprint('blog_post', __name__, url_prefix='/blog')

@blueprint.route('/new', methods=['GET', 'POST'])
@authentication.can_write(Blog_Post.__name__)
def blog_post_new():
	blogForm = BlogPostForm()
	if request.method == 'POST':
		if blogForm.validate_on_submit():
			user		= authentication.getCurrentUser()
			title		= blogForm.title.data
			contents	= blogForm.delta.data
			access		= blogForm.access.data
			created	= datetime.datetime.now()

			newBlogPost	= Blog_Post(title=title, content=contents, author=user.username, access=access, created=created)
			db.session.add(newBlogPost)
			user.actions.append(UserAction(model_type=Blog_Post.__name__, model_title=title, action='Created', when=created))
			db.session.commit()
			flash('Blog Post Created', 'success')
			return redirect(newBlogPost.getEditRoute())

	return authentication.auth_render_template('admin/model.html', form=blogForm, type='new', model=Blog_Post, breadcrumbTitle='New Blog Post')

@blueprint.route('/<int:blog_post_id>/edit', methods=['GET', 'POST'])
@authentication.can_read(Blog_Post.__name__)
def blog_post_edit(blog_post_id):
	editingBlogPost = Blog_Post.exists_id(blog_post_id)
	if editingBlogPost == None:
		flash('Blog Post does not exist', 'danger')
		return redirect(Blog_Post.getAllRoute())
	
	blogForm = BlogPostForm()
	if request.method == 'POST':
		if blogForm.validate_on_submit():
			user		= authentication.getCurrentUser()
			title		= blogForm.title.data
			contents	= blogForm.delta.data
			access		= blogForm.access.data

			editingBlogPost.title	= title
			editingBlogPost.content	= contents
			editingBlogPost.access	= access

			user.actions.append(UserAction(model_type=Blog_Post.__name__, model_title=title, action='Edited', when=datetime.datetime.now()))
			db.session.commit()
			flash('Blog Post Edited', 'success')

	blogForm.title.data		= editingBlogPost.title
	blogForm.delta.data		= editingBlogPost.content
	blogForm.access.data	= editingBlogPost.access
	return authentication.auth_render_template('admin/model.html', form=blogForm, type='edit', model=Blog_Post, breadcrumbTitle=editingBlogPost.title, data=editingBlogPost)

@blueprint.route('/<int:blog_post_id>/delete', methods=['POST'])
@authentication.can_write(Blog_Post.__name__)
def blog_post_delete(blog_post_id):
	editingBlogPost = Blog_Post.exists_id(blog_post_id)
	if editingBlogPost == None:
		flash('Blog Post does not exist', 'danger')
	else:
		user = authentication.getCurrentUser()
		user.actions.append(UserAction(model_type=Blog_Post.__name__, model_title=editingBlogPost.title, action='Deleted', when=datetime.datetime.now()))
		db.session.delete(editingBlogPost)
		db.session.commit()
		flash('Blog Post Deleted', 'success')

	return redirect(Blog_Post.getAllRoute())

@blueprint.route('/<int:blog_post_id>/')
def blog_post_get(blog_post_id):
	pass

@blueprint.route('blog_posts')
@authentication.can_read(Blog_Post.__name__)
def blog_posts_get():
	posts = Blog_Post.query.all()
	return authentication.auth_render_template('admin/getAllBase.html', data=posts, model=Blog_Post, hidden_fields=Blog_Post.hidden_fields)

