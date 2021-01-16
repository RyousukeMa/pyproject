# -*- coding: utf-8 -*-

import blossom
import re

#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# userの取得
	#
	# 画像の有無を確かめる
	sql = """
		SELECT `uno`
		FROM `icon`
		WHERE `uno` = %(uno)s
		"""
	params = {
			'uno':web.uno,
		}
	uno_image = web.db.exe(sql, params=params)

	#
	# 有無に応じてクエリを変更
	#
	if uno_image:
		sql = """
			SELECT *
			FROM `user`
			INNER JOIN `icon`
			ON `icon`.`uno` = `user`.`uno`
			WHERE `user`.`uno` = %(uno)s;"""
		params = {
			'uno':web.uno,
		}
		user = web.db.exe(sql ,params=params ,key=True)
		#
		# 画像はbool型に変換
		#
		user ={
			'uno'     :user['uno'],
			'name0'   :user['name0'],
			'name1'   :user['name1'],
			'name2'   :user['name2'],
			'name3'   :user['name3'],
			'mailaddr':user['mailaddr'],
			'has_icon':bool(user['uno']),
		}
	else:
		sql = """
			SELECT *
			FROM `user`
			WHERE `uno` = %(uno)s;"""
		params = {
			'uno':web.uno,
		}
		user = web.db.exe(sql ,params=params ,key=True)

	local = {
 		'user':user
	}

	#
	# 内容を変更した場合
	#
	if web.environ('REQUEST_METHOD') == 'POST':
		#
		# パスワードの変更（メール送信）
		#
		if web.post('passreset'):
			web.setcookie_secure('user', str(web.uno), maxage=1800)
			hash = web.cookie('user')
			web.log(web.cookie('user'),"RED")
			txt = blossom.read('../template/eml/open.passremind.eml')
			txt = txt % {
			'mailaddr' :'matsuokagb@gmail.com',
			'HTTP_HOST':web._environ['HTTP_HOST'],
			'uno'      :web.uno,
			'hash'     :hash
			}
			web.log(txt, 'purple')
			result = blossom.Mail.send(txt)
			web.log(result,"blue")
			return build(web, local,'/user/' \
		 		+ web.path.replace('/', '.')[1:] + '.html')

		name0  = web.post('name0')
		name1  = web.post('name1')
		name2  = web.post('name2')
		name3  = web.post('name3')
		password1 = web.post('password1')
		password2 = web.post('password2')
		mailaddr = web.post('mailaddr')

		sql = """
		UPDATE `user`
		SET `name0` = %(name0)s ,`name1` = %(name1)s ,`name2` = %(name2)s,
		`name3` = %(name3)s ,`mailaddr` = %(mailaddr)s ,
		WHERE `uno` = %(uno)s;"""

		params = {
			'name0'   :name0,
			'name1'   :name1,
			'name2'   :name2,
			'name3'   :name3,
			'mailaddr':mailaddr,
			'uno':web.uno,
		}
		web.db.exe(sql, params=params)

		#
		# 画像の更新
		image = web.post('image')
		web.log(image,"RED")
		if not image['filename'] == None:
			icon = image['body']
			icon = icon.hex()
			if uno_image:
				sql = """
				UPDATE `icon`
				SET `img` =  0x""" + icon + """
				WHERE `uno` = %(uno)s;"""
				params = {
					'uno':uno,
				}
				web.db.exe(sql, params=params)
			else:
				sql = """
				INSERT INTO `icon` (`uno`,`img`)
				VALUES (%(uno)s, 0x""" + icon + ");"""
				params = {
					'uno':uno,
				}
				web.db.exe(sql, params=params, key=True)

	return build(web, local,'/user/user.index.html')
