# -*- coding: utf-8 -*-

import math

#
#
# pagenav
#
#
def pagenav(pagemax, cur=0, shown=7, skip=10):
	#
	# pagemax = found_rows/page
	#
	if pagemax<=1:
		return []
	pagemax = math.ceil(pagemax)
	#
	# cur 変換 (開始0 -> 開始1)
	#
	cur += 1
	half = math.floor(shown/2)
	items = []
	#
	# fst
	#
	# 左端の数値 i を算出してから
	# それと cur の距離を評価し、独立表示させるかどうか判定する。
	#
	i = max(1, math.floor(min(cur-half, pagemax-shown)/10)*10)
	if cur>i+half and pagemax>shown:
		items.append({
			'i'  :i,
			'css':'fst',
		})
	#
	# prv, cur, nxt
	#
	i = max(1, min(cur-half, pagemax-shown+1) + len(items))
	while i<=pagemax and len(items)<shown:
		items.append({
			'i'  :i,
			'css':'prv' if i<cur else 'nxt' if i>cur else 'cur',
		})
		i += 1
	#
	# end
	#
	i = min(pagemax, math.floor((cur+half-1)/10)*10+skip)
	if i!=items[-1]['i']:
		items[-1] = {
			'i'  :i,
			'css':'end',
		}
	return items