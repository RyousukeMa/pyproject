# -*- coding: utf-8 -*-

#
# class
#
from . import web
Web = web.Web

from . import mysql
MySQL = mysql.MySQL

from . import mail
Mail = mail.Mail

from . import aes
AESCipher = aes.AESCipher

from . import rsa
RSACipher = rsa.RSACipher

#
# function
#
from . import pagenav
pagenav = pagenav.pagenav

from . import template
template = template.template

from . import assemble
assemble = assemble.assemble

from . import io
read = io.read
write = io.write
glob = io.glob

from . import net
domain = net.domain
nslookup = net.nslookup
ip = net.ip

from . import string
base58 = string.base58
json = string.json
md5 = string.md5
num = string.num
unicode = string.unicode
urlenc = string.urlenc
urldec = string.urldec
hiragana = string.make_function_hiragana()
katakana = string.make_function_katakana()