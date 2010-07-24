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

scrape = proxytools.ProxyTools()
socket.setdefaulttimeout(10)


proxy_pattern = re.compile(r"[1-2]?[0-9]{1,3}\.[1-2]?[0-9]{1,3}\.[1-2]?[0-9]{1,3}\.[1-2]?[0-9]{1,3}")

port_numbers = re.compile(r'"t_port">(\d{2},?)+</td>')
port_image = re.compile(r'\d{2}')

js_code = re.compile(r"parseInt\S+\d+")
key_image = re.compile(r"\d+")

class Http_Proxy:
	def decode_port (self, key, port_codes_str):
		port = ""
		port_codes = []
		
		#print "Got this string of ports:", port_codes_str, "so I'm starting with these port codes:"
		
		while 1:
			try:
				result = (port_image.search(port_codes_str)).group()
				port_codes_str = re.sub(port_image,"",port_codes_str,1)
				port_codes.append(result)
			except Exception, e:
				break
		
		#for code in port_codes:
			#print code," ",
		sys.stdout.flush()
		
		#print page

		#print "Using key:", key
		for code in port_codes:
			port = port + str(chr(int(code) + int(key)))
		
		#print "The decoded port was found:", port
		
		#raw_input("")
		return port
		
		
		
	def scrape_page (self, url):
		plist = []
		port_list = []
		string_list = []
		
		print "Scraping ",url,
		sys.stdout.flush()
		
		try:
			html = scrape.html_proxy_get(url, True)
		except Exception, e:
			print "Error scraping the page:", e
			return plist;
		
		try:
			clean_page = html2text.html2text(remove_control_chars(html))
		except Exception, e:
			print e
			try:
				f =  open("html2text_errors","a")
				f.write(url)
				f.close()
			except:
				pass
			return plist;
		
		java = (js_code.search(html)).group()
		key = (key_image.search(java)).group()
		
		oper = java[14]
		#print oper
		if oper == "-":
			key = int(key) * -1
			
		
		#print "Found the js_code: ", java
		#print "Looks like the key is:", key
		
		while 1:
			try:
				result = (port_numbers.search(html)).group()
				html = re.sub(port_numbers,"",html,1)
				port_list.append(result)
				result = (proxy_pattern.search(html)).group()
				html = re.sub(proxy_pattern,"",html,1)
				string_list.append(result)
			except Exception, e:
				#print e
				break
		#print "start"
		#for port in port_list:
			#print port
		
		#print "len stringlist:", len(string_list)
		#print "len portlist:", len(port_list)
		
		for string in string_list:
			#print "Working on ", string, " now."
			#print string_list.index(string)
			decoded_port = self.decode_port(key, port_list[int(string_list.index(string))])
			#print string, ":",decoded_port
			new_proxy = proxy.Proxy(string,decoded_port)
			new_proxy.set_url(url)
			plist.append(new_proxy)

		print "Got ", len(plist), " proxies."
		return plist;
		
		
	def execute (self):
		urls = ["http://proxyhttp.net/"]
		
		for x in range(1,10):
			urls.append('http://proxyhttp.net/list/anonymous-server-hide-ip-address/' + str(x) + '#proxylist')
			
		list = []
		plist = []
		url = 0
		
		for x in range(0, len(urls)):
			list.extend(self.scrape_page(urls[x]))
			for new_proxy in list:
				new_proxy.set_url(urls[x])

			
		return list;
