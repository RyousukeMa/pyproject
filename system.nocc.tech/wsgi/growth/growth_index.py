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
	# 自分を評価する人の割合
	#
	params = {
		'uno':web.uno
	}
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
		GROUP BY `uno`
	) AND NOT `depth` = 0
	ORDER BY `depth` DESC"""
	involvement_users = web.db.exe(sql1, params=params)
	#
	# 自分が評価する人に割合
	#
	sql = """
	SELECT SQL_CALC_FOUND_ROWS CONCAT(name0, name1) AS `fullname`, `asname`,
	`depth` ,`vuno`,`involvement`.`uno`, `involvement`.`time4`,
	`involvement`.`deleted`
	FROM `user`
	LEFT JOIN `involvement`
	ON `user`.`uno` = `involvement`.`uno`
	LEFT JOIN `assign` USING (`asno`)
	WHERE (`involvement`.`vuno`,`involvement`.`time4`) IN (
		SELECT `vuno`,MAX(`time4`) AS `time4`
		FROM `involvement`
		WHERE `vuno` = %(uno)s
		AND NOT `depth` = 0
		GROUP BY `uno`
	) AND NOT `depth` = 0
	ORDER BY `depth` DESC"""
	involvement_users2 = web.db.exe(sql, params=params)
	#
	# 100分率用に全員のdepthを合計
	#
	sumdepth = 0
	for k, v in enumerate(involvement_users):
		sumdepth += v['depth']
	sumdepth2 = 0
	#for k, v in enumerate(involvement_users2):
	#	sumdepth2 += v['depth']
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
	#for k, v in enumerate(involvement_users2):
	#	if v['depth'] == 0:
	#		continue
	#	v['parcent']  = round((v['depth'] / sumdepth2* 100),1)
	#	icon          = matsuoka_func.get_icon(web,int(v['uno']))
	#	v['icon']     = icon['has_icon']
	#	v['icon_uno'] = icon['uno']

	local = {
		'involvement_users'  :involvement_users,
		'involvement_users2' :involvement_users2,
		'user_icon'          :web.user_icon,
	}
	return build(web, local, \
		'/growth/' + web.path.replace('/', '.')[1:] + '.html')
