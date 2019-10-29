# coding: utf-8
#usr/bin/python3

import socket
import AStarCsv
import re

MAX_LENGHT = 1024

agv2IP = "192.168.10.231"
agv2Port = 10001
agvgetpos = 'robot get2dcodepos\r\n'
#Message = 'robot get2dcodepos\r\n'
#agvsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#agvsock.settimeout(3)
#agvsock.connect((agv2IP,agv2Port))
def from_bytes (data, big_endian = False):
	if isinstance(data, str):
		data = bytearray(data)
	if big_endian:
		data = reversed(data)
	num = 0
	for offset, byte in enumerate(data):
		num += byte << (offset * 8)
	return num


class agv:
	def __init__(self):
		self.id = 0
		self.direct = 0
		self.battery = 0
	def from_bytes(self,data, big_endian = False):
		if isinstance(data, str):
			data = bytearray(data)
		if big_endian:
			data = reversed(data)
		num = 0
		for offset, byte in enumerate(data):
			num += byte << (offset * 8)
		return num
	def getstatus(self):
		data = b'\x00\x01\x02\x01\xfd'
		agvsock.send(data)
		rec = agvsock.recv(1024)
		print(rec)
		self.test()
		#self.from_byte(rec[7:8])
		self.id = self.from_bytes(rec[7:8])
		self.direct = self.from_bytes(rec[9:10])
		self.battery = self.from_bytes(rec[13:14])
	def test(self):
		print('ok')
	
	
	
#data = agvsock.recvfrom(4096)
def sendmassage(Message):

	agvsock.connect((agv2IP,agv2Port))
	agvsock.sendall(Message.encode('utf-8'))
	tmp_data = ""
	all_data = ""
	while len(tmp_data) == 0:
		tmp_data = str(agvsock.recv(MAX_LENGHT))
		if tmp_data == "":
			break
		all_data += tmp_data
		if len(tmp_data) == MAX_LENGHT:
			tmp_data = ""
	#print("recevied message:",all_data)
	#agvsock.close()
	return all_data;
def agvgopos(point):
	currentpos = re.search(r'Pos_ID (.*) DIR (.)',sendmassage(agvgetpos))
	print(currentpos.groups(0))
	startpoint = int(currentpos.groups(0)[0])
	direct = int(currentpos.groups(0)[1])
	print(startpoint)
	robotpath = 'robot path '
	robotpath = robotpath + AStarCsv.configpath(AStarCsv.searchpath(startpoint, point), direct)+'\r\n'
	print(robotpath)
	#sendmassage(robotpath)
	#agvsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#agvsock.settimeout(3)
	#agvsock.connect((agv2IP,agv2Port))
	ok = 'ok\r\n'
	#ok = 'robot setpathflag 0\r\n'
	agvsock.send(ok.encode('utf-8'))
	#agvsock.send(ok.encode('utf-8'))
	agvsock.send(robotpath.encode('utf-8'))
	tmp_data = ""
	all_data = ""
	while 1:
			tmp_data = str(agvsock.recv(MAX_LENGHT))
			if tmp_data == "":
				break
			all_data += tmp_data
			if len(tmp_data) == MAX_LENGHT:
				tmp_data = ""
			print(tmp_data)
if __name__ == '__main__':
	#agvgopos(431)
	#print(AStarCsv.configpath(AStarCsv.searchpath(134, 426),4))
	agvsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	agvsock.settimeout(3)
	agvsock.connect((agv2IP,agv2Port))
	agv = agv()
	agv.getstatus()
	print(agv.id,agv.direct,agv.battery)
	path,pathex = AStarCsv.configpath(AStarCsv.searchpath(agv.id, 270), agv.direct)
	print(pathex)
	pathb = bytes(pathex)
	print(pathb)
	agvsock.send(pathb)