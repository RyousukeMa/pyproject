# -*- coding: utf-8 -*-

#
#
# web
#
#
def application(environ, start_response):
	try:
		import index
		return index.main(environ, start_response)
	except:
		import traceback
		start_response('500 Internal Server Error', [('Content-type', 'text/plain')])
		return [traceback.format_exc().encode()]

#
#
# cron
#
#
if __name__=='__main__':
	import os
	import sys
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	try:
		slash = sys.argv[1].find('/')
		environ = {
			'HTTP_HOST'  :sys.argv[1][:slash],
			'REQUEST_URI':sys.argv[1][slash:],
		}
	except:
		environ = {}
	application(environ, None)
