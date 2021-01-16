# -*- coding: utf-8 -*-

import os
import re

#
#
# assemble
#
#
# basedir は関連ファイルが絶対パスで指定された場合のルートディレクトリを示す
#
#   type  |       syntax              |  error
# --------+---------------------------+-----------------------------
#   html  |     @import "(path)";     |  <ins>(message)</ins>
#     js  |  /* include "(path)"; */  |  console.log('(message)');
#
#
# 多少アレンジした表記にも対応させる:
#     /***                    ← * 多め、改行あり
#     include "(path)"        ← セミコロンなし
#     ***/
#
#
def assemble(path, basedir=None, readfunc=None):
	basedir = basedir or ''
	ext = path.split('.')[-1].lower()
	# -------------------------------------------------------------------- _read
	#
	# body = _read(path, basedir)
	#
	# 外部関数 readfunc が未指定であれば自前でファイルを読み込む。
	#
	def _read(path, basedir):
		if callable(readfunc):
			return readfunc(path, basedir)
		else:
			with open(basedir + path, 'rb') as f:
				return f.read().decode()
	# ------------------------------------------------------------------- /_read
	# ------------------------------------------------------------------ _export
	#
	# body = _export(body, roots)
	#
	# 再帰エクスポート
	#
	def _export(body, roots):
		m = re.match(r'^@export\s+([\'"])([-\w._/]+)\1;\n', body)
		if m:
			body = body[len(m.group(0)):]
			path1 = m.group(2)
			path1 = os.path.join(os.path.dirname(path), path1)
			path1 = os.path.normpath(path1)
			#
			# 無限ループ対策
			#
			if path1 in roots:
				return body,
			roots.append(path1)
			#
			# ロード
			#
			txt1 = _read(path1, basedir)
			if txt1:
				#
				# @import "(ここ)"; を絶対パスに変換する
				#
				for m in re.finditer(r'@import\s*([\'"])([-\w._/]+)\1;', txt1):
					tag = m.group(0)
					path2 = m.group(2)
					path2 = os.path.join(os.path.dirname(path1), path2)
					path2 = os.path.normpath(path2)
					txt1 = txt1.replace(tag, '@import "' + path2 + '";')
			else:
				return body
			body = re.sub(r'@import\s+\*;', body, txt1)
			return _export(body, roots)
		return body
	# ----------------------------------------------------------------- /_export
	# ----------------------------------------------------------------- _imports
	#
	# body = _imports(path, roots)
	#
	# 再帰インポート
	#
	def _imports(path, roots):
		#
		# read
		#
		body = ''
		result = _read(path, basedir)
		if result:
			body = result
		#
		# 強制的に文字列化する
		#
		if not isinstance(body, str):
			body = body.decode(errors='replace')
		#
		# /* include "*.js"; */
		#         変換 ↓
		#    @import "*.js";
		#
		if ext=='js':
			body = re.sub(r'[\t ]*/\*+\s*include\s+([\'"])([-\w._/]+\.js)\1;?\s*\*+/', r'@import "\2";', body)
		#
		# roots
		#
		roots.append(path)
		#
		# body|not
		#
		if body:
			#
			# @export "(path1)";
			#
			if len(roots)==1:
				body = _export(body, roots)
			#
			# @import "(path1)";
			#
			for m in re.finditer(r'(\s*)@import\s+([\'"])([-\w._/]+)\2;', body):
				tag = m.group(0)
				brs = '\n' * m.group(1).count('\n')
				path1 = m.group(3)
				path1 = os.path.join(os.path.dirname(path), path1)
				path1 = os.path.normpath(path1)
				#
				# 無限ループ対策
				#
				if path1 in roots:
					if ext=='html':
						txt1 = '<ins>ImportLoop:' + path1 + '</ins>'
					else:
						txt1 = 'console.log("ImportLoop:' + path1 + '");'
				else:
					txt1 = _imports(path1, roots[:])
				body = body.replace(tag, brs + txt1)
			return body
		elif len(roots)>1:
			#
			# ファイルなし
			#
			if ext=='html':
				return '<ins>NotFound:' + path + '</ins>'
			else:
				return 'console.log("NotFound:' + path + '");'
		else:
			#
			# 始祖ファイルなし -> "404 Not Found"
			#
			return False
	# ---------------------------------------------------------------- /_imports
	#
	# main
	#
	return _imports(path, roots=[])