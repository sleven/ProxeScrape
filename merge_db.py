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

import re
import sys
import os
import time
import random
import math
import urllib
import urllib2
import socket
from time import gmtime, strftime
import generate_poast
import judgestest
os.chdir('/home/sleven/apps/v2')
import proxy

"""for sorting algorithm"""
from operator import itemgetter, attrgetter

"""import sql modules"""
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.sql import select
from sqlalchemy.sql import and_


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

try:

	second_db_name = str(sys.argv[1])
except:
	print "Enter an amount of search terms to use for google"
	sys.exit(2)
	


def update_database(all):
	print "Updating proxy.db with new information...",
	sys.stdout.flush()
	try:
		params = []
		
		for item in all:
			dict = {"ip" : item.ip, "port" : item.port, "hostname" : item.hostname, 
					"location" : item.location, "alive" : item.alive, "safe" : item.safe,
					 "last_checked" : item.last_checked, "url" : item.url, "resp" : item.resp, "good" : item.good, "bad" : item.bad, "flags_bin" : item.get_flags_bin()}
			params.append(dict)
		
		conn = engine.connect()
		conn.execute(main_tbl.delete())
		conn.execute(main_tbl.insert(), params)
		
	except Exception, e:
		print "Threw exception in insert loop", e
	print "Database updated successfuly."
	
def add_new_to_cache(current, all):
		print "* Adding new proxies to cache."
		dupe = 0
		for item in current:
			all.append(item)
		
		start_len = len(all)
		print "start_len: ", start_len
		"""Now we sort all the proxies in the cache/list"""
		all[:] = sorted(all, key=attrgetter('ip', 'port', 'last_checked'))

		"""...and delete the duplicates"""
		x = 0
		
		print "* Removing duplicates"
		while x + 1 < len(all) - 1:
			if all[x].ip == all[x+1].ip and all[x].port == all[x+1].port:
				#~ print all[x], "is the same as", all[x+1]
				#~ print "removing the latter"
				del all[x+1]
			else:
				x += 1
		
		total_len = len(all)
		
		dupe = start_len - total_len
		if dupe < 0:
			dupe = 0
		print dupe, " duplicates removed."
		return all


print "* Loading proxies from db 1",
sys.stdout.flush()
all = []

try:
	s = select([main_tbl])
	conn = engine.connect()
	result = conn.execute(s)

	for row in result:
		new_proxy = proxy.Proxy(row.ip, row.port, row.location, row.hostname, row.alive, row.safe, row.last_checked, row.url, row.resp, row.good, row.bad, row.flags_bin)
		all.append(new_proxy)
	
	len_all = len(all)
	print len_all, " proxies loaded."
except Exception, e:
	print e
	

print "* Loading proxies from db 2",
sys.stdout.flush()
all2 = []
"""Database part"""
engine2 = create_engine('sqlite:///' + second_db_name,echo=False)

metadata2 = MetaData(bind=engine2)

second_tbl = Table('main', metadata2,
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
metadata2.create_all()

try:
	s = select([second_tbl])
	conn = engine2.connect()
	result = conn.execute(s)

	for row in result:
		new_proxy = proxy.Proxy(row.ip, row.port, row.location, row.hostname, row.alive, row.safe, row.last_checked, row.url, row.resp, row.good, row.bad, row.flags_bin)
		all2.append(new_proxy)
	
	len_all2 = len(all2)
	print len_all2, " proxies loaded."
except Exception, e:
	print e

print "Combining lists"

total = add_new_to_cache(all, all2)
print ""
print len(total)
raw_input("")

print "Updating database"
update_database(total)
print "done"
