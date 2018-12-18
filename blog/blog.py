from flask import (
	Blueprint, render_template
)

blueprint = Blueprint('blog', __name__, url_prefix='/blog')

@blueprint.route('/')
def index():
	return render_template('blog/index.html')