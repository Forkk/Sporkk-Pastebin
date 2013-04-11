function createAlertDiv(content, title, alertType, alertBlock, closeCallback)
{
	if (typeof(alertBlock) === 'undefined')
		alertBlock = false;
	if (typeof(closeCallback) === 'undefined')
		closeCallback = null;

	var alertDiv = $('<div class="alert"></div>').hide();
	var alertDivText = $('<span>' + content + '</span>');
	var alertDivClose = $('<button type="button" class="close">&times;</button>');

	switch (alertType)
	{
	case "success":
		alertDiv.addClass("alert-success");
		break;

	case "error":
		alertDiv.addClass("alert-error");
		break;
	}

	var alertDivTitle;
	if (alertBlock)
	{
		alertDivTitle = $('<h4>' + title + '</h4>');
		alertDiv.addClass("alert-block");
	}
	else
	{
		alertDivTitle = $('<strong>' + title + '</strong>');
	}

	if (closeCallback === null)
	{
		closeCallback = function() 
		{
			alertDiv.slideUp(300, function() { alertDiv.remove(); });
		};
	}

	alertDiv.append(alertDivClose);
	alertDiv.append(alertDivTitle);
	alertDiv.append(alertDivText);

	alertDiv.click(closeCallback);
	alertDivClose.click(closeCallback);

	return { div: alertDiv, bodySpan: alertDivText, titleBlock: alertDivTitle, closeBtn: alertDivClose, closeCallback: closeCallback };
}