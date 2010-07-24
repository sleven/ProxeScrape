"""proxytest.py v2"""
import urllib2
from urllib import request, parse

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
judgePool = Queue.Queue()

engine = create_engine('sqlite:///proxy.db',echo=False)

metadata = MetaData(bind=engine)


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
mydata = threading.local()

class Mini_Thread (threading.Thread):
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
	
	def run (self):
		global chan_mode
		global working_proxies
		global plist
		
		item = threadPool.get()
		this_judge = judgePool.get()
		
		print "Hi, im thread, ", self.getName(), "responsible for ", item.ip
		
		item = self.process_proxy(item, this_judge)
		item.last_checked = strftime("%d/%m/%Y %H:%M:%S %Z", time.localtime())
		
		if item.alive and item.safe:
			print self.getName(), "here, responsible for ", item.ip, " found it to be WORKING"
			#print 'id#%-5d %-10s %s:%-6s country=%s hostname=%s %d health=%f' % (theVar, item.last_checked, item.ip, item.port, item.get_country_code(), item.hostname,item.resp, item.get_health())
			working_proxies += 1
			sys.stdout.flush()
		else:
			print self.getName(), "here, responsible for ", item.ip, " found it to be BROKEN"
		plist.append(item)				
		threadPool.task_done()

	def process_proxy(self, item, this_judge):
		global ip
		global block_list
		

		try:
			if len(item.port) < 2:
				item.alive = False
				item.safe = False
				return item
		except:
				item.alive = False
				item.safe = False
				return item
			
		try:
			location = str(GEOIP.lookup(item.ip))
			item.location = location
			
			if location.find("CA") > -1 or location.find("GB") > -1 or location.find("US") > -1 or location==None or location=="":
				item.safe = False
				item.alive = False
				#print "US proxy"
				return item
		except Exception, e:
			#print "country lookup failure.", e
			item.safe = False
			item.alive = False
			return item
			
		try:
			gname = socket.gethostbyaddr(item.ip)
			item.hostname = gname[0]
			
			
			for bad in block_list:
				if gname[0].find(bad) > -1:
					#print item.ip, item.hostname, "found in blocklist"
					item.safe = False
					item.alive = False
					return item
					
		except Exception, e:
			#print "Couldn't find hostname: ", item.ip, e
			item.hostname = "no hostname"
			

		try:
			print self.getName(), " here, testing ", item.ip
			
			resp_s = float(time.time())
			proxies = {'http': item.ip + item.port}
			
			print "1"
			
			opener = request.build_opener(urllib2.HTTPHandler(debuglevel=1))

			request.install_opener(opener)

			usock = opener.open(this_judge)
			print usock.read()
			
			opener = urllib2.build_opener()
			#opener = urllib.FancyURLopener(proxies)
			opener.addheaders = [('User-agent', 'Mozilla/5.0')]
			print "2"
			print this_judge
			print opener
			
			opener.open(this_judge)
			
			print "3"
			page = opener.read()
			

			print self.getName(), " here, requested  for ", item.ip
			resp_f = float(time.time())
			item.resp = round((resp_f - resp_s), 3)
			

			host = pattern1.search(page)
			host = host.group()
			print self.getName(), " here, requested ", this_judge, " for ", item.ip, " and got ", host
			addr = pattern2.search(page)
			addr = addr.group()
			print self.getName(), " here, requested  ", this_judge,  " for ", item.ip, " and got ", addr
			f.close()
			
			if not ip.search(page) == None:
				item.safe = False
				item.alive = True
				#print "leaks IP address"
				return item
			else:
				if(chan_mode):
					for i in range(3):
						time.sleep(10)
						try:
							proxy_handler = urllib2.ProxyHandler({'http': item.ip})        
							opener = urllib2.build_opener(proxy_handler)
							opener.addheaders = [('User-agent', 'Mozilla/5.0')]
							urllib2.install_opener(opener)
							
							req=urllib2.Request('http://boards.4chan.org/b')  # change the url address here
							sock=urllib2.urlopen(req)			
							page = str(sock.read())
							
							sock.close()
							
							if page.find('banned') > -1:
								print "Working proxy but banned on teh chan :(", item.ip
								print "Still looking."
								item.alive = False
								item.safe = True
								return item
							else:
								print ""
								print "Found a working chan proxy!"
								print "** ** ",
								item.alive = True
								item.safe = True
								return item
								
						except Exception, e:
							print "chan error# ",i,item.ip, e
							item.alive = False
							item.safe = True
					return item
				else:
					item.alive = True
					item.safe = True
					#print this_judge
					#print page
					return item
			
		except urllib2.HTTPError, e:        
			print ' Error code: ', e.code
			item.alive = False
			return item
		except Exception, detail:
			print " ERROR:", detail
			item.alive = False
			return item
	
class Mini_Test:	
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
		theVar = 0
		x = 1
		update_freq = 1000
		all = []
		test_size = 10000


		print "CHAN_MODE: ", chan_mode
				
		threadPool = Queue.Queue ()
		
		f = open("block_list.txt")
		for line in f:
			block_list.append(line.strip())
		f.close()
		

		f =open("judges.txt")
		for line in f:
			judges.append(line.strip())
		f.close()
		
		#jtest = judgestest.judgesTest()
		#judges = jtest.run_test(judges)
		
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
		
		pool_size = 5
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
					for y in range(pool_size):
						y += 1
						this_judge = judges[y % len(judges)]
						t = Mini_Thread()
						threadlist.append(t)
						t.start()
						
				except Exception, e:
					print e
					for t in threadlist:
						t.join(15)
						
					pass

				for t in threadlist:
					t.join(15)
					
		print "Elapsed Time: %s" % (time.time() - start)
		print len(return_batch)
		return_batch.extend(plist)
		return return_batch;
	
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
		
