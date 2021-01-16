# -*- coding: utf-8 -*-

import os
import re

#
#
# read
#
#
def read(path, raw=False):
	try:
		with open(path, 'rb') as f:
			data = f.read()
	except IOError:
		return None
	if not raw:
		try:
			data = data.decode()
		except:
			pass
	return data

#
#
# write
#
#
def write(path, data):
	if isinstance(data, str):
		data = data.encode()
	try:
		os.makedirs(os.path.dirname(path))
	except:
		pass
	with open(path, 'wb') as f:
		f.write(data)

#
#
# glob
#
#
# ディレクトリ rootdir に含まれる全ファイルを取得する。
# 拡張子を限定する場合は ext にリストで指定する。
# 戻り値は dict でキーは rootdir から見たルート相対パスとなる。
#
#
def glob(rootdir, exts=[]):
	def _glob(top):
		ents = {}
		for dirpath, dirnames, filenames in os.walk(top, followlinks=True):
			for dirname in dirnames:
				abspath = os.path.join(top, dirname)
				ents.update(_glob(abspath))
			for filename in filenames:
				if not exts or filename.split('.')[-1].lower() in exts:
					abspath = os.path.join(top, filename)
					relpath = '/' + os.path.relpath(abspath, rootdir)
					ents[relpath] = read(abspath)
			break
		return ents
	return _glob(rootdir)