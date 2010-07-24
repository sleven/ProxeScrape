import random
import urllib
import urllib2
import socket
import re
import sys
import time
import os
from time import gmtime, strftime
socket.setdefaulttimeout(10)

class ProxyTools:
	def __init__(self):
		socket.setdefaulttimeout(6)
		self.reloaded = []
		self.minproxies = 0
		self.proxyList = []
		copy = []
		self.totalproxies = 0


	def html_proxy_get(self, url, google_bot = False):
		sentinel = 0
		sleep = 1
		while(sentinel == 0):
			
			try:
				opener = urllib2.build_opener()
				if google_bot:
					opener.addheaders = [('User-agent', 'Googlebot/2.1 (+http://www.google.com/bot.html)')]
				else:
					opener.addheaders = [('User-agent', 'Mozilla/5.0 Firefox/2.0.0.12')]
				urllib2.install_opener(opener)
				req = urllib2.Request(url)
				response = urllib2.urlopen(req)
				the_page = response.read()
				sentinel = 1
				response.close()
				
			except Exception, detail:
				sys.stdout.flush()
				print url, "Err ", detail
				#print "X,",
				sentinel = 0
				sleep *= 2
				if (sleep < 3):
					print "Can't find url, waiting for ", sleep, " seconds"
					time.sleep(sleep)
				else:
					sentinel = 1
					print "Catastrophic error, could not locate the page."
					the_page = "blank"
					response = "blank"
					break
				
		return the_page

	def sort_dict(ip_list):
		
		temp_list = []
		return_list = []
		return_dict = {}
		
		temp_list = ip_list.keys()
		
		for x in temp_list:
			print x
			
		return_list = sorted(temp_list, key=lambda ip:IP(ip).int())
		
		for item in return_list:
			return_dict[item] = ip_list[item]
			
		return return_dict
		
	def remove_dupes(self, ip_list):

		for value in ip_list:
			while ip_list.count(value) > 1:
				ip_list.remove(value)
		return ip_list

"""cool load bar"""
"""print "Progress: ", round((float(i)/float(len(proxylist)) * 100), 2), "% complete"""
