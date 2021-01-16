# -*- coding: utf-8 -*-

import importlib

#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# 例えば /foobar にアクセスがあった場合に次の２行と同等の処理を行う
	# import open.open_foobar
	# return open.open_foobar.main(web, build)
	#
	relpath = web.path.split('/')
	if len(relpath) == 3:
		module = 'open.open_' + (relpath[2] or 'signin')
	else:
		module = 'open.open_' + (relpath[1] or 'signin')
	web.log(module,"Blue")
	web.log(relpath,"RED")
	try:
		return importlib.import_module(module).main(web, build)
	except ImportError as e:
		#
		# *.py が無くても HTML テンプレートが存在すればそれを表示する。
		#
		web.log("err","Blue")
		relpath = web.path.split('/')
		relpath = '/open'  \
			+ '/open.' + (relpath[1] or 'signin') + '.html'
		web.log(relpath,"RED")
		web.statuscode = 404
		return build(web, local={}, relpath=relpath)
	#
	# 404 Not Found
	#
	return web.echo()
