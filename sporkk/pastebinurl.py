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

from urltype import URLType
from urlmodel import URLMapping, generate_unused_url_id

def get_url_types_provided():
	"""Returns a list of the URL types provided by this module."""
	return url_types

class PastebinURLType(URLType):
	"""URL type representing a pastebin URL."""

	def handle_view(self, url_id, paste):
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


	def handle_submit(self, request):
		paste_content = request.form['paste_content']

		syntax_highlight = 'none'
		if 'syntax_highlight' in request.form and request.form['syntax_highlight']:
			syntax_highlight = 'auto'

		poster_name = None
		if 'poster_name' in request.form and request.form['poster_name'] is not None: 
			poster_name = request.form['poster_name']

		# Generate a random string for the URL ID. Make sure it's not in use.
		url_id = generate_unused_url_id(app.config.get('SHORTURL_LENGTH'))

		paste = PasteModel()
		paste.url_id = url_id
		paste.paste_content = paste_content
		paste.highlight_lang = syntax_highlight
		paste.posted_by = poster_name

		db.session.add(paste)
		db.session.commit()

		return redirect(url_id)


	def get_model_type(self):
		return PasteModel

	def get_specifiers(self):
		return [ 'p', 'paste' ]

	def get_submit_action_id(self):
		return 'paste'


class PasteModel(URLMapping):
	"""Database model for pastes in the pastebin."""
	__tablename__ = "pastes"

	url_id = db.Column(db.String(64), db.ForeignKey('url_map.url_id'), primary_key = True)	

	paste_content = db.Column(db.Text)

	highlight_lang = db.Column(db.String(6))

	__mapper_args__ = { 'polymorphic_identity': 'paste', }

def get_paste(url_id):
	"""Looks up the given URL ID in the database and returns its corresponding paste.
	Returns None if the URL ID is not a paste"""
	return Paste.query.filter_by(url_id = url_id).first()

url_types = [ PastebinURLType() ]
