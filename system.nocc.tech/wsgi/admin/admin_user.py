# -*- coding: utf-8 -*-

import blossom
import re
import matsuoka_func
import datetime
#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	get_uno = web.get('uno')
	#
	# ログイン中のユーザーの画像を取得
	#
	login_user_icon = matsuoka_func.get_icon(web,web.uno)

	#
	# エラー時の送信メッセージを準備
	#
	message = '?uno=' + str(get_uno) + '&mode=show'

	#
	# userの更新
	#
	if web.environ('REQUEST_METHOD') == 'POST':
		#
		#パスワードの再設定
		#
		if web.post('passreset'):
			web.setcookie_secure('user', str(get_uno), maxage=1800)
			hash = web.cookie('user')
			web.log(web.cookie('user'),"RED")
			txt = blossom.read('../template/eml/open.passremind.eml')
			txt = txt % {
			'mailaddr' :'matsuokagb@gmail.com',
			'HTTP_HOST':web._environ['HTTP_HOST'],
			'uno'      :get_uno,
			'hash'     :hash
			}
			web.log(txt, 'purple')
			result = blossom.Mail.send(txt)
			web.log(result,"blue")

			return web.redirect('/admin/users?message12=passreset')

		#
		# 登録内容の変更
		#
		asno     = web.post('assign')
		name0    = web.post('name0')
		name1    = web.post('name1')
		#
		# カタカナ以外が入力されているとFalseが帰ってくる
		#
		name2    = matsuoka_func.katakana_validator(web.post('name2'))
		name3    = matsuoka_func.katakana_validator(web.post('name3'))

		#
		# その結果メッセージが送信される
		#
		if name2 == False or name3 == False:
			message += "&message1=name_notkatakana"

		admin    = web.post('admin', 0)
		mailaddr = web.post('mailaddr')
		gender   = web.post('gender', 0)

		#
		# 8桁の数字か確認する、違うならメッセージ送信
		#
		if len(web.post('birthday')) != 8:
				message += "&message2=birthday_notlen8"
		if not re.match(r'[0-9]+', web.post('birthday')):
				message += "&message3=birthday_notnumeric"

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
		birthday = datetime.datetime(int(bayear),int(bamonth),int(baday),0,0).strftime('%s')
		joinday  = datetime.datetime(int(jyear),int(jmonth),int(jday),0,0).strftime('%s')

		#
		# 画像
		#
		icon = web.post('icon')
		#
		# エラーがあればまとめて送信
		#
		if re.match('.+&message.+' ,message):
			return web.redirect('/admin/user' + str(message))

		sql = """
		UPDATE `user`
		SET `name0` = %(name0)s ,`name1` = %(name1)s , `name2` = %(name2)s ,
			`name3` = %(name3)s ,`admin` = %(admin)s , `asno` = %(asno)s, `mailaddr` = %(mailaddr)s,
			`gender` = %(gender)s ,`birthday` = %(birthday)s ,`joinday` = %(joinday)s
		WHERE `uno` = %(uno)s;
		"""
		params = {
			'uno'     :get_uno,
			'name0'   :name0,
			'name1'   :name1,
			'name2'   :name2,
			'name3'   :name3,
			'asno'    :asno,
			'admin'   :admin,
			'mailaddr':mailaddr,
			'gender'  :gender,
			'birthday':birthday,
			'joinday' :joinday,
		}
		web.db.exe(sql, params=params, key=False)

		sql = """
		INSERT INTO `icon`
		SET `name0` = %(name0)s ,`name1` = %(name1)s , `name2` = %(name2)s ,
			`name3` = %(name3)s ,`admin` = %(admin)s , `asno` = %(asno)s, `mailaddr` = %(mailaddr)s,
			`gender` = %(gender)s ,`birthday` = %(birthday)s ,`joinday` = %(joinday)s
		WHERE `uno` = %(uno)s;
		"""

		return web.redirect('/admin/user?mode=show&uno=' + str(get_uno) + '&message4=change_user')

	#
	# admin.usersで名前をクリックした場合
	#
	if web.get('mode') == 'show':
		#
		# 画面の仕様が固まり切るまで [*] にしておく
		#
		sql = """
		SELECT *
		FROM `user`
		LEFT JOIN `assign` USING (`asno`)
		WHERE `uno` = %(uno)s
		"""
		params = {
			'uno':get_uno,
		}
		user = web.db.exe(sql, params=params, key=True)
		user['birthday'] = datetime.datetime.fromtimestamp(
						int(user['birthday'])).strftime("%Y%m%d")
		user['joinday']  = datetime.datetime.fromtimestamp(
						int(user['joinday'])).strftime("%Y%m%d")

		sql = """
		SELECT `asno`,`asname`
		FROM `assign`
		WHERE `ano` = %(ano)s
		AND NOT `asno` = %(asno)s
		"""
		params = {
			'ano' :user['ano'],
			'asno':user['asno']
		}
		assign = web.db.exe(sql, params=params, key=False)

		#
		# 選択したuserのアイコン
		#
		user_icon = matsuoka_func.get_icon(web,get_uno)

		local = {
			'user'     		 :user,
			'assign'		 :assign,
			'user_icon'		 :user_icon,
			'login_user_icon':login_user_icon,
		}

		return build(web, local,'/admin/' \
 			+ web.path.replace('/', '.')[1:] + '.html')

	#
	# 削除ボタンを押した場合
	#
	if web.get('mode') == 'delete':
		if web.uno == int(get_uno):
			return web.redirect('/admin/users?message11=thisuser')
		sql = """
		UPDATE `user`
		SET `deleted` = '1'
		WHERE `uno` = %(uno)s;
		"""
		params = {
			'uno':get_uno,
		}
		#
		# 削除を実行
		#
		web.db.exe(sql, params=params, key=False)
		return web.redirect('/admin/users?message7=delete_user')

	#
	# 復帰ボタンを押した場合
	#
	if web.get('mode') == 'revive':
		if web.uno == int(get_uno):
			return web.redirect('/admin/users?message11=thisuser')
		sql = """
		UPDATE `user`
		SET `deleted` = '0'
		WHERE `uno` = %(uno)s;
		"""
		params = {
			'uno':get_uno,
		}

		#
		# 復帰を実行
		#
		web.db.exe(sql, params=params, key=False)
		return web.redirect('/admin/users?message8=rivive_user')

	return web.redirect('/admin/users')
