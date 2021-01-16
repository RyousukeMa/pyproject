# -*- coding: utf-8 -*-

import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):
	def __init__(self, password, block_size=16):
		self.block_size = block_size
		self.key = hashlib.md5(password.encode()).hexdigest()
	
	def encrypt(self, raw):
		iv = Random.new().read(self.block_size)
		shortage = self.block_size - len(raw)%self.block_size
		raw = raw + (chr(shortage) * shortage).encode()
		return iv + AES.new(self.key, AES.MODE_CBC, iv).encrypt(raw)
	
	def decrypt(self, enc):
		iv = enc[:self.block_size]
		enc = enc[self.block_size:]
		dec = AES.new(self.key, AES.MODE_CBC, iv).decrypt(enc)
		return dec[:-ord(dec[-1:])]