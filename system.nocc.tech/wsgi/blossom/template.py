# -*- coding: utf-8 -*-

#
# {name}     <- エスケープあり (default)
# {name:br}  <- エスケープあり + <br>
# {name:p}   <- エスケープあり + <p>...</p>
# {name:raw} <- エスケープなし
# {name:url} <- urlencode
# <!--{name}-->
# <!--{!name}-->
# <!--{name==value0,value1}--> ... <!--{/}-->
# <!--{name!=value0,value1}--> ... <!--{/}-->
# <!--{@array}--> ... {array/name} ... <!--{/}-->
#

import html
import re
import urllib.parse

#
#
# template
#
#
def template(src, vals, remove_ctrl_chars=True, remove_comment=True):
	#
	# .build()
	#
	def build(src, vals, indexlist):
		#
		# 制御タグ <!--{*}--> が現れるまで範囲 dst に含まれる変数 {*} を全展開する。ファイルの末尾に到達した場合は src=None となる。
		#
		dst, src = replace(src, vals, indexlist)
		#
		# src 冒頭の <!--{*}--> に応じた置換処理を行う
		#
		while src:
			tag = src[5:src.find('}-->')]
			src = src[len(tag) + 9:]
			if tag=='/':
				#
				# <!--{/}-->
				#
				# 次の制御タグ <!--{*}--> が出現するまで全ての変数を展開する
				#
				add, src = replace(src, vals, indexlist)
				dst += add
			elif tag and tag[0]=='@':
				#
				# <!--{@array}-->
				#
				val = find(vals, tag[1:], indexlist)
				if isinstance(val, list):
					sub, src = cut(src)
					for i in range(len(val)):
						indexlist2 = indexlist[:]
						indexlist2.append(i)
						add, xxx = build(sub, vals, indexlist2)
						dst += add
				else:
					xxx, src = cut(src)
			elif tag and tag[0]=='!':
				#
				# <!--{!name}-->
				#
				val = find(vals, tag[1:], indexlist)
				if val and val!='0':
					xxx, src = cut(src)
				else:
					add, src = replace(src, vals, indexlist)
					dst += add
			elif tag.find('==')>1:
				#
				# <!--{name==val0,val1}-->
				#
				tag = tag.split('==')
				val = find(vals, tag[0], indexlist)
				if str(val) in tag[1].split(','):
					add, src = replace(src, vals, indexlist)
					dst += add
				else:
					xxx, src = cut(src)
			elif tag.find('!=')>1:
				#
				# <!--{name!=val0,val1}-->
				#
				tag = tag.split('!=')
				val = find(vals, tag[0], indexlist)
				if str(val) not in tag[1].split(','):
					add, src = replace(src, vals, indexlist)
					dst += add
				else:
					xxx, src = cut(src)
			else:
				#
				# <!--{name}-->
				#
				val = find(vals, tag, indexlist)
				if val and val!='0':
					add, src = replace(src, vals, indexlist)
					dst += add
				else:
					xxx, src = cut(src)
		return dst, src
	
	#
	# .cut()
	#
	# 現階層を分離する。終了タグは後半部分に残す。
	# "foo<!--{/}-->bar" → ("foo", "<!--{/}-->bar")
	#
	def cut(src):
		depth = 1
		index = 0
		while True:
			index = src.find('<!--{', index)
			if index==-1:
				break
			index += 5
			tag = src[index:src.find('}-->', index)]
			depth += -1 if tag=='/' else 1
			if depth<1:
				index -= 5
				break
			index += len(tag) + 4
		return src[0:index], src[index:]
	
	#
	# .replace()
	#
	# "<!--{" が現れるまでの変数 {*} を全て置換する
	#
	def replace(src, vals, indexlist):
		#
		# "<!--{" が現れるまでを切り取り、処理の範囲を限定する
		#
		tmp = None
		index = src.find('<!--{')
		if index>=0:
			tmp, src = src[0:index], src[index:]
		else:
			tmp = src
			src = None
		#
		# 置換ペア作成
		#
		pair = {}
		for match in re.finditer(r'\{(\w[\w_/]*)(:raw|:url|:int|:br|:p)?\}', tmp):
			if not match.group(0) in pair:
				val = find(vals, match.group(1), indexlist)
				if val is None:
					val = ''
				elif isinstance(val, bool):
					val = 1 if val is True else 0
				else:
					val = str(val)
					func = match.group(2)
					if func==':raw':
						pass
					elif func==':int':
						val = re.sub(r'(\d+?)(?=(?:\d{3})+$)', r'\1,', val)
					elif func==':url':
						val = urllib.parse.quote(val)
					else:
						val = html.escape(val)
						val = val.replace('\r', '')
						if func==':p':
							val = re.sub(r'\n\n+', '</p><p>', val)
							val = '<p>' + val + '</p>'
							val = val.replace('\n', '<br>')
						elif func==':br':
							val = val.replace('\n', '<br>')
				pair[match.group(0)] = val
		#
		# 置換
		#
		for key, val in pair.items():
			tmp = tmp.replace(key, val if isinstance(val,str) else str(val))
		return tmp, src
	
	#
	# .find()
	#
	# 変数リスト vals の中から (tag, indexlist) の示す値を得る
	# 文字列化して返す
	#
	# e.g.
	#        vals = {
	#                 foo:{
	#                   bar:[
	#                     {baz:{qux:[0,1,2,3],},
	#                     {baz:{qux:[4,5,6,7],},
	#                   ],
	#                 },
	#               }
	#         tag = foo/bar/baz/qux
	#   lndexlist = [1, 2]
	#   ------------------------------------------
	#             = vals[foo][bar][1][baz][qux][2]
	#             = 6
	#
	def find(vals, tag, indexlist):
		indexlist2 = indexlist[:]
		ref = vals
		tag = tag.split('/')
		for key in tag:
			try:
				ref = ref[key]
				if isinstance(ref, (list, tuple)) and len(indexlist2):
					index, indexlist2 = indexlist2[0], indexlist2[1:]
					ref = ref[index]
			except:
				ref = ''
				break
		return ref
	
	#
	#
	# build
	#
	#
	txt, xxx = build(src, vals, [])
	#
	# \r\n -> \n
	#
	if remove_ctrl_chars or remove_comment:
		txt = re.sub(r'\r\n?', '\n', txt)
	#
	# (先) remove_ctrl_chars
	#
	# <script>(ここの内容)</script> にミニファイの影響が及ばないようにエスケープする。中央の値を (.+?) ではなく (.*?) としているのは、次のタグが連続２回出現した場合に正しくマッチさせる意図がある。
	# <script src=""></script>
	#
	# <pre> はインデント量(最初に現れるタブの連続)をオフセットとして各行の冒頭から除去する。。
	#
	if remove_ctrl_chars:
		for tag in ('pre', 'script', 'textarea'):
			pattern = '(<' + tag + r'\b.*?>)(.*?)(</' + tag + '>)'
			for match in re.finditer(pattern, txt, flags=re.I|re.S):
				sub = match.group(2)
				if sub:
					if tag=='pre':
						sub = re.sub(r'^\n+|\s+$', '', sub)
						m = re.search(r'^\s+', sub)
						if m:
							sub = re.sub(r'^' + m.group(0), '', sub, flags=re.M)
						sub = sub.replace('\t', '&BLOSSOMx9;')
						sub = sub.replace('\n', '&BLOSSOMxA;')
					elif tag=='script':
						sub = re.sub(r'^<!--|-->$', '\n', sub.strip()).strip()
						sub = sub.replace('\t', '')
					else:
						sub = sub.replace('\t', '&BLOSSOMx9;')
					sub = sub.replace('\n', '&BLOSSOMxA;')
					sub = match.group(1) + sub + match.group(3)
					txt = txt.replace(match.group(0), sub)
	#
	# (後) remove_comment
	#
	if remove_comment:
		#
		# <script><!--(ここ) を削除しないようにエスケープする。ただし先に制御文字の除去が行われている場合はすでに <!-- が除去されているのでその必要はない。
		#
		if not remove_ctrl_chars:
			txt = re.sub(r'(<script[^>]*>\s*)<!--(.+?)-->(\s*</script>)', r'\1&BLOSSOMx3C;!--\2--&BLOSSOMx3E;\3', txt, flags=re.I|re.S)
		txt = re.sub(r'\s*<!--.*?-->', '', txt, flags=re.S)
		if not remove_ctrl_chars:
			txt = txt.replace('&BLOSSOMx3C;', '<').replace('&BLOSSOMx3E;', '>')
	elif remove_ctrl_chars:
		#
		# コメント除去しない場合で、かつ制御文字の除去が指定されている場合は、領域末端の改行に続く空白の連続を除去する。そうすることで閉じタグ "-->" が行頭に来る。
		#
		for match in re.finditer('<!--(.*?)-->', txt, flags=re.S):
			sub = match.group(1)
			if re.search(r'\n\s*$', sub):
				sub = sub.rstrip() + '\n'
			sub = sub.replace('\t', '&BLOSSOMx9;')
			sub = sub.replace('\n', '&BLOSSOMxA;')
			txt = txt.replace(match.group(0), '<!--' + sub + '-->')
	#
	# 制御文字の除去 + アンエスケープ
	#
	if remove_ctrl_chars:
		txt = re.sub(r'\s*\n\s*', '', txt)
		txt = txt.replace('&BLOSSOMx9;', '\t').replace('&BLOSSOMxA;', '\n')
	return txt