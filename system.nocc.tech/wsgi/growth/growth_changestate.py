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
	# 繋がりのあるユーザー一覧
	#
	sql1 = """
	SELECT CONCAT(name0, name1) AS `fullname`, `asname`, `depth`, `vuno`,
	`involvement`.`uno`, `involvement`.`time4`,`involvement`.`deleted`
	FROM `user`
	LEFT JOIN `involvement`
	ON `user`.`uno` = `involvement`.`vuno`
	LEFT JOIN `assign` USING (`asno`)
	WHERE (`involvement`.`uno`,`involvement`.`time4`) IN (
		SELECT `uno`,MAX(`time4`) AS `time4`
		FROM `involvement`
		WHERE `uno` = %(uno)s
	"""
	sql2 = """
		GROUP BY `uno`
	)
	AND `user`.`deleted` = 0
	ORDER BY `depth` DESC
	LIMIT 0,20
	"""
	sql = sql1 + sql2
	params = {
		'uno':web.uno
	}
	involvement_users = web.db.exe(sql, params=params)
	#
	# 全てのユーザー(検索)
	#
	if web.get('q'):
		web.log("OK","RED")
		search_word = web.get('q')
		sql3 = """
			GROUP BY `uno`
		)
		AND (CONCAT(`fullname`, `asname`, `depth`)
		LIKE %(search)s)
		LIMIT 0,20
		"""
		sql1 += sql3
		params = {
			'search_word':str('%' + search_word + '%'),
		}
	else:
		#
		# 全てのユーザー
		#
		search_word = ""
		sql2 = """
			GROUP BY `uno`
		) AND `vuno` = %(uno)s
		AND `user`.`deleted` = 0
		LIMIT 0,20
		"""
		sql1 += sql2
	allusers = web.db.exe(sql1, params=params)
	#
	# 画像の取得
	#
	for k, v in enumerate(involvement_users):
		icon          = matsuoka_func.get_icon(web,v['uno'])
		v['icon']     = icon['has_icon']
		v['icon_uno'] = icon['uno']
	for k, v in enumerate(allusers):
		icon          = matsuoka_func.get_icon(web,v['uno'])
		v['icon']     = icon['has_icon']
		v['icon_uno'] = icon['uno']
		if v['deleted'] == 0:
			del allusers[k]['deleted']

	local = {
		'allusers'         :allusers,
		'involvement_users':involvement_users,
		'user_icon'        :web.user_icon,
	}
	return build(web, local, \
		'/growth/' + web.path.replace('/', '.')[1:] + '.html')
