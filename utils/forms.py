from wtforms import HiddenField
from flask_wtf import FlaskForm
from flask import request, url_for, redirect
import utils.utils as utils

class RedirectForm(FlaskForm):
	next = HiddenField()

	def __init__(self, *args, **kwargs):
		FlaskForm.__init__(self, *args, **kwargs)
		if not self.next.data:
			self.next.data = utils.get_redirect_url() or ''
		
	def redirect(self, endpoint, **values):
		if utils.is_safe_url(self.next.data):
			return redirect(self.next.data)
		url = utils.get_redirect_url()
		return redirect(url or url_for(endpoint, **values))