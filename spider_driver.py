import sys
from sqlalchemy import *
import random
import time
import spider_engine
from operator import itemgetter, attrgetter
import search_book_page
import re
import os
import scrape_file_3

def sort_by_url (result_book):
	"""Now we sort all the proxies in the cache/list"""
	result_book[:] = sorted(result_book, key=attrgetter('url','date'))

	"""...and delete the duplicates"""
	x = 0
	while x + 1 < len(result_book):
		if result_book[x].url == result_book[x+1].url:
			print result_book[x].url, " is the same as ", result_book[x+1].url
			del result_book[x + 1]
		else:
			x += 1
	return result_book

def read_database():
	result_book = []
	try:
		engine = create_engine('sqlite:///search_book.db',echo=False)
	 
		metadata = MetaData(bind=engine)
		
		main_tbl = Table('main', metadata,
							Column('id', Integer, primary_key=True),
							Column('url', String),
							Column('visited', Boolean),
							Column('date', String)
							)
							
		metadata.create_all()
		
		s = select([main_tbl])
		conn = engine.connect()
		result = conn.execute(s)
		
		for page in result:
			if page.url != None:
				new_page = search_book_page.Search_Book_Page(page.url, page.visited, page.date)
				result_book.append(new_page)
			
	except Exception, e:
		print "Error accessing database.", e
		return result_book;
		
	return result_book;
	
seed_book = read_database()
seed_book = sort_by_url(seed_book)	
seed_book = sorted(seed_book, key=attrgetter('page_yield'))
seed = seed_book.pop()
MAX_THREADS = 3
startURL = seed.url

domain = re.compile(r'\.\w+/')

print "before:", startURL
domain_found = domain.search(startURL).group()
print "found: ", domain_found
startURL = startURL[:startURL.find(domain_found)+len(domain_found)]

print "after: ", startURL
print "yield", seed.page_yield
raw_input("")
os.chdir('spider_dump')
spider = spider_engine.Spider(startURL, MAX_THREADS)
URLs = spider.run()

print "* Checking spider dump for new proxies"
y = 0

current = []

def processDirectory (args, dirname, filenames ):
	print 'Directory',dirname
	for filename in filenames:
		print ' File',filename
		try:
			f = open(filename,"r")
			body = f.read()
			scraper = scrape_file_3.ScrapePage()
			new_proxies = scraper.execute(body)
			current.extend(new_proxies)
			f.close
			print len(new_proxies)," proxies found."
		except Exception, e:
			print e
			pass
	return 0
 
top_level_dir = "/home/sleven/apps/v2/spider_dump"
os.path.walk(top_level_dir, processDirectory, None )

print "proxies got", len(current)
sys.exit()
