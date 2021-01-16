# -*- coding: utf-8 -*-

import dns.resolver
import json
import re
import smtplib
import socket
import time

from email.mime.text import MIMEText

#
#
# Mail
#
#
class Mail(object):
	#
	# .mx()
	#
	# 成功時: MX
	# 失敗時: False
	#
	@staticmethod
	def mx(addr):
		if '@' not in addr:
			return False
		fqdn = re.sub(r'^.+?@(.+)$', r'\1', addr) + '.'
		try:
			mxs = dns.resolver.query(fqdn, 'MX')
		except:
			return False
		for mx in mxs:
			#
			# "10 alt1.gmail-smtp-in.l.google.com."
			#
			return mx.to_text().split(' ')[-1][:-1]
		return False
	
	#
	# @gmail.com 正規化
	#
	@staticmethod
	def sanitize(addr):
		name, domain = addr.lower().split('@')
		if domain=='gmail.com':
			name = name.split('+')[0].replace('.', '')
		return name + '@' + domain
	
	#
	# 連投対策
	#
	@staticmethod
	def ratelimit(addr):
		FILE = '/tmp/blossom.Mail.ratelimit.log'
		now8 = time.time()
		#
		# load
		#
		try:
			with open(FILE, 'rb') as f:
				log = f.read()
			log = log.decode()
			log = json.loads(log)
		except:
			log = {}
		#
		# gc
		#
		for when in list(log):
			if float(when) < now8-3600:
				del log[when]
		#
		# ratelimit
		#
		if list(log.values()).count(addr) >= 3:
			return True
		#
		# append, save
		#
		log[now8] = addr
		log = json.dumps(log, separators=(',', ':'))
		log = log.encode()
		with open(FILE, 'wb') as f:
			f.write(log)
		return False
	
	#
	# .send()
	#
	# 成功時: True
	# 失敗時: エラーメッセージ
	#
	@staticmethod
	def send(text):
		head, body = tuple(text.split('\n\n', 1))
		encoding = 'iso-2022-jp'
		msg = MIMEText(body.encode(encoding, 'ignore'), 'plain', encoding)
		for line in head.split('\n'):
			key, val = tuple(line.split(':', 2))
			msg[key] = val
		#
		# 送信
		#
		# msg[Return-Path] は無視され、第１引数の値が Return-Path の値となる。
		#
		try:
			smtp = smtplib.SMTP()
			smtp.connect()
			smtp.sendmail(
				msg.get('Return-Path') or msg.get('From'),
				msg.get('To'),
				msg.as_string())
			smtp.close()
			return True
		except Exception as e:
			return e