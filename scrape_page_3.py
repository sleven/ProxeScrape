import re
import proxy
import sys
import proxytools
import urllib2
import html2text
import socket
import unicodedata, re

all_chars = (unichr(i) for i in xrange(0x110000))
control_chars = ''.join(map(unichr, range(0,46) + range(45,48,2) + range(58,256)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))
def remove_control_chars(s):
    return control_char_re.sub(' ', s)

#ip_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
#port_pattern = re.compile(r"D+\d{2,5}\D+")
#proxy_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\D+\d{2,5}\D")
#proxy_pattern_1 = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:d{2,5}")
scrape = proxytools.ProxyTools()
socket.setdefaulttimeout(10)
#proxy_pattern = re.compile(r"[1-2]?[0-9]{1,3}[.][1-2]?[0-9]{1,3}[.][1-2]?[0-9]{1,3}[.][1-2]?[0-9]{1,3}[: ][1-9]?[0-9]{1,5}")
proxy_pattern = re.compile(r"[1-2]?[0-9]{1,3}\.[1-2]?[0-9]{1,3}\.[1-2]?[0-9]{1,3}\.[1-2]?[0-9]{1,3}[: ][1-9]?[0-9]{1,5}")



class ScrapePage:	
	def execute (self, url, v):
		plist = []
		if v:
			print "Scraping ",url,
		sys.stdout.flush()

		try:
			html = scrape.html_proxy_get(url, True)
		except Exception, e:
			if v:
				print "Scrape Error: html error:", e
			return plist;
		
		try:
			clean_page = html2text.html2text(remove_control_chars(html))
		except Exception, e:
			if v:
				print e
			try:
				f =  open("html2text_errors","a")
				f.write(url)
				f.close()
			except:
				pass
			return plist;
		
		try:
			string_list = proxy_pattern.findall(clean_page)
			for string in string_list:
				stack = re.split("[: ]", string)
				new_proxy = proxy.Proxy(stack[0],stack[1])
				#~ f= open("scrape_debug","a")
				#~ f.write(stack[0] + "<=>" + stack[1] + "|")
				#~ f.close()
				new_proxy.set_url(url)
				plist.append(new_proxy)
		except Exception, e:
			print "Error stacking strings: ", e
		if v:
			print "Got ", len(plist), " proxies."
		return plist;
