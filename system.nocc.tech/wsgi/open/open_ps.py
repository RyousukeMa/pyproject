# -*- coding: utf-8 -*-

import time
import os

import blossom
import matsuoka_func


#
#
# main
#
#
def main(web, build):
	# --------------------------------------------------------------------------
	#
	#
	try:
		path = "../resource/PS/scale3"
		scale3 = os.listdir(path)
	except:
		web.log('miss')
		scale3 = []
	try:
		path = "../resource/PS/scale2"
		scale2 = os.listdir(path)
	except:
		web.log('miss')
		scale2 = []
	try:
		path = "../resource/PS/gs"
		gs = os.listdir(path)
	except:
		web.log('miss')
		gs = []
	# --------------------------------------------------------------------------
	#
	# build
	#
	local = {
		'scale3' : scale3,
		'scale2' : scale2,
		'gs'     : gs,
	}
	return build(web, local, '/open/open.ps.html')
