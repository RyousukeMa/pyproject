# -*- coding: utf-8 -*-

import importlib
import re
import blossom
import matsuoka_func

#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# 認証失敗 → 認証ページへ転送
	#
	if web.getcookie_secure('admin'):
		m_uno = web.getcookie_secure('admin')
		m_name = 'admin'
	elif web.getcookie_secure('user'):
		m_uno = web.getcookie_secure('user')
		m_name = 'user'
	else:
		return web.redirect('/signin?message=failed')

	if m_uno:
		#
		# 成功
		#
		m_uno = int(m_uno)
		web.uno = m_uno
		web.user_icon = matsuoka_func.get_icon(web,web.uno)
		web.ano = matsuoka_func.from_uno_getdb_ano(web,web.uno,False)
		web.setcookie_secure(m_name, str(m_uno), maxage=1800)
	else:
		#
		# 失敗
		#
		return web.redirect('/signin?message=failed')
	# --------------------------------------------------------------------------
	#
	# 例えば /user/foobar にアクセスがあった場合に次の２行と同等の処理を行う
	# import user.user_foobar
	# return user.user_foobar.main(web, build)
	#
	if web.path.startswith('/user'):
		module = web.path[len('/user/'):].replace('.', '_')
		module = 'user.user_' + (module or 'index')
		try:
			return importlib.import_module(module).main(web, build)
		except ImportError as e:
			web.log(e, 'red')
		#
		# 404 Not Found
		#
		web.statuscode = 404
		return web.echo()
	elif web.path.startswith('/jh'):
		module = web.path[len('/jh/'):].replace('.', '_')
		module = 'jh.jh_' + (module or 'index')
		try:
			return importlib.import_module(module).main(web, build)
		except ImportError as e:
			web.log(e, 'red')
		#
		# 404 Not Found
		#
		web.statuscode = 404
		return web.echo()
	elif web.path.startswith('/growth'):
		module = web.path[len('/growth/'):].replace('.', '_')

		module = 'growth.growth_' + (module or 'index')
		web.log(module,"RED")
		try:
			return importlib.import_module(module).main(web, build)
		except ImportError as e:
			web.log(e, 'red')
		#
		# 404 Not Found
		#
		web.statuscode = 404
		return web.echo()
