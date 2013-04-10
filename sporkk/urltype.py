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

from . import app

from flask import url_for

class URLTypeSubmitForm:
	def __init__(self, form, form_tab_id, form_tab_title):
		self.form = form
		self.form_tab_id = form_tab_id
		self.form_tab_title = form_tab_title

	def to_template_dict(self, tabhref):
		return { "tabhref": tabhref, "tabtitle": self.form_tab_title, "form": self.form }


class URLType:
	"""
	Abstract base class for a URL type.

	A URL type represents a type of URL that Sporkk handles, such as a pastebin URL or a shortener URL.
	"""

	def get_submit_form_info(self):
		"""
		Renders this URL type's submit form, returning it as a URLTypeSubmitForm.
		"""
		raise NotImplementedError("get_submit_form_info is not implemented for this URL type.")

	def handle_submit_form(self, form_info_list):
		"""
		Function that handles this URL type's submit form. Should return a rendering of the submit form.
		The form_info_list argument is a list of dicts generated from the URLTypeSubmitForms of all the loaded URL types. This list is used for displaying tabs.
		"""
		raise NotImplementedError("handle_submit_form is not implemented for this URL type.")

	def handle_view(self, url_id, dbobj):
		"""
		Function that handles this URL type's view. Should return the appropriate response for this URL type.
		Both the URL ID and the database entry for said URL ID are passed to this function. When overriding this function, you should not do additional lookups for the given URL ID in the database (doing so would be a bit inefficient), but rather use the one given.
		"""
		raise NotImplementedError("handle_view is not implemented for this URL type.")

	def handle_submit(self, request):
		"""Function called when a user submits something for this URL type."""
		raise NotImplementedError("handle_submit is not implemented for this URL type.")

	def get_model_type(self):
		"""
		Returns this URL type's database model type.
		This is used in database lookups to determine which URL type a certain URL mapping belongs to.
		"""
		raise NotImplementedError("get_model_type is not implemented for this URL type.")

	def get_specifiers(self):
		"""
		Returns a list of URL specifiers that can be put before a URL ID to specify that the user wants this URL type only.
		For example: If this type's specifiers are ['p', 'paste'], the user can go to the URL /p/<url_id> to ensure that the given URL is a paste, not something else. If the user goes to /p/<url_id> and the URL ID is not that of a paste, it will be treated as if it does not exist.
		You must override this function and provide at least one URL specifier when subclassing or the submit URL won't work.
		"""
		raise NotImplementedError("get_specifiers is not implemented for this URL type.")

	def get_submit_action_id(self):
		"""
		Returns what the value of 'action' field on this URL type's submission form should be.
		This value is used to determine which URL type a form corresponds to when it is submitted.
		"""
		raise NotImplementedError("get_submit_action_id is not implemented for this URL type.")

	def error_url(self, err_id):
		return url_for('submit_form', type_spec = self.get_specifiers()[0], err_id = err_id)

err_id_map = {
	"too-fast": "You're posting too fast! Please wait %i seconds between posts." % app.config.get('POST_COOLDOWN_TIME'),
}
