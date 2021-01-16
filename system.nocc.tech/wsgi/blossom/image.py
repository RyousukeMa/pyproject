# -*- coding: utf-8 -*-

from io import BytesIO
from PIL import Image

#
# (対策) IOError: image file is truncated (0 bytes not processed)
#
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import math

#
#
# resize
#
# q 指定あり: jpeg
# q 指定なし: png
#
#
def resize(web, body, w=None, h=None, q=None, longside=None):
	#
	# 画像処理
	#
	try:
		im = Image.open(BytesIO(body))
	except:
		return False
	#
	# orientation
	#
	try:
		orientation = im._getexif().get(0x112, 1)
	except:
		orientation = 0
	if orientation>=2:
		func = {
			2:lambda img:img.transpose(Image.FLIP_LEFT_RIGHT),
			3:lambda img:img.transpose(Image.ROTATE_180),
			4:lambda img:img.transpose(Image.FLIP_TOP_BOTTOM),
			5:lambda img:img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90),
			6:lambda img:img.transpose(Image.ROTATE_270),
			7:lambda img:img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270),
			8:lambda img:img.transpose(Image.ROTATE_90),
		}
		im = func[orientation](im)
	web.log('orientation = ' + str(orientation), 'purple')
	#
	# size
	#
	if w or h or longside:
		w0, h0 = im.size
		web.log('w0, h0 = {0}, {1}'.format(w0, h0), 'purple')
		#
		# longside が指定されている場合は w, h を無視して、
		# 変更後の長辺が longside となるように変更後の短辺を算出する。
		#
		if longside:
			if w0>=h0:
				w1, h1 = longside, round(h0*longside/w0)
			else:
				w1, h1 = round(w0*longside/h0), longside
		else:
			if w:
				w1, h1 = w, h or round(h0*w/w0)
			else:
				w1, h1 = w or round(w0*h/h0), h
		web.log('w1, h1 = {0}, {1}'.format(w1, h1), 'purple')
		#
		# crop
		#
		# thumbnail() の結果は指定した高さ h1 を下回ることがある。
		# これを防ぐために、切り抜いてできる画像の高さ h_ を
		# math.ceil() によって w1 よりも少しだけ大きめにする。
		#
		if w0!=w1 or h0!=h1:
			if w1/w0<h1/h0:
				w_ = w1*h0/h1
				offset = round((w0-w_)/2)
				im = im.crop((offset, 0, offset+w_, h0))
				web.log('左右カット offset = {0}'.format(offset), 'purple')
				web.log('切り抜き後 {0}, {1}'.format(w_, h0), 'purple')
			elif w1/w0>h1/h0:
				h_ = math.ceil(h1*w0/w1)
				offset = round((h0-h_)/5)
				im = im.crop((0, offset, w0, offset+h_))
				web.log('上下カット offset = {0}'.format(offset), 'purple')
				web.log('切り抜き後 {0}, {1}'.format(w0, h_), 'purple')
		#
		# thumbnail
		#
		im.thumbnail((w1, h1), Image.ANTIALIAS)
	#
	# save
	#
	im = im.convert('RGB')
	with BytesIO() as f:
		im.save(f, 'jpeg' if q else 'png', quality=q)
		im.close()
		body = f.getvalue()
	return body