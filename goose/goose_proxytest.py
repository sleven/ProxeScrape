"""proxytest.py v2"""
import urllib2
import socket
import threading
import re
import Queue
import sys
import proxy
import judgestest
import geoip
import proxytools
from time import gmtime, strftime
import time

socket.setdefaulttimeout(10)

renig_judges = False
block_list = []
theVar = 0
plist = []
x = 0
pool_size = 60
judges = []
ip = re.compile(r"173.67.3.34")
pattern1 = re.compile(r"HTTP_HOST") #\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
pattern2 = re.compile(r"REMOTE_ADDR") #\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
		
		
threadPool = Queue.Queue ()		
		
class Proxytest (threading.Thread ):
	
	def run (self):
		global theVar
		global x
		global threadPool
		
		item = threadPool.get()
		item = self.process_proxy(item)
		item.last_checked = strftime("%d/%m/%Y %H:%M:%S %Z", time.localtime())
		
		if item.alive and item.safe:
			print '%-5d %-10s ALIVE==> %s:%-6s %s %s ' % (theVar, item.last_checked, item.ip, item.port,item.location, item.hostname)
			sys.stdout.flush()						
		threadPool.task_done()
		x -= 1

	def process_proxy(self, pip):
		global judges
		global ip
		global block_list
		
		try:
			location = geoip.country(pip.ip)
			pip.location = location
			
			if location == "US" or location==None or location=="":
				pip.safe = False
				pip.alive = False
				print "US proxy"
				return pip
		except:
			print "country lookup failure."
			pip.safe = False
			pip.alive = False
			return pip
			
		try:
			gname = socket.gethostbyaddr(pip.ip)
			pip.hostname = gname[0]
			
			
			for bad in block_list:
				if gname[0].find(bad) > -1:
					print pip.ip, pip.hostname, "found in blocklist"
					pip.safe = False
					pip.alive = False
					return pip
					
		except Exception, e:
			#print "Couldn't find hostname: ", pip.ip, e
			pip.hostname = "no hostname"
			

		try:
			this_judge = judges[theVar % len(judges)]
			
			proxy_handler = urllib2.ProxyHandler({'http': pip.ip})        
			opener = urllib2.build_opener(proxy_handler)
			opener.addheaders = [('User-agent', 'Mozilla/5.0')]
			urllib2.install_opener(opener)
			
			req=urllib2.Request(this_judge)  # change the url address here
			sock=urllib2.urlopen(req)			
			page = str(sock.read())
			
			host = pattern1.search(page)
			host = host.group()
			
			addr = pattern2.search(page)
			addr = addr.group()
			
			sock.close()
			
			if not ip.search(page) == None:
				pip.safe = False
				pip.alive = True
				print "leaks IP address"
				return pip
			else:
				pip.alive = True
				pip.safe = True
				return pip
			
		except urllib2.HTTPError, e:        
			print theVar,' Error code: ', e.code
			pip.alive = False
			return pip
		except Exception, detail:
			print theVar," ERROR:", detail
			pip.alive = False
			return pip
	
		
	def run_test(self, upstream):
		global plist
		global threadPool
		global rejects
		global working
		global judges
		global x
		global theVar
		global block_list
		global renig_judges
		
		start = time.time()
		threadlist = []
		judges[:] = []
		plist[:] = upstream
		test_list = []
		theVar = 0
		x = 1
		threadPool = Queue.Queue ()
		
		with open("block_list.txt") as f:
			for line in f:
				block_list.append(line.strip())

		with open("judges.txt") as f:
			for line in f:
				judges.append(line.strip())
		
		if not renig_judges:
			jtest = judgestest.judgesTest()
			judges = jtest.run_test(judges)
		
		print "Booting up proxy test"
		g = 0
		
		for proxy in plist:
			if proxy.alive == True or proxy.last_checked == "never":
				g += 1
				threadPool.put(proxy)
			
		print "* Testing ", g, " proxies."
		
		
		while(theVar < g):
				if (x < pool_size):
					t = Proxytest()
					threadlist.append(t)
					theVar = theVar + 1
					t.start()
					x += 1
					
		for t in threadlist:
			t.join()
		
		print "Elapsed Time: %s" % (time.time() - start)
		
		x = 0
		
		return plist;
