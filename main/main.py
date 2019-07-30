from flask import (
	Blueprint, render_template, session, url_for, redirect, request
)
from wtforms import (
	HiddenField
)
from flask_wtf import FlaskForm
from database.sqldb import db as db
import database.models.document as document_models
import database.models.blog as blog_models
import database.models.page as page_models
import auth.auth as authentication
import math, datetime, os
import json

blueprint = Blueprint('main', __name__, url_prefix='/')

DOCUMENTS_PER_ROW		= 3
MAX_DOCUMENT_PER_PAGE 	= 9

MAX_BLOGS_PER_PAGE		= 5
BLOG_SPRING_SEMESTER	= datetime.date(year=1901, month=5, day=20)
BLOG_SUMMER_SEMESTER	= datetime.date(year=1901, month=8, day=20)

@blueprint.route('/')
def index():
	return render_template('main/index.html')

@blueprint.route('about', methods=['GET', 'POST'])
def about():
	from flask import current_app as app
	about_page = os.path.join(app.config['ADMIN_GENERATED'], 'about')

	form = page_models.PageEditForm()
	user = authentication.getCurrentUser()

	contents = '[]'

	if request.method == 'POST' and user != None and user.canWrite(page_models.Page.__name__) and form.validate_on_submit():
		contents = form.delta.data
		with open(about_page, 'w') as f:
			f.write(contents)
	else:
		if os.path.exists(about_page):
			with open(about_page, 'r') as f:
				contents = f.read()
	
	
	form.delta.data = contents
	
	return authentication.auth_render_template('main/about.html', form=form)

@blueprint.route('events')
def events():
	pages = page_models.getPagesByUserType(authentication.getCurrentUserType())
	return render_template('main/events.html', pages=pages)

@blueprint.route('blog')
def blog():
	return blog_page(1)

@blueprint.route('blog/<int:page>')
def blog_page(page):
	if page <= 0:
		page = 1

	title_filter	= request.args.get('title', default=None, type=str)
	year_filter		= request.args.get('year', default=None, type=int)
	semester_filter	= request.args.get('semester', default=None, type=str)

	if title_filter == '':
		title_filter = None
	if year_filter == '':
		year_filter = None
	if semester_filter == '':
		semester_filter = None

	blog_posts = [post for post in blog_models.getBlogsByUserType(authentication.getCurrentUserType()) if filter_post(post, title_filter, year_filter, semester_filter)]
	blog_texts = [json.loads(x.content) for x in blog_posts]
	for i,text in enumerate(blog_texts):
		actual_text = ''
		for section in text['ops']:
			if type(section['insert']) == str:
				actual_text += section['insert']
		blog_texts[i] = actual_text

	if len(blog_posts) == 0 or max(1, math.ceil(len(blog_posts) / MAX_BLOGS_PER_PAGE)) < page:
		page = 1

	sections = []
	current_section = None
	for post in blog_posts:
		section = f'{get_post_semester(post)} {str(post.created.year)}'
		if section != current_section:
			sections.append((section, post))
			current_section = section

	return authentication.auth_render_template(
		'main/blog.html', 
		blogs=blog_posts[(page - 1) * MAX_BLOGS_PER_PAGE:MAX_BLOGS_PER_PAGE * page],
		texts=blog_texts[(page - 1) * MAX_BLOGS_PER_PAGE:MAX_BLOGS_PER_PAGE * page],
		sections=sections,
		title_filter=title_filter,
		year_filter=year_filter,
		semester_filter=semester_filter,
		page=page,
		maxPages=max(math.ceil(len(blog_posts) / MAX_BLOGS_PER_PAGE), 1),
		zip=zip
	)

def filter_post(post, title_filter, year_filter, semester_filter):
	if title_filter != None:
		if title_filter.lower() not in post.title.lower():
			return False
	if year_filter != None:
		if post.created.year != year_filter:
			return False
	if semester_filter != None:
		if get_post_semester(post) != semester_filter:
			return False
	
	return True

def get_post_semester(post):
	if post.created.month < BLOG_SPRING_SEMESTER.month or post.created.month == BLOG_SPRING_SEMESTER.month and post.created.day <= BLOG_SPRING_SEMESTER.day:
		section = 'Spring'
	elif post.created.month < BLOG_SUMMER_SEMESTER.month or post.created.month == BLOG_SUMMER_SEMESTER.month and post.created.day <= BLOG_SUMMER_SEMESTER.day:
		section = 'Summer'
	else:
		section = 'Fall'
	return section

@blueprint.route('documents')
def documents():
	return documents_page(1)

@blueprint.route('documents/<int:page>')
def documents_page(page):
	if page <= 0:
		page = 1
	docs = document_models.getDocumentsByUserType(authentication.getCurrentUserType())
	
	if len(docs) == 0 or max(1, math.ceil(len(docs) / MAX_DOCUMENT_PER_PAGE)) < page:
		page = 1
		
	return authentication.auth_render_template(
		'main/documents.html',
		docs=docs[(page - 1) * MAX_DOCUMENT_PER_PAGE:MAX_DOCUMENT_PER_PAGE * page],
		page=page,
		maxPages=max(math.ceil(len(docs)/MAX_DOCUMENT_PER_PAGE), 1),
		per_row=DOCUMENTS_PER_ROW,
		per_page=MAX_DOCUMENT_PER_PAGE,
	)