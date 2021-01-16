# -*- coding: utf-8 -*-

#
#
# domain
#
#
import re
def domain(host):
	try:
		host = host.encode('idna').decode()
	except:
		return ''
	m = re.search(r'[^.]+\.(ac|ad|com?|edu?|gov?|gr|lg|mil|net?|org?)\.[a-z]{2}$', host, re.I) or re.search(r'[^.]+\.[-\w]{2,}$', host, re.I)
	return m.group(0) if m else host

#
#
# nslookup
#
#
import socket
def nslookup(src):
	if src.count('.')==3 and src.replace('.', '').isnumeric():
		try:
			return socket.gethostbyaddr(src)[0]
		except:
			return False
	else:
		try:
			return socket.gethostbyname(src)
		except:
			return False
#
#
# ip
#
#
from struct import pack
from struct import unpack
from socket import inet_ntoa
from socket import inet_aton
def ip(src):
	if isinstance(src, str):
		if '.' in src:
			return unpack('!L', inet_aton(src))[0]
		if src.isnumeric():
			return inet_ntoa(pack('!L', int(src)))
	if isinstance(src, int):
		return inet_ntoa(pack('!L', src))
	return False