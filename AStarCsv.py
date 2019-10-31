#!/usr/bin/python3
import mapxsl
import AStar
import copy
import numpy as np
import operator
import os
#import numba

mapTest = mapxsl.mapcsv();

#@numba.jit()
def searchid(maps,id):
	maps = maps
	id = id
	for x in range(maps.h):
		if maps.databack[x].index(id):
			y = maps.databack[x].index(id)
	return x, y;
#@numba.jit()
def Find(target, array):
	#mapTest = mapxsl.mapcsv();
	coord = np.array([0,0])
	for index in range(len(array)):
		if target in array[index]:
			coord[0] = index
			coord[1] = array[index].index(target)
	return coord
def searchpath(start,end):
	#maps = mapxsl.mapcsv();
	#mapTest = mapxsl.mapcsv();
	startid = Find(start, mapTest.databack)
	endid = Find(end, mapTest.databack)
	#print(startid)
	#print(endid)
	aStar = AStar.AStar(mapTest, AStar.Node(AStar.Point(endid[0],endid[1])), AStar.Node(AStar.Point(startid[0],startid[1])))
	if aStar.start():
		aStar.setMap();
		#mapTest.showMap();
	else:
		print("no way")
	aStar.pathpoint = list(filter(lambda x : x!=0,aStar.pathpoint))
	#print(aStar.pathpoint)
	return aStar.pathpoint;
def configpath(pathb,direct):
	pathex = bytearray(b'\x00\x01\x0c')
	pathex2 = bytearray(b'\x00\x00\x01\x01')
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
		pathex2.append(0)
		pathex2.append(1)
		#print(pathex2)
		p2 = Find(patha[p],mapTest.databack)
		p3 = Find(patha[p+1],mapTest.databack)
		if p == 0:
			p1[0] = p2[0]+arrows[direct-1][0]
			p1[1] = p2[1]+arrows[direct-1][1]
			pp = (p3 - p2) - (p2 - p1)
			#print(pp)
			if abs(pp[0]) == 2 or abs(pp[1]) == 2:
				path[p] = str(path[p])+'LD'
				pathex2[-2] = 7
				#pathex2[-1] = bytes(1)
		else :
			p1 = Find(patha[p-1],mapTest.databack)
		
		
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
				pathex2[-2] = 16
				#pathex2.append(10)
				#pathex2.append(1)
	pathex2.append(path[-1]//256)
	pathex2.append(path[-1]%256)
	pathex2.append(0)
	pathex2.append(0)
	#pathex2[-1] = 0
	pathex.append(len(pathex2)//256)
	pathex.append(len(pathex2)%256)
	pathex += pathex2
	#check = bytes(0)
	check = 0
	for i in range(0,len(pathex)):
		#check = bytes(map(operator.xor, bytes(pathex[i]), check))
		check = check ^ pathex[i]
	#print(check)
	check = ~check & 0xFF
	#print(check)
	#print(pathex)
	pathex.append(check)
	#check = operator.invert(check)
	path = '->'.join(str(i) for i in path)
	#print(pathex)
	return path,pathex;	
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
def test(time = 1):
	for i in range(0,time):
		path,pathex = configpath(searchpath(216, 850), 2)
		#print('time .')
if __name__ == '__main__':
	##构建地图
	#mapTest = mapxsl.mapcsv();
	##mapTest.showMap();
	##构建A*
	#print(configpath(searchpath(206, 207),4))
	#test(100)
	path,pathex = configpath(searchpath(210, 290), 2)
	print('robot path '+path)
	print(len(pathex))
	print(" ".join(map(hex,pathex)))
#	pathexascii = ''
#	pathexascii2 = ''
#	for i in range(0,len(pathex)):
#		#pathexascii.join(' 0x{:02}'.format(pathex[i]))
#		
#		pathexascii += hex(pathex[i])
#		pathexascii2 += hex(pathex[i])
#		pathexascii += ' '
	#print(pathexascii)
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
