from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect

def is_safe_url(url):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, url))
	return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def get_redirect_url():
	for url in request.args.get('next'), request.referrer:
		if not url:
			continue
		if is_safe_url(url):
			return url