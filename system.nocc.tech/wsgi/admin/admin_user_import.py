# -*- coding: utf-8 -*-

import blossom
import re
import matsuoka_func
import random
import string
import datetime
#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# エラー時の送信メッセージを準備
	#
	message = '/admin/user.import' + '?'
	#
	# userの新規登録
	#
	if web.environ('REQUEST_METHOD')=='POST':
		asno  = web.post('assign')
		admin = web.post('admin')
		name0 = web.post('name0')
		name1 = web.post('name1')
		#
		# フルネールを生成
		#
		fullname = str(name0 + name1)
		#
		# カタカナ以外が入力されているとFalseが帰ってくる
		#
		name2 = matsuoka_func.katakana_validator(web.post('name2'))
		name3 = matsuoka_func.katakana_validator(web.post('name3'))
		#
		# その結果メッセージが送信される
		#
		if name2 == False or name3 == False:
			message += "&message1=name_notkatakana"
		#
		# 誕生日のバリテーションチェック
		#
		if len(web.post('birthday')) != 8:
			message += "&message2=birthday_notlen8"
		if not re.match(r'[0-9]+', web.post('birthday')):
			message += "&message3=birthday_notnumeric"
		#
		# エラーが存在していればリダイレクト
		#
		if re.match('.+&message.+' ,message):
			return web.redirect(str(message))

		mailaddr = web.post('mailaddr')
		letters  = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
		password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
		gender   = web.post('gender', 0)
		ba = web.post('birthday')
		bayear = ba[0:4]
		bamonth = ba[4:6]
		baday = ba[6:8]
		months = re.match('0([0-9])', bamonth)
		days = re.match('0([0-9])', baday)
		if months:
			bamonth = months.group(1)
		if days:
			baday = days.group(1)
		ba = web.post('joinday')
		jyear = ba[0:4]
		jmonth = ba[4:6]
		jday = ba[6:8]
		jmonths = re.match('0([0-9])', jmonth)
		jdays = re.match('0([0-9])', jday)
		if jmonths:
			jmonth = jmonths.group(1)
		if jdays:
			jday = jdays.group(1)

		birthday = datetime.datetime(int(bayear),int(bamonth),int(baday),0,0).strftime('%s')
		joinday  = datetime.datetime(int(jyear),int(jmonth),int(jday),0,0).strftime('%s')
		created4 = web.now4
		#
		# passwordをハッシュ化
		#
		passhash16 = blossom.md5(password, 16)
		#
		# userテーブルに登録
		#
		sql = """
		INSERT INTO
		`user` (`uno`, `ano`, `asno`, `admin`, `name0`, `name1`, `name2`,
		`name3`, `mailaddr`, `passhash`, `gender`, `birthday`, `joinday`, `created4`)
		VALUES
 		(NULL, %(ano)s, '%(asno)s', %(admin)s, %(name0)s, %(name1)s, %(name2)s,
 		%(name3)s, %(mailaddr)s, 0x""" + passhash16 + """, %(gender)s,
		%(birthday)s, %(joinday)s, %(created4)s);"""
		params = {
			'ano'		:int(web.ano),
			'asno'		:int(asno),
			'admin'		:int(admin),
			'name0'		:str(name0),
			'name1'		:str(name1),
			'name2'		:str(name2),
			'name3'		:str(name3),
			'mailaddr'	:str(mailaddr),
			'gender'	:int(gender),
			'birthday'	:int(birthday),
			'joinday'   :int(joinday),
			'created4'	:int(created4),
		}
		web.db.exe(sql, params=params,key=True)
		#
		# 登録したユーザーにメールを送信
		#
		sql = """
		SELECT `uno`
		FROM `user`
		WHERE 1
		ORDER BY `uno` ASC
		LIMIT 1
		"""
		appuseruno = web.db.exe(sql,key=True)
		uno16 = blossom.md5(appuseruno, 16)
		hash = str(uno16) + '.' + str(web.uno)
		txt = blossom.read('../template/eml/admin.import_user.eml')
		txt = txt % {
		'fullname' :fullname,
		'mailaddr' :mailaddr,
		'password' :password,
		'HTTP_HOST':web._environ['HTTP_HOST'],
		'hash'     :hash
		}
		#
		# メールが送信できなかった時の処理(demonは除く)
		#
		try:
			result = blossom.Mail.send(txt)
		except:
			sql = """
			DELETE `uno`
			FROM `user`
			WHERE `uno` = %(uno)s
			"""
			params = {
				'uno':user['uno'],
			}
			web.db.exe(sql, params=params,key=True)
			message += "&message10=mail_notsend"
			return web.redirect(str(message))

		#
		# 空のroleを作成
		# ここで作っておかないと/growth/role内で処理するのが面倒になる
		#
		sql = """
		SELECT *
		FROM `user`
		WHERE `ano` = %(ano)s"""
		params = {
			'ano':web.ano,
		}
		users = web.db.exe(sql, params=params)

		sql = """
		SELECT * FROM `user`
		ORDER BY `user`.`created4` DESC
		LIMIT 1
		"""
		user = web.db.exe(sql,key=True)

		for i,v in enumerate(users):
			#
			# 登録したばかりのユーザーをvunoとして、
			# 全てのunoに対してjsonが入っていないレコードを作成
			#
			# sql = """
			# INSERT INTO `role`
			# (`uno`, `vuno`, `time4`, `deleted`)
			# VALUES
			# (%(uno)s, %(vuno)s, %(time4)s, %(deleted)s);"""
			# params = {
			# 	'uno'    :user['uno'],
			# 	'vuno'   :users[i]['uno'],
			# 	'time4'  :web.now4,
			# 	'deleted':0,
			# }
			# web.db.exe(sql,params=params)
			# #
			# # ↑の処理だけだと、既存unoに対してのvunoは作成できるが、
			# #  逆は存在しないので改めて作る
			# #
			# sql = """
			# INSERT INTO `role`
			# (`uno`, `vuno`,`time4`,`deleted`)
			# VALUES
			# (%(vuno)s, %(uno)s, %(time4)s, %(deleted)s)
			# """
			# params = {
			# 	'uno'    :user['uno'],
			# 	'vuno'   :users[i]['uno'],
			# 	'time4'  :web.now4,
			# 	'deleted':1,
			# 	}
			# web.db.exe(sql,params=params)
			#
			# invlovmentoも同様に生成する
			#
			sql = """
			INSERT INTO `involvement`
			(`uno`, `vuno`, `time4`, `depth`, `deleted`)
			VALUES
			(%(uno)s, %(vuno)s, %(time4)s, `depth` ,%(deleted)s);"""
			params = {
				'uno'    :user['uno'],
				'vuno'   :users[i]['uno'],
				'time4'  :web.now4,
				'depth'  :0,
				'deleted':0,
			}
			web.db.exe(sql,params=params)
			if users[i]['uno'] == user['uno']:
				continue
			sql = """
			INSERT INTO `involvement`
			(`uno`, `vuno`, `time4`, `depth`, `deleted`)
			VALUES
			(%(vuno)s, %(uno)s, %(time4)s, `depth` ,%(deleted)s);"""
			params = {
				'uno'    :user['uno'],
				'vuno'   :users[i]['uno'],
				'time4'  :web.now4,
				'depth'  :0,
				'deleted':0,
			}
			web.db.exe(sql,params=params)
		#
		# 登録が成功したメッセージ
		#
		return web.redirect('/admin/users?message1=appuser')

	#
	# 部署一覧を取得して新規登録画面へ遷移
	#
	sql = """
	SELECT `asname`,`asno`
	FROM `assign`
	WHERE `ano` = %(ano)s"""
	params = {
		'ano':web.ano,
	}
	assign = web.db.exe(sql, params=params, key=False)

	local = {
		'item'     :assign,
		'user_icon':web.user_icon,
	}
	return build(web, local,'/admin/' \
	 	+ web.path.replace('/', '.')[1:] + '.html')
