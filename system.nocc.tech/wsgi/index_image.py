# -*- coding: utf-8 -*-

import base64

import blossom

#
#
# main
#
#
def main(web):
	#
	# バイナリ取得
	#
	sql = """
	SELECT `img`
	FROM `icon`
	WHERE `uno` = """ + str(web.get('uno')) + ";"
	image = web.db.exe(sql, key=True)
	#
	# 出力する
	#
	web.setheader('Content-Type: image/jpeg')
	return web.echo(image)
