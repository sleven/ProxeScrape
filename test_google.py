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
import google
import proxy

def main():
	plist = []
	new_proxy = proxy.Proxy("92.52.125.20", "80")
	plist.append(new_proxy)
	url = 'http://www.hlgzs.com/Html/?6052.html'
	test = google.Google()
	plist = test.execute(plist)
	
	#for l in plist:
		#print l
	return 0

if __name__ == '__main__':
	main()
