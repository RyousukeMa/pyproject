# -*- coding: utf-8 -*-

import blossom
import matsuoka_func
import re
#
#
# main
#
#
def main(web, build):
#------------------------------------------------------------------------------
	#
	# anoを取得
	#
	ano = matsuoka_func.from_uno_getdb_ano(web,web.uno, cookie=False)

	#
	# 部署の登録
	#
	if web.post('asname'):
		#
		# 同じ名前の部署があった場合
		#
		sql = """
		SELECT `asname`
		FROM `assign`
		WHERE `asname` = %(asname)s;"""
		params = {
			'asname':web.post('asname'),
		}
		just = web.db.exe(sql, params=params)
		if just == web.post('asname'):
			return web.redirect('/admin/assign?message=just_assign')
		#
		# 部署名を登録
		#
		sql = """
		INSERT INTO
		`assign` (`ano`,`asname`,`deleted`)
		VALUES
 		(%(ano)s, %(asname)s,0);"""
		params = {
			'ano':ano,
			'asname':str(web.post('asname')),
		}
		web.db.exe(sql, params=params)
		return web.redirect('/admin/assign?message=app_assign')

	if web.get('cs'):
		for k, v in web._get.items():
			if k == 'cs':
				continue
			u = re.match('changeasname([0-9]+)',k)
			asname = v
			asno   = int(u.group(1))
			sql = """
			UPDATE  `assign`
			SET `asname` = %(asname)s
			WHERE `asno` = %(asno)s
			AND `deleted` = 0"""
			params = {
				'asno':asno,
				'asname':asname,
			}
			web.db.exe(sql, params=params)
		return web.redirect('/admin/assign?message=changename_assign')
	#
	# 部署の削除
	#
	if web.get('dno'):
		asno = web.get('dno')
		#
		# 部署を削除する
		#
		sql = """
		UPDATE `assign` SET `deleted` = '1'
		WHERE `asno` =""" + str(asno) + ";"
		web.db.exe(sql)
		#
		# 削除した部署に所属するuserを全て未所属にする
		#
		sql = """
		UPDATE `user`
		SET `asno` = 1
		WHERE `asno` =""" + str(asno) + ";"
		web.db.exe(sql)
		return web.redirect('/admin/assign?message=delete_assign')

	#
	# 部署を取得
	#
	# 再帰処理
	#
	#def _func(web, pasno, ano):
	#	sql = """
	#	SELECT *
	#	FROM `assign`
	#	WHERE `pasno` = %(pasno)s
	#	AND `ano` = %(ano)s
	#	AND `deleted` = 0"""
	#	params = {
	#		'pasno':pasno,
	#		'ano'  :ano,
	#	}
	#	rows = web.db.exe(sql,params=params)
	#	web.log(rows,"RED")
	#	row = {}
	#	for i, row in enumerate(rows):
	#		rows[i] = {
	#			'asno'    :row['asno'],
	#			'asname'  :row['asname'],
	#			'children':_func(web, row['asno'], ano)
	#		}
	#	return row

	#tree = _func(web, 0, ano)

	sql = """
	SELECT *
	FROM `assign`
	WHERE `pasno` = %(pasno)s
	AND `ano` = %(ano)s
	AND `assign`.`deleted` = 0"""
	params = {
		'pasno':0,
		'ano'  :ano,
	}
	tree = web.db.exe(sql,params=params)
	tree[0]['farst'] = "none"

	#
	# 部署ごとの人数をカウント
	#
	for k, v in enumerate(tree):
		sql = """
		SELECT count( * )
		FROM `assign`
		LEFT JOIN `user`
		ON `user`.`asno` = `assign`.`asno`
		WHERE `pasno` = 0
		AND `assign`.`ano` = %(ano)s
		AND `assign`.`deleted` = 0
		AND `assign`.`asno` = %(asno)s
		AND `user`.`deleted` = 0"""
		params = {
			'asno': v['asno'],
			'ano'  :ano,
		}
		v['people'] = web.db.exe(sql, params=params, key=True)
		web.log(v['people'],"RED")

	local = {
		'user_icon':web.user_icon,
		'tree'   :tree,
	}
	return build(web, local,'/admin/' \
	 	+ web.path.replace('/', '.')[1:] + '.html')
