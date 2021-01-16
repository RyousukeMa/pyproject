# -*- coding: utf-8 -*-

"""
[リリース版]

サーバ側からキャッシュ制御を出力し、ページ遷移ではリクエストが発生しないようにするため快適な表示が行われる。

  キャッシュ制御  |  リクエスト  |  If-Modifi  |
          "あり"  |        発生  |   ed-Since  |  結果
------------------+--------------+-------------+----------------------
  初回            |  あり        |  なし       |  cache
------------------+--------------+-------------+----------------------
  ページ遷移      |  なし        |  なし       |  -
------------------+--------------+-------------+----------------------
  ソフトリロード  |  あり        |  あり       |  304
------------------+--------------+-------------+----------------------
  ハードリロード  |  あり        |  なし       |  cache


[開発版]

ブラウザがサーバからキャッシュ制御を受け取った場合、Firefox と webkit では動作が異なる。Firefox は（ページ遷移・ソフトリロード）でリクエスト発生は（なし・あり）となるため、意図的にリロードしない限りは高速な表示が行われる理想的な動作を行う。一方 webkit では（なし・なし）となり、表示確認のためにハードリロードを強いられる。
不本意ではあるものの開発版では webkit に合わせる形をとる。つまりサーバーからキャッシュ制御は出力せず、ブラウザにはページ遷移であってもリクエストを発生させる。304 の判定ためにはソースコード群の更新日時の最大値を得て、これを If-Modified-Since の日時と比較する必要がある。

  キャッシュ制御  |  リクエスト  |  If-Modifi  |
          "なし"  |        発生  |   ed-Since  |  結果
------------------+--------------+-------------+----------------------
  初回            |  あり        |  なし       |  rebuild
------------------+--------------+-------------+----------------------
  ページ遷移      |  あり        |  あり       |  ソースコードの日時
------------------+--------------+-------------+  から 304 / rebuild
  ソフトリロード  |  あり        |  あり       |  の判定を行う
------------------+--------------+-------------+----------------------
  ハードリロード  |  あり        |  なし       |  rebuild

"""

import os

import blossom
import gulp

#
#
# main
#
#
def main(web, basedir, rebuild, maxage=1800):
	path_info = web.environ('PATH_INFO')
	#
	# css|js
	#
	src = basedir + path_info
	dst = basedir + path_info + '/_cache'
	ext = path_info.split('.')[-1]
	#
	# 304|cache|rebuild
	#
	if rebuild:
		#
		# 304 Not Modified
		#
		mtime = scan_mtime(src)
		if not web.if_modified_since(mtime):
			return web.echo(b'')
		#
		# rebuild
		#
		if ext=='css':
			#
			# .css
			#
			files = blossom.glob(src, ['css', 'scss'])
			option = {
				'type'               :'scss',
				'autoprefixer'       :'on',
				'sourcemaps'         :'',
				'merge_media_queries':'on',
				'csscomb'            :'on',
				'clean_css'          :'on',
			}
			body = gulp.compile(
				web,
				ext='scss',
				files=files,
				option=option)
		else:
			#
			# .js
			#
			files = {
				'/body.js':blossom.assemble(path_info, basedir=src),
			}
			option = {}
			body = gulp.compile(
				web,
				ext='js',
				files=files,
				option=option)
		#
		# write
		#
		blossom.write(dst, body)
		#
		# web.if_modified_since() の処理の過程で指定される最終更新日は
		# 前回の古いキャッシュの日時なので、今回の日時をここで指定する。
		#
		web.last_modified = os.stat(dst).st_mtime
		#
		# Cache-Control: max-age=900
		# Expires: Thu, 01 May 2018 23:59:59 GMT
		#
		web.maxage = maxage
	else:
		#
		# 304 Not Modified
		#
		mtime = os.stat(dst).st_mtime
		if not web.if_modified_since(mtime):
			return web.echo(b'')
		#
		# reuse
		#
		body = blossom.read(dst)
	#
	# output
	#
	ext = ext if ext=='css' else 'javascript'
	web.setheader('Content-Type: text/' + ext + '; charset=UTF-8')
	return web.echo(body)


#
# 対象ソースファイル群の最終更新日の最新値を得る
#
def scan_mtime(rootdir):
	def _scan(top):
		mtime = 0
		for dirpath, dirnames, filenames in os.walk(top, followlinks=True):
			for dirname in dirnames:
				abspath = os.path.join(top, dirname)
				mtime = max(mtime, _scan(abspath))
			for filename in filenames:
				abspath = os.path.join(top, filename)
				mtime = max(mtime,os.stat(abspath).st_mtime)
			break
		return mtime
	return _scan(rootdir)