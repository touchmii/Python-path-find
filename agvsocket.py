# coding: utf-8
#!/usr/bin/python3

import socket
import AStarCsv
import re
import logging
import logg
from threading import Timer
import time
#from kivy.app import App
#from kivy.uix.button import Button
import asyncio

log = logg.Logger('all.log',level='debug')

logger = logging.getLogger('fib')
logger.setLevel(logging.DEBUG)

hdr = logging.StreamHandler()

formatter = logging.Formatter("[%(asctime)s] %(name)s:%(levelname)s: %(message)s")
hdr.setFormatter(formatter)

logger.addHandler(hdr)

MAX_LENGHT = 1024

#agv2IP = "192.168.0.157"
agv2IP = "192.168.10.239"
#agv2IP = "127.0.0.1"
agv2Port = 10001
agvgetpos = 'robot get2dcodepos\r\n'
#Message = 'robot get2dcodepos\r\n'
#agvsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#agvsock.settimeout(3)
#agvsock.connect((agv2IP,agv2Port))
agv_error_list = ['方向偏离设定值', '直线行驶安全触碰边信号', '调节方向没有找到二维码', '方向调节超时', '陀螺仪出错', '旋转安全触边信号', '旋转时编码器超标', '旋转时陀螺仪超标',
'空8', '空9', '举升超时', '下降超时', '旋转调整超时', '举升后未检测到二维码', '托盘选超时', '空15',
'左电机错误', '右电机错误', '旋转电机错误', '举升电机错误', '保留1', '保留2', '保留3', '保留4',]
agv_status_list = ['standby', 'run', 'finish', 'pause', 'target']

class agv:
	def __init__(self):
		self.id = 0
		self.direct = 0
		self.battery = 0
		self.error_list = []
		self.agvsock = None
		self.id = None
		self.pre_id = 99
		
		self.direct = None
		self.battery = None
		self.speed = None
		self.dis_ob = None 
		self.radar_roi = None 
		self.radar_depth = None
		self.agv_status = None
		self.agv_status_error = None
		self.status_overview = ''
		self.recive_data = b''
	def connect(self, ip, port):
		self.agvsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.agvsock.settimeout(5)
		try:
			self.agvsock.connect((ip,port))
		except socket.error:
			log.logger.error('socket cant connect')
			self.agvsock.close()
			return 'socket cant connect'
		return 'socket connected'
	def disconect(self):
		if self.agvsock:
			self.agvsock.close()
		self.agvsock = None
	def send_message(self,message):
		if not self.agvsock:
			return None
		try:
			self.agvsock.send(message)
			rec = self.agvsock.recv(64)
			return rec
		except socket.error:
			logger.debug('socket error')
			return -1
		finally:
			pass
			#self.agvsock.close()
	def from_bytes(self,data, big_endian = False):
		if isinstance(data, str):
			data = bytearray(data)
		if big_endian:
			data = reversed(data)
		num = 0
		for offset, byte in enumerate(data):
			num += byte << (offset * 8)
		return num
	def action(self,*action):
		data = AStarCsv.action(*action)
		self.debug(data, 'send to agv: ')
		#self.agvsock.send(data)
		rec = self.send_message(data)
		if not rec:
			return None
		self.debug(rec)
		return rec
	def go_pos(self,pos):
		self.getstatus()
#		rec = self.getstatus()
#		if not self.id:
		if self.getstatus() == -1:
			return -1
		self.path,self.pathex = AStarCsv.configpath(AStarCsv.searchpath(self.id, pos), self.direct)
		self.pathb = bytes(self.pathex)
		# self.agvsock.send(self.pathb)
		log.logger.info('send path to agv: '+self.path)
		rec = self.send_message(self.pathb)
		self.response_check(rec)
#		logger.debug('path response form agv: '+(" ".join(map(hex,rec))))
		#self.path_rec = self.agvsock.recv(64)
		#return self.path_rec
		return rec

	def getstatus(self):
		data = b'\x00\x01\x02\x01\xfd'
		#agv_status_enum = []
		#self.agvsock.send(data)
		#rec = self.agvsock.recv(1024)
		#try:
		#rec = self.agvsock.recv(64)
		rec = self.send_message(data)    #except Exception:
#		if not rec:
#			return
#		elif len(rec) < 18:
#			return
		return self.response_check(rec)
#		print(rec)
			#continue
#		logger.debug('recive form agv: '+(" ".join(map(hex,rec))))
		#print(" ".join(map(hex,rec)))
		#print('recive:'+str(rec.hex()))
		#self.test()
		#self.from_byte(rec[7:8])
	def response_check(self, rec):
		if rec == -1 or len(rec) < 18 or rec[:3] != b'\x00\x01\x82':
			log.logger.error('recive form agv: '+(" ".join(map(hex,rec))))
			return -1
		if rec == self.recive_data:
			return 0
		self.recive_data = rec
#		if self.pre_id != self.id:
#			self.pre_id = self.id
		self.id = self.from_bytes(rec[6:8], True) #高位在前需设置big_endian
		self.direct = self.from_bytes(rec[9:10])
		self.battery = self.from_bytes(rec[11:12])
		self.speed = self.from_bytes(rec[8:9])
		self.dis_ob = self.from_bytes(rec[13:14]) 
		self.radar_roi = self.from_bytes(rec[14:15]) 
		self.radar_depth = self.from_bytes(rec[15:16])*10
		self.agv_status = agv_status_list[int.from_bytes(rec[12:13],"big")]
		#self.agv_status_error = self.from_bytes(rec[3:6])
		self.error_list_set(self.from_bytes(rec[3:6]))
		self.status_overview = 'current id:'+str(self.id)+' direct:'+str(self.direct)+' battery:'+str(self.battery)+' speed: '+str(self.speed)+' agv status: '+self.agv_status+'\n'+'dis stop: '+str(self.dis_ob)+' radar_depth: '+str(self.radar_depth)+' radar_roi: '+str(self.radar_roi)+'\n'+'agv error: '+str(self.error_list)+'\n'
		log.logger.debug('agv status check:'+self.status_overview)
		return 0
	def error_list_set(self, error_code):
		##error_code = 0x2CAD #测试 0x2CAD = 0b10110010101101
		i = 0
		while error_code > 0:
			if (error_code & 1) == True:
				self.error_list.append(agv_error_list[-(i+1)]) #反向	
			error_code = error_code >> 1
			i += 1
	def debug(self, rec, prompt='recive from gav: '):
		logger.debug(prompt+(" ".join(map(hex,rec))))
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

def status_loop(instance):
	#print('pressed')
	#logger.debug('thread')
	agv.getstatus()
	logger.debug('current id:'+str(agv.id)+' direct:'+str(agv.direct)+' battery:'+str(agv.battery)+' speed: '+str(agv.speed)+' agv status: '+agv.agv_status)
	logger.debug('dis stop: '+str(agv.dis_ob)+' radar_depth: '+str(agv.radar_depth)+' radar_roi: '+str(agv.radar_roi))
	logger.debug('agv error: '+str(agv.error_list))
	#t=Timer(1.0, lambda: status_loop())
	#t.start()

#class TestApp(App):
#	def build(self):
#		return bt1

async def path_test():
	while 1:
#		await go_pos(122)
#		await go_pos(107)
#		await go_pos(541)
#		await go_pos(169)
#		await go_pos(192)
#		await go_pos(541)
#		await go_pos(195)

		await go_pos(270)
#		await go_pos(850) #包衣
#		await go_pos(825) #压片1
#		await go_pos(805) #压片2
##		await go_pos(785) #胶囊1
		await go_pos(752) #胶囊2
##		await go_pos(745) #胶囊3
#		await go_pos(729) #铝塑1
#		await go_pos(685) #铝塑2
#		await go_pos(665) #铝塑3
#		await go_pos(647) #瓶包
#		await go_pos(628) #批料 
		await go_pos(605) #制粒
		await go_pos(880) #批混
		await go_pos(588) #容器存放
		await go_pos(571) #容器清洗
		
#		target_id = pointbk[0]
#		target_id = 192
#		print(agv.go_pos(target_id))
#		await asyncio.sleep(1)
#		while 1:
#			await asyncio.sleep(.5)
#			agv.getstatus()
#			if agv.id == target_id and agv.agv_status == 'standby':
#				await asyncio.sleep(.5)
#				break
#		target_id = pointbk[3]
async def go_pos(target_pos):
	log.logger.info('go to new pos: '+str(target_pos))
	target_id = target_pos
	rec = agv.go_pos(target_id)
	if rec == -1:
#		print('resend path')
		log.logger.error('resend path')
		rec = agv.go_pos(target_id)
	await asyncio.sleep(1)
	while 1:
		await asyncio.sleep(.5)
		agv.getstatus()
		if agv.id == target_id and agv.agv_status == 'standby':
			await asyncio.sleep(1)
			log.logger.info('reach to target pos: '+str(target_pos))
			break

if __name__ == '__main__':
	#agvgopos(431)
	#print(AStarCsv.configpath(AStarCsv.searchpath(134, 426),4))
#	agvsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#	agvsock.settimeout(3)
#	agvsock.connect((agv2IP,agv2Port))
	current_id = 0
	target_id = 0
#	pointbk = AStarCsv.get_point()
	pointbk = {192:0, 152:0, 107:0, 173:0}
	agv = agv()
	agv.connect(agv2IP, agv2Port)
	agv.getstatus()
	if agv.id == 0:
		sys.exit("sorry, goodbye!")
	else:
		current_id = agv.id
	
	loop = asyncio.get_event_loop()
	tasks = [asyncio.Task(path_test())]
	loop.run_until_complete(asyncio.wait(tasks))
#	logging.debug('current id:'+str(agv.id)+' direct:'+str(agv.direct)+' battery:'+str(agv.battery)+' speed: '+str(agv.speed)+' agv status: '+agv.agv_status)
#	logging.debug('dis stop: '+str(agv.dis_ob)+' radar_depth: '+str(agv.radar_depth)+' radar_roi: '+str(agv.radar_roi))
#	logging.debug('agv error: '+str(agv.error_list))
	#path,pathex = AStarCsv.configpath(AStarCsv.searchpath(agv.id, 161), agv.direct)
	#logging.debug('hex path: '+str(" ".join(map(hex,pathex))))
#	agv = agv()
#	agv.error_list_set()
#	logging.debug(agv.error_list)
	#print(pathex)
	#pathb = bytes(pathex)
	#logging.debug('path length: '+str(len(pathex)))
	#agvsock.send(pathb)
	
	#rec = agvsock.recv(1024)
	#logging.debug('recive form agv path response: '+(" ".join(map(hex,rec))))
	
	#t=Timer(1.0, lambda: status_loop())
	#t.start()
	#bt1 = Button(text='get status', pos=(300,350), size_hint = (.25, .18))
	#bt1.bind(on_press=status_loop)
	#TestApp().run()
	#rec = agv.go_pos(230)
	#print(rec)
	#agv.agvsock.close()