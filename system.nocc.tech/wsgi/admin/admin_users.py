# -*- coding: utf-8 -*-

import blossom
import re
import datetime
import matsuoka_func as mf
#
#
# main
#
#
def main(web, build):
# -----------------------------------------------------------------------------
	#
	# anoを取得
	#
	ano = mf.from_uno_getdb_ano(web,web.uno,cookie=False)
	#
	# 未処理の意義があるかどうか
	#
	#
	# ログイン中のユーザーの画像を取得
	#
	user_icon = mf.get_icon(web, web.uno)

	#
	# ページリングの設定
	#
	if web.get('userspage'):
		userspage_page = web.get('userspage')
		deletedpage_page = 0
		userspage_page = int(userspage_page) - int(1)
	elif web.get('deletedpage'):
		deletedpage_page = web.get('deletedpage')
		userspage_page = 0
		deletedpage_page = int(deletedpage_page) - int(1)
	else:
		deletedpage_page = 0
		userspage_page = 0

	length = 10
	sql_order = "CONCAT(name2, name3) ASC"

	#
	# 一覧表示(初期表示、及び検索欄が空白のまま検索した時)、除名リスト(deleted=1)も取得
	#
	if not web.get('q') or web.get('q') == "":
		for i in range(2):
			if i == 0:
				page = userspage_page
			else:
				page = deletedpage_page

			search_word = ""
			sql = """
			SELECT SQL_CALC_FOUND_ROWS `user`.`uno`, `user`.`name0`,
			`user`.`name1`, `user`.`name2`, `user`.`name3`, `user`.`passhash`,
			`user`.`created4`, `assign`.`asname`,
			`icon`.`uno` AS `has_icon`
			FROM `user`
			LEFT JOIN `assign`
			ON `user`.`asno` = `assign`.`asno`
			LEFT JOIN `icon`
			ON `icon`.`uno` =  `user`.`uno`
			WHERE `user`.`deleted`  = %(deleted)s AND `user`.`ano` = %(ano)s
			AND `user`.`ano` = %(ano)s
			ORDER BY """ + sql_order + """
			LIMIT """ + str(length*page) + ", " + str(length) + ";"
			params = {
			'ano'    :ano,
			'deleted':i
			}

			if i == 0:
				users = web.db.exe(sql, params=params, key=False)
				users_found =  web.db.exe('SELECT FOUND_ROWS();',params=params, key=True)
			else:
				deleted_users = web.db.exe(sql, params=params, key=False)
				deleted_found =  web.db.exe('SELECT FOUND_ROWS();',params=params, key=True)
	#
	# 検索結果表示
	#
	if web.get('q'):
		search_word = web.get('q')
		for i in range(2):
			if i == 0:
				page = userspage_page
			else:
				page = deletedpage_page

			sql = """
			SELECT SQL_CALC_FOUND_ROWS `user`.`uno`, `user`.`name0`,
			`user`.`name1`,`user`.`name2`, `user`.`name3`, `user`.`passhash`,
			`user`.`created4`, `assign`.`asname`,
			`icon`.`uno` AS `has_icon`
			FROM `user`
			LEFT JOIN `assign`
			ON `user`.`asno` =  `assign`.`asno`
			LEFT JOIN `icon`
			ON `icon`.`uno` =  `user`.`uno`
			WHERE (CONCAT(`user`.`name0` ,`user`.`name1` ,`user`.`name2`, `user`.`name3`)
			LIKE %(search)s)
			AND `user`.`deleted`  = %(deleted)s
			ORDER BY """ + sql_order + """
			LIMIT """ + str(length*page) + ", " + str(length) + ";"
			params = {
				'ano':ano,
				'search':str('%' + search_word + '%'),
				'deleted':i,
			}

			if i == 0:
				users = web.db.exe(sql, params=params, key=False)
				users_found =  web.db.exe('SELECT FOUND_ROWS();',params=params, key=True)
			else:
				deleted_users = web.db.exe(sql, params=params, key=False)
				deleted_found =  web.db.exe('SELECT FOUND_ROWS();',params=params, key=True)
	#
	# 画像とタイムスタンプの変換
	#
	for i, user in enumerate(users):
		umode = blossom.md5(user['uno'], 16)
		created4 = user['created4']
		user['created4'] = datetime.date.fromtimestamp(created4)
		users[i] = {
			'uno'     :user['uno'],
			'umode'   :umode,
			'name0'   :user['name0'],
			'name1'   :user['name1'],
			'name2'   :user['name2'],
			'name3'   :user['name3'],
			'created4':user['created4'],
			'asname'  :user['asname'],
			'has_icon':bool(user['has_icon'])
		}

	for i, deleted_user in enumerate(deleted_users):
		umode = blossom.md5(deleted_user, 16)
		created4 = deleted_user['created4']
		deleted_user['created4'] = datetime.date.fromtimestamp(created4)
		deleted_users[i] = {
			'uno'     :deleted_user['uno'],
			'umode'   :umode,
			'name0'   :deleted_user['name0'],
			'name1'   :deleted_user['name1'],
			'name2'   :deleted_user['name2'],
			'name3'   :deleted_user['name3'],
			'created4':deleted_user['created4'],
			'asname'  :deleted_user['asname'],
			'has_icon':bool(deleted_user['has_icon'])
		}

	#
	# pagenav
	#
	#urlをリセット
	if web.environ("SERVER_NAME") == "system.nocc.tech":
		web.url =  "https://system.nocc.tech/admin/users"
	else:
		web.url =  "https://design.nocc.tech/admin/users"
	users_pagenav = blossom.pagenav(users_found/length, userspage_page)
	deleted_pagenav = blossom.pagenav(deleted_found/length, deletedpage_page)
	for i, v in enumerate(users_pagenav):
		users_pagenav[i]['href'] = web.urljoin([{'userspage':v['i'], 'message':None}])
	for i, v in enumerate(deleted_pagenav):
		deleted_pagenav[i]['href'] = web.urljoin([{'deletedpage':v['i'], 'message':None}])

	web.log(type(users_pagenav),"RED")
	local = {
		'user_icon'      :user_icon,
 		'users'          :users,
		'deleted_users'  :deleted_users,
		'users_pagenav'  :users_pagenav,
		'deleted_pagenav':deleted_pagenav,
		'search_word'    :search_word,
	}

	return build(web, local,'/admin/' \
		+ web.path.replace('/', '.')[1:] + '.html')
