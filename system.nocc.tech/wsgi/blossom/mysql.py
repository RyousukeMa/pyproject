# -*- coding: utf-8 -*-

import pymysql

#
#
# MySQL
#
#
class MySQL(object):
	#
	# __init__
	#
	# e.g.
	# 	db = mysql.MySQL('user', 'passwd', log=web.log)
	# 	db = mysql.MySQL('user', 'passwd', log='/tmp/log.txt')
	#
	def __init__(self, user, passwd, host=None, db=None, log=None):
		self._host = host if host else 'localhost'
		self._user = user
		self._passwd = passwd
		self._db = db if db else user
		self._log = log
		self.connect = None
		self.cursor = None
	
	#
	# .log()
	#
	def log(self, text, color=None):
		if callable(self._log):
			self._log(text, color)
		elif isinstance(self._log, str):
			with open(self._log, 'a') as f:
				f.write(text + "\n")
	
	#
	# .__connect()
	#
	def __connect(self):
		#
		# log
		#
		if self._log:
			self.log('mysql'
				+ ' -h ' + self._host
				+ ' -u ' + self._user
				+ ' --database ' + self._db)
		#
		# connect
		#
		try:
			self.connect = pymysql.connect(
				host=self._host,
				user=self._user,
				passwd=self._passwd,
				db=self._db,
				charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor)
			self.cursor = self.connect.cursor()
		except pymysql.Error as e:
			if self._log:
				self.log('[%d]: %s' % (e.args[0], e.args[1]), 'red')
	
	#
	# .exe()
	#
	def exe(self, operation, params=None, key=None):
		#
		# connect
		#
		if not self.cursor:
			self.__connect()
			if not self.cursor:
				return False
		#
		# operation
		#
		operation = operation.strip()
		ope_type = operation.split(None, 1)[0].upper()
		#
		# log
		#
		if self._log:
			self.log(operation % params if params else operation)
		#
		# execute
		#
		try:
			self.cursor.execute(operation, params)
			self.connect.commit()
		except pymysql.Error as e:
			if self._log:
				self.log('[%d]: %s' % (e.args[0], e.args[1]), 'red')
			return False
		result = self.cursor.fetchall()
		#
		# log
		#
		if self._log:
			log = 'mysql.rowcount = ' + str(self.cursor.rowcount)
			if self.cursor.lastrowid:
				log += "\n" + 'mysql.lastrowid = ' + str(self.cursor.lastrowid)
			self.log(log, 'blue')
		#
		# result
		#
		if ope_type in ('SELECT', 'SHOW', 'CHECK'):
			#
			# SELECT, SHOW
			#
			if len(result):
				fields = len(result[0])
				if fields==1:
					result = [list(row.values())[0] for row in result]
					if key is True:
						result = result[0]
				elif key is True:
					result = result[0]
				elif key and key in result[0].keys():
					result = {v.pop(key): v for i, v in enumerate(result)}
					if fields==2:
						result = {k: list(v.values())[0] for k, v in result.items()}
				else:
					result = list(result)
			else:
				return None if key is True else [] if key is None else {}
		else:
			#
			#          | rowcount | lastrowid             |
			# ---------+----------+-----------------------+
			#  INSERT  |       >0 | >0 if changed else =0 |
			#  REPLACE |       >0 |                    >0 |
			#  UPDATE  |       >0 |                    =0 |
			#
			class MySqlResult(object):
				def __init__(self, rowcount, lastrowid):
					self.rowcount = rowcount
					self.lastrowid = lastrowid
			result = MySqlResult(self.cursor.rowcount, self.cursor.lastrowid)
		return result
	
	#
	# .unlock()
	#
	def unlock(self):
		rows = self.exe('SHOW FULL PROCESSLIST;')
		if self._log:
			for row in rows:
				if row['Info'] and row['Info']!='SHOW FULL PROCESSLIST':
					self.log(row['Info'], 'red' if row['Time'] else 'purple')
		#
		# Info が "Waiting for table metadata lock" を発見したら、Command が Sleep となっているプロセスを全キルして終了する。
		#
		for row in rows:
			if row['Info'] and row['Info']=='Waiting for table metadata lock':
				for row in rows:
					if row['Command']=='Sleep':
						self.exe('KILL ' + str(row['Id']) + ';')
				return
		#
		# 規定秒数を要しているSELECT系コマンドをキルする。ただしState が Locked となっているプロセスは順番待ちをしているだけなのでキルしない。また問題のプロセスをキルした後、順番待ちしていた処理までキルされないように、最初のKILLが行われたら処理を中止する。
		#
		for row in rows:
			if row['Time']>6 \
				and row['State']!='Locked' \
				and row['Info'] \
				and row['Info'].strip().upper().startswith('SELECT'):
				self.exe('KILL ' + str(row['Id']) + ';')
				return
	
	#
	# .escape()
	#
	def escape(self, text):
		#
		# connect
		#
		if not self.cursor:
			self.__connect()
			if not self.cursor:
				return False
		return self.connect.escape_string(text)
	
	#
	# .quit()
	#
	def quit(self):
		if self._log:
			try:
				self.log('QUIT;')
			except:
				pass
		try:
			self.cursor.close()
		except:
			pass
		finally:
			self.cursor = None
		try:
			self.connect.close()
		except:
			pass
		finally:
			self.connect = None
	
	#
	# __del__
	#
	def __del__(self):
		self.quit()