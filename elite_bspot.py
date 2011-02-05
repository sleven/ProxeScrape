




import re
import proxy
import sys
import proxytools


url = "http://elite-proxies.blogspot.com/"

plist = []
ip_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}")
port_pattern = re.compile(r"<td>\d{2,5}</td>")
scrape = proxytools.ProxyTools()

class EliteBSpot:	
	
	def execute (self, v):
		global plist
		global url
		
		if v:
			print "Scraping ",url,
		sys.stdout.flush()

		infile = scrape.html_proxy_get(url, v)
		
		page_clip = infile[infile.find((ip_pattern.search(infile)).group()):len(infile)]
		switch = True
		
		while (switch):
			try:
				new_ip = (ip_pattern.search(page_clip)).group()
				ip_index = page_clip.find(new_ip)
				page_clip = page_clip.replace(new_ip,"")
				
				iport = new_ip.split(":")				
				new_ip = iport[0]
				new_port = iport[1]
				
				#print "Found ==>", new_ip,
				sys.stdout.flush()
				
				#print "and port::", new_port
				
				new_proxy = proxy.Proxy(new_ip, new_port)
				new_proxy.set_url(url)
				plist.append(new_proxy)
			
			except Exception, e:
				#print e, "..the fuck?"
				switch = False
			
		return plist;

