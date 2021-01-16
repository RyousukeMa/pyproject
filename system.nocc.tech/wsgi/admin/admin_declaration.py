# -*- coding: utf-8 -*-

import blossom
import re
import matsuoka_func
import datetime
import json
#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# メモの追加
	#
	if web.get("objectionchange"):
		#
		# 状態を更新
		#
		sql = """
		UPDATE
		`significance`
		SET `state` = %(state)s
		WHERE `sno` = %(sno)s;
		"""
		params = {
			'sno'                 :int(web.get("sno")),
			'state'				  :int(web.get("memostate")),
		}
		web.db.exe(sql, params=params)
		#
		# メモを更新
		#
		sql = """
		INSERT INTO
		`significance_memo`
		VALUES
		(%(sno)s, %(admin_uno)s, %(memo)s, %(memo_time4)s, %(memocreated_snostate)s)
		"""
		params = {
			'sno'                 :int(web.get("sno")),
			'admin_uno'			  :web.uno,
			'memo'                :str(web.get("memo")),
			'memo_time4'          :web.now4,
			'memocreated_snostate':web.get("memostate"),
		}
		web.db.exe(sql, params=params)
		#
		# リダイレクト用にunoを取得
		#
		sql = """
		SELECT `uno`
		FROM `significance`
		WHERE `sno` = %(sno)s;
		"""
		params = {
			'sno'                 :int(web.get("sno")),
		}
		uno = web.db.exe(sql, params=params, key=True)
		joinurl = 'details=' + str(uno) +'&message1=changememo'
		return web.redirect('/admin/valueweight?details=' + str(uno) + '&message1=changememo')

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
		'uno':web.get("from")
	}
	user = web.db.exe(sql, params=params)

	sql = """
	SELECT CONCAT(name0, name1) AS `fullname`, `asname`,
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
		'uno':web.get("from")
	}

	involvement_users = web.db.exe(sql, params=params)

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


	sql = """
	SELECT
	CONCAT(name0,name1) AS fullname,
	`significance_text`,
	`significance_time4`,
	`significance_statetext`.`state`,
	`text` AS `state_text`,
	`significance`.`sno`
	FROM `significance`
	LEFT JOIN `significance_statetext`
	ON `significance`.`state` =  `significance_statetext`.`state`
	LEFT JOIN `user`
	ON `user`.`uno` =  `significance`.`vuno`
	WHERE `significance`.`sno` = %(sno)s
	"""
	params = {
		'sno':web.get("sno"),
	}
	significance = web.db.exe(sql,params=params, key=True)
	significance['significance_time4'] = datetime.datetime.fromtimestamp(int(v['time4'])).strftime('%Y-%m-%d')

	sql = """
	SELECT SQL_CALC_FOUND_ROWS *
	FROM `significance`
	LEFT JOIN `significance_memo`
	ON `significance`.`sno` =  `significance_memo`.`sno`
	LEFT JOIN `user`
	ON `significance_memo`.`admin_uno` =  `user`.`uno`
	LEFT JOIN `significance_statetext`
	ON `significance_memo`.`memocreated_snostate` =  `significance_statetext`.`state`
	WHERE `significance`.`sno` = %(sno)s
	AND `user`.`deleted`  =0"""
	params = {
		'sno':web.get("sno"),
	}
	found = web.db.exe('SELECT FOUND_ROWS();',params=params, key=True)


	if found != 0:
		significance_memo = web.db.exe(sql, params=params)
		for k, v in enumerate(significance_memo):
			v['time4'] = datetime.datetime.fromtimestamp(int(v['time4'])).strftime('%Y-%m-%d')
	else:
		significance_memo = "NONE"

	sql = """
	SELECT *
	FROM `significance_statetext`
	WHERE 1"""
	state_text = web.db.exe(sql)

	local = {
		'user'			   :user,
		'involvement_users':involvement_users,
		'significance'      :significance,
		'significance_memo' :significance_memo,
		'state_text'        :state_text,
		'user_icon'         :web.user_icon
	}
	return build(web, local, \
		'/admin/' + web.path.replace('/', '.')[1:] + '.html')
