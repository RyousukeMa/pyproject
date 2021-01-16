# -*- coding: utf-8 -*-

#
#
# base58
#
#
def base58(num):
	if num<0:
		return ''
	char58 = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
	encode = ''
	while num>=58:
		encode = char58[num%58] + encode
		num = int(num/58)
	return char58[num] + encode if num else encode

#
#
# json
#
#
import json as lib_json
import re
def json(data, alt=None):
	if isinstance(data, str) or alt is not None:
		try:
			data = re.sub(r'^\t*#.*', '', data, flags=re.M)
			return lib_json.loads(data)
		except:
			return alt
	else:
		return lib_json.dumps(data, separators=(',', ':'))

#
#
# md5
#
#
import hashlib
def md5(data, length=None):
	if not isinstance(data, str):
		data = str(data)
	if length is None:
		return hashlib.md5(data.encode()).hexdigest()
	else:
		return hashlib.md5(data.encode()).hexdigest()[-length:]

#
#
# num
#
#
import locale
import re
def num(num, places=0):
	num = locale.format("%.*f", (places, num), True)
	num = num.split('.')
	num[0] = re.sub(r'(\d+?)(?=(?:\d{3})+$)', r'\1,', num[0])
	return '.'.join(num)

#
#
# unicode
#
#
def unicode(data):
	for enc in ('euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'shift_jis', 'shift_jis_2004','shift_jisx0213'):
		try:
			return data.decode(enc), enc
		except:
			pass
	return data.decode(errors='replace'), None

#
#
# urlenc
#
#
import urllib.parse
def urlenc(data):
	data = str(data)
	try:
		return urllib.parse.quote(data)
	except:
		return None
def urldec(data):
	try:
		return urllib.parse.unquote(data)
	except:
		return None

#
#
# ひらがな変換, カタカナ変換
#
#
import re
def make_function_hiragana():
	compiled = re.compile(r'[ァ-ヴ]')
	def func(txt):
		return compiled.sub(lambda x: chr(ord(x.group(0))-0x60), txt)
	return func
def make_function_katakana():
	compiled = re.compile(r'[ぁ-ゔ]')
	def func(txt):
		return compiled.sub(lambda x: chr(ord(x.group(0))+0x60), txt)
	return func
