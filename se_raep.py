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

"""import sql modules"""
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.sql import select

def main():
	seed_list = []
	"""Database part"""
	engine = create_engine('sqlite:///proxy.db',echo=False)
 
	metadata = MetaData(bind=engine)
	
	main_tbl = Table('main', metadata,
						Column('id', Integer, primary_key=True),
						Column('ip', String),
						Column('port', String),
						Column('hostname', String),
						Column('location', String),
						Column('alive', String),
						Column('safe', String),
						Column('last_checked', String)
						)
						
	metadata.create_all()
	
	s = select([main_tbl])
	conn = engine.connect()
	result = conn.execute(s)
	
	for proxy in result:
		if proxy.last_checked != "never":
			seed_list.append(proxy)
	
	load_new_module = google.Google()
	google_rape = load_new_module.execute(seed_list)
	
	print "google raped", len(google_rape), " proxies."
	
	print "Updating proxy.db with new information..."
	
	if len(google_rape) > 0:
		try:
			params = []
			
			for item in google_rape:
				dict = {"ip" : item.ip, "port" : item.port, "hostname" : item.hostname, "location" : item.location, "alive" : item.alive, "safe" : item.safe, "last_checked" : item.last_checked}
				params.append(dict)
			
			conn = engine.connect()
			conn.execute(main_tbl.delete())
			conn.execute(main_tbl.insert(), params)
			
		except Exception, e:
			print "Threw exception in insert loop", e

if __name__ == '__main__':
	main()
