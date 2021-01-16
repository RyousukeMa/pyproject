# -*- coding: utf-8 -*-

import importlib
import re
import blossom

#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	# 認証失敗 → 認証ページへ転送
	#
	m_uno = web.getcookie_secure('root')
	if m_uno:
		#
		# 成功
		#
		web.setcookie_secure('root', 'root', maxage=1800)
	else:
		#
		# 失敗
		#
		return web.redirect('/signin?message=failed')


	# --------------------------------------------------------------------------
	#
	# 例えば /root/foobar にアクセスがあった場合に次の２行と同等の処理を行う
	# import root.root_foobar
	# return root.root_foobar.main(web, build)
	#
	module = web.path[len('/root/'):].replace('.', '_')
	module = 'root.root_' + (module or 'index')
	try:
		return importlib.import_module(module).main(web, build)
	except ImportError as e:
		web.log(e, 'red')
		#
		# *.py が無くても HTML テンプレートが存在すればそれを表示する。
		#	web.path: /root/foobar
		# 	 relpath: /root/root.foobar.html
		#
		relpath = web.path.split('/')
		relpath = '/' + relpath[1] \
		 	+ '/' + relpath[1] + '.' + (relpath[2] or 'index') + '.html'
		return build(web, local={}, relpath=relpath)
	#
	# 404 Not Found
	#
	web.statuscode = 404
	return web.echo()
