# -*- coding: utf-8 -*-

import blossom
import re
import matsuoka_func
import tool
import json
import datetime
import sys
import pprint

#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# 質問のタイプ別にjsonを読み込み
	#
	with open("jsondate/rg_q.json", "r", encoding="utf-8") as rg_qjson:
		rg_text = json.load(rg_qjson)
	with open("jsondate/rs_q.json", "r", encoding="utf-8") as rs_qjson:
		rs_text = json.load(rs_qjson)
	with open("jsondate/v_q.json", "r", encoding="utf-8") as v_qjson:
		v_text = json.load(v_qjson)

	q_values = {}
	if web.environ('REQUEST_METHOD')=='POST':
		web.log("OK","RED")

		for k, v in web._post.items():

			#
			# 一番最初のデータがhiddenなので、無視する
			#
			if k == 'offunolist':
				continue
			notallnottingflg = 1
			#
			# 正規表現でpostnameからunoを取得
			#
			u    = re.match(r'certain([0-9]+)id(.+)', k)
			if not u:
				continue
			uno  = int(u.group(1))
			id   = u.group(2)
			#
			# unoをdictに格納
			#
			if uno not in q_values:
				q_values[uno] = {}
			q_values[uno][id] = 'on'
		#
		# values = {
		#	3:{
		#		'idaa':on,
		#		'idaa':on,
		#		'idbb':on,
		#		'idcc':on,
		#	},
		#	4:{
		#		'idaa':on,
		#		'idbb':on,
		#		'idcc':on,
		#		'idaa':on,
		#	},
		#
		time4 = web.now4
		message = "/growth/role?"
		dictend = list(q_values.items())
		#
		# 全てが０だった場合
		#
		if not notallnottingflg:
			unolist = web.post('unolist').split(',')
			if uno not in q_values:
				q_values[uno] = {}
				deleted = 0
			for uno, v in q_values.items():
				q_values[uno] = '(' + str(uno) + ", " + str(web.uno) + ", " \
	 				+ str(web.now4) + ", '" + str('NULL') + "', " + str(deleted) + ")"
				q_values = ', '.join(q_values.values())
		else:
			for uno, v in q_values.items():
				#
				# パラムを生成
 				#
				deleted = 0
				q_values[uno] = '(' + str(uno) + ", " + str(web.uno) + ", " \
 					+ str(web.now4) + ", '" + str(blossom.json(v)) + "', " + str(deleted) + ")"
					#
					# どのユーザーのどの質問が更新されたかメッセージを生成
					#
				message +=  "message=changeparam"
				q_values = ', '.join(q_values.values())

		#
		# values = "(3, '{'id1':on,'id4':on,'id5':on,'id7':on,}'),
		#			(4, '{'id1':on,'id4':on,'id5':on,'id':on,}')"
		#

		sql = """
		INSERT INTO `role`
		(uno, vuno, time4, json, deleted)
		VALUES """ +  str(q_values) + ";"
		web.db.exe(sql)
		return web.redirect(message)

	#
	# 評価するユーザーを選択し、そのユーザーを評価する
	#
	if re.match('user_select',web.environ('QUERY_STRING')):
		#
		# 選択したユーザーを取得する
		#
		values = []
		for k, v in web._get.items():
			if k == 'user_select':
				continue
			uno  = v
			values.append(uno)
		web.log(values,"RED")
		#
		# 選択した評価対象のユーザーを元にクエリを作成
		#
		# こんな感じになる
		# SELECT `uno`,`vuno`,max(`time4`) AS `time4`
		# FROM `role`
		# 	WHERE (`uno`,`vuno`) IN (
		# 	SELECT `uno`, `vuno`
		# 	FROM `role`
		# 	WHERE vuno` = 41
		#	GROUP BY `uno
		# 	)
		# AND (`uno` = 44 OR `uno` = 42 OR `uno` = 41)
		#
		#
		sql = """
		SELECT  `uno`, `vuno`, `json`, CONCAT(name0, name1) AS fullname
		FROM `role`
		LEFT JOIN `user`  USING (`uno`)
		WHERE (`uno`, `time4`) IN (
		SELECT `uno`, max(`time4`) AS `time4`
		FROM `role`
		WHERE `vuno` = %(uno)s
		GROUP BY `uno`
		) AND
 		"""
		sql += "("
		for v in values:
			sql += "`uno` = " + v + ""
			if not v == values[-1]:
				sql += " OR "
		sql += ") AND `vuno` = %(uno)s"
		params = {
			'uno':web.uno,
		}
		role_users = web.db.exe(sql, params=params)


		#
		# ユーザーが選択したユーザーの名前、htmlの記述量が減らせるので、
		# フルネームで取得
		# ↑role_usersと同時に取得しても良いが、
		# クエリが複雑になり過ぎるので別に取得
		#
		# こんな感じになる
		# SELECT CONCAT(`name0`, `name1`) AS fullname
		# FROM `user`
		# WHERE
		# `uno` = 42 OR `uno` = 43
		#
		sql = """
		SELECT CONCAT(`name0`, `name1`) AS fullname
		FROM `user`
		WHERE
		"""
		if role_users == False:
			return web.redirect('/growth/role?message1=not_selectuser')
		for i, v in enumerate(role_users):
			uno = str(role_users[i]['uno'])
			if i != 0:
				sql += " OR "
			sql += " `uno` = " + str(uno)
		fullname = web.db.exe(sql, params=params)
		#
		# 質問と回答を格納するリストを定義
		#
		rg_q = []	# ゼネラリスト質問
		rg_a = []	# ゼネラリスト質問と回答
		rs_q = []	# スペシャリスト質問
		rs_a = []	# スペシャリスト質問と回答
		v_q = []	# バリュー質問
		v_a = []	# バリュー質問と回答
		#
		# ゼネラリスト
		#
		for k1, v1 in rg_text.items():
			#
			# invalidが"1"(無効)なら処理を飛ばす
			#
			if rg_text[k1]['invalid'] == str(1):
				continue
			intext = rg_text[k1]['text']
			#
			# 一つの質問ごとに空にする
			#
			rg_q = []
			#
			# 1つの質問ごとにrole_usersをループさせる
			#
			for k2, v2 in enumerate(role_users):
				#
				# 存在しないキーを指定するとエラーになるので、tryに分岐役をさせる
				#
				try:
					on_answer = json.loads(role_users[k2]['json'])
				except:
					on_answer = ""
				if rg_text[k1]['id'] in str(on_answer):
					rg_q.append({
						'fullname':str(role_users[k2]['fullname']),
						'value'   :'on',
						'id'      :rg_text[k1]['id'],
						'uno'     :role_users[k2]['uno'],
								})

				else:
					rg_q.append({
						'fullname':str(role_users[k2]['fullname']),
						'id'      :rg_text[k1]['id'],
						'uno'     :role_users[k2]['uno'],
								})
			rg_a.append({
				'text':str(intext),
				'rg'  :rg_q,
				'id'  :rg_text[k1]['id']
						})

		#
		# スペシャリスト
		#
		for k1, v1 in rs_text.items():
			#
			# invalidが"1"(無効)なら処理を飛ばす
			#
			if rs_text[k1]['invalid'] == str(1):
				continue
			intext = rs_text[k1]['text']
			rs_q = []
			#
			# 1つの質問ごとにrole_usersをループさせる
			#
			for k2, v2 in enumerate(role_users):
				#
				# 存在しないキーを指定するとエラーになるので、tryに分岐役をさせる
				#
				try:
					on_answer = json.loads(role_users[k2]['json'])
				except:
					on_answer = ""
				if rs_text[k1]['id'] in str(on_answer):
					rs_q.append({
							'fullname':str(role_users[k2]['fullname']),
							'value'   :'on',
							'id'      :rs_text[k1]['id'],
							'uno'	  :role_users[k2]['uno'],
								})
				else:
					rs_q.append({
							'fullname':str(role_users[k2]['fullname']),
							'id'      :rs_text[k1]['id'],
							'uno'     :role_users[k2]['uno'],
								})

			rs_a.append({
				'text':str(intext),
				'rs'  :rs_q,
				'id'  :rs_text[k1]['id']
						})
		#
		# バリュー
		#
		for k1, v1 in v_text.items():
			#
			# invalidが"1"(無効)なら処理を飛ばす
			#
			if v_text[k1]['invalid'] == str(1):
				continue
			intext = v_text[k1]['text']
			v_q = []
			for k2, v2 in enumerate(role_users):
				#
				# 存在しないキーを指定するとエラーになるので、tryに分岐役をさせる
				#
				try:
					on_answer = json.loads(role_users[k2]['json'])
				except:
					on_answer = ""
				if v_text[k1]['id'] in str(on_answer):
					v_q.append({
						'fullname':str(role_users[k2]['fullname']),
						'value'   :'on',
						'id'      :v_text[k1]['id'],
						'uno'     :role_users[k2]['uno'],
								})
				else:
					v_q.append({
						'fullname':str(role_users[k2]['fullname']),
						'id'      :v_text[k1]['id'],
						'uno'     :role_users[k2]['uno'],
								})
			v_a.append({
				'text':str(intext),
				'v'   :v_q,
				'id'  :v_text[k1]['id']
					})
		#
		# userの一覧と、選択したユーザーごとのQAを送信
		#
		sql = """
		SELECT CONCAT(name0, name1) AS fullname,`user`.`uno`
		FROM `user`
		LEFT JOIN `role`
		ON `role`.`vuno` = `user`.`uno`
		WHERE `ano` = %(ano)s
		AND `role`.`deleted` = 0
		AND `user`.`deleted` = 0
		GROUP BY `uno`;
		"""
		params = {
			'ano':web.ano
		}
		all_user = web.db.exe(sql, params=params)
		users = []
		onunolist = []
		offunolist = []
		#
		# 選択したユーザーを保持し、usersに格納
		#
		for i1, v1 in enumerate(all_user):
			if str(all_user[i1]['uno']) in values:
				users.append({
					'fullname':all_user[i1]['fullname'],
					'uno'     :all_user[i1]['uno'],
					'value'   :'on',
							})
				onunolist.append(all_user[i1]['uno'])
			else:
				users.append({
					'fullname':all_user[i1]['fullname'],
					'uno'     :all_user[i1]['uno'],
							})
				offunolist.append(str(all_user[i1]['uno']))
		onunolist = ",".join(offunolist)
		offunolist = ",".join(offunolist)
		local = {
			'rg_a'     :rg_a,
			'rs_a'     :rs_a,
			'v_a'      :v_a,
			'offunolist'  :offunolist,
			'onunolist'  :onunolist,
			'user_icon':web.user_icon,
		}
		return build(web, local, \
			'/growth/' + web.path.replace('/', '.')[1:] + '.html')

	#
	# 回答が更新されたときの処理
	#
	#showuno = []
	#for k, v in web._get.items():
	#	if re.match(r'show([0-9]+)', k):
	#		showuno.append(int(v))
	#web.log(showuno,"RED")

		#
		# 全員の評価の合計点を見る
		#
	if web.get('all_uservaluer') or web.get('uservaluer_all'):
		if web.get('all_uservaluer'):
			sql = """
			SELECT `role`.`uno`, `vuno`, `json`, CONCAT(name0, name1) AS fullname, `time4`, `role`.`deleted`
			FROM `role`
			LEFT JOIN `user`
			ON `user`.`uno` = `role`.`uno`
			WHERE (`role`.`vuno`, `time4`) IN (
			SELECT `vuno`, max(`time4`) AS `time4`
			FROM `role`
			WHERE `vuno` = %(uno)s
			AND `json` is not Null
			GROUP BY `vuno`
			)"""
		if web.get('uservaluer_all'):
			sql = """
			SELECT `role`.`uno`, `vuno`, `json`, CONCAT(name0, name1) AS fullname, `time4`, `role`.`deleted`
			FROM `role`
			LEFT JOIN `user`
			ON `user`.`uno` = `role`.`vuno`
			WHERE (`role`.`uno`, `time4`) IN (
			SELECT `uno`, max(`time4`) AS `time4`
			FROM `role`
			WHERE `uno` = %(uno)s
			AND `json` is not Null
			AND `deleted` = 0
			GROUP BY `vuno`
			)"""
		params = {
			'uno':web.uno
		}
		alluser_valuer = web.db.exe(sql, params=params)
		all_userpoint = []
		for k1, v1 in enumerate(alluser_valuer):
			if not alluser_valuer[k1]['json']:
				time = datetime.date.fromtimestamp(alluser_valuer[k1]['time4'])
				all_userpoint.append({
					'fullname'   :alluser_valuer[k1]['fullname'],
					'time'       :time,
									})
				continue
			rg_pointtime = []	# ゼネラリストの各ポイントと評価時間
			rs_pointtime = []	# スペシャリストの " "
			v_pointtime  = []	# バリューの " "
			gs_pointtax  = 0    # ゼネラリストとスペシャリストの合計点
			rg_pointtax  = 0    # ゼネラリストの合計点
			rs_pointtax  = 0	# スペシャリストの " "
			v_pointtax   = 0	# バリューの " "
			#
			# ゼネラリスト
			#
			for k2, v2 in rg_text.items():
				try:
					on_answer = json.loads(alluser_valuer[k1]['json'])
				except:
					on_answer = alluser_valuer[k1]['json']
				if rg_text[k2]['id'] in str(on_answer):
					rg_pointtax += int(rg_text[k2]['point'])
					gs_pointtax += int(rg_text[k2]['point'])
			#
			# スペシャリスト
			#
			for k2, v2 in rs_text.items():
				try:
					on_answer = json.loads(alluser_valuer[k1]['json'])
				except:
					on_answer = ""
				if rs_text[k2]['id'] in str(on_answer):
					rs_pointtax += int(rs_text[k2]['point'])
					gs_pointtax += int(rs_text[k2]['point'])
			#
			# バリュー
			#
			for k2, v2 in v_text.items():
				try:
					on_answer = json.loads(alluser_valuer[k1]['json'])
				except:
					on_answer = ""
				if v_text[k2]['id'] in str(on_answer):
					v_pointtax += int(v_text[k2]['point'])
			time = datetime.date.fromtimestamp(alluser_valuer[k1]['time4'])



			all_userpoint.append({
				'fullname'   :alluser_valuer[k1]['fullname'],
				'rg_pointtax':rg_pointtax, #rgの合計点
				'rs_pointtax':rs_pointtax, #rsの合計点
				'v_pointtax' :v_pointtax,  #vの合計点
				'gs_pointtax':gs_pointtax, #rgとrsの合計点
				'time'       :time,
								})
		local = {
			'all_userpoint':all_userpoint,	# 全てのユーザーの合計点
			'user_icon'    :web.user_icon,  # アイコン
		}
		return build(web, local, \
			'/growth/' + web.path.replace('/', '.')[1:] + '.html')

	#
	# user一覧(初期画面)
	#
	sql = """
	SELECT  `uno`, `vuno`, `json`,
	CONCAT(name0, name1) AS fullname ,
	`asname` , `icon`.`uno` AS `has_icon`
	FROM `role`
	LEFT JOIN `user`  USING (`uno`)
	LEFT JOIN `icon`  USING (`uno`)
	LEFT JOIN `assign` USING (`ano`)
	WHERE (`vuno`, `time4`) IN (
	SELECT `vuno`, max(`time4`) AS `time4`
	FROM `role`
	WHERE `vuno` = %(uno)s
	GROUP BY `uno`
	) AND `role`.`deleted` = 0
	GROUP BY `uno`
	"""
	params = {
		'uno':web.uno
	}
	users = web.db.exe(sql, params=params)
	local = {
		'users'    :users,
		'user_icon':web.user_icon,
	}
	return build(web, local, \
		'/growth/' + web.path.replace('/', '.')[1:] + '.html')
