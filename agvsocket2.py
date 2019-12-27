# coding: utf-8
#!/usr/bin/python3

import socket
import AStarCsv
import re
import logging
import logg
from threading import Timer
import time
import asyncio_test

from getch import getch, pause
#from kivy.app import App
#from kivy.uix.button import Button
import asyncio
import sys
import random
from queue import PriorityQueue
from queue import Queue

#define

path_delay = 0.5 #到达目标点后延时




log = logg.Logger('all.log',level='debug')

logger = logging.getLogger('fib')
logger.setLevel(logging.DEBUG)

hdr = logging.StreamHandler()

formatter = logging.Formatter("[%(asctime)s] %(name)s:%(levelname)s: %(message)s")
hdr.setFormatter(formatter)

logger.addHandler(hdr)

MAX_LENGHT = 1024

#agv2IP = "192.168.0.157"
agv2IP = "127.0.0.1"
#agv2IP = "192.168.10.139"
agv1IP = "127.0.0.1"
#agv1IP = "192.168.10.194"
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

room_dict = {'中间站B': 231, '中间站A': 270, '胶囊3': 745, '压片2': 805, '批料': 628, '制粒': 605, '容器清洗': 588, '容器存放': 571, '批混': 880, '包衣': 850, '胶囊1': 785, '胶囊2': 752, '压片1': 825, '铝塑1': 729, '铝塑2': 685, '铝塑3': 665, '瓶装': 647}
room_list = ['中间站B', '中间站A', '胶囊3', '压片2', '批料', '制粒', '容器清洗' , '容器存放', '批混', '包衣', '胶囊1', '胶囊2', '压片1', '铝塑1', '铝塑2', '铝塑3', '瓶装']
container_point = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 115, 116, 132, 133, 134, 135, 136, 137, 141, 142, 143, 144, 145, 146, 148, 149, 150, 151, 152, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 172, 173, 174, 175, 176, 177, 178, 179, 204, 206, 208]

class agv:
	def __init__(self, ip, port, loop=asyncio.get_event_loop(), auto_reconnect=True, num=1, queue=None, local_port=None):
		self.num = num
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
#		self.status_key_list = []
#		self.status_key_list = []
		self.status_dic = {}
		self.status_overview = ''
		self.recive_data = b''
		self.recive_data2 = b''
		self.ip = ip
		self.port = port
		self.connected = False
		self.closed = False
		self.receivered = False
		self.retry_interval = 0.5
		self.send_query = False
		self.command_succeed = False
		self.command_list = []
		self.query_response = ''
		self.auto_reconnect = auto_reconnect
		self._loop = loop
		self.queue = queue
		self.local_port = local_port
	def data_received_callback(self, data):
			#print(type(data))
			
			#print(data[:3])
			if data[:3] == b'\x00\x01\x82' and len(data) == 18:
				self.command_succeed = True
				#del self.command_list[0]
				self.recive_data2 = data
#				print('command_succeed')
				self.receivered = True
			elif len(data) < 18:
				self.recive_data2 += data
				if len(self.recive_data2) > 17:
					self.receivered = True
			
#			print('data_received_callback, data:%r from %r:%r' % (data, self.ip, self.port))
#			self.response_check(data)
	async def creat_connect(self):
		#设置断开连接标志位，此函数供tcp断连时调用
		def set_lost_connected():
			self.connected = False
#		def data_received_callback(data):
#			print('data_received_callback, data:%r' % data)
		#connect.client = TcpClient(connection_lost_callback=set_lost_connected)
		self.client = TcpClient(connection_lost_callback=set_lost_connected, data_received_callback=self.data_received_callback, loop=self._loop)
		#self._reader.set_transport(self.client.transport)
		while not self.closed:
			#if not self.connected:
			if not self.connected:
				try:
					#self.co = await self._loop.create_connection(lambda: self.client, self.ip, self.port) #需使用lambda否则无法不能传递回调函数
					if self.local_port:
						local_add = ('127.0.0.1', self.local_port)
						await self._loop.create_connection(lambda: self.client, self.ip, self.port, local_addr=local_add) #需使用lambda否则无法不能传递回调函数
					else:
						await self._loop.create_connection(lambda: self.client, self.ip, self.port) #需使用lambda否则无法不能传递回调函数
					#self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)
#					tcp_server = await loop.create_connection(TcpClient, '192.168.10.197', 10001)
					log.logger.info('Sever %r %r connected in %r seconds' % (self.ip, self.port, self.retry_interval))
					#self._reader.set_transport(self.client.transport)
					self.connected = True #防止连接成功后再次重连
					self.retry_interval = 0.5
				except OSError:
					self.retry_interval = min(60,self.retry_interval*2)
					log.logger.error('Server can connecte retrying in %r seconds..' % self.retry_interval)
					await asyncio.sleep(self.retry_interval)
			await asyncio.sleep(.5) #间隔0.2秒，防止CPU过高
	async def received(self, wait_time=3):
		wait_times = 0.0
		ret = 0
		while not self.receivered:
			wait_times += 0.2 #等待超过1秒钟判断为接收失败
			await asyncio.sleep(.2)
			if wait_times > wait_time: #不能使用==
				ret = -1
				break
			if not self.connected: #接收过程中出现断连跳出循环
				ret = -2
				break
		if ret < 0:
			return ret
		return self.recive_data2
	def connect(self, ip, port):
		self.agvsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.agvsock.settimeout(3)
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
	async def send_message(self,message):
#		if not self.agvsock:
		if not self.connected:
			return None
		try:
#			self.command_succeed = False
			self.client.transport.write(message)
#			logger.info('send message %r to %r:%r' % (message, self.ip, self.port))
			
			rec = await self.received(wait_time=3)
			self.recive_data2 = b''
			self.receivered = False # 发送查询指令后需也需要把接收标志关闭
			#rec = await self.client.transport.
			#rec = await self._reader.read()
			#logger.info('receiver message %r form %r:%r' % (rec, self.ip, self.port))
			#return reader, writer
			#await asyncio.sleep(.5)
			return rec
		except OSError:
			log.logger.error('cant send to %r:%r' % (self.ip, self.port))
#		try:
#			self.agvsock.send(message)
#			rec = self.agvsock.recv(64)
#			if len(rec) < 18:
#				rec22 = self.agvsock.recv(64)
#				rec = rec + rec22
#			return rec
#		except socket.error:
#			log.logger.error('socket error: ' + str(socket.error))
#			time.sleep(3)
#			self.connect(agv2IP, agv2Port)
#			return -1
#		finally:
#			pass
#			return -1
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
	async def action(self,*action):
		data = AStarCsv.action(*action)
#		self.debug(data, 'send to agv: ')
		log.logger.info('send action: %r data: %r to agv' % (action,data))
		#self.agvsock.send(data)
		rec = await self.send_message(data)
		if rec is not isinstance(rec, int) and self.response_check(rec) == -1:
			rec = self.send_message(data)
#		if rec < 0:
#			return None
#		self.debug(rec)
		log.logger.info('receved action respond from agv: %r' % rec)
		return rec
	async def go_pos(self, pos, action=None):
		await self.getstatus()
#		rec = self.getstatus()
#		if not self.id:
		if await self.getstatus() == -1:
			return -1
		self.path_list = AStarCsv.searchpath(self.id, pos)
		self.path,self.pathex = AStarCsv.configpath(self.path_list, self.direct, lift=action)
		self.pathb = bytes(self.pathex)
		# self.agvsock.send(self.pathb)
		log.logger.info('send path to agv: '+self.path)
		rec = await self.send_message(self.pathb)
		rec = self.response_check(rec)
		if rec == -2:
			log.logger.error('not recive path respond from agv')
			return -2
#		logger.debug('path response form agv: '+(" ".join(map(hex,rec))))
		#self.path_rec = self.agvsock.recv(64)
		#return self.path_rec
		return rec
	async def go_pos_action(self, target_pos, open_door_id=None, door_id=None, close_door_id=1, door_id2=None, action=None, radar_point=None):
		if await self.getstatus() and self.id == target_pos:
			log.logger.info('agv already in %r direct: %r ' % (self.id, self.direct))
			return 0
		else:
			log.logger.info('go to new pos: '+str(target_pos))		
		target_id = target_pos
		if self.id > 0 and self.id == open_door_id:
	#	if 0:
			log.logger.info('try open autodoor : %r in point : %r' % (asyncio_test.door_dic[door_id], self.id))
			rec = await asyncio_test.door_action(door_id, action='open')
			if isinstance(rec, int):
				log.logger.error('autodoot can\'t open, do you want to continue' + str(asyncio_test.door_dic[door_id]))
				pause()
			log.logger.info('succeed open autodoor : %r in point : %r' % (asyncio_test.door_dic[door_id], agv.id))
	#				log.logger.info()
			open_door_id_status = 0
			await asyncio.sleep(3)
	#		rec = await asyncio_test.door_action(door_id=tp_list[0][i+1], action='status')
	#		rec = await asyncio_test.door_action(door_id, action='status')
			return 0
		rec = await self.go_pos(target_id, action=action)
		if rec == -1:
	#		print('resend path')
			log.logger.error('resend path')
			rec = self.go_pos(target_id, action=action)
		await asyncio.sleep(1)
		open_door_id_status = 1
		close_door_id_status = 1
		while 1:
			await asyncio.sleep(.5)
			if await self.getstatus() > 0 and self.id > 0:
	#			if agv.id == 0:
	#				continue
				if self.id == open_door_id and open_door_id_status:
					log.logger.info('try open autodoor : %r in point : %r' % (asyncio_test.door_dic[door_id], self.id))
					rec = await asyncio_test.door_action(door_id, action='open')
					if isinstance(rec, int):
						log.logger.error('autodoot can\'t open, do you want to continue' + str(asyncio_test.door_dic[door_id]))
						pause()
					log.logger.info('succeed open autodoor : %r in point : %r' % (asyncio_test.door_dic[door_id], self.id))
	#				log.logger.info()
					open_door_id_status = 0
				if self.id == close_door_id and close_door_id_status:
					rec = await asyncio_test.door_action(door_id2, action='close')
					close_door_id_status = 0
				if radar_point is not None and self.id in radar_point:
					if AStarCsv.mapTest.point_radar_dir.get(self.id) is not None and AStarCsv.mapTest.point_radar_dir[self.id] > 0:
						if self.direct == AStarCsv.mapTest.point_radar_dir[self.id]:
							log.logger.info('disable radar in %r point direct %r' % (self.id, self.direct))
							self.action('radar',30, 35, 200)
					else:
						if self.dis_ob < 25:
							log.logger.info('enable radar in %r point direct %r' % (self.id, self.direct))
							self.action('radar',50, 35, 200)
	#					log.logger.info('enable radar in %r point direct %r' % (agv.id, agv.direct))
				if self.id == target_id and self.agv_status == 'standby':
	#				await asyncio.sleep(1) #到达目标点后延时
					await asyncio.sleep(path_delay) #到达目标点后延时
					self.path_list = []
					log.logger.info('reach to target pos: '+str(target_pos))
	#				if action:
	#					await asyncio.sleep(1)
	#					log.logger.info('agv action : %r in point : %r' % (action, agv.id))
	#					rec = agv.action(action)
	##					rec = agv.action(action)
	#					if isinstance(rec, int):
	#						rec = agv.action(action)
	##						await asyncio.sleep(3)
	#					if action == 'liftup' or action == 'liftdown':
	#						await asyncio.sleep(4)
	#						agv.getstatus() #发送升降指令后再发路径会失败
					break

	async def trans_task(self, action_id, action=None):
	#	through_point_list = AStarCsv.searchpath(fetch_id, release_id, autodoor=True)
		if await self.getstatus() < 0:
			log.logger.error('can\'t get agv status')
	#		pause()
			sys.exit()
		tp_list = AStarCsv.searchpath(self.id, action_id, autodoor=True)
		self.tp_list = tp_list
		
		for i in range(len(tp_list[1])):
			await self.go_pos_action(tp_list[2][i], open_door_id=tp_list[1][i],door_id=tp_list[0][i+1],close_door_id=tp_list[3][i], door_id2=tp_list[0][i], radar_point=tp_list[-1])
			rec = await asyncio_test.door_action(door_id=tp_list[0][i+1], action='status')
	#	await go_pos(tp_list[2][1], tp_list[1][1] ,tp_list[0][1], tp_list[3][0], tp_list[0][0])
	#	rec = await asyncio_test.door_action(door_id=tp_list[0][1], action='status')
		await self.go_pos_action(action_id, close_door_id=tp_list[3][-1], door_id2=tp_list[0][-1], radar_point=tp_list[-1], action=action)
		self.tp_list = []
	#		await rec = asyncio_test.door_action(door_id=tp_list[0][1], action='status')

	async def getstatus(self):
		data = b'\x00\x01\x02\x01\xfd'
		#agv_status_enum = []
		#self.agvsock.send(data)
		#rec = self.agvsock.recv(1024)
		#try:
		#rec = self.agvsock.recv(64)
		rec = await self.send_message(data)    #except Exception:
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
		if rec == -1:
#			log.logger.error('not recive from')
			return -2
#		elif len(rec) < 18 and rec[:3] != b'\x00\x01\x82':
		elif len(rec) < 18:
			log.logger.error('recive form agv: '+(" ".join(map(hex,rec))))
#			log.logger.error('recive from agv: '+str(rec))
			return -1
		elif len(rec) == 18 and rec[:3] != b'\x00\x01\x82':
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
		self.status_overview = 'agv_number: ' + str(self.num) + ' current id:'+str(self.id)+' direct:'+str(self.direct)+' battery:'+str(self.battery)+' speed: '+str(self.speed)+' agv_status: '+self.agv_status+'\n'+'dis_stop: '+str(self.dis_ob)+' radar_depth: '+str(self.radar_depth)+' radar_roi: '+str(self.radar_roi)+'\n'+'agv_error: '+str(self.error_list)+'\n'
#		self.status_overview = f'agv_number: {self.num} current_id: {self.id} direct: {self.direct} battery: {self.battery} speed: {self.speed} agv_status: {self.agv_status} \n dis_stop: {self.dis_ob} radar_depth: {self.radar_depth} radar_roi: {self.radar_roi} \n agv_error: {self.error_list} \n'
#		self.status_dic = {'agv_number':self.num, 'current_id':self.id, 'direct':self.direct, 'battery':self.battery, 'speed':self.speed, 'agv_status':self.agv_status, 'dis_stop':self.dis_stop, 'radar_depth':radar_depth, 'radar_roi': self.radar_roi, 'agv_error':self.agv_error}
		log.logger.debug('agv status check:'+self.status_overview)
		if self.queue:
			self.queue.put(self.status_overview)
#			self.queue.put(self.status_dic)
		return 1
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
#继承asyncio.Protocol，并重新定义connnection_lost方法，调用传递过来函数
class TcpClient(asyncio.Protocol):
	def __init__(self,connection_lost_callback=None, data_received_callback=None, loop=None):
		self._connection_lost_callback = connection_lost_callback
		self._data_received_callback = data_received_callback
		self._loop = loop or asyncio.get_event_loop()
		self.is_connected = False
	#socket创建成功回调函数，会传入transport，接受用于发送消息
	def connection_made(self, transport):
		self.transport = transport
		self._reader = asyncio.StreamReader(loop=self._loop)
		self._reader.set_transport(transport)
		#self._reader_f = ensure_future(self._reader_coroutine(), loop=self._loop)
		self.is_connected = True
	#socket断开连接回调函数，传入exc
	def connection_lost(self, exc):
		log.logger.error('Connection lost with exec: %s' % exc)
		self.is_connected = False
		if self._connection_lost_callback:
			self._connection_lost_callback()
	def data_received(self, data):
		#logger.info('receiver data : %r' % data)
		if self._data_received_callback:
			self._data_received_callback(data)
	#@asyncio.coroutine
	async def _reader_corotine(self):
		while True:
			try:
				c = await self._reader.read()
				logger.info(c)
			except ConnectionError:
				return
			except asyncio.streams.IncompleteReadError:
				return
#class TestApp(App):
#	def build(self):
#		return bt1
dict_slice = lambda adict, start, end: { k:adict[k] for k in adict.keys()[start:end] }
async def container():
	container_point1 = container_point[20:-10]
#	random.shuffle(container_point)
	random.shuffle(container_point1)
#	await go_pos(141)
#	for i in container_point:
	for i in container_point1:
		if i == 162 or i == 161 or i == 160:
			continue
		await go_pos(i)
async def room():
#	room_point = room_list[4:-1]
	room_point = room_list[13:]
#	room_point = dict_slice(room_dict, 5, -1)
#	random.shuffle(room_point)
	for i in room_point:
		if i == '胶囊3' or i == '胶囊1' or i == '中间站A' or i == '中间站B':
			pass
#			continue
		await agv.trans_task(room_dict[i])
#		await trans_task(230)
async def path_test(agv, pq):
#	await trans_task(420)
	await asyncio.sleep(1)
	await agv.getstatus()
	await asyncio.sleep(1)
	if not pq.empty():
		print('status queue: %r' % pq.get())
#		print('status dic: %r' % pq.get())
#	await agv.trans_task(102)
#	await trans_task(room_dict['制粒'], 'liftdown')
#	await trans_task(230)
#	await go_pos(206)
	return 0
	while 0:
		await asyncio.sleep(.5)
		await agv.getstatus()
		await asyncio.sleep(.5)
		await agv.action('charge')
		await agv.action('charge')
		await asyncio.sleep(.5)
		await agv.action('discharge')
#	await go_pos(173)
	while 0:
		await go_pos(151)
		await asyncio.sleep(.5)
		await go_pos(165)
		await asyncio.sleep(.5)
#		return 0
#	await go_pos(420)
#	await trans_task(588)
#	await container()
	while 1:
		await room()
	return 0

if __name__ == '__main__':
	#agvgopos(431)
	#print(AStarCsv.configpath(AStarCsv.searchpath(134, 426),4))
#	agvsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#	agvsock.settimeout(3)
#	agvsock.connect((agv2IP,agv2Port))
	loop = asyncio.get_event_loop()
	loop2 = asyncio.new_event_loop()
	current_id = 0
	target_id = 0
#	pointbk = AStarCsv.get_point()
	pointbk = {192:0, 152:0, 107:0, 173:0}
#	agv = agv()
	pq = Queue()
#	pq = Queue()
	
	agv1 = agv(agv1IP, agv2Port, loop, queue=pq, local_port=10000)
	agv2 = agv(agv2IP, agv2Port, loop, queue=pq, local_port=20000)
#	if agv.getstatus() < 0:
#		log.logger.error('can\'t get agv status')
#		sys.exit()
#	if agv.id == 0:
#		sys.exit("sorry, goodbye!")
#	else:
#		current_id = agv.id
	tasks = [asyncio.Task(agv2.creat_connect()), asyncio.Task(agv1.creat_connect()), asyncio.Task(path_test(agv2, pq))]
	loop.run_until_complete(asyncio.wait(tasks))
	
#	tasks = [asyncio.Task(path_test())]
#	loop.run_until_complete(asyncio.wait(tasks))
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