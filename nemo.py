#!/usr/bin/env python

#standard
import logging
import os
import socket
import sys
import threading

#3d party
import rrdtool

#custom
from classes import Host, PollProfile
import poller

VERSION=0.1

MAXTHREADS=2
semaphore_poll_icmp=threading.Semaphore(value=MAXTHREADS)
DIR_BASE="/home/mau/nemo"
DIR_RRD=DIR_BASE+"/"+"rrd"

def add_host(hosts, hostname, ip, poll_profile_id):
	try:
		#check_ip_sanity
		dest_info=socket.getaddrinfo(ip, 0)
		
		#add host to db only if ip not present !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		#find index of last item in dict
		if hosts:
			index=max(hosts.keys())+1
		else:
			index=1
		hosts[index]=Host(hostname=hostname, ip=ip, poll_profile_id=1)
		logging.debug("Host \"" + hostname + "\" (" + ip + ") added to db")
		
		#create RRD directory
		dir=DIR_RRD+"/host_"+str(index)
		if not os.path.isdir(dir):
			logging.debug("Creating directory \"" + dir + "\" for host \"" + hostname + "\" (" + ip + ")")
			#should we change dir perm?
			os.mkdir(dir,755)
		else:
			logging.warning("Already existing directory \"" + dir + "\" for host \"" + hostname + "\" (" + ip + ")")
		
	except Exception as e:
		logging.warning("While adding host \"" + hostname + "\" (" + ip + ") to db: " + str(e))
		return False

	return False
		
def main(argv=None):
	logging.basicConfig(stream=sys.stdout,format='%(asctime)s:%(levelname)s:nemo:%(lineno)s-> %(message)s',level=logging.INFO)

	poll_profiles=dict()
	hosts=dict()
	try:
		poll_profiles[1]=PollProfile("icmp", timeout=1000)
	except Exception as e:
		logging.error(e)
	try:
		add_host(hosts, hostname="c7609.ca-01", ip="213.205.0.14", poll_profile_id=1)
		add_host(hosts, "garbage", "www.nonfunge.com", poll_profile_id=1)
		add_host(hosts, "google", "www.google.com", poll_profile_id=1)
		add_host(hosts, "aol", "www.aol.com", poll_profile_id=1)
	except Exception as e:
		logging.warning(str(e))
		
	#populate poller
	poller.add_host(hosts, host_id=1)
	poller.add_host(hosts, host_id=2)
	poller.add_host(hosts, host_id=3)
	#create module threads
	threads=[]
	threads.append(threading.Thread(target=poller.poller, args=(hosts,poll_profiles)))
	
	#start all threads
	for t in threads:
		t.start()
		
	while 1:
		pass

	return
	
if __name__ == "__main__":
	main(sys.argv[1:])