"""proxytest.py v2"""
import urllib2
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
import random
import os

import pygeoip
import contextlib

# Load the database once and store it globally in interpreter memory.
GEOIP = pygeoip.Database('GeoIP.dat')

socket.setdefaulttimeout(8)

renig_judges = False
theVar = 0
plist = []
x = 0
pool_size = 60
threadlist = []
#5-31-2010
ip = re.compile(r"173.64.68.97")
judge_identifier = []
block_list = []

""" head /head body /body html /html"""

pattern2 = re.compile(r"REMOTE_HOST") #\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
pattern1 = re.compile(r"REMOTE_ADDR") #\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
pattern3 = re.compile(r"HTTP_USER_AGENT")
# Load the database once and store it globally in interpreter memory.
GEOIP = pygeoip.Database('GeoIP.dat')

chan_mode = False
phase_one_complete = False
phase_two_complete = False

threadPool = Queue.Queue ()
processedPool = Queue.Queue()
judgePool = Queue.Queue()
phase_twoPool = Queue.Queue()

class Proxytest:
	def run_test(self, all, judges, judge_identifier_l, block_list_l):
		global plist
		global threadPool
		global renig_judges
		global pool_size
		global chan_mode
		global proxy
		global theVar
		global x
		global phase_one_complete
		global phase_two_complete
		global block_list
		global judge_identifier
		
		test_list = []
		no_test_list = []
		return_batch = []
		block_list = block_list_l
		judge_identifier = judge_identifier_l
		thresh = .5
		
		"""flags"""
		#black = dead from the start, 0/2 tests
		#	   = for ex. failed past 2 tests

		#Test everything that hasn't failed the last two tests
		
		for proxy in all:
			if proxy.is_dead():
				no_test_list.append(proxy)
			else:
				test_list.append(proxy)	
		
		if len(test_list) == 0:
			return all
		
		start = time.time()
		update_freq = 1000
		all = []
		test_size = 10000
		
		print "CHAN_MODE: ", chan_mode
		
		print strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),"\n", 
		print "Booting up proxy test"
		g = 0
		i = -1
		batch = []
		return_batch = []
		temp = []
		batch_list = []
		v = 0
			
		total = len(test_list)
		if pool_size > total:
			pool_size = total
		jnum = 0
		
		while jnum < total * 2:
			for j in judges:
				judgePool.put(j)
				jnum += 1
				
		while 1:
			if len(test_list) > test_size:
				batch_list.append(test_list[:test_size])
				del test_list[:test_size]
			else:
				if len(test_list) > 0:
					batch_list.append(test_list[:])
				break
		
		print "Test params"
		print "Testing ", total, "total proxies."
		
		a = 0
		x = 0
		theVar = 0
		number_of_batches = len(batch_list)
		
		#~ for batch in batch_list:
			#~ batch_number = batch_list.index(batch)
			#~ print "* batch", batch_number, " is ", len(batch_list[batch_number]), "proxies long"
		phase_one_complete = False
		phase_two_complete = False
		print "Starting phase_two processor..."
		self.phase_two()
		print "started."
				
		for batch in batch_list:
			batch_number = batch_list.index(batch)
			
			for proxy in batch:
				threadPool.put(proxy)
			plist = []
			
			while theVar < len(batch):
				if (x < pool_size):
					theVar = theVar + 1
					self.run_in_thread(chan_mode)
					x+=1
			theVar = 0
			x = 0
		phase_one_complete = True
		print "Phase one is done. Waiting for phase two."
		
		#~ while not phase_two_complete:
			#~ print "phase_twoPool.qsize:", phase_twoPool.qsize()
			#~ print "threadPool.qsize:", threadPool.qsize()
			#~ print "processedPool.qsize:", processedPool.qsize()
			#~ time.sleep(5)
			
		for i in range(total):
			plist.append(processedPool.get())
				
		print "Elapsed Time: %s" % (time.time() - start)
		return_batch.extend(plist)
		return_batch.extend(no_test_list)

		print len(return_batch)
		return return_batch;
		
	def run_in_thread(self, chan_mode):
		class MyThread ( threading.Thread ):
			def run (self):
				global x
				item = threadPool.get()
				this_judge = judgePool.get()

				item = self.process_proxy(item, this_judge)
				item.last_checked = strftime("%d/%m/%Y %H:%M:%S %Z", time.localtime())			
				
				if item.alive == True:
					item.clear()
					item.plus_good()
					print 'Passed phase 1, put in phase two stack --> id#%-5d %-10s %s:%-6s c:%s host: %s %f health: %f g: %d b: %d bf: %d murdered: %s' % (theVar, item.last_checked, item.ip, item.port, item.get_country_code(), item.hostname,item.resp, item.get_health(), item.good, item.bad, item.get_flags_bin(), item.is_dead())
					phase_twoPool.put(item)
					
					#print 'above used judge:', this_judge, this_judge2
					#print ""
					#print self.getName(), "here, responsible for ", item.ip, " found it to be WORKING"
					#print 'id#%-5d %-10s %s:%-6s c:%s host: %s %f health: %f tests: %d' % (theVar, item.last_checked, item.ip, item.port, item.get_country_code(), item.hostname,item.resp, item.get_health(), item.good + item.bad)
					sys.stdout.flush()
				else:
					item.plus_bad()
					processedPool.put(item)
					#print self.getName(), "here, responsible for ", item.ip, " found it to be BROKEN"
					
				threadPool.task_done()
				judgePool.task_done()
				
				x -= 1
	
			def process_proxy(self, item, this_judge):
				global ip
				global block_list
				global jude_identifier
				
				self.item = item
				self.this_judge = this_judge
				self.sock = None
				self.item.resp = 0
				
				if self.is_fine_location(self.item):
					if self.is_fine_hostname(self.item):
						self.item.safe = True
						self.item.resp, alive_status = self.is_alive(self.item, self.this_judge)
						if alive_status:
							self.item.alive = True
						else:
							if self.item.alive == False:
								self.item.flags["black"] += 1
								#This proxy failed twice in a row
							else:
								self.item.alive = False
					else:
						self.item.safe = False
						self.item.alive = False
						self.item.kill()
				else:
					self.item.safe = False
					self.item.alive = False
					self.item.kill()
				
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
					
					if self.location==None or self.location=="" or self.location.find("US") > -1:
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
							#print item.ip, item.hostname, "found in blocklist"
							return False
							
				except Exception, e:
					#print "Couldn't find hostname: ", pip.ip, e
					pip.hostname = "unknown"
					return True
				return True
			
			def is_alive(self, pip, this_judge):
				global x
				global judge_identifier
				resp = 0
				page = ""
				try:
					resp_s = time.time()
					prox = pip.ip + ":" + pip.port
					proxy_handler = urllib2.ProxyHandler({'http': prox})
					opener = urllib2.build_opener(proxy_handler)
					opener.addheaders = [('User-agent', 'Mozilla/5.0')]
					urllib2.install_opener(opener)
					req=urllib2.Request(this_judge)  # change the URL to test here

					with contextlib.closing(urllib2.urlopen(req)) as sock:
						present_url = sock.geturl()
						page = sock.read().lower()
						
					resp_f = time.time()
					resp = round((resp_f - resp_s), 3)
					
					for identifier in judge_identifier:
						if not page.find(identifier) > -1:
							#~ print "**********"
							#~ print ""
							#~ print prox, "identifier", identifier, "not found"
							#~ os.chdir('/home/sleven/apps/v2/proxytest_dump')
							#~ f = open("rejected" + str(prox) + ".html","w")
							#~ f.write(page)
							#~ f.close()
							#~ os.chdir('..')
							#~ print "judge used:", this_judge
							#~ print ""
							#~ print "**********"
							return resp, False
							
					if not present_url == this_judge:
						#~ print "Requested page", this_judge, ", but was redirected to", present_url, ". Please confirm."
						#~ print pip.ip, ":", pip.port
						#~ print page
						return resp, False
					
					if page.find('codeen') > -1:
						print "codeen found in html"
						return resp, False
						
					if not ip.search(page) == None:
						#print "leaks IP address"
						return resp, False
				except urllib2.HTTPError, e:
					#print 'Error code: ', e.code
					return resp, False
				except Exception, detail:
					#print page
					#print "ERROR:", detail
					return resp, False
				
				#os.chdir('/home/sleven/apps/v2/proxytest_dump')
				#f = open(str(prox) + "_1_.html","w")
				#f.write(page)
				#f.close()
				#os.chdir('..')
				
				return resp, True
		MyThread().start()
		##MyThread.join(10)

	def phase_two(self):
		class MyThread ( threading.Thread ):
			def run (self):
				global phase_one_complete
				global phase_two_complete
				num = 0
				while 1:
					time.sleep(1)
					print self.getName(), "..Phase2 still alive here.."
					try:
						item = phase_twoPool.get()
						num += 1
						print "we got #", num, phase_twoPool.qsize(), "objects so far in pool to process."
						
						try:
							this_judge2 = "http://membres.multimania.fr/pej7000/pej7000.php"
							
							item = self.process_proxy(item, this_judge2)
							item.last_checked = strftime("%d/%m/%Y %H:%M:%S %Z", time.localtime())
							
							processedPool.put(item)
												
							if item.alive == True:
								item.clear()
								item.plus_good()
								print 'PASSED id#%-5d %-10s %s:%-6s c:%s host: %s %f health: %f g: %d b: %d bf: %d murdered: %s' % (num, item.last_checked, item.ip, item.port, item.get_country_code(), item.hostname,item.resp, item.get_health(), item.good, item.bad, item.get_flags_bin(), item.is_dead())
								
								#print 'above used judge:', this_judge, this_judge2
								#print ""
								#print self.getName(), "here, responsible for ", item.ip, " found it to be WORKING"
								#print 'id#%-5d %-10s %s:%-6s c:%s host: %s %f health: %f tests: %d' % (theVar, item.last_checked, item.ip, item.port, item.get_country_code(), item.hostname,item.resp, item.get_health(), item.good + item.bad)
								sys.stdout.flush()
							else:
								item.plus_bad()
								#print self.getName(), "here, responsible for ", item.ip, " found it to be BROKEN"
						except Exception, e:
							print "phase_two error:", e
						#~ print "taking a break"
						#~ time.sleep(random.randint(1,3))
					except Exception, e:
						print "P2 ERROR:", e
						pass
				

			def process_proxy(self, item, this_judge2):
				global ip
				global block_list
				global jude_identifier
				
				self.item = item
				self.this_judge2 = this_judge2
				self.sock = None
				self.item.resp = 0
				
				self.item.resp, alive_status = self.is_alive(self.item, self.this_judge2)
				if alive_status:
					self.item.alive = True
				else:
					if self.item.alive == False:
						self.item.flags["black"] += 1
						#This proxy failed twice in a row
					else:
						self.item.alive = False
						
				return self.item
				
			#Tests with 2 proxy judges if first one is successful
			def is_alive(self, pip, this_judge2):
				global judge_identifier
				resp = 0
				page = ""

				"""test #2"""
				sentinel = False
				j = 0
				
				try:
					resp_s = time.time()
					prox = pip.ip + ":" + pip.port
					proxy_handler = urllib2.ProxyHandler({'http': prox})
					opener = urllib2.build_opener(proxy_handler)
					opener.addheaders = [('User-agent', 'Mozilla/5.0')]
					urllib2.install_opener(opener)
					req=urllib2.Request(this_judge2)  # change the URL to test here
					

					with contextlib.closing(urllib2.urlopen(req)) as sock:
						present_url = sock.geturl()
						page = sock.read().lower()
					
					
					resp_f = time.time()
					resp = round((resp_f - resp_s), 3)
					
					for identifier in judge_identifier:
						if not page.find(identifier) > -1:
							print "**********"
							print prox, "identifier", identifier, "not found. Dumped to proxytest_dump"
							os.chdir('/home/sleven/apps/v2/proxytest_dump')
							f = open("rejected" + str(prox) + ".html","w")
							f.write(page)
							f.close()
							os.chdir('..')
							print "judge used:", this_judge2
							print ""
							print ""
							print "**********"
							return resp, False
					
					if not present_url == this_judge2:
						print "Requested page", this_judge2, ", but was redirected to", present_url, ". Please confirm."
						print pip.ip, ":", pip.port
						print page
						print prox, "failed test #2"
						return resp, False
					if not ip.search(page) == None:
						#print "leaks IP address"
						#print prox, "failed test #2 IP leak"
						return resp, False
						
					if page.find('codeen') > -1:
						print "codeen found in html"
						return resp, False
				except urllib2.HTTPError, e:
					print 'Error code: ', e.code
					print prox, "failed test #2."
					#~ if j < 2:
						#~ j += 1
						#~ time.sleep(random.randint(3,20))
						#~ 
					#~ else:
						#~ print prox, "failed test #2 permanently"
					return resp, False
				except Exception, detail:
					print "ERROR:", detail
					print prox, "failed test #2."
					#~ if j < 2:
						#~ j += 1
						#~ time.sleep(random.randint(3,20))
					#~ else:
						#~ print prox, "failed test #2 permanently"
					return resp, False
				
				#os.chdir('/home/sleven/apps/v2/proxytest_dump')
				#f = open(str(prox) + "_2_.html","w")
				#f.write(page)
				#f.close()
				#os.chdir('..')
				
				return resp, True
		MyThread().start()
		#threadp2.join(10)
