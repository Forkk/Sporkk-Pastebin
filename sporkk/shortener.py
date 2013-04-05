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

from flask import render_template, request, redirect

import string, random, re

# TODO: Support subdomains.

class URLMapping(db.Model):
	"""Model for shortened URLs. Maps the short URL to the long version."""
	id = db.Column(db.Integer, primary_key = True)
	urlid = db.Column(db.String(64), unique = True)
	longurl = db.Column(db.Text)


urlregex = re.compile(r'^(http|ftp)s?://')

def get_mapping(urlid):
	return URLMapping.query.filter_by(urlid = urlid).first()

def shorturl_taken(urlid):
	return get_mapping(urlid) is not None

def generate_shorturl(length):
	return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(length))


@app.route('/', methods = ['GET'])
def submit_form():
	"""The page for submitting things to the URL shortener."""
	return render_template("shortener/submit-form.html")

@app.route('/submit', methods = ['GET', 'POST'])
def submit_url():
	mapping = URLMapping()

	mapping.longurl = request.form['longurl']

	# Generate a random string for the short URL. Make sure it's not in use.
	urlid = generate_shorturl(8)
	while shorturl_taken(urlid):
		urlid = generate_shorturl(8)

	mapping.urlid = urlid

	db.session.add(mapping)
	db.session.commit()

	return "Shortened to: http://localhost/%s" % mapping.urlid


@app.route('/<url_id>')
def shortener_redirect(url_id):
	"""URL shortener page that redirects users from the shortened URL to the full URL."""
	mapping = get_mapping(url_id)

	return redirect(mapping.longurl)


# Initialize the DB table.
db.create_all()
