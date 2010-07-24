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
import proxy
import proxytools
import re
import sys
import scrape_page_3

class Free_Proxy_Lists():
	
	def execute(self):
		
		sys.stdout.flush()
		scrape = proxytools.ProxyTools()
		junk_pattern2 = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\S{21}\d{2,5}")
		u_index = 0
		plist = []

		url = 'http://www.freeproxylists.com/elite.html'
		page_clip = scrape.html_proxy_get(url)
		print "Scraping ",url,
		sub_urls = []
		sub_index = 0
		
		while(True):
			try:
				sub_pattern = re.compile(r"<a href='elite/d\d+")
				junk_is = "<a href='elite/d"
				pg_num = sub_pattern.search(page_clip)
				grouped = pg_num.group()
				set = grouped.split(junk_is)
				sub_urls.append(str(set[1]))
				page_clip = page_clip.replace(pg_num.group(),"")
			except Exception, e:
				print e
				break
		
		while(sub_index < len(sub_urls)):
			sub_url = "http://www.freeproxylists.com/load_elite_" + sub_urls[sub_index] + ".html"
			#print "  Scraping child page ", sub_url
			new_list = scrape_page_3.ScrapePage()
			list = new_list.execute(sub_url)
			
			for new_proxy in list:
				plist.append(new_proxy)

			sub_index += 1
			
			
		url = 'http://freeproxylists.com/anonymous.html'
		page_clip = scrape.html_proxy_get(url)
		print "Scraping ",url,
		sub_urls = []
		sub_index = 0
		
		while(True):
			try:
				sub_pattern = re.compile(r"<a href='anon/d\d+")
				junk_is = "<a href='anon/d"
				pg_num = sub_pattern.search(page_clip)
				grouped = pg_num.group()
				set = grouped.split(junk_is)
				sub_urls.append(str(set[1]))
				page_clip = page_clip.replace(pg_num.group(),"")
			except Exception, e:
				print e
				break
				
		while(sub_index < len(sub_urls)):
			sub_url = "http://www.freeproxylists.com/load_anon_" + sub_urls[sub_index] + ".html"
			#print "  Scraping child page ", sub_url
			new_list = scrape_page_3.ScrapePage()
			list = new_list.execute(sub_url)
			
			for new_proxy in list:
				plist.append(new_proxy)

			sub_index += 1
		return plist;
