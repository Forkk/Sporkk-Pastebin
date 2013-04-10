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

from collections import OrderedDict

local_err_id_map = {
	"empty-paste": "You can't post an empty paste.",
}

def get_url_types_provided():
	"""Returns a list of the URL types provided by this module."""
	return url_types

class PastebinURLType(URLType):
	"""URL type representing a pastebin URL."""

	def get_submit_form_info(self):
		return URLTypeSubmitForm("pastebin-form.html", "paste", "Pastebin")

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

		return render_template("pastebin-form.html", submit_forms = form_info_list, syntax_options = pp_langs, error = errormsg)

	def handle_view(self, url_id, paste):
		if paste is None:
			return redirect("/")

		dbhname = paste.highlight_lang
		ppname = None
		if dbhname in pp_langs:
			ppname = pp_langs[dbhname]['ppname']

		poster = paste.posted_by
		if poster == '':
			poster = None

		return render_template("pastebin-view.html", 
			paste_content = paste.paste_content, 
			syntax_highlight = ppname is not None and ppname != '', 
			lang = ppname,
			poster = poster)


	def handle_submit(self, request):
		user_lastpost = get_poster_timestamp(request.remote_addr)
		if datetime.utcnow() < user_lastpost + timedelta(seconds = app.config.get('POST_COOLDOWN_TIME')):
			return redirect(self.error_url('too-fast'))

		paste_content = request.form['paste_content']

		if paste_content.strip() == '':
			return redirect(self.error_url('empty-paste'))

		syntax_highlight = None
		if 'syntax' in request.form and request.form['syntax'] is not None:
			syntax_highlight = request.form['syntax']

		poster_name = None
		if 'poster_name' in request.form and request.form['poster_name'] is not None: 
			poster_name = request.form['poster_name'].strip()

		if poster_name == '':
			poster_name = None

		# Generate a random string for the URL ID. Make sure it's not in use.
		url_id = generate_unused_url_id(app.config.get('SHORTURL_LENGTH'))

		paste = PasteModel()
		paste.url_id = url_id
		paste.paste_content = paste_content
		
		paste.posted_by = poster_name
		paste.poster_ip = request.remote_addr
		paste.highlight_lang = syntax_highlight
		db.session.add(paste)

		# Update the poster's timestamp
		update_poster_timestamp(request.remote_addr, False)

		db.session.commit()

		return redirect(url_for('url_type_spec_view', type_spec = 'paste', url_id = url_id))


	def get_model_type(self):
		return PasteModel

	def get_specifiers(self):
		return [ 'paste', 'p' ]

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

# google-code-prettify language info
pp_langs = OrderedDict([
	(None, dict(dispname="Plain Text")), # I'm sorry.
	("auto", dict(ppname="auto", dispname="Automatic")),
	("C", dict(ppname="c", dispname="C")),
	("C++", dict(ppname="cpp", dispname="C++")),
	("C#", dict(ppname="cs", dispname="C#")),
	("HTML", dict(ppname="html", dispname="HTML")),
	("XML", dict(ppname="xml", dispname="XML")),
	("Java", dict(ppname="java", dispname="Java")),
	("JS", dict(ppname="js", dispname="JavaScript")),
	("Python", dict(ppname="py", dispname="Python")),
	("Perl", dict(ppname="perl", dispname="Perl")),
	("Ruby", dict(ppname="rb", dispname="Ruby")),
	("Bash", dict(ppname="bash", dispname="Bash"))
])

url_types = [ PastebinURLType() ]

