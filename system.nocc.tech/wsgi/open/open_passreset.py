# -*- coding: utf-8 -*-

import blossom
import re
import matsuoka_func
#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# urlの妥当性の確認
	#
	#if not web.get('type'):
	#	return web.redirect('/open/passremind')
	u = re.match(r'(.+)\.([0-9]+)', web.get('type'))
	uno = u.group(2)
	unohash = u.group(1)
	uno16 = blossom.md5(uno, 16)
	#
	# クッキーの値に妥当性がないとメールアドレスの入力画面へ戻る
	#
	if uno16 != unohash:
		return web.redirect('/passremind')

	if web.post('pass1'):
		pass1 = web.post('pass1')
		pass2 = web.post('pass2')
		#
		# バリテーションチェック、入力内容に問題がなければmassageに"notvalidator"が入る
		# 問題があればエラー内容がmassageに入る
		#
		massage = matsuoka_func.pass_validator(pass1, pass2, varchar=8)
		if not massage == "notvalidator":
			return web.redirect('/signin?message=' + str(massage))

		#
		# パスワードの再設定
		#
		passhash16 = blossom.md5(pass1, 16)
		sql = """
			UPDATE `user`
			SET `passhash` = 0x""" + passhash16 + """
			WHERE `uno` = %(uno)s;"""
		params = {
			'uno':uno
		}
		web.db.exe(sql, params=params, key=True)


		return web.redirect('/signin?message=passwordChanged')
	local = {
	}
	return build(web, local,'/open/open.passreset.html')
