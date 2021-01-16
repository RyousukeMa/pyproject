# -*- coding: utf-8 -*-

"""
[API署名の取得／live環境]
	ログイン後 → "ツール" → "ビジネスの設定"
	↓
	(2択) "オプションA PayPalに実装済みのeコマースソリューションと連携する"
	↓
	(2択) "API認証情報の取得"
	↓
	(2択) "オプション2 API認証情報を請求してAPIユーザー名とパスワードを作成します。"
	↓
	電話による本人確認

[API署名の取得／Sandbox環境]
	live環境（paypal.com）にログインしている状態でこちら↓にアクセスする。
	https://developer.paypal.com/
	↓
	ページ右上のアカウントのメニューから "Dashboard" へ移動する。
	https://developer.paypal.com/developer/applications/
	↓
	左側メニューから "Accounts" のページへ移動する。
	https://developer.paypal.com/developer/accounts/
	↓
	あらかじめ作られているアカウントの BUSINESS の方の "Profile" を選択
	↓
	"API Credencial" のページにて Username, Password, Signeture の3点を確認する。

[Sandbox]
	以前はLive環境の登録メールアドレスとは別にSandbox用のアカウントを作成できたが、現在はできない。Live環境でログインした状態で developer.paypal.com にアクセスしてSandbox環境を制御する。

[method]
	Sandboxは2017年からGET送信に未対応となりPOSTのみの対応となった。

[テクニカルサポート]
	https://jp.paypal-techsupport.com/app/ask
"""

import blossom

import math
import requests
import urllib.parse

#
#
# PayPal
#
#
class PayPal(object):
	#
	# __init__
	#
	def __init__(self, web, username, password, signature):
		live_or_sandbox = 'sandbox' if web.dev else 'live'
		#
		# API署名
		#
		self._username = username
		self._password = password
		self._signature = signature
		#
		# API エンドポイント
		# お支払いページ (転送先)
		#
		hostname = 'sandbox.paypal.com' if web.dev else 'paypal.com'
		self._endpoint = 'https://api-3t.' + hostname + '/nvp'
		self._webscr = ('https://www.' + hostname
			+ '/cgi-bin/webscr'
			+ '?cmd=_express-checkout'
			+ '&token=')
		#
		# log
		#
		web.log('self._endpoint = ' + self._endpoint, 'purple')
		web.log('self._webscr = ' + self._webscr, 'purple')
	
	#
	# [1/3] SetExpressCheckout
	#
	# ユーザが管理ページの支払いボタンを押した際の処理
	#	1. サーバから PayPal に "SetExpressCheckout" を送信する
	#	2. PayPal から TOKEN を含む nvp が返される
	#	3. TOKEN を含む PayPal の URL へ転送する
	#
	def set_express_checkout(self, web, amount, tax, itemcode, itemname, email, return_url, cancel_url):
		#
		# [1/3] SetExpressCheckout
		#
		# 自由な使用が許可された PAYMENTREQUEST_0_CUSTOM に商品コードを格納し
		# 後の GetExpressCheckoutDetails にてその値を得る。
		#
		nvp = {
			'METHOD'   :'SetExpressCheckout',
			'VERSION'  :93,
			'USER'     :self._username,
			'PWD'      :self._password,
			'SIGNATURE':self._signature,
			'RETURNURL':return_url,
			'CANCELURL':cancel_url,
			'EMAIL'    :email,
			'L_PAYMENTREQUEST_0_AMT0'         :amount,
			'L_PAYMENTREQUEST_0_NAME0'        :itemname,
			'L_PAYMENTREQUEST_0_QTY0'         :1,
			'L_PAYMENTREQUEST_0_TAXAMT0'      :0,
			'L_PAYMENTREQUEST_0_ITEMCATEGORY0':'Physical',
			'PAYMENTREQUEST_0_PAYMENTACTION'  :'Sale',
			'PAYMENTREQUEST_0_CURRENCYCODE'   :'JPY',
			'PAYMENTREQUEST_0_AMT'            :amount + tax,
			'PAYMENTREQUEST_0_ITEMAMT'        :amount,
			'PAYMENTREQUEST_0_TAXAMT'         :tax,
			'PAYMENTREQUEST_0_CUSTOM'         :itemcode,
			'NOSHIPPING':1,
			'LOCALECODE':'ja_JP',
		}
		web.log(nvp, 'purple')
		#
		# 送信
		#
		req = requests.post(url=self._endpoint, data=nvp)
		#
		#	TOKEN=EC-XXXXXXXXXX
		#	TIMESTAMP=2014-10-10T11:12:42Z
		#	CORRELATIONID=b2220b38a5117
		#	ACK=Success
		#	VERSION=93
		#	BUILD=13637230
		#
		text = req.text
		web.log(text, 'purple')
		try:
			nvp = urllib.parse.parse_qs(text)
			nvp = {k: v[0] for k, v in nvp.items()}
		except:
			nvp = {}
		web.log(nvp, 'purple')
		#
		# 評価
		#
		if nvp.get('ACK')=='Success':
			#
			# (成功)
			#
			return web.redirect(self._webscr + nvp.get('TOKEN'))
		else:
			#
			# メール通知
			#
			txt = blossom.read('../resource/eml/paypal.err1.eml')
			txt = txt % {
				'text':text,
			}
			web.log(txt, 'purple')
			lossom.Mail.send(txt)
			#
			# (失敗)
			#
			return web.redirect(cancel_url)
	
	#
	# [2/3] GetExpressCheckoutDetails
	# [3/3]  DoExpressCheckoutPayment
	#
	# ユーザが PayPal で支払いを終えて戻ってくるページの処理 (前半)
	#	1. このページのURLの末尾に付与された ?token=(TOKEN) を取得する
	#	2. サーバから PayPal に "GetExpressCheckoutDetails” を送信する
	#	3. PayPal から itemcode, PAYERID などが返される
	#	4. サーバから PayPal に "DoExpressCheckoutPayment” を送信する
	#	5. PayPal の応答を評価して次の形で評価を返す
	#
	#		    成功: itemcode ←┬─ 接頭の https:// による判別
	#		リトライ: url      ←┘
	#		    失敗: False
	#
	def get_express_checkout_details(self, web):
		#
		# 現在のURLに付与された ?token= の値を得る
		#
		token = web.get('token')
		# ----------------------------------------------------------------------
		#
		# [2/3] GetExpressCheckoutDetails
		#
		nvp = {
			'METHOD'   :'GetExpressCheckoutDetails',
			'VERSION'  :93,
			'USER'     :self._username,
			'PWD'      :self._password,
			'SIGNATURE':self._signature,
			'TOKEN'    :token,
		}
		web.log(nvp, 'purple')
		#
		# 送信
		#
		req = requests.post(url=self._endpoint, data=nvp)
		#
		#	TOKEN=EC-XXXXXXXXXX
		#	BILLINGAGREEMENTACCEPTEDSTATUS=0
		#	CHECKOUTSTATUS=PaymentActionNotInitiated
		#	TIMESTAMP=2014-10-10T11:13:50Z
		#	CORRELATIONID=b2220b38a5117
		#	ACK=Success
		#	VERSION=93
		#	BUILD=13630372
		#	EMAIL=buyer@piyo.jp
		#	PAYERID=XXXXXXXXXX
		#	PAYERSTATUS=verified
		#	FIRSTNAME=Taro
		#	LASTNAME=Yamada
		#	COUNTRYCODE=JP
		#	CURRENCYCODE=JPY
		#	AMT=108
		#	ITEMAMT=100
		#	SHIPPINGAMT=0
		#	HANDLINGAMT=0
		#	TAXAMT=8
		#	INSURANCEAMT=0
		#	SHIPDISCAMT=0
		#	L_NAME0=バナナ
		#	L_QTY0=1
		#	L_TAXAMT0=8
		#	L_AMT0=100
		#	L_ITEMWEIGHTVALUE0=0.00000
		#	L_ITEMLENGTHVALUE0=0.00000
		#	L_ITEMWIDTHVALUE0=0.00000
		#	L_ITEMHEIGHTVALUE0=0.00000
		#	L_ITEMCATEGORY0=Digital
		#	PAYMENTREQUEST_0_CURRENCYCODE=JPY
		#	PAYMENTREQUEST_0_AMT=108
		#	PAYMENTREQUEST_0_ITEMAMT=100
		#	PAYMENTREQUEST_0_SHIPPINGAMT=0
		#	PAYMENTREQUEST_0_HANDLINGAMT=0
		#	PAYMENTREQUEST_0_TAXAMT=8
		#	PAYMENTREQUEST_0_INSURANCEAMT=0
		#	PAYMENTREQUEST_0_SHIPDISCAMT=0
		#	PAYMENTREQUEST_0_INSURANCEOPTIONOFFERED=false
		#	L_PAYMENTREQUEST_0_NAME0=バナナ
		#	L_PAYMENTREQUEST_0_QTY0=1
		#	L_PAYMENTREQUEST_0_TAXAMT0=8
		#	L_PAYMENTREQUEST_0_AMT0=100
		#	L_PAYMENTREQUEST_0_ITEMWEIGHTVALUE0=0.00000
		#	L_PAYMENTREQUEST_0_ITEMLENGTHVALUE0=0.00000
		#	L_PAYMENTREQUEST_0_ITEMWIDTHVALUE0=0.00000
		#	L_PAYMENTREQUEST_0_ITEMHEIGHTVALUE0=0.00000
		#	L_PAYMENTREQUEST_0_ITEMCATEGORY0=Digital
		#	PAYMENTREQUESTINFO_0_ERRORCODE=0
		#
		text = req.text
		web.log(text, 'purple')
		try:
			nvp = urllib.parse.parse_qs(text)
			nvp = {k: v[0] for k, v in nvp.items()}
		except:
			nvp = {}
		web.log(nvp, 'purple')
		#
		# 本来は PAYERSTATUS=verfied だが実際は unverified が頻発する。
		# しかし続く支払い処理は問題なく行われる傾向にあるため続行する。
		#
		if nvp.get('PAYERSTATUS')!='verfied':
			web.log('[PAYERSTATUS] = ' + nvp.get('PAYERSTATUS'), 'red')
		#
		# 商品コード
		#
		itemcode = nvp.get('PAYMENTREQUEST_0_CUSTOM')
		# ----------------------------------------------------------------------
		#
		# [3/3] DoExpressCheckoutPayment
		#
		nvp = {
			'METHOD'   :'DoExpressCheckoutPayment',
			'VERSION'  :93,
			'USER'     :self._username,
			'PWD'      :self._password,
			'SIGNATURE':self._signature,
			'TOKEN'    :token,
			'PAYERID'  :nvp.get('PAYERID'),
			'PAYMENTREQUEST_0_ITEMAMT'      :nvp.get('PAYMENTREQUEST_0_ITEMAMT'),
			'PAYMENTREQUEST_0_TAXAMT'       :nvp.get('PAYMENTREQUEST_0_TAXAMT'),
			'PAYMENTREQUEST_0_AMT'          :nvp.get('PAYMENTREQUEST_0_AMT'),
			'PAYMENTREQUEST_0_PAYMENTACTION':'Sale',
			'PAYMENTREQUEST_0_CURRENCYCODE' :'JPY',
		}
		web.log(nvp, 'purple')
		#
		# 送信
		#
		req = requests.post(url=self._endpoint, data=nvp)
		#
		# 成功例:
		#	TOKEN=EC-XXXXXXXXXX
		#	SUCCESSPAGEREDIRECTREQUESTED=false
		#	TIMESTAMP=2014-10-10T11:15:08Z
		#	CORRELATIONID=b2220b38a5117
		#	ACK=Success
		#	VERSION=93
		#	BUILD=13630372
		#	INSURANCEOPTIONSELECTED=false
		#	SHIPPINGOPTIONISDEFAULT=false
		#	PAYMENTINFO_0_TRANSACTIONID=XXXXXXXXXX
		#	PAYMENTINFO_0_TRANSACTIONTYPE=expresscheckout
		#	PAYMENTINFO_0_PAYMENTTYPE=instant
		#	PAYMENTINFO_0_ORDERTIME=2014-10-10T11:15:08Z
		#	PAYMENTINFO_0_AMT=108
		#	PAYMENTINFO_0_FEEAMT=44
		#	PAYMENTINFO_0_TAXAMT=8
		#	PAYMENTINFO_0_CURRENCYCODE=JPY
		#	PAYMENTINFO_0_PAYMENTSTATUS=Completed
		#	PAYMENTINFO_0_PENDINGREASON=None
		#	PAYMENTINFO_0_REASONCODE=None
		#	PAYMENTINFO_0_PROTECTIONELIGIBILITY=Ineligible
		#	PAYMENTINFO_0_PROTECTIONELIGIBILITYTYPE=None
		#	PAYMENTINFO_0_SECUREMERCHANTACCOUNTID=XXXXXXXXXX
		#	PAYMENTINFO_0_ERRORCODE=0
		#	PAYMENTINFO_0_ACK=Success
		#
		# 失敗例:
		#	TIMESTAMP=2016-02-20T09:56:33Z
		#	CORRELATIONID=fe96b084db538
		#	ACK=Failure
		#	VERSION=93
		#	BUILD=18316154
		#	L_ERRORCODE0=10445
		#	L_SHORTMESSAGE0=
		#	  This transaction cannot be processed at this time.
		#	  Please try again later.
		#	L_LONGMESSAGE0=
		#	  This transaction cannot be processed at this time.
		#	  Please try again later.
		#	L_SEVERITYCODE0=Error
		#
		text = req.text
		web.log(text, 'purple')
		try:
			nvp = urllib.parse.parse_qs(text)
			nvp = {k: v[0] for k, v in nvp.items()}
		except:
			nvp = {}
		web.log(nvp, 'purple')
		#
		# 評価
		#
		if nvp.get('ACK')=='Success':
			#
			# (成功)
			#
			return itemcode
		else:
			#
			# メール通知
			#
			txt = blossom.read('../resource/eml/paypal.err3.eml')
			txt = txt % {
				'text':text,
			}
			web.log(txt, 'purple')
			blossom.Mail.send(txt)
			#
			# 2017.8 以降 L_ERRORCODE0=10486 が返されるエラーがが頻発した。原因は不明のままだが、支払い手続きを何度か繰り返すことで成功することがあることがわかった。そこで管理ページ上に「もう一度お試しください」とのメッセージを出した上で、利用者にお支払い手続きを再度行わせる。ここではそのリンク先のURLを返す。
			#
			if nvp.get('L_ERRORCODE0')=='10486':
				#
				# (リトライ)
				#
				return web._webscr + token
			else:
				#
				# (失敗)
				#
				return False