# -*- coding: utf-8 -*-

import blossom

from datetime import datetime


#
#
# vars
#
#
def time_conversion(web, timestamp):
	web.log('tool.py','purple')
	if not timestamp:
		return None
	try:
		when = datetime.fromtimestamp(float(timestamp))
	except:
		return None
	m = when.strftime('%m')
	d = when.strftime('%d')
	return {
		'Y' : when.strftime('%Y'),
		'm' : int(m),
		'mm': m,
		'd' : int(d),
		'dd': d,
		'H' : when.strftime('%H'),
		'M' : when.strftime('%M'),
	}
