# -*- coding: utf-8 -*-

import blossom
import re
import matsuoka_func
import tool
import json
import datetime
import matsuoka_func
#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# 選択したuser情報
	#
	if web.get("details"):
		#
		# user情報
		#
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
		WHERE `user`.uno = %(uno)s
		AND `user`.`deleted`  = 0;"""
		params = {
			'uno':web.get("details"),
		}
		user = web.db.exe(sql, params=params)
		#
		# そのuserの関わり合い
		#
		sql1 = """
		SELECT SQL_CALC_FOUND_ROWS CONCAT(name0, name1) AS `fullname`, `asname`,
		`depth` ,`vuno`,`involvement`.`uno`, `involvement`.`time4`,
		`involvement`.`deleted`
		FROM `user`
		LEFT JOIN `involvement`
		ON `user`.`uno` = `involvement`.`vuno`
		LEFT JOIN `assign` USING (`asno`)
		WHERE (`involvement`.`uno`,`involvement`.`time4`) IN (
			SELECT `uno`,MAX(`time4`) AS `time4`
			FROM `involvement`
			WHERE `uno` = %(uno)s
			AND NOT `depth` = 0
			GROUP BY `vuno`
		) AND NOT `depth` = 0
		AND NOT `vuno` = %(uno)s
		ORDER BY `depth` DESC"""
		params = {
			'uno':web.get("details")
		}
		involvement_users = web.db.exe(sql1, params=params)
		#
		# 関わり合いがない場合、involvement_usersを送信しない
		#
		if not involvement_users:
			local = {
				'user'				 :user,
				'user_icon'          :web.user_icon,
				}
			return build(web, local, \
			'/admin/' + web.path.replace('/', '.')[1:] + '.html')
		#
		# 100分率用に全員のdepthを合計
		#
		sumdepth = 0
		for k, v in enumerate(involvement_users):
			sumdepth += v['depth']
		#
		# それぞれのdepthの割合を求める
		# 同時にvunoの画像も取得
		#
		for k, v in enumerate(involvement_users):
			if v['depth'] == 0:
				continue
			v['parcent']  = round((v['depth'] / sumdepth* 100),1)
			icon          = matsuoka_func.get_icon(web,int(v['uno']))
			v['icon']     = icon['has_icon']
			v['icon_uno'] = icon['uno']

		#
		# 異議
		#
		sql = """
		SELECT *
		FROM `significance`
		LEFT JOIN `user`
		ON `user`.`uno` =  `significance`.`vuno`
		LEFT JOIN `icon`
		ON `icon`.`uno` =  `user`.`uno`
		LEFT JOIN `significance_statetext`
		ON `significance`.`state` =  `significance_statetext`.`state`
		WHERE `significance`.`uno` = %(uno)s
		AND `user`.`deleted`  =0"""
		params = {
			'uno':web.get("details"),
		}
		significance = web.db.exe(sql, params=params)
		#
		# 異議が存在しなければスルー
		#
		if not significance:
			local = {
				'user'				 :user,
				'involvement_users'  :involvement_users,
				'user_icon'          :web.user_icon,
				}
			return build(web, local, \
			'/admin/' + web.path.replace('/', '.')[1:] + '.html')
		#
		# timestampをUNIXに
		#
		for k, v in enumerate(significance):
			v['time4'] = datetime.datetime.fromtimestamp(int(v['time4'])).strftime('%Y-%m-%d')

		local = {
			'user'				 :user,
			'involvement_users'  :involvement_users,
			'significance'  	 :significance,
			'user_icon'          :web.user_icon,
		}
		return build(web, local, \
			'/admin/' + web.path.replace('/', '.')[1:] + '.html')

	#
	# 初期画面
	#
	# ページリング
	#
	if web.get('page'):
		page = web.get('page')
		page = int(page) - int(1)
	else:
		page = 0

	length = 10
	sql_order = "CONCAT(name2, name3) ASC"
	#
	# 一覧表示(初期表示、及び検索欄が空白のまま検索した時)、除名リスト(deleted=1)も取得
	#
	if not web.get('q') or web.get('q') == "":
		search_word = ""
		sql = """
		SELECT SQL_CALC_FOUND_ROWS `user`.`uno`, `user`.`name0`,
		`user`.`name1`, `user`.`name2`, `user`.`name3`, `user`.`passhash`,
		`user`.`created4`, `assign`.`asname`,
		`icon`.`uno` AS `has_icon`,
		`significance`.`state`
		FROM `user`
		LEFT JOIN `significance`
		ON `significance`.`uno` =  `user`.`uno`
		LEFT JOIN `assign`
		ON `user`.`asno` = `assign`.`asno`
		LEFT JOIN `icon`
		ON `icon`.`uno` =  `user`.`uno`
		WHERE `user`.`deleted`  = 0
		AND `user`.`ano` = %(ano)s
		AND `user`.`ano` = %(ano)s
		ORDER BY """ + sql_order + """
		LIMIT """ + str(length*page) + ", " + str(length) + ";"
		params = {
		'ano'    :web.ano,
		}
		users = web.db.exe(sql, params=params, key=False)
		users_found =  web.db.exe('SELECT FOUND_ROWS();',params=params, key=True)
	#
	# 検索結果表示
	#
	if web.get('q'):
		search_word = web.get('q')
		sql = """
		SELECT SQL_CALC_FOUND_ROWS `user`.`uno`, `user`.`name0`,
		`user`.`name1`,`user`.`name2`, `user`.`name3`, `user`.`passhash`,
		`user`.`created4`, `assign`.`asname`,
		`icon`.`uno` AS `has_icon`
		`significance`.`sno`
		FROM `user`
		LEFT JOIN `significance`
		ON `significance`.`uno` =  `user`.`uno`
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
			'ano':web.ano,
			'search':str('%' + search_word + '%'),
			}
		users = web.db.exe(sql, params=params, key=False)
		users_found =  web.db.exe('SELECT FOUND_ROWS();',params=params, key=True)
	#
	# 画像とタイムスタンプの変換
	#
	for i, user in enumerate(users):
		umode = blossom.md5(user['uno'], 16)
		created4 = user['created4']
		user['created4'] = datetime.date.fromtimestamp(created4)
		#web.log(user['state'],"RED")
		web.log(user['state'],"RED")
		if user['state'] == 4 or user['state'] == None:
			users[i] = {
				'uno'     :user['uno'],
				'umode'   :umode,
				'name0'   :user['name0'],
				'name1'   :user['name1'],
				'name2'   :user['name2'],
				'name3'   :user['name3'],
				'created4':user['created4'],
				'asname'  :user['asname'],
				'state'   :bool(False),
				'has_icon':bool(user['has_icon'])
			}
		else:
			users[i] = {
				'uno'     :user['uno'],
				'umode'   :umode,
				'name0'   :user['name0'],
				'name1'   :user['name1'],
				'name2'   :user['name2'],
				'name3'   :user['name3'],
				'created4':user['created4'],
				'asname'  :user['asname'],
				'state'   :bool(True),
				'has_icon':bool(user['has_icon'])
			}

	#
	# pagenav
	#
	if web.environ("SERVER_NAME") == "system.nocc.tech":
		web.url =  "https://system.nocc.tech/admin/users"
	else:
		web.url =  "https://design.nocc.tech/admin/users"
	pagenav = blossom.pagenav(users_found/length, page)
	for i, v in enumerate(pagenav):
		pagenav[i]['href'] = web.urljoin([{'page':v['i'], 'message':None}])

	local = {
		'user_icon'      :web.user_icon,
 		'users'          :users,
		'pagenav'		 :pagenav,
		'search_word'    :search_word,
	}
	return build(web, local,'/admin/' \
		+ web.path.replace('/', '.')[1:] + '.html')
