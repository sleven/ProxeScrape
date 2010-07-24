import proxytools

scrape = proxytools.ProxyTools()

print "Scraping"
try:
	html = scrape.html_proxy_get('http://www.google.com', False)
except Exception, e:
	print "Error scraping the page:", e

print "********************************"
print html
