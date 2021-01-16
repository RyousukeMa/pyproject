# -*- coding: utf-8 -*-

import base64
import re
import time
import datetime
import matsuoka_func

#
# main
#
def main(web, build):
	#
	# ログイン中のユーザーの画像を取得
	#
	user_icon = matsuoka_func.get_icon(web,web.uno)

	#
	# unoから所属する会社を取得
	#
	if web.environ('REQUEST_METHOD') == 'POST':
		aname = web.post('aname')
		ano = web.post('ano')
		sql = """
			UPDATE `account`
			SET `aname` = %(aname)s
			WHERE `ano` = %(ano)s;"""
		params = {
			'ano':ano,
			'aname':aname,
		}
		web.db.exe(sql, params=params, key=True)

	#
	# cookieからunoを取得
	#
	m_uno = re.match(r'.+\..+\.([0-9]+)', web.cookie('admin'))
	uno = m_uno.groups()[0]

	#
	# unoからuserが所属するaccountを取得
	#
	sql = """
	SELECT `account`.`ano`,`account`.`aname`
	FROM `account`
	INNER JOIN `user`
	ON `user`.`ano` = `account`.`ano`
	WHERE `account`.`deleted` = 0 AND `user`.`uno` = %(uno)s;"""
	params = {
		'uno':uno,
	}
	account = web.db.exe(sql, params=params, key=True)

	sql ="""
	SELECT `sno`
	FROM `significance`
	LEFT JOIN `user`
	ON `significance`.`uno` =  `user`.`uno`
	WHERE `user`.`ano` = %(ano)s
	AND `significance`.`state` != 4
	AND `user`.`deleted`  = 0"""
	params = {
		'ano':account['ano'],
	}
	significance = web.db.exe(sql, params=params, key=True)
	if significance:
		significance = {
			'state':True
		}
	else:
		significance = {
			'state':False
		}
	# --------------------------------------------------------------------------
	# build
	#
	local = {
		'item'     		:account,
		'significance'	:significance,
		'user_icon'		:user_icon,
	}
	return build(web, local,'/admin/admin.index.html')
