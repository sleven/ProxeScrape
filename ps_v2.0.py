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
os.chdir('/home/sleven/prog/ps_v2')

"""for sorting algorithm"""
from operator import itemgetter, attrgetter

"""import sql modules"""
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.sql import select
from sqlalchemy.sql import and_

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

def do_proxy_test(all):
	test_size = 1000
	batch_list = []
	final_return_list = []
	test_list = []
	no_test_list = []
	total = len(test_list)
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
	random.shuffle(judges)
	
	for proxy in all:
		if proxy.is_dead():
			no_test_list.append(proxy)
		else:
			test_list.append(proxy)	
			
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

		return_list = proxy_test.run_test(batch, judges, judge_identifier, block_list)
		final_return_list.extend(return_list)
		
		if batch_number % 10 == 0 and batch_number != 0:
			try:
				jfile[:] = []
				f =open("judges.txt")
				for line in f:
					jfile.append(line.strip())
				f.close()
				jtest = judgestest.judgesTest()
				judges = jtest.run_test(jfile)
				random.shuffle(judges)
			except:
				print "Error running judges test"
				pass
	
	update_database(final_return_list)
	final_return_list.extend(no_test_list)

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
	
	
	"""program controls"""
	chan_mode = False	#Test for chan proxies
	rigorous = False 	#Test the proxy list more than once per update.
	
	renig = False		#Clear all reject proxies from DB. Only happens once at the start.
	debug = False		#If true, skips contacting the web pages for new scrapes
	run_google = False #run the google spider module
	poast = True
	test_a = True	#Run proxy test after update
	test_size = 10000	#number of proxies to test per batch
	manual_add = False	#scrape proxies from manual_add.txt as well
	rigorosity_lvl = 2	#Total number of times the new proxy list is checked after each update.
	moderate_lvl = 4 	#loops until alternate instructions, initially 0
	proxies_loaded = False
	tick = 9000		#2 1/2 hours
	shallow_scan = 12	#cycles per shallow
	deep_scan = 36		#cycles per deep
	raep_lvl = 40		#max google pages to raep per search result * 10
	thresh = .5			# threshold until proxy is dumped for being a faggit
	min_poast = 100
	poasts_done = 0
	
	"""special controls"""
	skip = False
	start_time = strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
	os.system("clear")
	while 1:
	
		import proxy
		
		try:
			del new_proxy
		except:
			pass
			
		new_proxy = proxy.Proxy()
		
		print strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),"\n", 
		print "","Start Loop #", loop
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
		
		if renig:
			#raw_input("About to renig, press enter to continue")
			for item in all:
				#item.last_checked = "never"
				item.good = 0
				item.bad = 0
				item.alive = True
				#item.safe = True
				item.clear()
			renig = False
			print "Renigged."
			
		"""Check for debug, if not get updates"""
		if(debug or skip):
			print"## Goin on a break..."
		else:
			
			print "" "* Checking for updates..."
			for x in range(len(module)):
				try:
					new = module[x].execute()
					for item in new:
						current.append(item)
					print "==Module results: ", len(new), "proxies found =="
				except:
					print "Some error with module", x
			print len(current), " total new proxies scraped."

			temp = len_all
			all[:] = add_new_to_cache(current, all)
			update_database(all)
			update_total_added = len(all) - temp
			len_all = len(all)
				
			print "done."	
		"""Check for manual add"""
		if(manual_add):
			print "* Checking for new manual proxies",
			sys.stdout.flush()
			y = 0
			try:
				f = open("google_dump","r")
				for line in f:
					y += 1
					line = line.strip("\n")
					new_proxy = proxy.Proxy(line[0:line.find(":")], line[line.find(":") + 1 : len(line)])
					current.append(new_proxy)
				f.close()
				print y, " proxies found."
				temp = len_all
				all[:] = add_new_to_cache(current, all)
				update_database(all)
				update_total_added = len(all) - temp
				len_all = len(all)
			except:
				pass
				

		print "\n" "* Status --", len(all), "unique proxies that I know about."
		if update_total_added > 0:
			print "* Found ", update_total_added, " new proxies."
		else:
			print "* No new proxies found."
		
		if test_a:
			all = do_proxy_test(all)
				
		if poast:
			if len(all) >= min_poast:
				try:
					new_poast = generate_poast.Generate_Poast()
					new_poast.execute(all)
					poasts_done += 1
				except Exception, e:
					print "Had trouble poasting", e
								
		"""Get some stats"""
		working_proxies = 0
		dead = 0
		
		for i in all:
			if i.alive == True:
				working_proxies += 1
			if i.is_dead():
				dead += 1
		running_time = 0
		current_time = strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
		try:
			running_time = current_time - start_time
		except:
			pass
		
		print ""
		print ""
		print strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),
		print "running for", running_time
		#print "---====UPDATE COMPLETE====---",
		print "Loop #", loop, "Stats",
		#print "+ ", len(google_rape), "new proxies were found by google."
		#print "@ ", duplicates, "proxies were removed because they were already indexed."
		if update_total_added > 0:
			print "| Found ", update_total_added, " new proxies.",
		else:
			print "| No new proxies found.",
		print "| Posted", poasts_done, "times.",
		print "| Currently",
		print  working_proxies, "working",
		print "|", dead, " murdered",
		print "|", len(all), "total in proxy.db",
		#print "@ ", working_proxies, "working proxies."
		
		loop += 1			
		
		if working_proxies < 30:
			renig = True
		else:
			renig = False
		
		debug = False
		#~ if loop != 0 and loop % 4 == 0:
			#~ debug = False
			#~ run_google = False
			#~ poast = True
			#~ manual_add = False
			#~ time.sleep(5400)
		#~ else:
			#~ debug = True
			#~ run_google = False
			#~ manual_add = False
			#~ poast = True

		snooze = (tick)# + random.randint(30,300))
		print "|| ZZzz.."
		time.sleep(snooze)
			
		u_index = 0
		update_total_found = 0
		update_total_added = 0
		working_proxies = 0
		print "Awake!!"

	return 0
if __name__ == '__main__':


		main()
