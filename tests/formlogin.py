#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       untitled.py
#       
#       Copyright 2010 Unknown <geoff@arch-box>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


import sys
sys.path.append('ClientCookie-1.0.3')
import ClientCookie
sys.path.append('ClientForm-0.1.17')
import ClientForm
import re
from mechanize import Browser

br = Browser()
response1 = br.open("http://www.proxyfire.net/forum/login.php")
br.set_handle_robots(False)
assert br.viewing_html()
print br.title()
print response1.geturl()
#print response1.info()  # headers
#print response1.read()  # body

#ClientForm.ParseResponse(response1)

f = br.forms()
	#~ print "vvvvv"
	#~ print f.name
	#~ print "^^^^^"

# .links() optionally accepts the keyword args of .follow_/.find_link()
#for link in br.links():
    #print link
    
br.select_form(f[0])
form["vb_login_username"] = "sleven"
form["vb_login_password"] = "nehalem"


raw_input("")
response2 = br.submit()

print br.title()
print response2.geturl()

# Create special URL opener (for User-Agent) and cookieJar
#~ cookieJar = ClientCookie.CookieJar()

#~ opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cookieJar))
#~ opener.addheaders = [("User-agent","Mozilla/5.0 (compatible)")]
#~ ClientCookie.install_opener(opener)
#~ fp = ClientCookie.urlopen("http://www.proxyfire.net/forum/login.php")
#~ forms = ClientForm.ParseResponse(fp)
#~ fp.close()

# print forms on this page
#~ for form in forms: 
    #~ print "***************************"
    #~ print form

form = forms[0]
form["vb_login_username"]  = "sleven" # use your userid
form["vb_login_password"] = "nehalem"      # use your password
#~ 
fp = ClientCookie.urlopen(form.click())

fp = ClientCookie.urlopen("http://www.proxyfire.net/forum/showthread.php?t=50200") # use your group
forms = ClientForm.ParseResponse(fp)
for form in forms: 
    print "***************************"
    print form

fp.close()
