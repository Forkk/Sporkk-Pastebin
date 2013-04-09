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

from urlmodel import URLMapping, get_mapping, url_id_taken, generate_unused_url_id

# List of URL types. These act as 'modules' for Sporkk features.
url_types = []

@app.route('/')
def index():
	if len(url_types) > 0:
		return redirect(url_for('submit_form', type_spec = url_types[0].get_specifiers()[0]))
	else:
		abort(500)

@app.route('/submit/<type_spec>', methods = ['GET', 'POST'])
def submit_form(type_spec):
	"""The page for submitting things to the URL shortener."""
	if request.method == 'GET':
		submit_forms = []
		url_type = None
		
		# Get a list of submit forms and find the apropriate URL type in the same loop.
		for utype in url_types:
			submit_forms.append(utype.get_submit_form_info().
				to_template_dict(url_for("submit_form", type_spec = utype.get_specifiers()[0])))

			# If the given type spec matches one of the URL type's specifiers, show its submit page. 
			# We'll do this after we're done getting the submit form list.
			if type_spec in utype.get_specifiers():
				url_type = utype
				submit_forms[len(submit_forms)-1]["active"] = True

		# Now, we show the submit form page (or error if the URL type wasn't found)
		if url_type is not None:
			return url_type.handle_submit_form(submit_forms)
		else:
			return redirect("/")

	elif request.method == 'POST':
		for utype in url_types:
			if type_spec in utype.get_specifiers():
				return utype.handle_submit(request)


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


@app.route('/<type_spec>/<url_id>')
def url_type_spec_view(type_spec, url_id):
	"""View that goes to the URL of the given type that the given ID maps to"""
	for utype in url_types:
		# If the given type spec matches one of the URL type's specifiers.
		if type_spec in utype.get_specifiers():
			mapping = get_mapping(url_id)

			# Make sure the model type matches the URL type's model type as well.
			if type(mapping) is utype.get_model_type():
				return utype.handle_view(url_id, mapping)

	# It's not valid, so go home.
	return redirect("/")


####################
#### INITIALIZE ####
####################

# Load URL type modules.
import shortenedurl
import pastebinurl

# FIXME: This is a pretty stupid way of loading things.
typemodules = [ pastebinurl, shortenedurl ]

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
