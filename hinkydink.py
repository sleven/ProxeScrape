


import re
import proxy
import sys
import proxytools
import socket

url = "http://www.mrhinkydink.com/proxies.htm"

plist = []
ip_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
port_pattern = re.compile(r"<td>\d{2,5}</td>")
pages = 6
start = 2
scrape = proxytools.ProxyTools()
socket.setdefaulttimeout(10)
class HinkyDink:
	
	def execute (self):
		global hinkylist
		global url
		
		print "Scraping ",url,
		sys.stdout.flush()
		for x in range(start, pages + 1):
			switch = True

			infile = scrape.html_proxy_get(url)
			page_clip = infile[infile.find((ip_pattern.search(infile)).group()):len(infile)]
			
			while (switch):
				try:
					new_ip = (ip_pattern.search(page_clip)).group()
					ip_index = page_clip.find(new_ip)
					page_clip = page_clip.replace(new_ip,"")
					
					#print "Found ==>", ip,
					sys.stdout.flush()

					try:
						new_port = ((port_pattern.search(page_clip[ip_index:len(infile)])).group()).strip("<td>/")
						#print "and port::", port
										
						new_proxy = proxy.Proxy(new_ip, new_port)
						new_proxy.set_url(url)
						plist.append(new_proxy)
					except:
						print "Proxy ", new_ip, " doesn't have a port?"
				
				except Exception, e:
					#print e, "..the fuck?"
					switch = False
			
			url = "http://www.mrhinkydink.com/proxies" + str(x) + ".htm"
			switch = True
			
		return plist;
