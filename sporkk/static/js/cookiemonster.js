// Copyright (C) 2013 Andrew Okin

// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
// documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
// the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and 
// to permit persons to whom the Software is furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
// THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
// TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

// Yes, I did name my cookie utils script cookiemonster. I couldn't help myself...

function setCookie(cookiename, value, expire_days)
{
	var expire_date = new Date();

	expire_date.setDate(expire_date.getDate() + expire_days);

	var cookie_value = escape(value) + ((expire_days==null) ? "" : "; expires=" + expire_date.toUTCString());
	document.cookie = cookiename + "=" + cookie_value;
}

function getCookie(name)
{
	var cookies = document.cookie.split(';');
	for(var i = 0; i < cookies.length; i++)
	{
		var cookie = cookies[i];
		while (cookie.charAt(0)==' ')
			cookie = cookie.substring(1, cookie.length);

		if (cookie.indexOf(name) == 0)
			return cookie.substring(name.length+1, cookie.length);
	}
	return null;
}
