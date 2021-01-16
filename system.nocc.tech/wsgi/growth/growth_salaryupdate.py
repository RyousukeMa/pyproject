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
	SELECT  `uno`, `vuno`, `hourlywage`,
	CONCAT(name0, name1) AS fullname,
	`asname`, `icon`.`uno` AS `has_icon`
	FROM `salary_evaluation`
	LEFT JOIN `user`  USING (`uno`)
	LEFT JOIN `icon`  USING (`uno`)
	LEFT JOIN `assign` USING (`ano`)
	WHERE (`vuno`, `time4`) IN (
	SELECT `vuno`, max(`time4`) AS `time4`
	FROM `salary_evaluation`
	WHERE `vuno` = %(uno)s
	GROUP BY `uno`
	) AND `salary_evaluation`.`deleted` = 0
	GROUP BY `uno`
	"""
	params = {
		'uno':web.uno
	}
	users = web.db.exe(sql, params=params)

	s_values = {}  # salary
	for k, v in web._post.items():
		if re.match(r'salary([0-9]+)', k):
			#
			# 正規表現でunoとdepthを取得
			#
			u     = re.match(r'salary([0-9]+)', k)
			uno   = int(u.group(1))
			#
			# 空白時はエラーをメッセージで返す
			#
			try:
				salary = int(v)
			except:
				return web.redirect("/growth/salary?message =" \
					+ "notint")
			#
			# unoと値をdictで格納する
			#
			if uno not in s_values:
				s_values[uno] = {}
			s_values[uno] = int(salary)

	#
	# depthを更新する用のパラムを生成
 	#
	for uno, v in sorted(s_values.items(), key=lambda x: x[1]):
		s_values[uno] = '(' + str(web.uno) + ", " + str(uno) + ", " \
 			+ str(web.now4) + ", " + str(v) + ", '" + str(0) + "')"

	#
	# depthの更新、生成したクエリをcookieに保存
	#
	s_values = ', '.join(s_values.values())
	sql = """
	INSERT INTO `salary_evaluation`
	(uno, vuno, time4, hourlywage, deleted)
	VALUES """ +  str(s_values) + ";"
	web.setcookie_secure('sql', sql, maxage=1800)

	#
	# 更新後の数値をリストに格納
	#
	udepth = 0
	now_salary = {} # depth
	for k, v in web._post.items():
		if re.match(r'salary([0-9]+)', k):
			u        = re.match(r'salary([0-9]+)', k)
			uno      = int(u.group(1))
			salary   = int(v)
			web.log(salary,"BLUE")
			#
			# unoを取得
			#
			user     = matsuoka_func.get_user(web,uno)
			apdict = {
					str(user['uno']):{
						'nowsalary':salary,
						}
					}
			now_salary.update(apdict)
	if users:
		#
		# 100分率用に全員のdepthを合計
		#
		for k, v in enumerate(users):
			#
			# 画像の取得
			#
			icon = matsuoka_func.get_icon(web,v['uno'])
			#
			# 既に登録されているsalaryを更新する時
			#
			v['now_icon']     = icon['has_icon']
			v['now_icon_uno'] = icon['uno']
			web.log(now_salary[str(v['vuno'])]['nowsalary'],"RED")
			v['afterhourlywage'] = now_salary[str(v['vuno'])]['nowsalary']

		local = {
			'users':users,
			}

		return build(web, local, \
			'/growth/' + web.path.replace('/', '.')[1:] + '.html')
