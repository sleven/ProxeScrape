import blogspot
from sqlalchemy import *
import time
from time import gmtime, strftime
import proxy
from operator import itemgetter, attrgetter

class Generate_Poast():
	def execute(self, upstream):
		plist = []
		for proxy in upstream:
			if proxy.alive==True and proxy.safe==True and proxy.last_checked != "never":
				# alive means currently alive & safe
				plist.append(proxy)
					
		#with open("detail", "w") as f:
			#for item in plist:
				#f.write('%-10s ALIVE==> %s:%-6s %s %s \n' % (item.last_checked, item.ip, item.port,item.location, item.hostname))
		if len(plist) < 10:
			print "Less than 10 proxies eligible to be poasted. Cancelling poast."
			return
		new_poast = blogspot.BlogSpot()
		speed_list = sorted(plist, key=attrgetter('resp'))
		speed = ""
		
		for row in speed_list:
			speed = speed + str(row.resp) + " " + row.ip + ":" + row.port + row.get_country_code() + '\n'
		
		print "logging in"

		blogger_service = new_poast.login()
		blog_id = new_poast.PrintUserBlogTitles(blogger_service)
		new_poast.generate_poast(plist, speed, blogger_service, blog_id)
		print "Poasted ", len(plist), " new proxies."
		print "done."
