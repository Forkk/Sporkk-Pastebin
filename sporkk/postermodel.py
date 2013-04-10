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

from datetime import datetime

class PosterModel(db.Model):
	"""Model for IP addresses that have posted to the table."""
	__tablename__ = "posters"

	poster_ip = poster_ip = db.Column(db.String(46), primary_key = True)
	last_post = db.Column(db.DateTime)

def get_poster_timestamp(ip):
	"""Gets the last post timestamp for the given IP."""
	pm_object = PosterModel.query.filter_by(poster_ip = ip).first()

	if pm_object is not None:
		return pm_object.last_post
	else:
		return None

def update_poster_timestamp(ip, auto_commit = True):
	"""Updates the last post timestamp for the given IP."""

	pm_object = PosterModel.query.filter_by(poster_ip = ip).first()

	if pm_object is None:
		pm_object = PosterModel()
		pm_object.poster_ip = ip
		pm_object.last_post = datetime.utcnow()
		db.session.add(pm_object)

	else:
		pm_object.last_post = datetime.utcnow()

	if auto_commit:
		db.session.commit()
