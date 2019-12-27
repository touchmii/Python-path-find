# coding: utf-8
#!/usr/bin/python3
#import mapxsl
import mapxslfast as mapxsl
import AStar2 as AStar
import copy
from collections import Counter
import numpy as np
#import tinyarray as np
import operator
import os
#from threading import Timer
import time
# import numba

mapTest = mapxsl.mapcsv();

#@numba.jit()
# def searchid(maps,id):
# 	maps = maps
# 	id = id
# 	for x in range(maps.h):
# 		if maps.databack[x].index(id):
# 			y = maps.databack[x].index(id)
# 	return x, y;
#@numba.jit()
def Find(target):
	#mapTest = mapxsl.mapcsv();
	id = mapTest.pointdic[target]
	coord = np.array([0,0])
	coord[0] = id[0]
	coord[1] = id[1]
	return coord
	# for index in range(len(array)):
	# 	if target in array[index]:
	# 		coord[0] = index
	# 		coord[1] = array[index].index(target)
	# 		return coord
def searchpath(start, end, path_fix=0, autodoor=False, radar_toggle=False):
	#默认情况下进752经过750，空车出不经过750，进785经过789，出785不经过789。可通过设置341，750，788，789为障碍物控制路径
	#path_fix = 1 时 空车进752，设置341为1（障碍物），fix = 。。。
	if start not in mapTest.pointdic or end not in mapTest.pointdic:
		return 'No Point'
	mapcopy = copy.deepcopy(mapTest)
	if start == end:
		return 'No Path'
#	if end == 785 or end == 752:
#		mapcopy.data[3][16] = 1
#		mapcopy.data[2][20] = 1
#	elif end == 206 or end == 204:
#		mapcopy.data[20][39] = 1
#		mapcopy.data[19][37] = 1
#	elif start == 204:
#		mapcopy.data[20][39] = 1
	#maps = mapxsl.mapcsv();
	#mapTest = mapxsl.mapcsv();
	startid = Find(start)
	endid = Find(end)
	# print(startid)
	# print(endid)
	aStar = AStar.AStar(mapcopy, AStar.Node(AStar.Point(endid[0],endid[1])), AStar.Node(AStar.Point(startid[0],startid[1])))
	if aStar.start():
		aStar.setMap();
		#mapTest.showMap();
	else:
		print("no way")
	aStar.pathpoint = list(filter(lambda x : x!=0,aStar.pathpoint))
	print(aStar.pathpoint)
	if autodoor:
			set1 = set(aStar.pathpoint)
			set2 = set(mapTest.pointdoor)
			set3 = list(set1 & set2)
			set3.sort(key=aStar.pathpoint.index)
			set40 = set(mapTest.point_radar)
			set5 = list(set1 & set40)
			set5.sort(key=aStar.pathpoint.index)
			print(set5)
			
			set6 = list(map(lambda x:x if mapTest.point_radar_dir[x] >0 else aStar.pathpoint[aStar.pathpoint.index(x)+1], set5))
			set7 = list(set(set6))
#			set7.sort(key=set6.index)
			if aStar.pathpoint[-1] == 628:
				set7.remove(627)
			#将方向值小于等于0的点往前挪一位，作为避障恢复。方向值大于0的点为避障关闭点，保持不变。根据当前ID跟方向确定是否关闭避障，可以达到单方向生效，返回路径不影响。
	#		stop_point = map(lambda x:pathb(pathb.index(x)-2), set3)
#			open_door_point = list(map(lambda x:aStar.pathpoint[aStar.pathpoint.index(x)-3], set3))
#			wait_door_point = list(map(lambda x:aStar.pathpoint[aStar.pathpoint.index(x)-2], set3))
#			print(aStar.pathpoint.index(set3[0]))
#			leng = aStar.pathpoint.index(set3[0])
			open_door_point = list(map(lambda x:aStar.pathpoint[aStar.pathpoint.index(x)-3] if aStar.pathpoint.index(x) > 2 else aStar.pathpoint[aStar.pathpoint.index(x)-aStar.pathpoint.index(x)+0], set3))
			wait_door_point = list(map(lambda x:aStar.pathpoint[aStar.pathpoint.index(x)-2] if aStar.pathpoint.index(x) > 2 else aStar.pathpoint[aStar.pathpoint.index(x)-aStar.pathpoint.index(x)+0], set3))
#			wait_door_point = list(map(lambda x:aStar.pathpoint[aStar.pathpoint.index(x)-2], set3))
			close_door_point = list(map(lambda x:aStar.pathpoint[aStar.pathpoint.index(x)+1], set3))
			set3.insert(0,0)
			close_door_point.insert(0,0)
			print('through_door: '+str(set3))
			print('open_door_point: '+str(open_door_point))
			print('wait_door_point: '+str(wait_door_point))
			print('close_door_point: '+str(close_door_point))
			print('point_radar: '+str(set7))
			set4 = []
			set4.append(set3)
			set4.append(open_door_point)
			set4.append(wait_door_point)
			set4.append(close_door_point)
			set4.append(set7)
			return set4

	return aStar.pathpoint;
def sign(a):
	if a < 0:
		return -1
	elif a > 0:
		return 1
	else:
		return 0
#十六进制最大发送60多个二维码210->289 ,字节数254
def configpath(pathb,direct,endir=0, back=True, maxlen = 60, lift=None):
	if isinstance(pathb, str):
		return pathb, 0
	pathex = bytearray(b'\x00\x01\x0c')
	pathex2 = bytearray(b'\x00\x00\x01\x01')
	pathex3 = bytearray(b'\x00\x00\x02\x02')
	path = pathb
	patha = copy.deepcopy(pathb)
	#print(path)
	arrows = np.array([[-1,0],[0,-1],[1,0],[0,1]])
	#p = 1
	p1 = np.array([0,0])
	p2 = np.array([0,0])
	p3 = np.array([0,0])
	pp1 = np.array([0,0])
	pp2 = np.array([0,0])
	pp = np.array([0,0])
	for p in range(0,len(path)-1):
		pp = p
		pathex2.append(path[p]//256)
		pathex2.append(path[p]%256)
#		if p == 0 and up:
##			pathex2.append(2)
#			pathex2.append(2)
#			path[p] = str(path[p])+'AA'
#		else:
		pathex2.append(0)
#		pathex2.append(lambda x:3 if x == 'liftup' else 0, lift)
		pathex2.append(1)
		
		
		if len(pathex2) > 59*4:
			pass
		#print(pathex2)
		p2 = Find(patha[p])
		p3 = Find(patha[p+1])
		if p == 0:
			p1[0] = p2[0]+arrows[direct-1][0]
			p1[1] = p2[1]+arrows[direct-1][1]
#			sign = lambda x:[1, -1][x < 0]
				
			pp22 = p3 - p2
			
#			pp23 = p3 - p2
			pp22[0] = sign(pp22[0])
			pp22[1] = sign(pp22[1])
			pp = pp22 - (p2 - p1)
#			pp = pp23 - (p2 - p1)
			
			#print(pp)
			if abs(pp[0]) == 2 or abs(pp[1]) == 2:
			#如果掉头点后面是虚拟点pp[0],pp[1]绝对值将大于2，故判定条件设为大于1
#			if (abs(pp[0]) > 1 and pp[1] == 0) or (abs(pp[1]) > 1 and pp[0] == 0):
				path[p] = str(path[p])+'LD'
				pathex2[-2] = 7
				#pathex2[-1] = bytes(1)
		else :
			p1 = Find(patha[p-1])
		
		
		#print(path[p],path[p+1],path[p+2])
		#print(path[p+1])
		if abs(p1[0]-p3[0]) == 1 and abs(p1[1]-p3[1]) == 1:
			#print(type(p1))
			pp1 = p2 - p1
			pp2 = p3 - p2
			'''
			pp1[0] = p2[0]-p1[0]
			pp1[1] = p2[1]-p1[1]
			pp2[0] = p3[0]-p2[0]
			pp2[1] = p3[1]-p2[1]
			'''
			#if pp1[0] and 
			#print(path[p],path[p+1],path[p+2])
			#print(p1,p2,p3)
			#print(pp1,pp2)
			if pp1[0] == 0 and ((pp1[1] > 0 and pp2[0] < 0) or (pp1[1] < 0 and pp2[0] > 0)):
				#LD
				path[p] = str(path[p])+'LL'
				pathex2[-2] = 4
				#pathex2.append(4)
				#pathex2.append(1)
				#print(path[p+1],"LD")
			elif pp1[1] == 0 and ((pp1[0] < 0 and pp2[1] < 0) or (pp1[0] > 0 and pp2[1] > 0)):
				#LD
				path[p] = str(path[p])+'LL'
				pathex2[-2] = 4
				#pathex2.append(4)
				#pathex2.append(1)
			#elif pp1[0] == 0 or (pp1[1] > 0 and pp2[0] > 0) or (pp1[1] < 0 and pp2[0] < 0):
			else :
				path[p] = str(path[p])+'RR'
				pathex2[-2] = 16 #0x10
				#pathex2.append(10)
				#pathex2.append(1)
	pathex2.append(path[-1]//256)
	pathex2.append(path[-1]%256)
#	if action == 'liftdown':
#	pathex2.append(18)
	if lift == 'liftup':
		pathex2.append(2)
#		path[-1] = str(path[-1])+'AA'
	elif lift == 'liftdown':
		pathex2.append(3)
#		path[-1] = str(path[-1])+'aa'
	else:
		pathex2.append(0)
#	pathex2.append(0)
#	pathex2.append(lambda x:0x18 if x == 'liftup' else 0, lift)
	pathex2.append(0)
	#pathex2[-1] = 0
	pathex.append(len(pathex2)//256)
	pathex.append(len(pathex2)%256)
	pathex += pathex2
	#check = bytes(0)
	# 定位桩倒退参数默认开启，判断倒数第一个码是否在列表pointbk里面，对倒数第二个码动作修改
	if back == True:
		# print(mapTest.pointdicbk) #列表第一位元素为101导致index（101）无法正常执行
		try:
			# if mapTest.pointbk.index(path[-1]):
			if path[-1] in mapTest.pointdicbk:
#				if len(path) == 2:
				if isinstance(path[-2], int):
					path[-2] = str(path[-2])+'BB'
					pathex[-6] = 0x20
				elif path[-2][-2:] == 'LD':
					path[-2] = path[-2][:3] + 'BK'
					pathex[-6] = 0x17
				elif path[-1] == 785:
					path[-3] = '787BR'
					pathex[-10] == 0x22
				elif path[-2][-2:] == 'RR':
					path[-2] = path[-2][:3] + 'BL'
					pathex[-6] = 0x21
				elif path[-2][-2:] == 'LL':
					path[-2] = path[-2][:3] + 'BR'
					pathex[-6] = 0x22
#				elif path[-1] == 571:
#					path[-2] = '570BR'
#					#print(pathex[-6])
#					pathex[-6] = 0x22
#				elif path[-1] == 729:
#					path[-2] = '729BL'
#					pathex[-6] = 0x21
#				elif path[-1] == 752:
#					path[-2] = '751BR'
#					pathex[-6] = 0x22
#				elif path[-1] == 204:
#					path[-2] = '205BR'
#					pathex[-6] = 0x22
#				elif path[-1] == 206:
#					path[-2] = '207BL'
#					pathex[-6] = 0x21
#				else:
#					path[-2] = str(path[-2])+'BB'
#					pathex[-6] = 0x20
		#except ValueError as error:
		except Exception as e:
			pass
			#print(e)
		#continue
	# check = 0
	# for i in range(0,len(pathex)):
	# 	#check = bytes(map(operator.xor, bytes(pathex[i]), check))
	# 	check = check ^ pathex[i]
	# #print(check)
	# check = ~check & 0xFF
	# #print(check)
	# #print(pathex)
	# pathex.append(check)
	pathex = check(pathex)
	#check = operator.invert(check)
	if lift == 'liftup':
#		pathex2.append(3)
		path[-1] = str(path[-1])+'AA'
	elif lift == 'liftdown':
#			pathex2.append(2)
		path[-1] = str(path[-1])+'aa'
	else:
		pass
#			pathex.append(0)
	path = '->'.join(str(i) for i in path)
	#print(pathex)
	return path,pathex;
	
def action(*action):
	if action[0] == 'pause':
		data = bytearray(b'\x00\x01\x06\x00\x02\x00\x00')
		return check(data)
	elif action[0] == 'resume':
		data = bytearray(b'\x00\x01\x05\x00\x02\x00\x01')
		return check(data)
	elif action[0] == 'liftup':
		data = bytearray(b'\x00\x01\x0d\x00\x02\x02\x00') #0x0 0x1 0xd 0x0 0x2 0x2 0x0 0xf3
		return check(data)
	elif action[0] == 'liftdown':
		data = bytearray(b'\x00\x01\x0d\x00\x02\x03\x00') #0x0 0x1 0xd 0x0 0x2 0x3 0x0 0xf2
		return check(data)
	elif action[0] == 'charge':
		data = bytearray(b'\x00\x01\x03\x00\x02\x02\x00') #0x0 0x1 0x3 0x0 0x2 0x2 0x0 0xfd
		return check(data)
	elif action[0] == 'discharge':
		data = bytearray(b'\x00\x01\x03\x00\x02\x03\x00') #0x0 0x1 0x3 0x0 0x2 0x3 0x0 0xfc
		return check(data)
	elif action[0] == 'up':
		data = bytearray(b'\x00\x01\x0c\x00\x00\x01\x01')
		data.append(action[1]//256)
		data.append(action[1]%256)
		data.append(2)
		data.append(0)
		return check(data)
		
	elif action[0] == 'radar' and len(action) == 4:
		data= bytearray(b'\x00\x01\x04\x00\x03')
		data.append(int(action[1]))
		data.append(int(action[2]))
		data.append(int(action[3])//10)
		return check(data)
	else:
		return 'not find action'

# @numba.jit()
def check(data):
	check = 0
	for i in range(0, len(data)):
		check = check ^ data[i]
	check = ~check & 0xFF
	#print(check)
	data.append(check)
	return data
'''class Solution:
	# array 二维列表
	def Find(array, target):
		if array == [[]]:
			return False
		nRow = len(array)
		nCol = len(array[0])
					for i in range(nRow):
				for j in range(nCol):
					if target == array[i][j]:
						return True
			else:
				return False
'''

def get_point():
	return mapTest.pointdic
def test(time = 1):
	for i in range(0,time):
		path,pathex = configpath(searchpath(208, 206), 2, lift='liftup')
		#print('time .')
if __name__ == '__main__':
	##构建地图
	#mapTest = mapxsl.mapcsv();
#	mapTest.showMap();
	##构建A*
	#print(configpath(searchpath(206, 207),4))
	#test(100)
	#path,pathex = configpath(searchpath(447, 447), 4)
	start = time.time()
	print(time)
#	path,pathex = configpath(searchpath(117, 107), 4)
#	path = searchpath(270, 850)
#	a = set(path)
#	b = set(mapTest.pointdoor)
#	print(a & b)
#	c = Counter(path)
#	c2 = Counter(mapTest.pointdoor)
##	print(mapTest.pointdoor)
##	c.subtract(Counter(mapTest.pointdoor))
#	diff = c2 - c
#	
#	print(list(diff.elements()))
#	set3 = searchpath(685, 729, autodoor=True)
#	print(set3)
#	set3 = searchpath(247, 628, autodoor=True)
#	print(set3)
#	set3 = searchpath(246, 628, autodoor=True)
#	print(set3)
#	set3 = searchpath(729, 605, autodoor=True)
#	print(set3)
#	path,pathex = configpath(searchpath(289, 150), 2, lift='liftup')
	path,pathex = configpath(searchpath(109, 468), 2)
	print('robot path '+path)
	print(len(pathex))
	print(pathex)
	print(" ".join(map(hex,pathex)))
	end = time.time()
	print('CPU执行时间: ', end - start)
#	start = time.time()
#	print(" ".join(map(hex,pathex)))
#	path,pathex = configpath(searchpath(210, 850), 4)
#	# print('robot path '+path)
#	# print(len(pathex))
#	print(" ".join(map(hex,pathex)))
#	end = time.time()
#	print('CPU执行时间: ', end - start)
#	start = time.time()
#	print(" ".join(map(hex,pathex)))
#	path,pathex = configpath(searchpath(210, 850), 4)
#	# print('robot path '+path)
#	# print(len(pathex))
#	print(" ".join(map(hex,pathex)))
#	end = time.time()
#	print('CPU执行时间: ', end - start)
#	pathexascii = ''
#	pathexascii2 = ''
#	for i in range(0,len(pathex)):
#		#pathexascii.join(' 0x{:02}'.format(pathex[i]))
#		
#		pathexascii += hex(pathex[i])
#		pathexascii2 += hex(pathex[i])
#		pathexascii += ' '
	#print(pathexascii)
	
	#action = action('radar',136,80,80)
#	action = action('discharge')
	action = action('resume')
	print(" ".join(map(hex,action)))
'''
	aStar = AStar.AStar(mapTest, AStar.Node(AStar.Point(20,40)), AStar.Node(AStar.Point(7,0)))
	print("A* start:")
	##开始寻路
	if aStar.start():
		aStar.setMap();
		#mapTest.showMap();
	else:
		print("no way")
	print(aStar.pathpoint)
'''
	#print(searchid(mapTest, 850))
	#print(Find(684, mapTest.databack))
	#search = Solution
	#print(search.Find(mapTest.data, 850))		
