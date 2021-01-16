# -*- coding: utf-8 -*-

import blossom
import time
import matsuoka_func
#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# POST
	#
	if web.environ('REQUEST_METHOD')=='POST':
		mailaddr = web.post('mailaddr')
		params = {
			'mailaddr':mailaddr
		}
		sql = """
			SELECT `uno`,`admin`,`ano`
			FROM `user`
			WHERE `mailaddr` = %(mailaddr)s
			AND `deleted` = 0;"""
		row = web.db.exe(sql, params=params, key=True)
		uno = row['uno']

		#
		# userが存在しない場合、メールを送信しない
		#
		if not row:
			return web.redirect('/signin?message=userNotFound')

		#
		# unoのhass化
		#
		uno16 = blossom.md5(row['uno'], 16)
		hash = str(uno16) + '.' + str(uno)
		#
		# パスワード再設定ページのメールを送信
		#
		txt = blossom.read('../template/eml/open.passremind.eml')
		txt = txt % {
		'mailaddr' :'matsuokagb@gmail.com',
		'HTTP_HOST':web._environ['HTTP_HOST'],
		'hash'     :hash
		}
		result = blossom.Mail.send(txt)

		
	local = {
	}
	#return build(web, local, '/open/open.passremind.html')
	return build(web, local,'/open/' \
	 	+ web.path.replace('/', '.')[1:] + '.html')
