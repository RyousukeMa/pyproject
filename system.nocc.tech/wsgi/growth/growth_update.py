# -*- coding: utf-8 -*-

import blossom
import re
import matsuoka_func
import tool
import json
import datetime
import matsuoka_func
from operator import itemgetter

#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# updateのページで「はい」を選択すると、cookieに保存されたSQLを実行
	#
	if web.get('send'):
		#
		# 値の更新
		#
		if web.getcookie_secure('dsql'):
			dsql = web.getcookie_secure('dsql')
			web.db.exe(dsql)
			web.setcookie_secure('dsql','',maxage=0.1)
			rsql = web.getcookie_secure('rsql')
			web.db.exe(rsql)
			web.setcookie_secure('rsql','',maxage=0.1)
		return web.redirect("/growth/changestate?message=update")

	#
	# 結果の確認画面に表示する処理、postされた内容でSQLを生成しcookieに保存する
	#
	sql = """
	SELECT *
	FROM `involvement`
	LEFT JOIN `user` USING (`uno`)
	WHERE `involvement`.`deleted` = 0
	AND `involvement`.`vuno` = %(uno)s
	LIMIT 0,20
	"""
	params = {
		'uno':web.uno,
	}
	farst = web.db.exe(sql, params=params)

	d_values = {}  # depth
	r_values = {}
	sumdepth = 0
	delete_uno = []
	for k, v in web._post.items():
		if re.match(r'up([0-9]+)', k):
			#
			# 正規表現でunoとdepthを取得
			#
			u     = re.match(r'up([0-9]+)', k)
			uno   = int(u.group(1))
			#
			# 空白時はエラーをメッセージで返す
			#
			try:
				depth = int(v)
			except:
				return web.redirect("/growth/changestate?message =" \
					+ "notint")
			#
			# unoと値をdictで格納する
			#
			if uno not in d_values:
				d_values[uno] = {}
			d_values[uno] = int(depth)
			if uno not in r_values:
				r_values[uno] = {}
			r_values[uno] = int(depth)
			sumdepth += int(depth)

	#
	# depthを更新する用のパラムを生成
 	#
	for uno, v in sorted(d_values.items(), key=lambda x: x[1]):
		if d_values[uno] == 0:
			d_values[uno] = '(' + str(web.uno) + ", " + str(uno) + ", " \
	 			+ str(web.now4) + ", " + str(v) + ", '" + str(0) + "')"
		else:
			d_values[uno] = '(' + str(web.uno) + ", " + str(uno) + ", " \
 				+ str(web.now4) + ", " + str(v) + ", '" + str(0) + "')"

	for uno, v in sorted(r_values.items(), key=lambda x: x[1]):
		sql = """
		SELECT `deleted`, max(`time4`) AS `time4`,`json`
		FROM `role`
		WHERE `uno` = %(uno)s
		AND `vuno` = %(vuno)s
		"""
		params = {
			'uno':uno,
			'vuno':web.uno,
		}
		rva =  web.db.exe(sql, params=params,key=True)

		if rva:
			if r_values[uno] == 0 and rva['deleted'] == 1:
				continue
			if r_values[uno] != 0 and rva['deleted'] == 0:
				continue
			if r_values[uno] == 0:
				r_values[uno] = '(' + str(web.uno) + ", " + str(uno) + ", " \
		 			+ str(web.now4) + ", " + str(rva['json'] or "NULL") + ", '" + str(1) + "')"
			else:
				r_values[uno] = '(' + str(web.uno) + ", " + str(uno) + ", " \
		 			+ str(web.now4) + ", " + str(rva['json'] or "NULL") + ", '" + str(0) + "')"
		else:
			if r_values[uno] == 0:
				r_values[uno] = '(' + str(web.uno) + ", " + str(uno) + ", " \
		 			+ str(web.now4) + ", " + str(rva['json'] or "NULL") + ", '" + str(1) + "')"
			else:
				r_values[uno] = '(' + str(web.uno) + ", " + str(uno) + ", " \
		 			+ str(web.now4) + ", " + str(rva['json'] or "NULL") + ", '" + str(0) + "')"

	r2_values = {}
	for uno, v in r_values.items():
		if r_values[uno] == 0:
 			continue
		r2_values[uno] = r_values[uno]
	#
	# depthの更新、生成したクエリをcookieに保存
	#
	d_values = ', '.join(d_values.values())
	r_values = ', '.join(r2_values.values())
	dsql = """
	INSERT INTO `involvement`
	(uno, vuno, time4, depth, deleted)
	VALUES """ +  str(d_values) + ";"
	rsql = """
	INSERT INTO `role`
	(uno, vuno, time4, json, deleted)
	VALUES """ +  str(r_values) + ";"
	web.setcookie_secure('dsql', dsql, maxage=1800)
	web.setcookie_secure('rsql', rsql, maxage=1800)

	#
	# getを元にdepthを計算
	# 新規のユーザーや削除されたユーザーもリストに格納する
	#
	udepth = 0
	now_dpercent = {} # depth
	now_state = {}    # 登録か削除か
	for k, v in web._post.items():
		if re.match(r'up([0-9]+)', k):
			u        = re.match(r'up([0-9]+)', k)
			uno      = int(u.group(1))
			udepth   = int(v)
			#
			# unoを取得
			#
			user     = matsuoka_func.get_user(web,uno)
			if udepth == 0:
				apdict = {
						str(user['uno']):{
							'parsent':0,
							'nowdepth':udepth,
							}
						}

				statedict = {
							str(user['uno']):{
								'nowstate':0,
								}
							}

			else:
				apdict = {
						str(user['uno']):{
							'parsent':round((udepth / sumdepth* 100),1),
							'nowdepth':udepth,
							}
						}
				statedict = {
							str(user['uno']):{
								'nowstate':1,
								}
							}

			now_dpercent.update(apdict)
			now_state.update(statedict)

	#
	# ユーザー一覧
	#
	sql = """
	SELECT CONCAT(name0, name1) AS `fullname`, `asname`, `depth` ,`vuno`,`involvement`.`uno`,
	`involvement`.`time4`,`involvement`.`deleted`
	FROM `user`
	LEFT JOIN `involvement`
	ON `involvement`.`vuno` = `user`.`uno`
	LEFT JOIN `assign` USING (`asno`)
	WHERE (`involvement`.`uno`,`involvement`.`time4`) IN (
		SELECT `uno`, MAX(`time4`)
		FROM `involvement`
		WHERE `uno` = %(uno)s
		GROUP BY `uno`
	)ORDER BY `depth` DESC
	"""
	params = {
		'uno':web.uno
	}
	involvement = web.db.exe(sql, params=params)

	if involvement:
		#
		# 100分率用に全員のdepthを合計
		#
		sumdepth = 0
		for k, v in enumerate(involvement):
			if ['depth'] != 0:
				sumdepth += v['depth']
		#
		# involvementを出力用に書き換え
		#
		for k, v in enumerate(involvement):
			#
			# 画像の取得
			#
			icon = matsuoka_func.get_icon(web,v['uno'])
			#if v['depth'] == now_dpercent[str(v['vuno'])]['nowdepth']:
			#	continue
			#
			# 既に登録されているdepthを更新する時
			#
			if v['depth'] != 0 and now_state[str(v['vuno'])]['nowstate'] != 0:
				v['parcent']  = round((v['depth'] / sumdepth* 100),1)
				v['oicon']     = icon['has_icon']
				v['oicon_uno'] = icon['uno']
				v['now_icon']     = icon['has_icon']
				v['now_icon_uno'] = icon['uno']
				v['now_depth']   = now_dpercent[str(v['vuno'])]['nowdepth']
				v['now_parcent'] = now_dpercent[str(v['vuno'])]['parsent']
			#
			# 新たに登録した場合
			#
			if v['depth'] == 0 and now_state[str(v['vuno'])]['nowstate'] != 0:
				v['depth'] = '新'
				v['oicon']     = icon['has_icon']
				v['oicon_uno'] = icon['uno']
				v['now_depth']   = now_dpercent[str(v['vuno'])]['nowdepth']
				v['now_parcent'] = now_dpercent[str(v['vuno'])]['parsent']
			#
			# 未登録のままの場合
			#
			if v['depth'] == 0 and now_state[str(v['vuno'])]['nowstate'] == 0:
				involvement[k]['None'] = "None"
				continue

			#
			# 削除した場合
			#
			if v['depth'] != 0 and now_state[str(v['vuno'])]['nowstate'] == 0:
				v['now_depth'] = '削'
				v['parcent'] = now_dpercent[str(v['vuno'])]['parsent']
				v['now_icon']     = icon['has_icon']
				v['now_icon_uno'] = icon['uno']

			if type(v['now_depth']) == int:
				v['now_icon']     = icon['has_icon']
				v['now_icon_uno'] = icon['uno']

		#
		# 最終的なパーセンテージ
		#

		sumdepth = 0
		for k, v in enumerate(involvement):
			if v['depth'] == 0:
				continue
			if type(v['depth']) == int:
				sumdepth += v['depth']
		for k, v in enumerate(involvement):
			if v['depth'] == 0:
				continue
			if type(v['depth']) == int:
				v['lastp'] = round((v['depth'] / sumdepth* 100),1)

		local = {
			'involvement':involvement,
			}

		return build(web, local, \
			'/growth/' + web.path.replace('/', '.')[1:] + '.html')
