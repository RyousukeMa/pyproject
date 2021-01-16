# -*- coding: utf-8 -*-

import importlib

import blossom

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
	if web.cookie('user'):
		#
		# cookie の 'user' の値を '.' の前後で分割する
		#
		#uno, passhash = web.cookie('user').split('.', 1)
		uno = web.cookie('user')
		sql = """
		SELECT `passhash`
		FROM `user`
		WHERE `uno` = %(uno)s;"""
		params = {
			'uno':uno,
		}
		passhash = web.db.exe(sql, params=params, key=True)

		if passhash:
			#
			# 誰がサインインしたのか uno を記録する
			#
			web.uno = int(uno)
	#
	# 認証失敗 → 認証ページへ転送
	#
	if not web.uno:
		return web.redirect('/signin?message=failed')
	# --------------------------------------------------------------------------
	#
	# 例えば /mypage/foobar にアクセスがあった場合に次の２行と同等の処理を行う
	# import mypage.mypage_foobar
	# return mypage.mypage_foobar.main(web, build)
	#
	module = 'mypage.mypage_' + (web.path[len('/mypage/'):] or 'index')
	try:
		return importlib.import_module(module).main(web, build)
	except ImportError as e:
		web.log(e, 'red')
	#
	# 404 Not Found
	#
	web.statuscode = 404
	return web.echo()
