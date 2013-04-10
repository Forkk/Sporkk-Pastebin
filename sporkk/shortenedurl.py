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

from flask import render_template, redirect, abort, url_for

from urltype import URLType, URLTypeSubmitForm, err_id_map
from urlmodel import URLMapping, generate_unused_url_id
from postermodel import PosterModel, get_poster_timestamp, update_poster_timestamp

from datetime import datetime, timedelta

import re

urlregex = re.compile(r'^(https?|ftp)://')

local_err_id_map = {
	"bad-longurl": "Please specify a valid URL to shorten.",
	"not-found": "The given short URL was not found.",
}

def get_url_types_provided():
	"""Returns a list of the URL types provided by this module."""
	return url_types

class ShortenedURLType(URLType):
	"""URL type representing a shortened URL."""

	def get_submit_form_info(self):
		return URLTypeSubmitForm("shortener-form.html", "shorten", "URL Shortener")

	def handle_submit_form(self, form_info_list, error_id):
		errormsg = None
		if error_id is None:
			errormsg = None
		elif error_id in local_err_id_map:
			errormsg = local_err_id_map[error_id]
		elif error_id in err_id_map:
			errormsg = err_id_map[error_id]
		else:
			errormsg = "An unknown error occurred."

		return render_template("shortener-form.html", submit_forms = form_info_list, error = errormsg)

	def handle_view(self, url_id, shorturl, error = None):
		if shorturl is None or type(shorturl) is not ShortenedURLModel:
			return redirect("/") # TODO: Add better error handling in this case.

		return redirect(shorturl.mapped_url)

	def handle_submit(self, request):
		longurl = request.form['longurl']

		# If the long URL is not a valid URL.
		if not urlregex.search(longurl):
			return redirect(self.error_url('bad-longurl'))

		# If prevent dupe IDs is enabled, check if this URL has already been shortened.
		if app.config.get('SHORTEN_PREVENT_DUPE_IDS'):
			shorturl = get_by_mapped_url(longurl)
			if shorturl is not None:
				# If this URL has already been shortened, give the user the already shortened URL, rather than creating a new shortened URL for it.
				return render_template("shorten-success.html", shortened_url = url_for('url_id_view', url_id = shorturl.url_id))

		user_lastpost = get_poster_timestamp(request.remote_addr)
		if datetime.utcnow() < user_lastpost + timedelta(seconds = app.config.get('POST_COOLDOWN_TIME')):
			return redirect(self.error_url('too-fast'))

		# Generate a random string for the URL ID. Make sure it's not in use.
		url_id = generate_unused_url_id(app.config.get('SHORTURL_LENGTH'))

		shorturl = ShortenedURLModel()
		shorturl.url_id = url_id
		shorturl.mapped_url = longurl
		shorturl.poster_ip = request.remote_addr

		db.session.add(shorturl)

		# Update the poster's timestamp
		update_poster_timestamp(request.remote_addr, False)

		db.session.commit()

		return render_template("shorten-success.html", shortened_url = url_for('url_id_view', url_id = shorturl.url_id))

	def get_model_type(self):
		return ShortenedURLModel

	def get_specifiers(self):
		return [ 'short', 's' ]

	def get_submit_action_id(self):
		return 'shorten'


class ShortenedURLModel(URLMapping):
		"""Database model for shortened URLs"""
		__tablename__ = "shortened_urls"

		url_id = db.Column(db.String(64), db.ForeignKey('url_map.url_id'), primary_key = True)

		mapped_url = db.Column(db.Text)

		__mapper_args__ = { 'polymorphic_identity': 'short', }

def get_shorturl(url_id):
	"""Looks up the given URL ID in the database and returns its corresponding shortened URL object.
	Returns None if the URL ID doesn't correspond to a shortened URL."""
	return ShortenedURLModel.query.filter_by(url_id = url_id).first()

def get_by_mapped_url(mapped_url):
	"""Finds a shortened URL in the database whose mapped URL matches the given URL."""
	return ShortenedURLModel.query.filter_by(mapped_url = mapped_url).first()


url_types = [ ShortenedURLType() ]
