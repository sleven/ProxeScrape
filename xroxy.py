#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       untitled.py
#       
#       Copyright 2010 Unknown <geoff@Arch-Linux>
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


import urllib2
import re
import os.path
import urllib
import sys
sys.path.append('ClientCookie-1.0.3')
import ClientCookie
sys.path.append('ClientForm-0.1.17')
import ClientForm
import proxy
import time
import socket
import random

proxy_pattern = re.compile(r"[1-2]?[0-9]{1,3}.[1-2]?[0-9]{1,3}.[1-2]?[0-9]{1,3}.[1-2]?[0-9]{1,3}[: ][1-9]?[0-9]{1,5}")
socket.setdefaulttimeout(10)
class Xroxy:

    def execute(self):
		
		print "proxyFire module loaded"
		sub_urls = []
		sub_titles = []
		sub_index = 0
		plist = []
		trys = 0
		
		# Create special URL opener (for User-Agent) and cookieJar
		cookieJar = ClientCookie.CookieJar()
		opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cookieJar))
		opener.addheaders = [("User-agent","Mozilla/5.0 (compatible)")]
		ClientCookie.install_opener(opener)
		try:
			fp = ClientCookie.urlopen("http://www.xroxy.com/xorum/login.php")
			forms = ClientForm.ParseResponse(fp)
			fp.close()
		except Exception, e:
			print e
			if trys < 6:
				time.sleep(5)
				print "trying again..."
				trys += 1
			else:
				print "xroxy is timing out"
				return plist;
				
		try:
			form = forms[1]
			form["username"]  = "sleven" # use your userid
			form["password"] = "nehalem"      # use your password

			fp = ClientCookie.urlopen(form.click())
			fp.close()
		except Exception, e:
			print e
		"""login part"""
		trys = 0
		try:
			time.sleep(5)
			top_thread = 'http://www.xroxy.com/xorum/viewforum.php?f=3'
			fp = ClientCookie.urlopen(top_thread)
			the_page = fp.read()
			
			fp.close()
		except Exception, e:
			print e
			if trys < 6:
				time.sleep(5)
				print "trying again..."
				trys += 1
			else:
				print "xroxy is timing out"
				return plist;
		
		while 1:
			try:
				
				sub_pattern = re.compile(r't=\d+')
				num_pattern = re.compile(r'\d+')
				pg_num = sub_pattern.search(the_page)
				grouped = pg_num.group()
				sub_urls.append(str(num_pattern.search(grouped).group()))
				
				the_page = the_page.replace(pg_num.group(),"")
				
			except Exception, e:
				print "Error finding threads", e
				break
		print "Found ", len(sub_urls), " threads."
		while(sub_index < len(sub_urls)):
			new = []
			new[:] =[]
			sub_url = "http://www.xroxy.com/xorum/viewtopic.php?t=" + sub_urls[sub_index]
			print '  Scraping thread ',
			
			try:
				time.sleep(random.randint(2,10))
				print sub_url,
				req = ClientCookie.urlopen(sub_url)
				html = req.read()
				
				"""Saying thanks"""
				#if html.find('<a href="member.php?u=34794" rel="nofollow">sleven</a>') > -1:
					#print "already said thanks before."
				#elif html.find('<a class="bigusername" href="member.php?u=34794">sleven</a>') > -1:
					#print "this is our thread, skipping thanks."
				#else:
					#fp = ClientCookie.urlopen("http://www.proxyfire.net/forum/post_thanks.php?do=post_thanks_add&using_ajax=1&p=102092") # use your group
					#print "we said thanks for this post."
				req.close()
			except Exception, e:
				print "Error scraping the page:", e

			try:
				
				string_list = proxy_pattern.findall(html)
				
				for string in string_list:
					stack = re.split("[: ]", string)
					new_proxy = proxy.Proxy(stack[0],stack[1])
					new_proxy.set_url(sub_url)
					new.append(new_proxy)
			
			except Exception, e:
				print "Error stacking strings: ", e

			print "Got ", len(new), " proxies."		
			sub_index += 1
			
			plist.extend(new)
		print "Final result ", len(plist), "proxies from xroxy forums."
		return plist;
