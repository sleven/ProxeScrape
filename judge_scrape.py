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

import re
import proxy
import sys
import proxytools
import threading
import socket
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.sql import select
from sqlalchemy.sql import and_
from sqlalchemy import *
import time
import scrape_page_3
import search_book_page
from time import gmtime, strftime
import judgestest
import urllib2
import random

"""for sorting algorithm"""
from operator import itemgetter, attrgetter

plist = []
start_search_results = re.compile(r'td valign="top"><div id="center_col"><div id="res"><div id="ires">')
end_search_results = re.compile(r'<div id="foot">')

socket.setdefaulttimeout(4)

url_pattern = re.compile(r'http://\S+')
pages = 6
start = 2
scrape = proxytools.ProxyTools()
total_results = 0
page_clip = ""
class Judge_Scrape(threading.Thread):
	def run(self):
		print "Scraping ",url,
		sys.stdout.flush()
	
	
	def sort_by_url(self, result_book):
		result_book[:] = sorted(result_book)

		"""...and delete the duplicates"""
		x = 0
		while x + 1 < len(result_book):
			if result_book[x]== result_book[x+1]:
				#print result_book[x].url, " is the same as ", result_book[x+1].url
				del result_book[x + 1]
			else:
				x += 1
		return result_book
	def bad_domain(self, url):
		for bad in self.domain_block_list:
			if url.find(bad) > -1:
				return True;
		return False;
		
	def google_crawl(self, upstream=['proxyjudge"HTTP_HOST="']):#'"inurl:prxjdg cgi" -list, -site, -keyword', '"inurl:azenv.php" -list, -site, -keyword']):
			self.domain_block_list = []
			f = open("domain_block_list", "r")
			for line in f:
				self.domain_block_list.append(line.strip('\n'))
			f.close()
			search_book = []
			result_book = []
			try:
				print "Google scrape started"
				
				for row in upstream:
					search_book.append(row)
				print "* Conducting ", len(search_book), "searches."
				
				for search_string in search_book:
					print search_book.index(search_string),"/",len(search_book),"Searching for ", search_string,
					sys.stdout.flush()
					search = 'http://www.google.com/search?hl=en&q=' + str(search_string) + '&start=0&sa=N'
					opener = urllib2.build_opener()
					opener.addheaders = [('User-agent', 'Mozilla/5.0 Firefox/2.0.0.12')]
					urllib2.install_opener(opener)
					req = urllib2.Request(search)
					response = urllib2.urlopen(req)
					html = response.read()
					response.close()
					result_num = 0
					
					try:
						print start_search_results.search(html).group()
					except Exception, e:
						print "couldn't find start"
						print e
						exit()
					try:
						page_clip = html[html.find((start_search_results.search(html)).group()):html.find((end_search_results.search(html)).group())]
					except Exception, e:
						print "search didn't return any results.", e
						result_num = 20
						pass

					nav_number = 90
					total_results = 0
					
					#while total_results == 0:
						#try_this_number = page_clip.find('&amp;start='+str(nav_number))
						#if try_this_number > -1:
							#total_results = nav_number
						#else:
							#nav_number = nav_number - 10
							#if nav_number < 20:
								#total_results = 10
								#break
						
					while result_num <= total_results:	#Start at 0 and end at total_results by 10 step
						search = 'http://www.google.com/search?hl=en&q=' + str(search_string) + '&start=' + str(result_num) + '&sa=N'
						print "  Crawling page #", ((result_num/10) + 1), " for urls."
						#80 = page 9
						try:
							page_clip = scrape.html_proxy_get(search)
							
						except Exception, e:
							print "search didn't return any results.", e
							total_results = 0
							break
						
						if page_clip.find('&amp;start='+str(total_results +10)) > -1:
							print "FOUND ANOTHER PAGE #", (result_num + 10)/10
							total_results += 10
							pass
							print "total_results =", total_results
							
						while 1:
							try:
								result = str((url_pattern.search(page_clip)).group())
								page_clip = page_clip.replace(result,"")
								
								if self.bad_domain(result) == True:
									print "rejected:", result
									pass
								else:
									""" 16 comes from <a href="""
									#result = result[6:len(result)]
									
									print "Found ==>", result
									
									#print page_clip
									
									result = result.replace("amp;","")
									result = result.replace('"',"")
									result = result.strip("\n")
									if result.find(".php") > -1:
										result = result[0:result.find(".php")+4]
									if result.find(".cgi") > -1:
										result = result[0:result.find(".cgi")+4]
									if result.find(".html") > -1:
										result = result[0:result.find(".html")+5]
										
									result_book.append(result)

							except Exception, e:
								print "search_book: ", e
								break
						"""check for any more pages beyond 10 in the google search"""
						result_num += 10
						time.sleep(random.randint(20,32))
				return result_book
			except Exception, e:
				print "google error: ", e
				#result_book = []
				return result_book

def main():

	judge_urls = []
	scrape = Judge_Scrape()
	judge_urls = scrape.google_crawl()
	f = open("judges.txt","r")
	for result in f:
		if result.find(".php") > -1:
			result = result[0:result.find(".php")+4]
		if result.find(".cgi") > -1:
			result = result[0:result.find(".cgi")+4]
		if result.find(".html") > -1:
			result = result[0:result.find(".html")+5]
		judge_urls.append(result.strip("\n"))
	
	judge_urls = scrape.sort_by_url(judge_urls)
	test = judgestest.judgesTest()
	judge_urls = test.run_test(judge_urls)
	f = open("judges.txt","w")
	
	for line in judge_urls:
		f.write(str(line) + '\n')
	f.close()
	print "Wrote", len(judge_urls), "judges to text file."
	
if __name__ == '__main__':
	main()
