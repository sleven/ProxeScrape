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
import proxytest

"""for sorting algorithm"""
from operator import itemgetter, attrgetter

"""import sql modules"""
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.sql import select
from sqlalchemy.sql import and_
from operator import itemgetter, attrgetter

"""import event modules"""
module = []

import hinkydink
load_new_module = hinkydink.HinkyDink()
module.append(load_new_module)

import free_proxy_lists
load_new_module = free_proxy_lists.Free_Proxy_Lists()
module.append(load_new_module)

import elite_bspot
load_new_module = elite_bspot.EliteBSpot()
module.append(load_new_module)
#~ 
import pf_publiclist
load_new_module = pf_publiclist.PF_PublicList()
module.append(load_new_module)
#~ 
import http_proxy
load_new_module = http_proxy.Http_Proxy()
module.append(load_new_module)

import proxyfire	
load_new_module = proxyfire.ProxyFire()
module.append(load_new_module)

#~ import xroxy	
#~ load_new_module = xroxy.Xroxy()
#~ module.append(load_new_module)

import checked_proxy_lists
load_new_module = checked_proxy_lists.Checked_Proxy_Lists()
module.append(load_new_module)

import google
"""import proxy modules"""
import proxytest
import proxytools

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
				#print all[x], "is the same as", all[x+1]
				del all[x+1]
			else:
				x += 1
		
		total_len = len(all)
		
		dupe = start_len - total_len
		if dupe < 0:
			dupe = 0
		print dupe, " duplicates removed."
		return all

def do_proxy_test(test_list):
	test_size = 1000
	batch_list = []
	final_return_list = []
	total = len(test_list)
	judges = []
	jfile = []
	
	f =open("judges.txt")
	for line in f:
		jfile.append(line.strip())
	f.close()
	
	jtest = judgestest.judgesTest()
	judges = jtest.run_test(jfile)
	
	while 1:
		if len(test_list) > test_size:
			batch_list.append(test_list[:test_size])
			del test_list[:test_size]
		else:
			if len(test_list) > 0:
				batch_list.append(test_list[:])
			break
	
	print ""
	print "Test params"
	print "Testing ", total, "total proxies."
	
	a = 0
	x = 0
	theVar = 0
	number_of_batches = len(batch_list)
	
	for batch in batch_list:
		
		batch_number = batch_list.index(batch)
		print "* batch", batch_number, " is ", len(batch_list[batch_number]), "proxies long"
		
	for batch in batch_list:
		batch_number = batch_list.index(batch)
		print strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),"\n",  
		print "* Testing batch #", batch_number, "of", number_of_batches, "which contains", len(batch_list[batch_number]), "proxies."
		proxy_test = proxytest.Proxytest()
		return_list = proxy_test.run_test(batch, judges)
		final_return_list.extend(return_list)
		
		if batch_number % 10 == 0 and batch_number != 0:
			try:
				jtest = judgestest.judgesTest()
				judges = jtest.run_test(jfile)
			except:
				print "Error running judges test"
				pass
				
	update_database(final_return_list)
	

	return final_return_list

def main():

	"""global variables"""
	all = []
	proxy_file = "pout.txt" #"/home/geoff/Documents/collective/input.txt"
	the_page = ""
	update_total_found = 0
	update_total_added = 0
	duplicates = 0
	working_proxies = 0
	working_proxies_start = 0
	page_clip = ""
	u_index = 0
	stored_name = 0
	res = "blank"
	last = 0
	added = 0
	name = ""
	scrape = proxytools.ProxyTools()
	current = []
	dupe = 0
	loop = 0
	min_poast = 100
	
	"""program controls"""
	chan_mode = False	#Test for chan proxies
	rigorous = False 	#Test the proxy list more than once per update.
	
	renig = False		#Clear all reject proxies from DB. Only happens once at the start.
	debug = True		#If true, skips contacting the web pages for new scrapes
	run_google = True #run the google spider module
	poast = True
	test_a = True	#Run proxy test after update
	test_b = True	#Run proxy test after google -- should be on
	test_size = 10000	#number of proxies to test per batch
	manual_add = False	#scrape proxies from manual_add.txt as well
	rigorosity_lvl = 2	#Total number of times the new proxy list is checked after each update.
	moderate_lvl = 4 	#loops until alternate instructions, initially 0
	proxies_loaded = False
	tick = 900		#20 minutes between cycles
	shallow_scan = 12	#cycles per shallow
	deep_scan = 36		#cycles per deep
	raep_lvl = 40		#max google pages to raep per search result * 10
	thresh = .5			# threshold until proxy is dumped for being a faggit
	
	"""special controls"""
	skip = False

	import proxy
	
	try:
		del new_proxy
	except:
		pass
		
	new_proxy = proxy.Proxy()
	
	print strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),"\n", 
	current[:] = []
	
	if not proxies_loaded:
		print "* Loading proxies from db",
		sys.stdout.flush()
		try:
			s = select([main_tbl])
			conn = engine.connect()
			result = conn.execute(s)

			for row in result:
				new_proxy = proxy.Proxy(row.ip, row.port, row.location, row.hostname, row.alive, row.safe, row.last_checked, row.url, row.resp, row.good, row.bad, row.flags_bin)
				all.append(new_proxy)
			
			len_all = len(all)
			print len_all, " proxies loaded."
			proxies_loaded = True
		except Exception, e:
			print e
			sys.exit()
	output = []
	test_list = []
	
	for proxy in all:
		if proxy.get_country_code().find("CA") > -1:
			output.append(proxy)
	
	output = sorted(output, key=attrgetter('resp'))
	
	for proxy in output:
		if not proxy.is_dead():
			test_list.append(proxy)
	judges = []
	jfile = []
	
	f =open("judges.txt")
	for line in f:
		jfile.append(line.strip())
	f.close()
	
	jtest = judgestest.judgesTest()
	judges = jtest.run_test(jfile)
	proxy_test = proxytest.Proxytest()
	test_result = proxy_test.run_test(test_list, judges)
	
	with open("/home/sleven/.mozilla/firefox/fqxkj6v8.default/foxyproxy.xml") as f:
		bak = f.read()
	
	for a in test_result:
		if a.alive and a.safe:
			print proxy, proxy.get_flags_bin()
	
	"""Get some stats"""
	working_proxies = 0
	dead = 0
	
	for i in all:
		if i.alive == True:
			working_proxies += 1
		if i.is_dead():
			dead += 1
	print strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),"\n", 
	print "\n" "     -----=========UPDATE COMPLETE=========-----"
	print "End Loop #", loop
	print "This updates stats: "
	#print "+ ", len(google_rape), "new proxies were found by google."
	#print "@ ", duplicates, "proxies were removed because they were already indexed."
	print "+ Currently", working_proxies, "working proxies in proxy.db"
	print "- and ", dead, " murdered proxies."
	print "+ ", len(all), "total unique proxies in proxy.db"
	#print "@ ", working_proxies, "working proxies."
		

	return 0
if __name__ == '__main__':


		main()
