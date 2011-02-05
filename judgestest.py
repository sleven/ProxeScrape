#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       untitled.py
#       
#       Copyright 2010 Unknown <geoff@arch-box>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import urllib2, socket
import time
import re
import sys
import proxy
import random

socket.setdefaulttimeout(2)
index = []
pattern1 = re.compile(r"HTTP_HOST") #\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
pattern2 = re.compile(r"REMOTE_ADDR") #\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
pattern4 = re.compile(r"173.64.122.161")
#pattern2b = re.compile(r"HTTP_X_FORWARDED_FOR\s+173.64.123.229")
#pattern2c = re.compile(r"HTTP_REMOTE_ADDR\s+173.64.123.229")
pattern3 = re.compile(r"HTTP_USER_AGENT")
class judgesTest():
	def is_bad_judge(self, this_judge):
		socket.setdefaulttimeout(2)
		try:			       
			opener = urllib2.build_opener()
			opener.addheaders = [('User-agent', 'Mozilla/5.0')]
			urllib2.install_opener(opener)        
			
			#print "Testing ", this_judge,
			sys.stdout.flush()
			
			req=urllib2.Request(this_judge)  # change the url address here
			sock=urllib2.urlopen(req)			
			page = str(sock.read())
			present_url = sock.geturl()
			sock.close()
			try:
				#print "Checking minimum requirements..."
				host = pattern1.search(page)
				host = host.group()
				#print "1", host
				#~ print "passed test# 1"
				

				addr = pattern2.search(page)
				addr = addr.group()

				#print "2", addr
				#~ print "passed test# 2"

				user_agent = pattern3.search(page)
				user_agent = user_agent.group()
				#print "3",user_agent
				#~ print "passed test# 3"
				
				ip = pattern4.search(page).group()
				
				if not present_url == this_judge:
					#print "Requested page", this_judge, ", but was redirected to", present_url, ". Please confirm."
					#print pip.ip, ":", pip.port
					return 2, present_url
					
			except Exception, e:
				print e
				print this_judge, "failed."
				return 1, this_judge
			
		except urllib2.HTTPError, e:        
			print this_judge, 'Error code: ', e.code
			return 1, this_judge
		except Exception, detail:
			print this_judge, "ERROR:", detail
			return 1, this_judge
		return 0, this_judge
		
		
	def run_test(self, upstream):
		
		index = upstream
		windex = []
		
		start = time.time()
		j_num = len(index)
		
		print "* Testing ", j_num, " judges."
		num = 1
		for judge in index:
			num += 1
			status, return_judge = self.is_bad_judge(judge)

			if status == 0:
				windex.append(judge)
				#print "+ is working."
				if not num % 10:
					print "•"
				print "•",
				sys.stdout.flush()
				
			elif status == 1:
				pass
				#print "- appears broken."
			elif status == 2:
				windex.append(return_judge)
				#print ""
				#print "windex appended", return_judge, " instead of", judge
				#print "+ is working. Redirected."
		
		print "Elapsed Time: %s" % (time.time() - start)
		
		j_num = len(windex)
		print "* ", j_num, " judges are alive."
		print "exit judges test."
		return windex;
