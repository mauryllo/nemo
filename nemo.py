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

maxthreads=2
semaphore_poll_icmp=threading.Semaphore(value=maxthreads)

def poll_icmp(host, poll_profile):
	try:
		#wait till the semaphore goes green
		semaphore_poll_icmp.acquire()
		
		if host.dns:
			ip=host.hostname
		else:
			ip=host.ip

		payload_size = 100
		result=ping(ip, poll_profile.timeout, payload_size)
		semaphore_poll_icmp.release()
	except Exception as e:
		raise e
	
	return result
	
def poller(hosts, poll_profiles):
	#initialize result
	result=dict()
	for host in hosts:
		result[host]=[]
	
	#poll interval in seconds
	poll_interval = 5

	while True:
		start=datetime.datetime.now()
		#set up threads
		threads=[]
		for host in hosts:
			try:
				poll_profile_id=hosts[host].poll_profile_id
				threads.append(threading.Thread(target=poll_icmp, args=(hosts[host],poll_profiles[poll_profile_id])))
			except Exception as e:
				logging.error("Host \"" + hosts[host].hostname + "\": " + str(e))
				
		#start all threads
		for t in threads:
			t.start()
		
		#wait for all threads to finish
		for t in threads:
			t.join()
			print(result)
			
		#wait before next pool cycle
		stop=datetime.datetime.now()-start
		waitfor="{:.2f}".format(poll_interval-((stop.seconds*1000000 + stop.microseconds)/1000000))
		time.sleep(float(waitfor))
	
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
		hosts[4]=Host("c7609.ca-02", dns=False, ip="213.205.0.15", poll_profile_id=1)
	except Exception as e:
		logging.warning("Host \"" + hostname + "\": " + str(e))
	
	poller(hosts, poll_profiles)

	return
	
if __name__ == "__main__":
	main(sys.argv[1:])