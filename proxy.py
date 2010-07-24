#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       proxy.py
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

import re

country = re.compile(r"(\s[A-Z]{1}[A-Z10]{1})|(\s[A-Z1]{1}[A-Z]{1}) ")

class Proxy():

	def __init__(self, ip = "0.0.0.0", port = "00", location = "unknown", hostname = "unknown", alive = True, safe = True, last_checked="never", url="", resp=0, good=0, bad=0, flags_bin=0, influence=0):
		self.ip = ip
		self.port = port
		self.location = location
		self.hostname = hostname
		self.alive = alive
		self.safe = safe
		self.last_checked = last_checked
		self.url = url
		self.resp = resp
		self.good = good
		self.bad = bad
		
		# set flags from flags_bin
		
		self.flags = {"black" : flags_bin}
		self.influence = influence
		
	def __repr__(self):
		return "%s:%s %s %s up:%s safe:%s checked:%s %f %f %f %f\n" % (self.ip, self.port, self.get_country_code(), self.hostname, self.alive, self.safe, self.last_checked, self.resp, self.good, self.bad, self.get_flags_bin())

	def set_url(self, url):
		self.url = url

	def get_url(self):
		return self.url
		
	def set_resp(self, resp):
		self.resp = resp
		
	def get_resp(self):
		return self.resp
		
	def plus_good(self):
		self.good = self.good + 1
		
	def plus_bad(self):
		self.bad = self.bad + 1
	
	def get_flags_bin(self):
		return self.flags["black"]
	
	def get_health(self):
		if self.good + self.bad > 0:
			return round(float(self.good) / (float(self.good) + float(self.bad)), 4)
		else:
			return 0
	
	def get_country_code(self):
		if self.location == "unknown":
			return "unknown"
		else:
			try:
				return country.search(self.location).group()
			except:
				return "unknown"
				
	def kill(self):
		self.flags["black"] = 5
	def clear(self):
		self.flags["black"] = 0
		
	def is_dead(self):
		if self.flags["black"] >= 5:
			return True
		else:
			return False
