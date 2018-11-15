#!/usr/bin/env python

#standard
import datetime
import random
import socket
import sys
import struct

class IcmpPacket():
	def __init__(self, type, code, identifier, sequence, payload_size):
		self.type=type
		self.code=code
		self.checksum=0
		self.identifier=identifier
		self.sequence=sequence
		#generate payload
		self.payload=str(random.randint(0,255))*payload_size
		#create header and packet
		self.header = struct.pack('BBHHH', self.type, self.code, self.checksum, self.identifier, self.sequence)
		self.packet = self.header + bytes(self.payload, 'utf-8')
		#calculate checksum and recreate header and packet
		self.checksum = self.get_checksum(self.packet)
		self.header = struct.pack('BBHHH', self.type, self.code, self.checksum, self.identifier, self.sequence)
		self.packet = self.header + bytes(self.payload, 'utf-8')
		
	def get_checksum(self, header):
		checksum = 0
		for i in range(0, len(header), 2):
			word=header[i]+(header[i+1]<<8)
			sum=checksum+word
			checksum=(sum & 0xffff) + (sum >> 16)
		return ~checksum & 0xffff

def msg_echo_request(af, identifier, sequence, payload_size):
	if (af==socket.AF_INET):
		type=8
	elif (af==socket.AF_INET6):
		type=128
	packet=IcmpPacket(type, 0, identifier, sequence, payload_size)
	
	return packet


def ping(destination, timeout, payload_size):
	#do we have ipv6? !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	ipv6=False
	try:
		timeout=float(timeout/1000)
	except ValueError:
		raise ValueError

	try:
		dest_info=socket.getaddrinfo(destination, 0)
		#get address family
		if ipv6:
			af=dest_info[0][0]
		else:
			for response in dest_info:
				af=response[0]
				if (af==socket.AF_INET):
					ip, port = response[4]
					destination=ip
					break

		#create input and ouput sockets
		in_sock=socket.socket(af, socket.SOCK_RAW, socket.IPPROTO_ICMP)
		out_sock=socket.socket(af, socket.SOCK_RAW, socket.IPPROTO_ICMP)
		
		#bind input socket to any address
		in_sock.bind(("", 0))
		#set timeout
		in_sock.settimeout(timeout)
		
		#set TTL in output socket
		ttl=255
		out_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
		
		#forge ip header
		in_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
		
		#random identifier
		identifier=random.randint(1,60000)
		sequence=1
		packet = msg_echo_request(af, identifier = identifier, sequence = sequence, payload_size=payload_size)
	
		#send packet
		out_sock.sendto(packet.packet, (destination, 0))
	#better exception management!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	except Exception as e:
		logging.debug(e)
		return False
	
	#wait for reply
	start=datetime.datetime.now()
	try:
		data=in_sock.recvfrom(10000)[0]
		
		if (af==socket.AF_INET):
			icmp_response=data[20:]
		elif (af==socket.AF_INET6):
			icmp_response=data[40:]
		
		resp_type=icmp_response[0]
		resp_code=icmp_response[1]
		resp_identifier=icmp_response[4:5]
		resp_sequence=icmp_response[6:7]
		resp_payload=icmp_response[8:]
		if (af==socket.AF_INET and resp_type==0) or (af==socket.AF_INET6 and resp_type==129) and (resp_identifier == identifier) and (resp_sequence == sequence) and (resp_payload == packet.payload):
			rtt=datetime.datetime.now()-start
			rtt=int((rtt.seconds*1000000 + rtt.microseconds)/10)
			return rtt
		else:
			return False
	except socket.timeout as e:
		return False
	
	return False

def main(argv=None):
	payload_size = 100
	timeout = 2000
	result=ping("www.google.com", timeout, payload_size)
	print(result)
	return
	
if __name__ == "__main__":
	main(sys.argv[1:])