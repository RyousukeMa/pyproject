# -*- coding: utf-8 -*-

import blossom
import re
import matsuoka_func
import datetime
import json
import matsuoka_func
#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	#
	#
	#if web.get('valuer'):
	#	vuno = web.get('valuer')
	#	uno = web.uno
	vuno = 4
	uno = 2

	if web.get('declaration'):
		Auser = matsuoka_func.get_user(web,web.uno)
		Buser = matsuoka_func.get_user(web,vuno)
		local = {
			'Auser'   :Auser,
			'Buser'   :Buser,
			'text'    :str(web.get('declaration')),
			'user_icon'  :web.user_icon
		}
		return build(web, local,'/user/user.weight.html')

	if web.get('q'):
		text = web.get('q')
		uno  = web.get('tgt')
		vuno = web.get('to')

		sql = """
		SELECT MAX(`time4`) AS `time4`
		FROM `involvement`
		WHERE `vuno` = %(vuno)s
		AND `uno` = %(uno)s
		AND `deleted` = 0
		LIMIT 1
		"""
		params = {
			'uno' : uno,
			'vuno':vuno,
		}
		time4 = web.db.exe(sql, params=params, key=False)
		nowtime = web.now4
		sql1 = """
		INSERT INTO `significance`
		(`uno`, `vuno`, `time4`, `significance_text`, `significance_time4`, `state`)
		VALUES (%(uno)s, %(vuno)s, %(time4)s, %(text)s, %(nowtime)s, 0);
		"""
		sql2  ="""
		INSERT INTO `significance_memo`
		(`memo`, `memo_time4`, `memocreated_snostate`)
		VALUES (%(text)s, %(nowtime)s, 0);
		"""
		params = {
			'uno'    :uno,
			'vuno'   :vuno,
			'time4'  :time4,
			'text'   :str(text),
			'nowtime':nowtime
		}
		web.db.exe(sql1, params=params)
		web.db.exe(sql2, params=params)
		return web.redirect('/user/weight')


	sql = """
	SELECT *
	FROM `user`
	LEFT JOIN `assign` USING (`asno`)
	LEFT JOIN `bind_user_job` USING (`uno`)
	LEFT JOIN `job` USING (`jno`)
	WHERE `user`.`uno` = %(vuno)s
	GROUP BY `jno`
	"""
	params = {
		'vuno':vuno,
	}
	userjob = web.db.exe(sql, params=params)
	userjob[0]['start'] = 'start'
	userjob[0]['updated4'] = str(datetime.datetime.fromtimestamp(
							userjob[0]['updated4']).strftime("%Y/%m/%d"))

	found_job = len(userjob)

	sql = """
	SELECT SQL_CALC_FOUND_ROWS *
	FROM `bind_user_job`
	WHERE jno = %(jno)s
	"""
	for k, v in enumerate(userjob):
		params = {
			'jno':v['jno']
		}
		v['havefound'] =  web.db.exe('SELECT FOUND_ROWS();',params=params, key=True)
		v['jupdated4'] = str(datetime.datetime.fromtimestamp(
								v['job.updated4']).strftime("%Y/%m/%d"))

	sql = """
	SELECT CONCAT(name0, name1) AS `fullname`, `asname`,
	`depth` ,`vuno`,`involvement`.`uno`, `involvement`.`time4`,
	`involvement`.`deleted`
	FROM `user`
	LEFT JOIN `involvement`
	ON `user`.`uno` = `involvement`.`uno`
	LEFT JOIN `assign` USING (`asno`)
	WHERE (`involvement`.`uno`,`involvement`.`time4`) IN (
		SELECT `uno`,MAX(`time4`) AS `time4`
		FROM `involvement`
		WHERE `vuno` = %(vuno)s
		AND `deleted` = 0
		GROUP BY `uno`
	) AND `involvement`.`vuno` = %(vuno)s
	AND `involvement`.`deleted` = 0
	AND NOT `user`.`uno` = %(vuno)s"""
	params = {
		'vuno':vuno,
	}
	involvement = web.db.exe(sql, params=params)

	if involvement:
		#
		# 100分率用に全員のdepthを合計
		#
		sumdepth = 0
		for k, v in enumerate(involvement):
			if v['deleted'] == 0:
				sumdepth += v['depth']
		#
		# involvementを出力用に書き換え
		#
		for k, v in enumerate(involvement):
			#
			# 画像の取得
			#
			icon = matsuoka_func.get_icon(web,v['uno'])
			v['icon']     = icon['has_icon']
			v['icon_uno'] = icon['uno']
			if v['depth'] != 0:
				v['parcent']  = round((v['depth'] / sumdepth* 100),1)
			else:
				v['parcent']  = 0

	local = {
		'userjob'    :userjob,
		'involvement':involvement,
		'found_job'  :found_job,
		'user_icon'  :web.user_icon
	}
	return build(web, local,'/user/user.weight.html')
