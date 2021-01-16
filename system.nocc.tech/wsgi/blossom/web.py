# -*- coding: utf-8 -*-

import gzip
import hashlib
import html
import re
import time
import urllib.parse
from datetime import datetime


#
#
# Web
#
#
class Web(object):
	#
	# __init__
	#
	def __init__(self, environ, start_response):
		self.start_response = start_response
		self.start_time = time.time()
		self.__logging = False
		self._log = []
		#
		# url
		#
		self.url = (environ.get('wsgi.url_scheme', '')
			+ '://' + environ.get('HTTP_HOST', '')
			+ environ.get('REQUEST_URI', ''))
		#
		# environ
		#
		self._environ = environ
		#
		# cookie
		#
		self._cookie = {}
		http_cookie = environ.get('HTTP_COOKIE', '')
		if http_cookie:
			http_cookie = re.sub(r';\s*', '&', http_cookie)
			http_cookie = urllib.parse.parse_qs(http_cookie, keep_blank_values=True)
			self._cookie = {key: val[0] for key, val in http_cookie.items()}
		#
		# get
		#
		self._get = {}
		qs = environ.get('QUERY_STRING', '')
		if qs:
			qs = urllib.parse.parse_qs(qs, keep_blank_values=True)
			self._get = {key: val[0] for key, val in qs.items()}
		#
		# post
		#
		self._post = {}
		content_length = environ.get('CONTENT_LENGTH')
		try:
			content_length = int(content_length)
		except:
			content_length = 0
		if content_length:
			post = environ['wsgi.input'].read(content_length)
			content_type = environ.get('CONTENT_TYPE')
			if content_type.startswith('multipart/'):
				#
				# multipart/form-data; boundary=(boundary)
				#
				m = re.search(r'boundary="?([^";\s]+)', content_type, re.I)
				if m:
					for part in post.split(('--' + m.group(1)).encode())[1:-1]:
						try:
							head, body = part.split(b'\r\n\r\n', 1)
						except:
							continue
						head = head.decode(errors='ignore')
						body = body.rstrip(b'\r\n')
						m0 = re.search(r'name="(.+?)"', head, re.I)
						if not m0:
							continue
						m1 = re.search(r'Content-Type:\s*([^;\s]+)', head, re.I)
						if m1:
							m2 = re.search(r'filename="(.+?)"', head, re.I)
							self._post[m0.group(1)] = {
								'Content-Type':m1.group(1),
								'filename'    :m2.group(1) if m2 else None,
								'body'        :body,
							}
						else:
							self._post[m0.group(1)] = body.decode()
			else:
				#
				# application/x-www-form-urlencoded
				#
				post = post.decode(errors='ignore')
				post = urllib.parse.parse_qs(post, keep_blank_values=True)
				self._post = {key: val[0] for key, val in post.items()}
		#
		# 出力パラメータ
		#
		self.statuscode = None
		self.__redirect = None
		self.__setheaders = {}
		self.__setcookies = {}
		#
		# サーバ側が Last-Modified: を出力すると、ブラウザは次回アクセス時に If-Modified-Since: をリクエストしてくるため 304 Not Modified での応答ができる。
		#
		self.last_modified = None
		#
		# self.maxage = None : 指定なし
		# self.maxage = 0    : Cache-Control: no-cache
		# self.maxage = *    : Cache-Control: max-age=
		#
		self.maxage = None
		#
		# __init__ の最後に実行。以後未知の属性については __getattr__ がコールされる。
		#
		self.__variables = []

	#
	# 汎用変数コンテナ
	#
	def __getattr__(self, name):
		if '__variables' in self.__dict__:
			if name in self.__variables:
				return self.__variables[name]
			else:
				return None
		else:
			try:
				super().__getattr__(name)
			except:
				return None

	def __setattr__(self, name, value):
		if '__variables' in self.__dict__:
			self.__variables[name] = value
		else:
			super().__setattr__(name, value)

	def __delattr__(self, name):
		try:
			del self.__variables[name]
		except:
			pass

	#
	# .logging
	#
	@property
	def logging(self):
		return self.__logging

	@logging.setter
	def logging(self, enable):
		if enable:
			#
			# (有効化)
			#
			self.__logging = True
			#
			# 開発中は速度を重視しないため敢えて内包表記していない。
			#
			if len(self._log)==0:
				text = ['web.url = ' + self.url]
				for key in sorted(self._environ):
					val = self._environ[key]
					text.append('web.environ[{0}] = {1}'.format(key, val))
				for key in sorted(self._cookie):
					val = self._cookie[key]
					text.append('web.cookie[{0}] = {1}'.format(key, val))
				for key in sorted(self._get):
					val = self._get[key]
					text.append('web.get[{0}] = {1}'.format(key, val))
				for key in sorted(self._post):
					val = self._post[key]
					if isinstance(val, dict):
						for k, v in val.items():
							text.append('web.post[{0}][{1}] = {2}'.format(key, k, v))
					else:
						text.append('web.post[{0}] = {1}'.format(key, val))
				self._log.append([time.time(), "\n".join(text), 'steelblue'])
		else:
			#
			# (無効化)
			#
			self.__logging = False

	#
	# .log()
	#
	def log(self, value, color=None):
		#
		# _dump()
		#
		def _dump(prefix, value):
			text = ''
			if isinstance(value, dict):
				for key in sorted(value):
					text += _dump(prefix + '[' + str(key) + ']', value[key])
			elif isinstance(value, (list, tuple)):
				for i, val in enumerate(value):
					text += _dump(prefix + '[' + str(i) + ']', val)
			elif prefix:
				text = prefix + ' = ' + str(value) + "\n"
			else:
				text = str(value)
			return text
		#
		# append
		#
		if self.__logging:
			self._log.append([time.time(), _dump('', value), color])

	#
	# .environ()
	# .cookie()
	# .get()
	# .post()
	#
	def _find(self, haystack, key, alt):
		try:
			val = haystack[key]
			if type(alt) is int:
				return int(val)
			elif type(alt) is float:
				return float(val)
			else:
				return val
		except:
			return alt

	def environ(self, key, alt=''):
		return self._find(self._environ, key, alt)

	def cookie(self, key, alt=''):
		return self._find(self._cookie, key, alt)

	def get(self, key, alt=''):
		return self._find(self._get, key, alt)

	def post(self, key, alt=''):
		return self._find(self._post, key, alt)

	#
	# .setheader()
	#
	# e.g.
	#	web.setheader('Content-Encoding: gzip')
	#
	def setheader(self, text):
		match = re.split(':', text, maxsplit=1)
		try:
			self.__setheaders[match[0]] = match[1].strip()
		except:
			pass

	#
	# .setcookie()
	#
	# e.g.
	#	web.setcookie('foo', 'bar', maxage=3600)
	#	web.setcookie('foo')                     # 削除
	#
	# Domain は未指定状態こそ最も限定的 → "Domain=mozilla.org を設定すると、developer.mozilla.org のようなサブドメインも含まれます。"
	#
	# 異なるパスであれば同名のCookieが複数同時に指定される可能性も考慮する。
	#
	def setcookie(self, name, value=None, maxage=None, domain=None, path='/', http_only=True, same_site='Strict'):
		text = urllib.parse.quote(name.encode()) + '='
		#
		# SET or UNSET
		#
		if value:
			text += urllib.parse.quote(value)
			if isinstance(maxage, int) and maxage>0:
				text += '; Max-Age=' + str(maxage)
		else:
			text += '; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
		#
		# Domain, Path
		#
		scope = ''
		if isinstance(domain, str):
			scope += '; Domain=' + domain
		if isinstance(path, str):
			scope += '; Path=' + path
		#
		# option (HttpOnly, Secure, SameSite)
		#
		option = ''
		if http_only:
			option += '; HttpOnly'
		if self._environ['wsgi.url_scheme']=='https':
			option += '; Secure'
			if same_site in ('Strict', 'Lax'):
				option += '; SameSite=' + same_site
			else:
				option += '; SameSite=None'
		self.__setcookies[name + scope] = text + scope + option

	#
	# 改ざん防止 cookie
	#
	def setcookie_secure(self, name, value, maxage, domain=None, path='/'):
		value = hex(int(self.start_time + maxage))[2:] + '.' + value
		value = hashlib.md5(value.encode()).hexdigest()[-8:] + '.' + value
		self.setcookie(name, value, maxage, domain, path)

	def getcookie_secure(self, name):
		value = self.cookie(name)
		if value.count('.')>=2:
			checksum, value = value.split('.', 1)
			if checksum==hashlib.md5(value.encode()).hexdigest()[-8:]:
				expiry, value = value.split('.', 1)
				if int(expiry, 16)>=self.start_time:
					return value
		return None

	#
	# .if_modified_since()
	#
	# e.g.
	#	modified = web.if_modified_since(os.stat(file).st_mtime)
	#	if not modified:
	#		return web.echo(b'')
	#
	def if_modified_since(self, last_modified):
		if isinstance(last_modified, (int, float)) and last_modified>0:
			#
			# If-Modified-Since: Wed, 21 Oct 2015 07:28:00 GMT
			#
			since = 0
			try:
				since = self._environ['HTTP_IF_MODIFIED_SINCE']
				since = datetime.strptime(since, '%a, %d %b %Y %H:%M:%S %Z')
				since = time.mktime(since.timetuple()) - time.altzone
			except:
				pass
			#
			# 304 Not Modified (1秒未満を切り捨てるため整数化して比較)
			#
			if since>=int(last_modified):
				self.statuscode = 304
				return False
			#
			# Last-Modified 設定
			#
			self.last_modified = last_modified
		return True

	#
	# .redirect()
	#
	# e.g.
	#	web.redirect('http://example.com/dir/file.html')
	#	web.redirect('/dir/file.html?message=applied')
	#	web.redirect('?message=applied')
	#	web.redirect('&message=applied')
	#	web.redirect('?')
	#	web.redirect()
	#
	def redirect(self, url=None, use_javascript=False):
		#
		# url
		#
		if type(url) is list:
			self.__redirect = self.urljoin(url)
		elif url:
			self.__redirect = self.urljoin([url])
		else:
			self.__redirect = self.url
		#
		# 転送
		#
		if use_javascript:
			#
			# (特殊な転送)
			#
			# t.co をモデルにした転送方式。location.href を使用するため、現在のURLが遷移先のページにとってのリンク元になる（location.replace() はリンク元を残さないためここで使用してはいけない）。
			#
			body = html.escape(self.__redirect)
			body = """
			<head>
				<meta name="referrer" content="always">
				<noscript>
					<meta http-equiv="refresh" content="0;URL=""" + body + """">
				</noscript>
				<title>refresh</title>
			</head>
			<script>
				window.opener=null;
				location.href='""" + self.__redirect.replace("'", r"\'") + """';
			</script>
			"""
			body = body.replace("\n", '').replace("\t", '')
			return self.echo(body=body)
		else:
			#
			# (一般的な転送)
			#
			# 現在のURLが遷移先のページにとってのリンク元にはならない。
			#
			self.__setheaders['Location'] = self.__redirect
			return self.echo(statuscode=303)

	#
	# .urljoin()
	#
	# 単にクエリ値を合成するなら urllib.parse.urljoin で解決するが
	# この関数では値が None のものをキーごと削除し、さらにキー名で
	# ソートされた結果を返す。
	#
	def urljoin(self, layers=[]):
		#
		# /dir?foo=bar → (/dir, {foo:bar})
		#
		def _parse_url(url):
			if '?' in url:
				url, query = url.split('?', 1)
				return url, _parse_qs(query)
			else:
				return url, {}
		#
		# foo=bar&baz=qux → {foo:bar, baz=qux}
		#
		def _parse_qs(query_string):
			qs = urllib.parse.parse_qs(query_string, keep_blank_values=True)
			return {k:v[0] for k, v in qs.items()}
		#
		# [?q=old&foo=bar&baz=qux, {q:new,foo:None}] -> baz=qux&q=new
		#
		def _query_join(qs, q2):
			qs.update(q2)
			qs = dict(filter(lambda q: q[1] is not None, qs.items()))
			return qs
		#
		# 合成
		#
		base, qs = _parse_url(self.url)
		for layer in layers:
			if type(layer) is dict:
				qs = _query_join(qs=qs, q2=layer)
			elif layer[0]=='&':
				qs = _query_join(qs=qs, q2=_parse_qs(layer[1:]))
			elif layer[0]=='?':
				qs = _parse_qs(layer[1:])
			else:
				url = base + '?' + urllib.parse.urlencode(qs)
				if layer[0] in ('.', '/'):
					url = urllib.parse.urljoin(url, layer)
				else:
					url = layer
				base, qs = _parse_url(url)
		#
		# ソート
		#
		if qs:
			qs = {k:urllib.parse.quote(str(v)) for k, v in qs.items()}
			qs = '&'.join([k + '=' + qs[k] for k in sorted(qs)])
			return base + '?' + qs
		else:
			return base

	#
	# .echo()
	#
	# e.g.
	#	HTMLを指定する場合
	#	web.echo(body=html)
	#
	# e.g.
	#	画像を指定する場合
	#	web.setheader('Content-Type: image/jpeg')
	#	web.echo(body=binary)
	#
	# e.g.
	#	すでに gzip 圧縮されているデータを指定する場合
	#	web.setheader('Content-Encoding: gzip')
	#	web.echo(body=gzip)
	#
	# e.g.
	#	ファイルが見つかりません 404 Not Found
	#	web.echo(body=text, statuscode=404)
	#
	def echo(self, body=None, statuscode=None):
		#
		# ステータスコード
		#
		if statuscode:
			self.statuscode = statuscode
		#
		# Content-Type:
		#	303 (None) と 304 (b'') には Content-Type を指定しない
		#
		if 'Content-Type' not in self.__setheaders and body:
			self.__setheaders['Content-Type'] = 'text/html'
		#
		# Cache-Control:
		#
		if isinstance(self.maxage, int):
			if self.maxage:
				self.__setheaders['Cache-Control'] = 'max-age=' + str(self.maxage)
				self.__setheaders['Expires'] = datetime.utcfromtimestamp(time.time()+self.maxage).strftime('%a, %d %b %Y %H:%M:%S GMT')
			else:
				self.__setheaders['Cache-Control'] = 'no-store, no-cache, must-revalidate'
				self.__setheaders['Pragma'] = 'no-cache'
		#
		# Last-Modified:
		#
		if isinstance(self.last_modified, (int, float)):
			self.__setheaders['Last-Modified'] = datetime.utcfromtimestamp(self.last_modified).strftime('%a, %d %b %Y %H:%M:%S GMT')
		#
		# P3P:
		#
		if len(self.__setcookies):
			self.__setheaders['P3P'] = 'CP="UNI PSA OUR"'
		#
		# レポート化
		#
		if self.__logging:
			body = self.__report(body)
		#
		# バイナリ化
		#
		if isinstance(body, str):
			body = body.encode()
			#
			# 圧縮
			#
			if 'Content-Encoding' not in self.__setheaders \
				and 'HTTP_ACCEPT_ENCODING' in self._environ \
				and 'gzip' in self._environ['HTTP_ACCEPT_ENCODING']:
				self.__setheaders['Content-Encoding'] = 'gzip'
				body = gzip.compress(body, compresslevel=1)
		#
		# 出力
		#
		headers = [(key, val) for key, val in self.__setheaders.items()]
		headers += [('Set-Cookie', text) for text in self.__setcookies.values()]
		self.start_response(self.statustext(self.statuscode), headers)
		return [body]

	#
	# .report()
	#
	def __report(self, body):
		#
		# 出力の内容をログに追加する
		#
		output = [self.statustext(self.statuscode)]
		output += [key + ': ' + val for key, val in self.__setheaders.items()]
		output += ['Set-Cookie: ' + text for text in self.__setcookies.values()]
		output.sort()
		output = "\n".join(output)
		if isinstance(body, str):
			output += '\n\n' + body
		elif isinstance(body, bytes):
			output += '\n\n(' + str(len(body)) + 'bytes)'
		self._log.append([time.time(), output, 'steelblue'])
		#
		# <table> 生成
		#
		log = ''
		if self.__redirect:
			url = html.escape(self.__redirect)
			log += '<tr><td>+<td><a href="' + url + '">' + url + '</a>'
		if len(self._log):
			for row in self._log:
				log += '<tr><td>' + '%.4f' % (row[0] - self.start_time)
				log += '<td style="color:' + row[2] + ';">' if row[2] else '<td>'
				log += html.escape(row[1]).replace("\n", '<br>')
		log = """
		<div id="blossom">
			<style scoped="scoped">
				#blossom table {
					border:0;
					border-spacing:0;
					border-collapse:collapse;
				}
				#blossom td {
					font:9pt/110% 'MS Gothic',Osaka-Mono,Courier,monospace;
					color:#000;
					background:#fff;
					padding:0;
				}
				#blossom td:nth-child(1) {
					padding:0 .4em;
					white-space:nowrap;
					vertical-align:top;
				}
				#blossom td:nth-child(2) {
					word-break:break-all;
				}
				#blossom a {
					color:#00f;
					text-decoration:none;
				}
				#blossom a:hover {
					color:#f00;
				}
			</style>
			<table>
				<tbody>
					""" + log + """
			</table>
		</div>
		"""
		log = log.replace('\n', '').replace('\t', '')
		#
		# <table> 挿入 or 丸ごと置換
		#
		if 'Content-Type' in self.__setheaders \
			and self.__setheaders['Content-Type'].startswith('text/html') \
			and 'Content-Encoding' not in self.__setheaders \
			and body:
			#
			# text/html (無圧縮) の場合は </body> の直前に挿入する
			#
			if '</body>' in body:
				try:
					body = re.sub('</body>', log + '</body>', body, flags=re.I)
				except:
					body = body + log
			else:
				body = body + log
		elif ('report' in self._get and self._get['report']=='on') or body is None:
			#
			# ?report=on
			# あるいは 303 (body is None) の場合は、コンテンツを丸ごと置き換える。
			#
			# ちなみに 304 は body is None ではなく b'' であり、
			# 同じゼロデータでもここでのログ出力の対象とししてはいけない。
			#
			body = """
			<!DOCTYPE html>
			<html lang="ja-JP">
				<head>
					<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
					<meta name="format-detection" content="telephone=no">
					<meta name="viewport" content="width=device-width">
					<style>
						body
						{
							margin:0;
						}
					</style>
					<title>""" + html.escape(self.url) + """</title>
				</head>
				<body>""" + log + """</body>
			</html>
			"""
			body = body.replace('\n', '').replace('\t', '')
			#
			# レスポンスヘッダ修正 (転送キャンセル, 圧縮キャンセル, text/html)
			#
			self.statuscode = 200
			self.__setheaders['Content-Type'] = 'text/html'
			if 'Content-Disposition' in self.__setheaders:
				del self.__setheaders['Content-Disposition']
			if 'Content-Encoding' in self.__setheaders:
				del self.__setheaders['Content-Encoding']
			if 'Location' in self.__setheaders:
				del self.__setheaders['Location']
		#
		# レスポンスヘッダ修正 (キャッシュ無効)
		#
		self.maxage = 0
		return body

	#
	# 200 -> "200 OK"
	#
	def statustext(self, statuscode=None):
		#
		# ステータスコード
		#
		statustexts = {
			100:'Continue',
			101:'Switching Protocols',
			102:'Processing',
			200:'OK',
			201:'Created',
			202:'Accepted',
			203:'Non-Authoritative Information',
			204:'No Content',
			205:'Reset Content',
			206:'Partial Content',
			207:'Multi-Status',
			208:'Already Reported',
			226:'IM Used',
			300:'Multiple Choices',
			301:'Moved Permanently',
			302:'Found',
			303:'See Other',
			304:'Not Modified',
			305:'Use Proxy',
			307:'Temporary Redirect',
			308:'Permanent Redirect',
			400:'Bad Request',
			401:'Unauthorized',
			402:'Payment Required',
			403:'Forbidden',
			404:'Not Found',
			405:'Method Not Allowed',
			406:'Not Acceptable',
			407:'Proxy Authentication Required',
			408:'Request Timeout',
			409:'Conflict',
			410:'Gone',
			411:'Length Required',
			412:'Precondition Failed',
			413:'Payload Too Large',
			414:'URI Too Long',
			415:'Unsupported Media Type',
			416:'Range Not Satisfiable',
			417:'Expectation Failed',
			418:'I\'m a teapot',
			421:'Misdirected Request',
			422:'Unprocessable Entity',
			423:'Locked',
			424:'Failed Dependency',
			426:'Upgrade Required',
			451:'Unavailable For Legal Reasons',
			500:'Internal Server Error',
			501:'Not Implemented',
			502:'Bad Gateway',
			503:'Service Unavailable',
			504:'Gateway Timeout',
			505:'HTTP Version Not Supported',
			506:'Variant Also Negotiates',
			507:'Insufficient Storage',
			508:'Loop Detected',
			509:'Bandwidth Limit Exceeded',
			510:'Not Extended',
		}
		if statuscode not in statustexts:
			statuscode = 200
		return str(statuscode) + ' ' + statustexts[statuscode]
