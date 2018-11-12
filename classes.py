#!/usr/bin/env python

import ipaddress

#class to store host information
class Host():
	#if dns==True all functions will try to resolve ip 
	def __init__(self, hostname, dns=False, ip="0.0.0.0", poll_profile_id=False):
		self.hostname=hostname
		if not((dns==False) or (dns==True)):
			raise ValueError("Invalid \"dns\" value: " + str(dns))
		self.dns=dns
		try:
			self.ip=ipaddress.ip_address(ip).exploded
		except Exception as e:
			raise ValueError("Invalid IP address: " + str(ip) + " " + str(e))
		self.poll_profile_id=poll_profile_id
			
class PollProfile():
	#poll_type can be "icmp", "snmp", "icmp/snmp"
	#poll interval in seconds
	#poll timeout in milliseconds
	#interval must be at least timeout+500msec
	def __init__(self, type, interval, timeout):
		try:
			self.type=type
			self.interval=int(interval)
			self.timeout=int(timeout)
			if (self.timeout+500>self.interval*1000):
				raise ValueError("Interval must be at least timeout+500msec")
		except Exception as e:
			raise ValueError("Invalid timeout/interval: ", str(e))

class SnmpData(object):
	name = ''
	# ver should be 1, 2, 3
	ver = ''
	# ver 1 & 2 only
	community = ''
	# auth should be noAuthNoPriv, authNoPriv , authPriv , ver 3 only
	auth = ''
	# auth_proto MD5 or SHA, ver 3 only
	auth_proto = ''
	# ver 3 only
	auth_pwd = ''
	# ver 3 only
	user = ''
	timeout = ''
	retries = ''
	def __init__(self, name, ver = 2, community = 'public', auth = 'noAuthNoPriv', auth_proto = '', auth_pwd = '', user = '', timeout = 10, retries = 3):
		self.name = name
		self.ver = ver
		self.community = community
		self.auth = auth
		self.auth_proto = auth_proto
		self.auth_pwd = auth_pwd
		self.user = user
		self.timeout = timeout
		self.retries = retries
		
class Module(object):
	index = ''
	serial = ''
	model =  ''
	hw_ver = ''
	fw_ver = ''
	sw_ver = ''
	name = ''
	fru = ''
	vendor = ''
	router_id = ''
	def __init__(self, index, serial, model, hw_ver, fw_ver, sw_ver, name, fru, vendor, router_id):
		self.index = index
		self.serial = serial
		self.model =  model
		self.hw_ver = hw_ver
		self.fw_ver = fw_ver
		self.sw_ver = sw_ver
		self.name = name
		self.fru = fru
		self.vendor = vendor
		self.router_id = router_id