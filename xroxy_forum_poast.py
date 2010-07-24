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
from datetime import date


socket.setdefaulttimeout(12)
proxy_pattern = re.compile(r"[1-2]?[0-9]{1,3}.[1-2]?[0-9]{1,3}.[1-2]?[0-9]{1,3}.[1-2]?[0-9]{1,3}[: ][1-9]?[0-9]{1,5}")
socket.setdefaulttimeout(10)
class Xroxy:
    def poast(self, plain, speed, detail, title, sum):
		print "xroxy module loaded"
		sub_urls = []
		sub_titles = []
		sub_index = 0
		plist = []
		trys = 0
		date_file = []
		last_poast = "none"
		today = date.today()
		
		try:
			with open('xroxy_poast.txt', 'r') as f:
				for line in f:
					date_file.append(int(line.strip()))
			
		except Exception, e:
			print "Error reading date file:", e
		try:
			last_poast = date(date_file[0],date_file[1],date_file[2])
		except:
			pass
			
		print ""
		print "today is", today
		print "last was on", last_poast
		if last_poast < today:
			trys = 0
			print "Creating new xroxy forum poast..."
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
				top_thread = 'http://www.xroxy.com/xorum/viewforum.php?f=6'
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

			request3 = ClientCookie.urlopen("http://www.xroxy.com/xorum/posting.php?mode=newtopic&f=6")

			forms = ClientForm.ParseResponse(request3, backwards_compat=False)
			page = request3.read()
			
			request3.close()
			
			## f = open("example.html")
			## forms = ClientForm.ParseFile(f, "http://example.com/example.html",
			##                              backwards_compat=False)
			## f.close()
			
			form = forms[1]
			print form  # very useful!

			form["subject"]  = title # use your userid
			form["message"] = "Working L1/L2 Proxies. Screened for and removed planetlab, .mil, .gov, .edu, and any non-anonomous proxies. No USA proxies either, these are all international (from an american point of view, at least), since that is all that I use. If you are curious about which country you would be using check out the python output for a two letter country code in the network information block." + "\nRanked by Speed w/Country Code(" + sum + "):\n[CODE]"+ speed  +"[/CODE]" + '\n' +  "Plain (" + sum + "):\n[CODE]" + plain +"[/CODE]" + '\n' + "More proxies at proxejaculate.blogspot.com" + '\n' + "Enjoy. Feedback is always welcome. :)" + "\n"
			#form["message"] = "Working L1/L2 Proxies(" + sum + ")" + "\n" + "Stripped format:" + "\n" + "[CODE]" + plain + "[/CODE]" + '\n' + "Ranked by speed:" + "\n" + "[CODE]"+ speed  +"[/CODE]" + "\n" + "More proxies at proxejaculate.blogspot.com" + '\n' + "Enjoy :)"

			fp = ClientCookie.urlopen(form.click("post"))
			page = fp.read()
			fp.close()
			with open('xroxy_poast.txt', 'w') as f:
					f.write(str(today.year) + '\n')
					f.write(str(today.month) + '\n')
					f.write(str(today.day) + '\n')
