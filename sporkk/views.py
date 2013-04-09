# Copyright (C) 2013 Andrew Okin

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and 
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from . import app, db

from flask import render_template, request, redirect, abort, url_for
from flask.ext.sqlalchemy import orm

from urlmodel import URLMapping, get_mapping, url_id_taken, generate_unused_url_id

# List of URL types. These act as 'modules' for Sporkk features.
url_types = []

@app.route('/', methods = ['GET', 'POST'])
def submit_form():
	"""The page for submitting things to the URL shortener."""
	if request.method == 'POST':
		action = request.form['action']

		# Find the URL type whose submit action corresponds to the action we received.
		for utype in url_types:
			if action == utype.get_submit_action_id():
				# When we find it, hand over processing to it.
				return utype.handle_submit(request)

		# If there isn't one, assume the request was invalid and give a 400 error.
		abort(400)

	elif request.method == 'GET':
		return render_template("submit-form.html")

	abort(500)


# For any URL types
@app.route('/<url_id>')
def url_id_view(url_id):
	"""View that goes to whatever the specified URL ID maps to."""
	mapping = get_mapping(url_id)

	if mapping is None:
		return redirect("/")

	mapping_type = type(mapping)

	# Find the URL type whose model type matches and let it handle rendering the view.
	for utype in url_types:
		if mapping_type is utype.get_model_type():
			return utype.handle_view(url_id, mapping)

	# If nothing is found, act like the URL ID doesn't even exist.
	return redirect("/")


####################
#### INITIALIZE ####
####################

# Load URL type modules.
import shortenedurl as su
import pastebinurl as pu

# FIXME: This is a pretty stupid way of loading things.
typemodules = [ su, pu ]

for typemod in typemodules:
	try:
		url_types += typemod.get_url_types_provided()

	except AttributeError:
		# If get_url_types_provided doesn't exist, this isn't a proper type module we can load URL types from.
		continue

# Initialize the DB table.
db.create_all()


# Dict that maps a language name as it's stored in the DB to its prettyprint name.
# Java, Python, Bash, SQL, HTML, XML, CSS, Javascript, Makefiles, and Rust
pp_langmap = {
	"c": "c",
	"c++": "cpp",
	"c#": "cs",
	"java": "java",
	"python": "py",
	"xml": "xml",
}
