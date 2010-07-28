#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       untitled.py
#       
#       Copyright 2010 Unknown <sleven@black-box>
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
import proxy
import re
import sys
import judgestest

"""import sql modules"""
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.sql import select
from sqlalchemy.sql import and_

import mini_test_new
import random
import proxytest
from operator import itemgetter, attrgetter
remove = '<proxies>'

country = re.compile(r"\s[A-Z1]{1}[A-Z10]{1}")

"""Database part"""
engine = create_engine('sqlite:///proxy.db',echo=False)

metadata = MetaData(bind=engine)

main_tbl = Table('main', metadata,
	Column('id', Integer, primary_key=True),
	Column('ip', String),
	Column('port', String),
	Column('hostname', String),
	Column('location', String),
	Column('safe', Boolean),
	Column('alive', Boolean),
	Column('last_checked', String),
	Column('url', String),
	Column('resp', Float(3,True)),
	Column('good', Integer),
	Column('bad', Integer),
	Column('flags_bin', Integer)
	)
# create tables in database
metadata.create_all()

class foxyProxy():
	def proxy_chunk(self, proxy):
		chunk = '<proxy name="' + proxy.location[proxy.location.find((country.search(proxy.location)).group()):len(proxy.location) - 1] + str(proxy.resp) + str(proxy.get_health()) + '" id="' + str(random.randint(1000000000,9999999999)) + '" notes="" enabled="true" mode="manual" selectedTabIndex="0" lastresort="false" animatedIcons="true" includeInCycle="true" color="#65BAD7" proxyDNS="true"><matches/><autoconf url="" loadNotification="true" errorNotification="true" autoReload="false" reloadFreqMins="60" disableOnBadPAC="true"/><manualconf host="' + proxy.ip + '" port="' + proxy.port + '" socksversion="5" isSocks="false"/></proxy>'
		return chunk
		
	def execute(self, proxies):
		new_text = ""
		ap_text = ""
		
		with open("/home/sleven/.mozilla/firefox/4lnqadx1.default/foxyproxy.xml") as f:
			ap_text = f.read()
			ap_text = ap_text[0:ap_text.find(remove)]
		
		with open("/home/sleven/.mozilla/firefox/4lnqadx1.default/foxyproxy.xml","w") as f:
			for i in proxies:
				new_text = new_text + self.proxy_chunk(i)
			f.write(ap_text + "<proxies>" + new_text + '</proxies></foxyproxy>')
		print "Done writing " + str(len(proxies)) + "proxies to foxyproxy config."

def main():
	all = []
	test_list = []
	print "importing..."
	try:
		s = select([main_tbl])
		conn = engine.connect()
		result = conn.execute(s)
	except:
		print "shit."
		sys.exit()
	chan_mode = False
	result = sorted(result, key=attrgetter('resp'))
	
	for row in result:
		new_proxy = proxy.Proxy(row.ip, row.port, row.location, row.hostname, row.alive, row.safe, row.last_checked, row.url, row.resp, row.good, row.bad, row.flags_bin)
		if new_proxy.alive and new_proxy.location.find("US") == -1 and new_proxy.location.find("CA") == -1 and new_proxy.location.find("GB") == -1:
			test_list.append(new_proxy)
	
	judges = []
	jfile = []
	
	block_list = []
	judge_identifier = []
	

	f =open("judges.txt")
	for line in f:
		jfile.append(line.strip())
	f.close()
	
	f = open("block_list.txt")
	for line in f:
		block_list.append(line.strip())
	f.close()

	f = open("judge_identifier.txt")
	for line in f:
		judge_identifier.append(line.strip())
	f.close()
	
	jtest = judgestest.judgesTest()
	judges = jtest.run_test(jfile)
	proxy_test = proxytest.Proxytest()
	test_result = proxy_test.run_test(test_list, judges, judge_identifier, block_list)
	
	with open("/home/sleven/.mozilla/firefox/4lnqadx1.default/foxyproxy.xml") as f:
		bak = f.read()
	
	for a in test_result:
		if a.alive and a.safe and a.last_checked != "never":
			all.append(a)
	try:
		if (len(all) > 0):
			fp = foxyProxy()
			all = sorted(all, key=attrgetter('resp'))
			all = all[0:20]
			fp.execute(all)
		else:
			print "No good proxies to add"
	except Exception, e:
		with open("/home/sleven/.mozilla/firefox/4lnqadx1.default/foxyproxy.xml","w") as f:
			f.write(bak)
		print "Wrote backup."
		print e
		
	return 0

if __name__ == '__main__':
	main()
