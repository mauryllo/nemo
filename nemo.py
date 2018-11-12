#!/usr/bin/env python

#standard
import datetime
import ipaddress
import logging
import os
from platform import system as platform_system
import sys
import subprocess
import threading
import time

#custom
from classes import Host, PollProfile
from pyng import ping

def poll_icmp(host, poll_profile):
	if host.dns:
		ip=host.hostname
	else:
		ip=host.ip
		
	try:
		start=datetime.datetime.now()
		payload_size = 100
		result=ping(ip, poll_profile.timeout, payload_size)
		print(host.ip,result)
		#wait before next ping
		stop=datetime.datetime.now()-start
		waitfor="{:.2f}".format(poll_profile.interval-((stop.seconds*1000000 + stop.microseconds)/1000000))
		time.sleep(float(waitfor))
	except Exception as e:
		raise e
	
	return result

def poller(hosts, poll_profiles):
	#initialize result
	result=dict()
	for host in hosts:
		result[host]=[]
	
	threads=[]
	
	#create threads
	for i in range(3):
		for host in hosts:
			try:
				poll_profile_id=hosts[host].poll_profile_id
				t = threading.Thread(target=poll_icmp, args=(hosts[host],poll_profiles[poll_profile_id]))
				threads.append(t)
				t.start()
			except Exception as e:
				logging.error("Host \"" + hosts[host].hostname + "\": " + str(e))
	
#	for i in range(3):
#		for host in hosts:
#			#MUST USE THREADS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#			try:
#				poll_profile_id=hosts[host].poll_profile_id
#				result[host].append(poll_icmp(hosts[host],poll_profiles[poll_profile_id]))
#			except Exception as e:
#				logging.error("Host \"" + hosts[host].hostname + "\": " + str(e))
#	
#	for host in result:
#		print(host,result[host])
		
def main(argv=None):
	logging.basicConfig(stream=sys.stdout,format='%(asctime)s:%(levelname)s:nemo:%(lineno)s-> %(message)s',level=logging.INFO)

	poll_profiles=dict()
	hosts=dict()
	try:
		poll_profiles[1]=PollProfile("icmp", interval=2, timeout=1000)
	except Exception as e:
		logging.error(e)
	try:
		hostname="c7609.ca-01"
		ip="213.205.0.14"
		hosts[1]=Host(hostname, dns=False, ip=ip, poll_profile_id=1)
		hosts[2]=Host("www.google.com", dns=True, poll_profile_id=1)
		hosts[3]=Host("www.nonfunge.com", dns=True, poll_profile_id=1)
	except Exception as e:
		logging.warning("Host \"" + hostname + "\": " + str(e))
	
	poller(hosts, poll_profiles)

	return
	
if __name__ == "__main__":
	main(sys.argv[1:])