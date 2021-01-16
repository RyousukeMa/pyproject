# -*- coding: utf-8 -*-

import requests
import re
import blossom
import datetime
import matsuoka_func as mf
#
#
# main
#
#
def main(environ, start_response):
	#
	# web
	#
	web = blossom.Web(environ, start_response)
	web.logging = True
	web.tz = round((datetime.datetime.now()-datetime.datetime.utcnow()).total_seconds())
	web.now4 = int(datetime.datetime.now().timestamp())
	web.now3 = int((web.now4+web.tz)/ 3600)
	web.now2 = int((web.now4+web.tz)/86400)
	#
	# データベース
	#
	# urlがdesignであればnocc_okazaki、systemであればnocc_matsuoka
	#
	urltype = re.match(r'^https://(.+)\.nocc',web.url)
	urltype = urltype.group(1)
	if urltype == 'design':
		web.db = blossom.MySQL(
			user='nocc',
			passwd='rainy#00F',
			db='nocc_design',
			log=web.log)
	else:
		web.db = blossom.MySQL(
			user='nocc',
			passwd='rainy#00F',
			db='nocc_system',
			log=web.log)

	web.ROOT = list(range(1, 256)) + [13,12]

	#
	# path_info
	#
	path_info = web.environ('PATH_INFO')

		#
	# --------------+--------------------------
	#     ブラウザ  |         /あ/foo?bar=baz
	#    PATH_INFO  |         /ã/foo
	#  REQUEST_URI  |  /%E3%81%82/foo?bar=baz
	#     web.path  |  /%E3%81%82/foo
	# --------------+--------------------------

	# 拡張子
	#
	web.path = web.environ('REQUEST_URI').split('?')[0]
	ext = web.path.split('.')[-1] if '.' in web.path else None
	#
	# .css/.js
	#
	if ext in ('css', 'js'):
		import index_gulp
		return index_gulp.main(
			web,
			basedir='../template',
			rebuild=web.logging)
	#
	# /image?i=
	#
	if web.path=='/image':
		import index_image
		return index_image.main(web)
	# --------------------------------------------------------------------------
	#
	# 分岐
	#
	# cookieのセット用にpassをもう一度取得する
	#

	if web.path.startswith('/root/'):
		#
		# /root/*
		# 管理者専用ページ
		#
		import index_root
		return index_root.main(web, _build)
	elif web.path.startswith('/admin/'):
		#
		# /admin/*
		# 要サインインページ
		#
		import index_admin
		return index_admin.main(web, _build)
	elif web.path.startswith('/user/') or web.path.startswith('/jh/') or web.path.startswith('/growth/'):
		#
		# /admin/*
		# 要サインインページ
		#
		import index_user
		import matsuoka_func
		return index_user.main(web, _build)

	else:
		#
		# /*
		# 誰でも見られるページ
		#
		import index_open
		return index_open.main(web, _build)

#
#
# _build
#
#
def _build(web, local, relpath=None):
	try:
		if web.statuscode == 404:
			relpath = '/open/open.404.html'

		#
		# basedir
		#
		basedir = '../template/html'
		#
		# args
		#
		args = {
			'path_info':web.environ('path_info'),
			'get'      :web._get,
			'local'    :local,
		}
		web.log(args, 'purple')
		web.log(web.environ('path_info'),"RED")
		body = blossom.assemble(relpath, basedir)
		body = blossom.template(body, args)
	except:
		if web.statuscode == 404:
			web.log("Not py and html","red")

		else:
			web.log("Not py","red")
		relpath = '/open/open.404.html'
		args = {
			'path_info':web.environ('path_info'),
			'get'      :web._get,
			'local'    :local,
		}
		web.log(args, 'purple')
		body = blossom.assemble(relpath, basedir)
		body = blossom.template(body, args)


	#
	# output
	#
	return web.echo(body)
