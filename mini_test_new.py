"""proxytest.py v2"""
import urllib2
import urllib
import socket
import threading
import re
import Queue
import sys
import proxy
import judgestest
import proxytools
from time import gmtime, strftime
import time

import pygeoip
"""import sql modules"""
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.sql import select
from sqlalchemy.sql import and_

# Load the database once and store it globally in interpreter memory.
GEOIP = pygeoip.Database('GeoIP.dat')


socket.setdefaulttimeout(8)

renig_judges = False
block_list = []
theVar = 0
plist = []
x = 0
pool_size = 60
judges = []
threadlist = []
ip = re.compile(r"173.64.123.229")
proxy_pattern = re.compile(r"[1-2]?[0-9]{1,3}\.[1-2]?[0-9]{1,3}\.[1-2]?[0-9]{1,3}\.[1-2]?[0-9]{1,3}")
pattern1 = re.compile(r"HTTP_HOST") #\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
pattern2 = re.compile(r"REMOTE_ADDR") #\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
# Load the database once and store it globally in interpreter memory.
GEOIP = pygeoip.Database('GeoIP.dat')

chan_mode = False
working_proxies = 0
sentinel = False

"""IMPORTANT!!! ONLY WORKS CORRECTLY FOR REQUESTS LESS THAT POOL SIZE"""
max_return_proxies = -1   	

	
threadPool = Queue.Queue ()
processedPool = Queue.Queue()

judgePool = Queue.Queue()

engine = create_engine('sqlite:///proxy.db',echo=False)

metadata = MetaData(bind=engine)
socks = []
ips = []

main_tbl = Table('main', metadata,
					Column('id', Integer, primary_key=True),
					Column('ip', String),
					Column('port', String),
					Column('hostname', String),
					Column('location', String),
					Column('safe', Boolean),
					Column('alive', Boolean),
					Column('last_checked', String),
					Column('url', String),
					Column('resp', Float(3,True))
					)
# create tables in database
metadata.create_all()

class Mini_Test:	
	def update_database(all):
		try:
			# change 'jack' to 'ed'
			conn.execute(main.update().
				where(main.c.alive=='jack').
				values(alive=item.alive)
				)
		except:
			pass
			
	def set_index(self, index):
		self.index = index


	def run_test(self, test_list, max_to_return=-1):
		global plist
		global threadPool
		global block_list
		global renig_judges
		global pool_size
		global chan_mode
		global working_proxies
		global max_return_proxies
		global proxy
		
		max_return_proxies = max_to_return
		
		start = time.time()
		judges = []
		update_freq = 1000
		all = []
		test_size = 10000
		
		print "CHAN_MODE: ", chan_mode
		
		f = open("block_list.txt")
		for line in f:
			block_list.append(line.strip())
		f.close()

		f =open("judges.txt")
		for line in f:
			judges.append(line.strip())
		f.close()
		
		jtest = judgestest.judgesTest()
		judges = jtest.run_test(judges)
		
		for j in judges:
			judgePool.put(j)

		print "Booting up proxy test"
		g = 0
		i = -1
		batch = []
		return_batch = []
		temp = []
		v = 0
			
		total = len(test_list)
		if pool_size > total:
			pool_size = total
		
		while 1:
			if len(test_list) > test_size:
				batch.append(test_list[:test_size])
				del test_list[:test_size]
			else:
				if len(test_list) > 0:
					batch.append(test_list[:])
				break
		
		print "Test params"
		print "Testing ", total, "total proxies."
		
		a = 0
		for i in batch:
			print "* batch", a, " is ", len(i), "proxies long"
			a += 1
	
		g = 0

						
		for i in batch:
			batch_num = batch.index(i)
			
			while len(batch[batch_num]) > 0:
				print "new pool"
				print "len batch", len(batch[batch_num])
				for u in range(pool_size):
					try:
						threadPool.put(batch[batch_num][0])
						batch[batch_num].remove(batch[batch_num][0])
						u+= 1
					except Exception, e:
						print e
						pass
				try:
					for d in range(pool_size):
						self.run_in_thread(working_proxies, chan_mode)
				except Exception, e:
					print e
					
			for i in range(total):
				plist.append(processedPool.get())
				
		print "Elapsed Time: %s" % (time.time() - start)
		print len(return_batch)
		return_batch.extend(plist)
		return return_batch;
		
	def run_in_thread(self, working_proxies, chan_mode):
		class MyThread ( threading.Thread ):
			
			def run (self):
				item = threadPool.get()
				this_judge = judgePool.get()
				
				#print "Hi, im thread, ", self.getName(), "responsible for ", item.ip
				
				item = self.process_proxy(item, this_judge)
				item.last_checked = strftime("%d/%m/%Y %H:%M:%S %Z", time.localtime())
				
				if item.alive and item.safe:
					#print self.getName(), "here, responsible for ", item.ip, " found it to be WORKING"
					print 'id#%-5d %-10s %s:%-6s country=%s hostname=%s %d health=%f' % (theVar, item.last_checked, item.ip, item.port, item.get_country_code(), item.hostname,item.resp, item.get_health())
					sys.stdout.flush()
				else:
					print self.getName(), "here, responsible for ", item.ip, " found it to be BROKEN"
				
				processedPool.put(item)						
				threadPool.task_done()
	
			def process_proxy(self, item, this_judge):
				global ip
				global block_list
				global ips
				
				self.item = item
				self.this_judge = this_judge
				self.sock = None
				
				self.item.alive = False
				self.item.safe = False
				
				if self.is_fine_location(self.item):
					if self.is_fine_hostname(self.item):
						if self.is_alive(self.item, self.this_judge):
							self.item.alive = True
							self.item.safe = True
							
				return self.item
										
			def is_fine_location(self, pip):
				try:
					if len(self.item.port) < 2:
						return False
				except:
						return False
					
				try:
					self.location = str(GEOIP.lookup(pip.ip))
					pip.location = self.location
					
					if self.location==None or self.location=="":
						return False
						#print "US proxy"

				except Exception, e:
					#print "country lookup failure.", e
					return False
				return True
				
			def is_fine_hostname(self, pip):
				try:
					self.gname = socket.gethostbyaddr(pip.ip)
					pip.hostname = self.gname[0]
					for bad in block_list:
						if self.gname[0].find(bad) > -1:
							print item.ip, item.hostname, "found in blocklist"
							return False
							
				except Exception, e:
					print "Couldn't find hostname: ", pip.ip, e
					pip.hostname = "no hostname"
					return True
				return True
					
			def is_alive(self, pip, this_judge):   
				try:
					prox = pip.ip + ":" + pip.port
					proxy_handler = urllib2.ProxyHandler({'http': prox})
					opener = urllib2.build_opener(proxy_handler)
					opener.addheaders = [('User-agent', 'Mozilla/5.0')]
					urllib2.install_opener(opener)
					req=urllib2.Request(this_judge)  # change the URL to test here
					sock=urllib2.urlopen(req)
					
				except urllib2.HTTPError, e:
					print 'Error code: ', e.code
					return False
				except Exception, detail:
					print "ERROR:", detail
					return False
				return True
		MyThread().start()

if __name__ == '__main__':
	
		mini_test = Mini_Test()
		all = []
		
		try:
			s = select([main_tbl])
			conn = engine.connect()
			result = conn.execute(s)

			for row in result:
				new_proxy = proxy.Proxy(row.ip, row.port, row.location, row.hostname, row.alive, row.safe, row.last_checked, row.url, row.resp, row.good, row.bad, row.flags)
				all.append(new_proxy)
			
			print len(all), " proxies loaded."

		except Exception, e:
			print e
			sys.exit()
		
		print "CHAN_MODE: ", chan_mode
		test_list = []
		no_test_list = []
		return_batch = []
				
		for proxy in all:
			if proxy.alive == True or proxy.last_checked == "never":
				test_list.append(proxy)
			else:
				no_test_list.append(proxy)
					
		proxy_test = Mini_Test()
		all = proxy_test.run_test(test_list)
		
