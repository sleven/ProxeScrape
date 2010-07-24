import sys
import proxytools
import scrape_page_3
import random
import time

class PF_PublicList:
	def execute (self):
		urls = []
		
		try:
			f = open("sites", "r")
			for line in f:
				urls.append(line.strip('\n'))
			f.close()
		except Exception, e:
			print e
		
		plist = []
		scrape = proxytools.ProxyTools()
		url = 0
		
		try:
			random.shuffle(urls)
		except Exception, e:
			print e
		try:
			for x in range(0, len(urls)):
				try:
					new_list = scrape_page_3.ScrapePage()
					list = new_list.execute(urls[x])
					for new_proxy in list:
						new_proxy.set_url(urls[x])
						plist.append(new_proxy)
				except Exception, e:
					print "...couldn't find page", e
					continue
		except Exception, e:
			print e
		return plist;
