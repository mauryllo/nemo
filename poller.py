#!/usr/bin/env python3

#standard
import datetime
#import ipaddress
import logging
#import os
from platform import system as platform_system
#import socket
#import sys
import subprocess
import threading
import time

#3d party
import rrdtool

#custom
from classes import Host, PollProfile
from pyng import ping

MAXTHREADS=2
semaphore_poll_icmp=threading.Semaphore(value=MAXTHREADS)
DIR_BASE="/home/mau/nemo"
DIR_RRD=DIR_BASE+"/"+"rrd"

#poll interval in seconds
POLL_INTERVAL=10

VERSION=0.1


def poll_icmp(host, poll_profile, result):
	try:
		#wait till the semaphore goes green
		semaphore_poll_icmp.acquire()
		
		payload_size = 100
		rtt=ping(host.ip, poll_profile.timeout, payload_size)
		#save result, 0 on not reply
		if rtt:
			result[:]=[rtt]
		else:
			result[:]=[0]
		semaphore_poll_icmp.release()
	except Exception as e:
		raise e
	
	return
	
def update_rrd(icmp_result, snmp_result):
	try:
		logging.debug("Updating poller rrd")
		for host in icmp_result:
			name=DIR_RRD+"/host_"+str(host)+"/poller.rrd"
			rrdtool.update(name, "-t", "icmp_rtt", "N:"+str(icmp_result[host][0]))
		logging.debug("Updated poller rrd")
	except Exception as e:
		logging.error("Can't update rrd " + str(name))
	
def add_host(hosts, host_id):
#sudo rrdtool fetch rrd/host_1/poller.rrd AVERAGE -s -2h
#rrdtool graph ping.png DEF:icmp=./rrd/host_1/poller.rrd:icmp_rtt:AVERAGE -t TITOLO -s -2h -e now -u 1000 -y 100:2 -X 0 LINE1:icmp#FF0000
	try:
		hosts[host_id].polling_on()
		
		#create rrd
		name=DIR_RRD+"/host_"+str(host_id)+"/poller.rrd"
		start="--startnow"
		step=str(POLL_INTERVAL)+"s"
		#unknown after POLL_INTERVAL*2 seconds, min value 0 max value UNKNOWN
		datasource1="DS:icmp_rtt:GAUGE:"+str(POLL_INTERVAL*2)+":0:U"
		datasource2="DS:snmp_rtt:GAUGE:"+str(POLL_INTERVAL*2)+":0:U"
	
		#2hours real time
		average1="RRA:AVERAGE:0.5:"+step+":2h"
		#24hours 5min average
		average2="RRA:AVERAGE:0.5:1m:24h"
		#7days 30min average
		average3="RRA:AVERAGE:0.5:30m:7d"
		#1month 2hours average
		average4="RRA:AVERAGE:0.5:2h:1M"
		#2year 1day average
		average5="RRA:AVERAGE:0.5:1d:2y"
		
		rrdtool.create(
			name,
			"--start", "now",
			"--step", step,
			datasource1,
			datasource2,
			average1,
			average2,
			average3,
			average4,
			average5)
		
		logging.debug("Host \"" + hosts[host_id].hostname + "\" (" + hosts[host_id].ip + ") added to poller")
	except Exception as e:
		logging.warning("Can't add host ID " + str(host_id) + " to poller")
		raise(e)
	return

def poller(hosts, poll_profiles):
	#initialize result
	icmp_result=dict()
	snmp_result=dict()
	total_hosts=0
	for host in hosts:
		if (hosts[host].poll):
			total_hosts+=1
			icmp_result[host]=[]
			#no snmp for now
			snmp_result[host]=[0]
	
	while True:
		start=datetime.datetime.now()
		#set up threads
		threads=[]
		for host in hosts:
			if (hosts[host].poll):
				try:
					poll_profile_id=hosts[host].poll_profile_id
					threads.append(threading.Thread(target=poll_icmp, args=(hosts[host],poll_profiles[poll_profile_id], icmp_result[host])))
				except Exception as e:
					logging.error("Host \"" + hosts[host].hostname + "\": " + str(e))
				
		#start all threads
		for t in threads:
			t.start()
		#wait for all threads to finish
		for t in threads:
			t.join()

		#save results to rrd
		update_rrd(icmp_result, snmp_result)
			
		#wait before next pool cycle
		stop=datetime.datetime.now()-start
		timer=(stop.seconds*1000000 + stop.microseconds)/1000000
		logging.info("poller report: " + str(total_hosts) + " hosts checked in " + str("{:.3f}".format(timer)) + " seconds")
		waitfor="{:.2f}".format(POLL_INTERVAL-timer)
		time.sleep(float(waitfor))

if __name__ == "__main__":
	print("poller "+str(VERSION))