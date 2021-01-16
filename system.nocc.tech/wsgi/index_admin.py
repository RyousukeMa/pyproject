# -*- coding: utf-8 -*-

import importlib
import re
import blossom
import matsuoka_func as mf

#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# 認証
	#
	# 認証失敗 → 認証ページへ転送
	m_uno = web.getcookie_secure('admin')
	if m_uno:
		#
		# 成功
		#
		m_uno = int(m_uno)
		web.uno = m_uno
		web.user_icon = mf.get_icon(web,web.uno)
		web.ano = mf.from_uno_getdb_ano(web,web.uno,cookie=False)
		web.setcookie_secure('admin', str(m_uno), maxage=1800)
	else:
		#
		# 失敗
		#
		return web.redirect('/signin?message=failed')

	# --------------------------------------------------------------------------
	#
	# 例えば /admin/admin にアクセスがあった場合に次の２行と同等の処理を行う
	# import admin.admin_foobar
	# return admin.admin_foobar.main(web, build)
	#
	module = web.path[len('/admin/'):].replace('.', '_')
	module = 'admin.admin_' + (module or 'index')
	web.log(module,"RED")
	try:
		return importlib.import_module(module).main(web, build)
	except ImportError as e:
		web.log(e, 'red')
		#
		# *.py が無くても HTML テンプレートが存在すればそれを表示する。
		#
		web.statuscode = 404
		return build(web, local={})
	#
	# 404 Not Found
	#
	web.statuscode = 404
	return web.echo()
