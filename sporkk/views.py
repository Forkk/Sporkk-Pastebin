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

from flask import render_template, request, redirect, abort
from flask.ext.sqlalchemy import orm

import string, random, re


class URLMapping(db.Model):
	"""Model for mapping URLs to their corresponding items."""
	__tablename__ = "url_map"

	url_id = db.Column(db.String(64), primary_key = True)
	url_type = db.Column(db.String(10))

	__mapper_args__ = { 'polymorphic_identity': 'urlmap', 
		'polymorphic_on': url_type,
		'with_polymorphic': '*',
	}


class ShortenedURL(URLMapping):
	"""Model for shortened URLs"""
	__tablename__ = "shortened_urls"

	url_id = db.Column(db.String(64), db.ForeignKey('url_map.url_id'), primary_key = True)

	mapped_url = db.Column(db.Text)

	__mapper_args__ = { 'polymorphic_identity': 'short', }


class Paste(URLMapping):
	"""Model for pastes in the pastebin."""
	__tablename__ = "pastes"

	url_id = db.Column(db.String(64), db.ForeignKey('url_map.url_id'), primary_key = True)	

	paste_content = db.Column(db.Text)

	__mapper_args__ = { 'polymorphic_identity': 'paste', }


urlregex = re.compile(r'^(https?|ftp)://')

def get_mapping(url_id):
	return db.session.query(db.with_polymorphic(URLMapping, '*')).filter_by(url_id = url_id).first()

def get_shorturl(url_id):
	return ShortenedURL.query.filter_by(url_id = url_id).first()

def get_paste(url_id):
	return Paste.query.filter_by(url_id = url_id).first()

def url_id_taken(url_id):
	return get_mapping(url_id) is not None

def generate_url_id(length):
	return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(length))


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


def shortener_submit():
	longurl = request.form['longurl']

	# If the long URL is not a valid URL.
	if not urlregex.search(longurl):
		return render_template("submit-form.html", shortener_errormsg = "You must specify a valid URL.")

	# Generate a random string for the URL ID. Make sure it's not in use.
	url_id = generate_url_id(8)
	while url_id_taken(url_id):
		url_id = generate_url_id(8)

	shorturl = ShortenedURL()
	shorturl.url_id = url_id
	shorturl.mapped_url = longurl

	db.session.add(shorturl)
	db.session.commit()

	return render_template("shorten-success.html", shortened_url = app.config['SHORTENER_ROOT_URL'] + shorturl.url_id)


def paste_submit():
	paste_content = request.form['paste_content']

	# Generate a random string for the URL ID. Make sure it's not in use.
	url_id = generate_url_id(8)
	while url_id_taken(url_id):
		url_id = generate_url_id(8)

	paste = Paste()
	paste.url_id = url_id
	paste.paste_content = paste_content

	db.session.add(paste)
	db.session.commit()

	return redirect(url_id)


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


@app.route('/s/<url_id>')
@app.route('/short/<url_id>')
def shorturl_view(url_id):
	"""View for shortened URLs only."""
	shorturl = get_shorturl(url_id)
	return handle_shorturl(shorturl)


@app.route('/p/<url_id>')
@app.route('/paste/<url_id>')
def paste_view(url_id):
	"""View for paste URLs only."""
	paste = get_paste(url_id)
	return handle_paste(paste)


def handle_shorturl(shorturl):
	if shorturl is None:
		return redirect("/")

	return redirect(shorturl.mapped_url)


def handle_paste(paste):
	if paste is None:
		return redirect("/")

	return render_template("pastebin-view.html", paste_content = paste.paste_content)


# Initialize the DB table.
db.create_all()
