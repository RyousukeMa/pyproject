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
	#
	#
	if web.get('valuer'):
		vuno = web.get('valuer')
		uno = web.uno
	vuno = 4
	uno = 2

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
	if userjob:
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


	else:
		userjob   = "None"
		found_job = "None"


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

	sql = """
	SELECT `role`.`uno`, `vuno`, `json`, CONCAT(name0, name1) AS fullname, `role`.`time4`,`role`.`deleted`
	FROM `role`
	LEFT JOIN `user`
	ON `user`.`uno` = `role`.`vuno`
	WHERE (`role`.`uno`, `time4`) IN (
		SELECT `uno`, max(`time4`) AS `time4`
		FROM `role`
		WHERE `vuno` = %(vuno)s
		GROUP BY `vuno`
		)
	AND `role`.`deleted` = 0
	AND NOT `user`.`uno` = %(vuno)s"""
	params = {
		'vuno':vuno
	}
	alluser_valuer = web.db.exe(sql, params=params)
	web.log(alluser_valuer,"Blue")
	with open("jsondate/rg_q.json", "r", encoding="utf-8") as rg_qjson:
		rg_text = json.load(rg_qjson)
	with open("jsondate/rs_q.json", "r", encoding="utf-8") as rs_qjson:
		rs_text = json.load(rs_qjson)
	with open("jsondate/v_q.json", "r", encoding="utf-8") as v_qjson:
		v_text = json.load(v_qjson)

	#
	# 得点の集計
	#
	point = []
	for k1, v1 in enumerate(alluser_valuer):
		rg_pointtime = []	# ゼネラリストの各ポイントと評価時間
		rs_pointtime = []	# スペシャリストの " "
		v_pointtime  = [] 	# バリューの " "
		gs_pointtax  = 0    # ゼネラリストとスペシャリストの合計点
		rg_pointtax  = 0    # ゼネラリストの合計点
		rs_pointtax  = 0	# スペシャリストの " "
		v_pointtax   = 0	# バリューの " "
		#
		# ゼネラリスト
		#
		for k2, v2 in rg_text.items():
			if rg_text[k2]['invalid'] == str(0):
				continue
			try:
				on_answer = json.loads(v1['json'])
			except:
				on_answer = ""
			if rg_text[k2]['id'] in on_answer:
				rg_pointtax += int(rg_text[k2]['point'])
				gs_pointtax += int(rg_text[k2]['point'])
		#
		# スペシャリスト
		#
		for k2, v2 in rs_text.items():
			if rs_text[k2]['invalid'] == str(0):
				continue
			try:
				on_answer = json.loads(v1['json'])
			except:
				on_answer = ""
			if rs_text[k2]['id'] in on_answer:
				rs_pointtax += int(rs_text[k2]['point'])
				gs_pointtax += int(rs_text[k2]['point'])
		#
		# バリュー
		#
		for k2, v2 in v_text.items():
			if v_text[k2]['invalid'] == str(0):
				continue
			try:
				on_answer = json.loads(v1['json'])
			except:
				on_answer = ""
			if v_text[k2]['id'] in on_answer:
				v_pointtax += int(v_text[k2]['point'])
		time = datetime.datetime.fromtimestamp(
						v1['time4']).strftime("%Y/%m/%d")
		point.append({
			'fullname'   :v1['fullname'],
			'rg_pointtax':rg_pointtax,
			'rs_pointtax':rs_pointtax,
			'v_pointtax' :v_pointtax,
			'gs_pointtax':gs_pointtax,
			'time'       :time,
					})

	local = {
		'point'      :point,
		'userjob'    :userjob,
		'involvement':involvement,
		'found_job'  :found_job,
		'user_icon'  :web.user_icon
	}
	return build(web, local,'/user/user.index.html')
