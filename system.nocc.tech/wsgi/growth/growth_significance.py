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
	# 初期画面
	#
	if web.get('to'):
		sql = """
			SELECT CONCAT(name0, name1) AS `fullname`
			FROM `user`
			WHERE `uno` = %(uno)s
		"""
		param1 = {
			'uno':web.uno
		}
		param2 = {
			'uno':web.get('to')
		}
		fromusers = web.db.exe(sql, params=param1,key=True)
		touser = web.db.exe(sql, params=param2,key=True)
		local = {
			'fromusers':fromusers,
			'touser'   :touser,
			'time4'    :web.get('time4'),
			'vuno'     :web.uno,
			'uno'      :web.get('to'),
		}
		return build(web, local, \
			'/growth/' + web.path.replace('/', '.')[1:] + '.html')

	#
	# 内容を送信
	#
	if web.get('vuno'):

		#
		# 申告対象の関係の時間を取得、申請
		#
		sql = """
			INSERT INTO `significance`
			(`uno`,`vuno`,`time4`,`significance_text`,`significance_time4`,`state`)
			 VALUES
			(%(uno)s, %(vuno)s, %(time4)s, %(significance_text)s, %(significance_time4)s, 0)
		"""
		params = {
			'uno':web.get('uno'),
			'vuno':web.get('vuno'),
			'time4':web.now4,
			'significance_text':web.get('significance_text'),
			'significance_time4':web.get('significance_time4'),
		}
		web.db.exe(sql, params=params)

		#
		# significance_memoも一行作成
		#
		sql = """
			INSERT INTO `significance_memo`
			(`sno`,`admin_uno`,`memo`,`memo_time4`,`memocreated_snostate`)
			 VALUES
			(%(sno)s, %(admin_uno)s, '申告', %(memo_time4)s, 0)
		"""
		params = {
			'sno'      :web.get('uno'),
			'admin_uno':web.uno, # 仮
			'memo_time4':web.now4,
		}
		web.db.exe(sql, params=params)
		return web.redirect('/growth/index?message=sendsignificance')
