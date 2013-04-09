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
	
import string, random, re


class URLMapping(db.Model):
	"""Model for mapping URLs to their corresponding items."""
	__tablename__ = "url_map"

	url_id = db.Column(db.String(64), primary_key = True)
	url_type = db.Column(db.String(10))

	posted_by = db.Column(db.String(50))

	__mapper_args__ = { 'polymorphic_identity': 'urlmap', 
		'polymorphic_on': url_type,
		'with_polymorphic': '*',
	}


urlregex = re.compile(r'^(https?|ftp)://')

def get_mapping(url_id):
	return db.session.query(db.with_polymorphic(URLMapping, '*')).filter_by(url_id = url_id).first()

def url_id_taken(url_id):
	"""Checks if the given URL ID is taken."""
	return get_mapping(url_id) is not None

def generate_url_id(length):
	"""Generates a random URL ID with the given length."""
	return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(length))

def generate_unused_url_id(length = app.config.get('SHORTURL_LENGTH')):
	"""Generates a URL ID that isn't in use."""
	url_id = generate_url_id(length)
	while url_id_taken(url_id):
		url_id = generate_url_id(length)
	return url_id


@app.route('/', methods = ['GET', 'POST'])
def submit_form():
	"""The page for submitting things to the URL shortener."""
	if request.method == 'POST':
		action = request.form['action']

		if action == 'shorten':
			return shortener_submit()

		elif action == 'paste':
			return paste_submit()

		else:
			abort(400)

	elif request.method == 'GET':
		return render_template("submit-form.html")

	else:
		abort(500)


# For any URL types
@app.route('/<url_id>')
def url_id_view(url_id):
	"""View that goes to whatever the specified URL ID maps to."""
	mapping = get_mapping(url_id)

	# If this URL maps to a shortened URL, redirect.
	if type(mapping) is ShortenedURL:
		return handle_shorturl(mapping)

	elif type(mapping) is Paste:
		return handle_paste(mapping)

	else:
		return redirect("/")



###################
#### SHORTENER ####
###################

# Shortened URLs
class ShortenedURL(URLMapping):
	"""Database model for shortened URLs"""
	__tablename__ = "shortened_urls"

	url_id = db.Column(db.String(64), db.ForeignKey('url_map.url_id'), primary_key = True)

	mapped_url = db.Column(db.Text)

	__mapper_args__ = { 'polymorphic_identity': 'short', }

# Get shortened URL
def get_shorturl(url_id):
	"""Looks up the given URL ID in the database and returns its corresponding shortened URL object.
	Returns None if the URL ID doesn't correspond to a shortened URL."""
	return ShortenedURL.query.filter_by(url_id = url_id).first()

# View shorten
@app.route('/s/<url_id>')
@app.route('/short/<url_id>')
def shorturl_view(url_id):
	"""View for shortened URLs only."""
	shorturl = get_shorturl(url_id)
	return handle_shorturl(shorturl)

# View shorten
def handle_shorturl(shorturl):
	"""Returns the response page for the given shortened URL"""
	if shorturl is None:
		return redirect("/")

	return redirect(shorturl.mapped_url)

# Submit shorten
def shortener_submit():
	longurl = request.form['longurl']

	# If the long URL is not a valid URL.
	if not urlregex.search(longurl):
		return render_template("submit-form.html", shortener_errormsg = "You must specify a valid URL.")

	# Generate a random string for the URL ID. Make sure it's not in use.
	url_id = generate_unused_url_id()

	shorturl = ShortenedURL()
	shorturl.url_id = url_id
	shorturl.mapped_url = longurl

	db.session.add(shorturl)
	db.session.commit()

	return render_template("shorten-success.html", shortened_url = url_for('url_id_view', url_id = shorturl.url_id))


##################
#### PASTEBIN ####
##################

# Paste
class Paste(URLMapping):
	"""Database model for pastes in the pastebin."""
	__tablename__ = "pastes"

	url_id = db.Column(db.String(64), db.ForeignKey('url_map.url_id'), primary_key = True)	

	paste_content = db.Column(db.Text)

	highlight_lang = db.Column(db.String(6))

	__mapper_args__ = { 'polymorphic_identity': 'paste', }

# Get a paste
def get_paste(url_id):
	"""Looks up the given URL ID in the database and returns its corresponding paste.
	Returns None if the URL ID is not a paste"""
	return Paste.query.filter_by(url_id = url_id).first()

# View paste
@app.route('/p/<url_id>')
@app.route('/paste/<url_id>')
def paste_view(url_id):
	"""View for paste URLs only."""
	paste = get_paste(url_id)
	return handle_paste(paste)

# View paste
def handle_paste(paste):
	"""Renders the page for viewing the given paste."""
	if paste is None:
		return redirect("/")

	pprint = False
	if paste.highlight_lang is not None and paste.highlight_lang != 'none':
		pprint = True

	poster = paste.posted_by
	if poster == '':
		poster = None

	return render_template("pastebin-view.html", paste_content = paste.paste_content, syntax_highlight = pprint, 
		poster = poster)

# Submit paste
def paste_submit():
	paste_content = request.form['paste_content']

	syntax_highlight = 'none'
	if 'syntax_highlight' in request.form and request.form['syntax_highlight']:
		syntax_highlight = 'auto'

	poster_name = None
	if 'poster_name' in request.form and request.form['poster_name'] is not None: 
		poster_name = request.form['poster_name']

	# Generate a random string for the URL ID. Make sure it's not in use.
	url_id = generate_unused_url_id()

	paste = Paste()
	paste.url_id = url_id
	paste.paste_content = paste_content
	paste.highlight_lang = syntax_highlight
	paste.posted_by = poster_name

	db.session.add(paste)
	db.session.commit()

	return redirect(url_id)



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
