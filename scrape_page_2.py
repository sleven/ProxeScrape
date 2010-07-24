




import re
import proxy
import sys
import proxytools
import urllib2

ip_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
port_pattern = re.compile(r"D+\d{2,5}\D+")
proxy_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\D+\d{2,5}\D")
proxy_pattern_1 = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:d{2,5}")
scrape = proxytools.ProxyTools()

proxy_pattern = re.compile(r"[1-2]?[0-9]{1,3}.[1-2]?[0-9]{1,3}.[1-2]?[0-9]{1,3}.[1-2]?[0-9]{1,3}[: ][1-9]?[0-9]{1,5}")


class ScrapePage:	
	
	def execute (self, url):
		
		plist = []
		
		print "Scraping ",url,
		sys.stdout.flush()
		
		try:
			try:
				infile, html = scrape.html_proxy_get(url, True)
				with open("infile", "w") as f:
					f.write(infile)
				
				page_clip = infile[infile.find((ip_pattern.search(infile)).group()):len(infile)]
			except urllib2.HTTPError, e:
				print e
				return plist;
				
		except Exception, e:
			print "Scrape Page 2:", e
			return plist;
			
		while 1:
			try:
				new_proxy = (proxy_pattern.search(page_clip)).group()
				page_clip = page_clip.replace(new_proxy,"")
				#print "new_proxy ==> ", new_proxy
			except:
				#print "error finding proxy_pattern in page"
				break
			
			try:
				new_ip = (ip_pattern.search(new_proxy)).group()
				new_proxy = new_proxy.replace(new_ip,"")
				#print "Found ==>", new_ip,
				sys.stdout.flush()
			except:
				print "error finding ip in proxy pattern"
			
			try:
				try:
					new_port = (port_pattern2.search(new_proxy)).group()
				except:
					pass
					
				try:
					new_port = (port_pattern.search(new_proxy)).group()
				except:
					pass
					
				#print "and port::", new_port

				add_this = proxy.Proxy(new_ip, new_port)
				add_this.set_url(url)
				plist.append(add_this)
			except:
				print "error finding port in proxy pattern"
				
		print "Got ", len(plist), " proxies."
		
		return plist;

