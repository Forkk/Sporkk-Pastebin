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

from . import db

import string, random

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

def get_mapping(url_id):
	"""Queries the database and returns the URL mapping for the given URL ID."""
	return db.session.query(db.with_polymorphic(URLMapping, '*')).filter_by(url_id = url_id).first()

def url_id_taken(url_id):
	"""Checks if the given URL ID is taken."""
	return get_mapping(url_id) is not None

def generate_url_id(length):
	"""Generates a random URL ID with the given length."""
	return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(length))

def generate_unused_url_id(length):
	"""Generates a URL ID that isn't in use."""
	url_id = generate_url_id(length)
	while url_id_taken(url_id):
		url_id = generate_url_id(length)
	return url_id
