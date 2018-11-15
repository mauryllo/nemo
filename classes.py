#!/usr/bin/env python3

import ipaddress

#class to store host information
class Host():
	def __init__(self, hostname, ip="0.0.0.0", poll=False, poll_profile_id=False):
		self.hostname=hostname
		self.ip=ip
		self.poll_profile_id=poll_profile_id
		self.poll=poll
	def polling_on(self):
		self.poll=True
	def polling_off(self):
		self.poll=False
			
class PollProfile():
	#poll_type can be "icmp", "snmp", "icmp/snmp"
	#poll timeout in milliseconds
	def __init__(self, type, timeout):
		try:
			self.type=type
			self.timeout=int(timeout)
		except Exception as e:
			raise ValueError("Invalid timeout: ", str(e))

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