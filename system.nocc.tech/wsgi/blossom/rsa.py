# -*- coding: utf-8 -*-

from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

class RSACipher(object):
	def __init__(self, prikey, pubkey):
		self.prikey = prikey
		self.pubkey = pubkey
		self.decode_cipher = None
		self.encode_cipher = None
	
	def encrypt(self, raw):
		if not self.encode_cipher:
			self.encode_cipher = PKCS1_OAEP.new(RSA.importKey(self.pubkey))
		enc = b''
		while raw:
			enc += self.encode_cipher.encrypt(raw[:214])
			raw = raw[214:]
		return enc
	
	def decrypt(self, enc):
		if not self.decode_cipher:
			self.decode_cipher = PKCS1_OAEP.new(RSA.importKey(self.prikey))
		raw = b''
		while enc:
			raw += self.decode_cipher.decrypt(enc[:256])
			enc = enc[256:]
		return raw
	
	@staticmethod
	def keys():
		rsa = RSA.generate(2048, randfunc=Random.new().read)
		return rsa.exportKey().decode(), rsa.publickey().exportKey().decode()