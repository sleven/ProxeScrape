from gdata import service
import gdata
import atom
import sys
import time
from time import gmtime, strftime
import pf_forumpoast
from operator import itemgetter, attrgetter
from sqlalchemy import *
import proxy
import re
import xroxy_forum_poast
import st_fp

country = re.compile(r"\s[A-Z1]{1}[A-Z10]{1}")
class BlogSpot:
	def login(self):
		blogger_service = service.GDataService('geoff.blogspot@gmail.com', 'rcsck7x890')
		blogger_service.source = 'exampleCo-exampleApp-1.0'
		blogger_service.service = 'blogger'
		blogger_service.account_type = 'GOOGLE'
		blogger_service.server = 'www.blogger.com'
		blogger_service.ProgrammaticLogin()
		return blogger_service

	def PrintUserBlogTitles(self, blogger_service):
		query = service.Query()
		query.feed = '/feeds/default/blogs'
		feed = blogger_service.Get(query.ToUri())

		print feed.title.text
		for entry in feed.entry:
			print "\t" + entry.title.text
		
		return feed.entry[0].GetSelfLink().href.split("/")[-1]

	def CreatePublicPost(self, blogger_service, blog_id, title, content):
	  entry = gdata.GDataEntry()
	  entry.title = atom.Title('xhtml', title)
	  entry.content = atom.Content(content_type='html', text=content)
	  return blogger_service.Post(entry, '/feeds/%s/posts/default' % blog_id)

	def generate_poast(self, plist, speed, blogger_service, blog_id):
		
		num = len(plist)
		poast = ""
		plain = ""
		detail = ""
		head = '<span style="color: rgb(204, 204, 204);font-size:100%;" >Note, the tables below are the same proxy list in different formats.<br><br></span><table width="1014px"><tbody><tr><td><span style="font-size:130%;">Stripped(' + str(num) + '):</span><pre style="border: 1px inset; margin: 1px; padding: 5px; overflow: auto; width: 400px; height: 150px; text-align: left;" dir="ltr" class="alt2"><span style="font-weight: bold;"></span><span style="font-weight: bold;font-size: large">'
		detail_head = '\n' + '</span></pre></td></tr></tbody></table><br><table width="905px"><tbody align="left"><tr><td><span style="font-size:130%;">Complete python engine output(' + str(num) + '):</span><pre style="border: 1px inset; margin: 0px; padding: 5px; overflow: auto; width: 672px; height: 317px; text-align: left;" dir="ltr" class="alt2"><span style="font-weight: bold;"></span><span style="font-weight: bold;font-size: large"">'
		middle = '</span></pre><br><span style="font-size:130%;">Ranked by Speed(sec) with Country Code(' + str(num) + '):</span><pre style="border: 1px inset; margin: 1px; padding: 5px; overflow: auto; width: 400px; height: 150px; text-align: left;" dir="ltr" class="alt2"><span style="font-weight: bold;"></span><span style="font-weight: bold;font-size: large"">'
		end = '</span></pre></td></tr></tbody></table><br><br>'
		title= 'New L1/L2 Proxies(' + str(num) + ') %s' % strftime("%A %d/%m/%y %I:%M%p %Z", time.localtime())
		
		
		print "Generating new poast content"

		for row in plist:
			plain = plain + row.ip + ":" + row.port + "\n"
			cn_code = row.get_country_code()
			detail = detail + 'id#%-5d last_checked=%-10s %s:%-6s country=%s hostname=%s \n' % (plist.index(row), row.last_checked, row.ip, row.port, cn_code, row.hostname)

		
		poast = head + plain + middle + speed + detail_head + detail + end
		f = open("poast.html", "w")
		f.write(poast)
		f.close()
		
		print "Poasting to blog...",
		sys.stdout.flush()
		
		blogEntry = self.CreatePublicPost(blogger_service, blog_id, title, poast)
		
		fp = pf_forumpoast.PF_ForumPoast()
		fp.poast(plain, speed, detail, title, str(num))
		xroxy = xroxy_forum_poast.Xroxy()
		xroxy.poast(plain, speed, detail, title, str(num))
		st = st_fp.ST_FP()
		st.poast(plain, speed, detail, title, str(num))
