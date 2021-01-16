# -*- coding: utf-8 -*-

import requests
import blossom
import re


def from_uno_getdb_ano(web,uno,cookie):
	try:
		if cookie:
			uno = re.match(r'.+\..+\.([0-9]+)', uno)
			uno = uno.groups()[0]

		#
		# unoからanoを取得
		#
		sql = """
		SELECT `ano`
		FROM `user`
		WHERE `uno` = %(uno)s"""
		params = {
		'uno':uno,
		}
		ano = web.db.exe(sql, params=params, key=True)
	except ImportError as e:
		return None
	return ano

def get_user(web,uno,cookie=False):
	try:
		if cookie:
			uno = re.match(r'.+\..+\.([0-9]+)', uno)
			uno = uno.groups()[0]

		#
		# unoからanoを取得
		#
		sql = """
		SELECT *
		FROM `user`
		WHERE `uno` = %(uno)s"""
		params = {
		'uno':uno,
		}
		user = web.db.exe(sql, params=params, key=True)
	except ImportError as e:
		return None
	return user



def get_icon(web,uno):
	try:
		sql = """
		SELECT `uno` AS `has_icon`
		FROM icon
		WHERE `uno` = %(uno)s"""
		params = {
		'uno':uno
		}
		icon = web.db.exe(sql, params=params, key=True)
		if icon:
			user_icon =  {
				'uno'     :icon,
				'has_icon':True
			}
		else:
			user_icon =  {
				'uno'     :icon,
				'has_icon':False,
			}
	except ImportError as e:
		return None
	return user_icon


#
# checker  -> object
# validator -> object （名詞 er/or
#
# method/function
#		check, validate (動詞
#
# 戻り値
#  成功                     True/False
#  失敗（なぜ失敗したのか） 数値・文字列
#
# validate_password() → 問題なければTrue・問題あれば文字列
# find_problem_of_password() → 問題がなければNone,

def pass_validator(pass1, pass2, varchar):
	#
	# バリテーションチェック
	#
	# 文字数
	if len(pass1) < varchar:
		return "pass1_notover_varchar"
	elif len(pass2) < varchar:
		return "pass2_notover_varchar"

	# 違う値
	if pass1 != pass2:
		return "passwords_notmatch"
	# 英数字以外が含まれているかどうか

	if re.match(r'.+[^a-zA-Z0-9]+.+', pass1):
		return "pass1_alphanumeric_varchar"
	elif re.match(r'.+[^a-zA-Z0-9]+.+', pass2):
		web.log("OK", "red")
		return "pass2_alphanumeric_varchar"

	return "notvalidator"

def katakana_validator(postname):
	import unicodedata
	for i in range(len(postname)):
			m = unicodedata.name(postname[i])
			if not re.match('KATAKANA', m):
				return False
	return postname


def input_log(web, sql_text, param, uno):
	sql = """
	INSERT INTO
	`log` (`logno`, `uno`, `param`, `sql_text`)
	VALUES
	(NULL, %(uno)s, %(param)s, %(sql_text)s);"""
	param_text = ""
	if param != None:
		for l,v in param.items():
			param_text += '/' + str(l)  + '(' + str(v) + ')'

	if uno != None:
		uno = 200

	log_params = {
		'uno':int(uno),
		'sql_text':sql_text,
		'param':param_text,
	}
	web.db.exe(sql, params=log_params, key=True)

def significance(web):
	sql = """
		SELECT SQL_CALC_FOUND_ROWS `state`
		FROM `significance`
		WHERE `state` != 4
		"""
	found = web.db.exe('SELECT FOUND_ROWS();', key=True)

	if found:
		web.significance = "on"
	else:
		web.significance = "off"
	return web.significance
