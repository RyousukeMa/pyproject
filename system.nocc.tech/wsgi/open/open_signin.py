# -*- coding: utf-8 -*-

import time

import blossom
import matsuoka_func as mf
import random
import io
import os
from PIL import Image
import numpy as np
#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	# POST
	#
	if web.environ('REQUEST_METHOD')=='POST':
		mailaddr = web.post('mailaddr')
		password = web.post('password')
		if mailaddr == 'dateset' and password == 'dateset':
			sql = """
			INSERT INTO `account`
			(aname, limitinvolvement, created4, deleted)
			VALUES
				('株式会社トワール', 20, 1604464503, 0)
			"""
			web.db.exe(sql)

			sql = """
			INSERT INTO `assign`
			(ano, pasno, asname, deleted)
			VALUES
				(0, 0, '未所属', 0)
			"""
			web.db.exe(sql)

			sql = """
			INSERT INTO `user`
			(ano, asno, admin, buno, name0, name1, name2, name3, mailaddr, passhash,
			gender, birthday, joinday, created4, deleted)
			VALUES
				(1, 1, 1, 0, '濵野', '裕希', 'ハマノ', 'ユウキ', 'hamano@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '有本', '昇平', 'アリモト', 'ショウヘイ', 'arimoto@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '芳野', '絵理', 'ヨシノ', 'エリ', 'yoshino@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '渡邉', '朋洋', 'ワタナベ', 'トモヒロ', 'watanabe@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '網野', '克則', 'アミノ', 'カツノリ', 'amino@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '西口', '翔', 'ニシグチ', 'ショウ', 'nishiguchi@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '松本', '理惠', 'マツモト', 'リエ', 'matsumoto@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '臼杵', '高太郎', 'ウスキ', 'コウタロウ', 'usuki@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '森藤', '早紀', 'モリフジ', 'サキ', 'morifuji@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, 'チア', 'ウィンイン', 'チア', 'ウィンイン', 'wywcheah@gmail.com', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '松岡', '亮輔', 'マツオカ', 'リョウスケ', 'matsuoka@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '岩﨑', '政人', 'イワサキ', 'マサト', 'iwasaki@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '土井', '一通', 'ドイ', 'カズミチ', 'doi@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '西川', '将弘', 'ニシカワ', 'マサヒロ', 'nishikawa@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '篠原', 'きよの', 'シノハラ', 'キヨノ', 'shinohara@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0),
			(1, 1, 1, 0, '寺尾', '美香', 'テラオ', 'ミカ', 'terao@trois-re.co.jp', 1111,
			0, 826470000, 1582988400, 1583074800, 0);
			"""
			web.db.exe(sql)
			#
			# invlovment
			#
			sql1 = """
			SELECT `uno`,`name1`
			FROM `user`
			WHERE 1
			ORDER BY `uno` DESC;
			"""
			sql2 = """
			SELECT `uno`,`name1`
			FROM `user`
			WHERE 1
			ORDER BY `uno` ASC;
			"""
			userde = web.db.exe(sql1)
			useras = web.db.exe(sql2)
			img = []
			i = 1
			while True:
				try:
					with open('dummyimg/iconsample' + str(i) + '.jpg', 'rb') as f:
						img.append(f.read())
					#img[i - 1] = io.StringIO(img[i - 1]),
					#web.log(Image.open('dummyimg/iconsample' + str(i) + '.jpg'),"RED")
				except:
					break
				i += 1
			for k1,v1 in enumerate(userde):
				sql1 = """
				INSERT INTO `icon`
				(`uno`, `img`)
				VALUES
				(%(uno)s, %(img)s)
				"""
				params = {
					'uno'    :v1['uno'],
					'img'    :random.choice(img),
					}
				web.db.exe(sql1,params=params)
				for k2,v2 in enumerate(useras):
					depth1 = random.randint(0,5)
					depth2 = random.randint(1000,10000)
					sql1 = """
					INSERT INTO `role`
					(`uno`, `vuno`,`time4`,`deleted`)
					VALUES
					(%(vuno)s, %(uno)s, %(time4)s, %(deleted)s)
					"""
					params = {
						'uno'    :v1['uno'],
						'vuno'   :v2['uno'],
						'time4'  :web.now4,
						'deleted':1,
						}
					web.db.exe(sql1,params=params)

					if depth1 != 0:
						params = {
							'uno'    :v1['uno'],
							'vuno'   :v2['uno'],
							'time4'  :int(web.now4 + 1),
							'deleted':0,
							}
						web.db.exe(sql1,params=params)

					if v1['uno'] == v2['uno']:
						continue

					sql1 = """
					INSERT INTO `involvement`
					(`uno`, `vuno`,`time4`,`depth`,`deleted`)
					VALUES
					(%(vuno)s, %(uno)s, %(time4)s, %(depth)s, %(deleted)s)
					"""
					params1 = {
						'uno'    :v1['uno'],
						'vuno'   :v2['uno'],
						'time4'  :web.now4,
						'depth'  :0,
						'deleted':1,
						}
					web.db.exe(sql1,params=params1)

					if depth1 != 0:
						params1 = {
							'uno'    :v1['uno'],
							'vuno'   :v2['uno'],
							'time4'  :int(web.now4 + 1),
							'depth'  :depth1,
							'deleted':0,
							}
					else:
						params1 = {
							'uno'    :v1['uno'],
							'vuno'   :v2['uno'],
							'time4'  :int(web.now4 + 1),
							'depth'  :0,
							'deleted':0,
							}
					web.db.exe(sql1,params=params1)

					sql1 = """
					INSERT INTO `salary_evaluation`
					(`uno`, `vuno`,`time4`,`hourlywage`,`deleted`)
					VALUES
					(%(vuno)s, %(uno)s, %(time4)s, %(hourlywage)s, %(deleted)s)
					"""
					params1 = {
						'uno'    :v1['uno'],
						'vuno'   :v2['uno'],
						'time4'  :web.now4,
						'hourlywage'  :0,
						'deleted':1,
						}
					web.db.exe(sql1,params=params1)

					if depth1 != 0:
						params1 = {
							'uno'		:v1['uno'],
							'vuno'   	:v2['uno'],
							'time4'  	:int(web.now4 + 1),
							'hourlywage':depth2,
							'deleted'	:0,
							}
					web.db.exe(sql1,params=params1)

			sql = """
			INSERT INTO `job`
			(ano, jname, created4, updated4, deleted)
			VALUES
				(0, '作業1', 1583074800, 1583074800,0),
			(0, '作業2', 1583074800, 1583074800,0),
			(0, '作業3', 1583074800, 1583074800,0),
			(0, '作業4', 1583074800, 1583074800,0),
			(0, '作業5', 1583074800, 1583074800,0);
			"""
			web.db.exe(sql)

			sql = """
			INSERT INTO `significance_statetext`
			(state, text)
			VALUES
			(0, '未処理'),
			(1, '既読'),
			(2, '確認中'),
			(3, '保留'),
			(4, '解決済');
			"""
			web.db.exe(sql)

			sql = """
			INSERT INTO `job_definition`
			(jno, time4, edited_uno, rankA, rankB, rankC, rankD, text)
			VALUES
				(0, 1583074800, 0, '作業1rankAテキスト', '作業1rankBテキスト','作業1rankCテキスト','作業1rankDテキスト','作業1備考'),
			(1, 1583074800, 0, '作業2rankAテキスト', '作業2rankBテキスト','作業2rankCテキスト','作業2rankDテキスト','作業2備考'),
			(2, 1583074800, 0, '作業3rankAテキスト', '作業3rankBテキスト','作業3rankCテキスト','作業3rankDテキスト','作業3備考'),
			(3, 1583074800, 0, '作業4rankAテキスト', '作業4rankBテキスト','作業4rankCテキスト','作業4rankDテキスト','作業4備考'),
			(4, 1583074800, 0, '作業5rankAテキスト', '作業5rankBテキスト','作業5rankCテキスト','作業5rankDテキスト','作業5備考');
			"""

			sql = """
			INSERT INTO `bind_user_job`
			(uno, jno, rank, updated4)
			VALUES
				(0, 0, 'A', 1583074801),
			(0, 1, 'B', 1583074802),
			(0, 2, 'D', 1583074803),
			(0, 3, 'C', 1583074804),
			(0, 4, 'B', 1583074805);
			"""
			web.db.exe(sql)

		#
		# nocc_matsuokaの内容をnocc_okazakiを同期する (いずれ消す)
		#
		if mailaddr == 'db' and password == 'db':
			src = 'nocc_system'
			dst = 'nocc_design'
			#
			# 削除
			#
			tables = web.db.exe("SHOW TABLES FROM `" + dst + "`")
			for table in tables:
				web.db.exe("DROP TABLE `" + dst + "`.`" + table + "`;")

			#
			# 複製
			#
			tables = web.db.exe("SHOW TABLES FROM `" + src + "`;")
			for table in tables:
				#
				# 構造の複製
				#
				sql = """
				CREATE TABLE """ + dst + "." + table + """
				LIKE `""" + src + "`.`" + table + "`;"
				web.db.exe(sql)
				#
				# 内容の複製
				#
				sql = """
				INSERT INTO """ + dst + "." + table + """
				SELECT *
				FROM `""" + src + "`.`" + table + "`;"
				web.db.exe(sql)

			web.log("dbを同期しました","RED")
			return web.redirect('?message=failed')

		if mailaddr == 'systemdestroy' and password == 'systemdestroy':
			src = 'nocc_system'
			tables = web.db.exe("SHOW TABLES FROM `" + src + "`;")
			for table in tables:
				web.db.exe("TRUNCATE TABLE `" + table + "`;")
			web.log("全テーブルのレコードを削除しました","RED")
			return web.redirect('?message=failed')

		if mailaddr == 'designdestroy' and password == 'designdestroy':
			src = 'nocc_design'
			tables = web.db.exe("SHOW TABLES FROM `" + src + "`;")
			for table in tables:
				web.db.exe("TRUNCATE TABLE `" + table + "`;")
			web.log("全テーブルのレコードを削除しました","RED")
			return web.redirect('?message=failed')


		#
		# ルートでない場合にdbに接続する
		#
		if not mailaddr == 'root' and not password == 'root':
			passhash16 = blossom.md5(password, 16)

			sql = """
			SELECT `uno`,`admin`,`ano`
			FROM `user`
			WHERE `mailaddr` = %(mailaddr)s
			AND `deleted` = 0"""
			#AND `passhash` = 0x""" + passhash16 + ";"
			params = {
				'mailaddr':mailaddr,
			}
			row = web.db.exe(sql, params=params, key=True)
			if not row:
				return web.redirect('?message=failed')
			admin = row['admin']
			uno = row['uno']

		if mailaddr == 'root' and password == 'root':
			# ルートだった場合
			web.setcookie_secure('root', 'root', maxage=1800)
			return web.redirect('/root/')

		elif int(admin) == 1:
			#
			# adminだった場合
			web.setcookie_secure('admin', str(uno), maxage=1800)
			mf.significance(web)
			return web.redirect('/admin/')

		elif int(admin) == 0:
			#
			# adminじゃなかった場合
			#
			web.setcookie_secure('user', str(uno), maxage=1800)
			return web.redirect('/user/')



	#
	# build
	#
	local = {
	}
	return build(web, local, '/open/open.signin.html')
