from datetime import datetime

from mako.runtime import supports_caller

# 2018-10-27 19:45:15.014656
dateFormat = "%Y/%m/%d"
@supports_caller
def date_to_string(x):
	x = datetime.strptime(x, dateFormat)
	return x.strftime(dateFormat)