import ClientForm
import urllib2
import sys
import ClientCookie
import ClientForm
from datetime import date
import socket
socket.setdefaulttimeout(12)

class PF_ForumPoast:
	def poast(self, plain, speed, detail, title, sum):
		last_poast = "none"
		today = date.today()
		date_file = []
		
		with open('fpoast.txt', 'r') as f:
			for line in f:
				date_file.append(int(line.strip()))
			
		last_poast = date(date_file[0],date_file[1],date_file[2])

		print ""
		print today
		print "last ", last_poast
		if last_poast < today:# or last_poast == None:
			trys = 0
			print "Creating new forum poast..."
			
			try:
				#Create special URL opener (for User-Agent) and cookieJar
				cookieJar = ClientCookie.CookieJar()
				opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cookieJar))
				opener.addheaders = [("User-agent","Mozilla/5.0 (compatible)")]
				ClientCookie.install_opener(opener)
				try:
					fp = ClientCookie.urlopen("http://www.proxyfire.net/forum/login.php")
					forms = ClientForm.ParseResponse(fp)
					fp.close()
				except Exception, e:
					print e
					if trys < 6:
						time.sleep(5)
						print "trying again..."
						trys += 1
					else:
						print "proxyfire.net is timing out"		

				form = forms[0]
				form["vb_login_username"]  = "sleven" # use your userid
				form["vb_login_password"] = "nehalem"      # use your password

				fp = ClientCookie.urlopen(form.click())
				fp.close()

				"""login part"""
				trys = 0

				request2 = ClientCookie.urlopen("http://www.proxyfire.net/forum/forumdisplay.php?f=14")
				request2.close()
				request3 = ClientCookie.urlopen("http://www.proxyfire.net/forum/newthread.php?do=newthread&f=14")

				forms = ClientForm.ParseResponse(request3, backwards_compat=False)

				## f = open("example.html")
				## forms = ClientForm.ParseFile(f, "http://example.com/example.html",
				##                              backwards_compat=False)
				## f.close()
				form = forms[0]
				print form  # very useful!

				form["subject"]  = title # use your userid
				form["message"] = "Working L1/L2 Proxies. Screened for and removed planetlab, .mil, .gov, .edu, and any non-anonomous proxies. No USA proxies either, these are all international (from an american point of view, at least), since that is all that I use. If you are curious about which country you would be using check out the python output for a two letter country code in the network information block." + "\nPython engine output (" + sum + "):" + "\n[CODE]"+ detail +"[/CODE]" + '\n' +  "Ranked by Speed (" + sum + "):\n[CODE]"+ speed  +"[/CODE]" + '\n' +  "Stripped (" + sum + "):\n[CODE]" + plain +"[/CODE]" + '\n' + "More proxies at proxejaculate.blogspot.com" + '\n' + "Enjoy :)" + "\n" + "Experienced python, shell, or perl coders please contact me through pm if you are interested in helping code."
				#form["message"] = "Working L1/L2 Proxies(" + sum + ")" + "\n" + "Stripped format:" + "\n" + "[CODE]" + plain + "[/CODE]" + '\n' + "Ranked by speed:" + "\n" + "[CODE]"+ speed  +"[/CODE]" + "\n" + "More proxies at proxejaculate.blogspot.com" + '\n' + "Enjoy :)"
				form.set_value(["6"], name="iconid", kind="list")

				fp = ClientCookie.urlopen(form.click())
				fp.close()
				with open('fpoast.txt', 'w') as f:
						f.write(str(today.year) + '\n')
						f.write(str(today.month) + '\n')
						f.write(str(today.day) + '\n')
			except Exception, e:
				print "Maybe we didn't poast to proxyfire?"
				pass
			

					
