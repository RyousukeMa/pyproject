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
	# 数値の更新
	#
	#
	# user一覧(初期画面)
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
	local = {
		'users'    :users,
		'user_icon':web.user_icon,
	}
	return build(web, local, \
		'/growth/' + web.path.replace('/', '.')[1:] + '.html')
