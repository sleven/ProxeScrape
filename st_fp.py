import ClientForm
import urllib2
import sys
import ClientCookie
import ClientForm
from datetime import date
import socket
socket.setdefaulttimeout(12)

class ST_FP:
	def poast(self, plain, speed, detail, title, sum):
		
		last_poast = "none"
		today = date.today()
		date_file = []
		
		with open('ST_FP.txt', 'r') as f:
			for line in f:
				date_file.append(int(line.strip()))
			
		last_poast = date(date_file[0],date_file[1],date_file[2])

		print ""
		print today
		print "last ", last_poast
		if last_poast < today:# or last_poast == None:
			trys = 0
			print "Creating new strumpf-ist-trumpf.com forum poast..."
			
			try:
				#Create special URL opener (for User-Agent) and cookieJar
				cookieJar = ClientCookie.CookieJar()
				opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cookieJar))
				opener.addheaders = [("User-agent","Mozilla/5.0 (compatible)")]
				ClientCookie.install_opener(opener)
				try:
					fp = ClientCookie.urlopen("http://www.stumpf-ist-trumpf.com/myprox/forum/ucp.php?mode=login")
					forms = ClientForm.ParseResponse(fp)
					fp.close()
				except Exception, e:
					print e
					if trys < 6:
						time.sleep(5)
						print "trying again..."
						trys += 1
					else:
						print "st_fp is timing out"		

				form = forms[1]
				form["username"]  = "sleven" # use your userid
				form["password"] = "nehalem"      # use your password

				fp = ClientCookie.urlopen(form.click("login"))
				fp.close()

				"""login part"""
				trys = 0

				request2 = ClientCookie.urlopen("http://www.stumpf-ist-trumpf.com/myprox/forum/anonymous-http-proxies-f4.html")
				request2.close()
				request3 = ClientCookie.urlopen("http://www.stumpf-ist-trumpf.com/myprox/forum/posting.php?mode=post&f=4")

				forms = ClientForm.ParseResponse(request3, backwards_compat=False)

				## f = open("example.html")
				## forms = ClientForm.ParseFile(f, "http://example.com/example.html",
				##                              backwards_compat=False)
				## f.close()
					
				form = forms[1]
				#print form  # very useful!
				print form
				
				form["subject"]  = title # use your userid
				form["message"] = "Working L1/L2 Proxies. Screened for and removed planetlab, .mil, .gov, .edu, and any non-anonomous proxies. No USA proxies either, these are all international (from an american point of view, at least), since that is all that I use. If you are curious about which country you would be using check out the python output for a two letter country code in the network information block." + "\nPython engine output (" + sum + "):" + "\n[CODE]"+ detail +"[/CODE]" + '\n' +  "Ranked by Speed (" + sum + "):\n[CODE]"+ speed  +"[/CODE]" + '\n' +  "Stripped (" + sum + "):\n[CODE]" + plain +"[/CODE]" + '\n' + "More proxies at proxejaculate.blogspot.com" + '\n' + "Enjoy :)" + "\n" + "Experienced python, shell, or perl coders please contact me through pm if you are interested in helping code."
				#form["message"] = "Working L1/L2 Proxies(" + sum + ")" + "\n" + "Stripped format:" + "\n" + "[CODE]" + plain + "[/CODE]" + '\n' + "Ranked by speed:" + "\n" + "[CODE]"+ speed  +"[/CODE]" + "\n" + "More proxies at proxejaculate.blogspot.com" + '\n' + "Enjoy :)"

				fp = ClientCookie.urlopen(form.click())
				page = fp.read()
				fp.close()
				
				with open('ST_FP.txt', 'w') as f:
						f.write(str(today.year) + '\n')
						f.write(str(today.month) + '\n')
						f.write(str(today.day) + '\n')
			except Exception, e:
				print "Maybe we didn't poast to st_fp?"
				print e
				pass
			

					
