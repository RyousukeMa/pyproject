# -*- coding: utf-8 -*-

import os
import re
import shutil
import time

import blossom

#
#
# compile
#
#
def compile(web, ext, files, option):
	#
	# src, dst, wch
	#
	timehash = blossom.md5(str(time.time()).encode(), 16)
	path_src = '../gulpd.workspace/src/' + timehash
	path_dst = '../gulpd.workspace/dst/' + timehash
	path_wch = '../gulpd.workspace/wch/' + timehash + '.' + ext
	#
	# ソースコード配置
	#
	for cid, body in files.items():
		blossom.write(path_src + cid, body)
	#
	# 削除のための所有権を得るために出力先ディレクトリを自前で作成しておく
	#
	os.mkdir(path_dst)
	os.chmod(path_dst, 0o777)
	#
	# コンパイル開始
	#
	blossom.write(path_wch, blossom.json(option))
	time.sleep(.3)
	#
	# コンパイル終了
	#
	body = None
	c = .0
	while c<4.0:
		time.sleep(.1)
		body = blossom.read(path_dst + '/gulp.' + ext)
		if body:
			break
		else:
			c += .1
	else:
		body = '@Error\nCompile Timeout.'
	#
	# @Error|not
	#
	if body.startswith('@Error\n'):
		#
		# エラーメッセージ整形
		#
		# 内容に含まれるファイルのフルパスが一般利用者に知られるのは
		# セキュリティ上の理由から好ましくないため、パスの接頭部分を削除して
		# ユーザのファイルシステム上のパスに変換する。
		#
		body = body[7:]
		body = re.sub(r'[./\w]+' + timehash, '', body)
		if body=='undefined':
			body = 'Unknown Error'
	else:
		#
		# ソースマップ
		#
		# ファイル末尾の表記を削除する
		# //# sourceMappingURL=gulp.scss.map
		#
		body = re.sub(r'\s*//# sourceMappingURL=.+\s*', '', body)
		#
		# 外部ファイルへ書き出されているマップを追記する。
		#
		if option.get('sourcemaps'):
			filename = path_dst + '/gulp.' + ext + '.map'
			sourcemap = blossom.read(filename, raw=True)
			if sourcemap:
				import base64
				body += ('\n'
					+ '/*# sourceMappingURL=data:application/json;base64,'
					+ base64.b64encode(sourcemap).decode()
					+ ' */')
			else:
				web.log('Not Found: ' + filename, 'red')
	#
	# 掃除
	#
	try:
		shutil.rmtree(path_src, ignore_errors=True)
	except:
		pass
	try:
		shutil.rmtree(path_dst, ignore_errors=True)
	except:
		pass
	try:
		os.remove(path_wch)
	except:
		pass
	#
	# 以上の処理で使用済みの作業ディレクトリは削除されているはずだが、
	# それ以前の処理にて削除されず残っているディレクトリがある場合は、
	# 60秒経過を基準にして削除する。
	#
	for dir0 in ('../gulpd.workspace/src', '../gulpd.workspace/dst'):
		for dir1 in os.listdir(dir0):
			abs_path = dir0 + '/' + dir1
			if os.stat(abs_path).st_mtime<web.now4-60:
				#
				# log
				#
				web.log('shutil.rmtree(' + abs_path + ')', 'red')
				#
				# 削除
				#
				shutil.rmtree(abs_path, ignore_errors=True)
	#
	# return
	#
	return body