# coding=utf-8
from __future__ import print_function
#import csv
import xlrd
import copy
import os

path = os.path.dirname(__file__)

class mapcsv:
	def __init__(self):
		self.w = 61
		self.h = 36
		self.pathTag = 0
		self.path = []
		#agvfile = open("AGV-Route.csv")
		#reader = csv.reader(agvfile)
		agvfile = xlrd.open_workbook(filename=path+'/AGV线路图-2019-10.11.xlsx')
		sheet = agvfile.sheet_by_index(0)
		sheet2 = agvfile.sheet_by_index(2)
		self.data = []
		self.pointbk = []
		for x in range(0,self.h):
			row = sheet.row_values(x)
			for item in range(len(row)-1,-1,-1):
				if row[item] == '':
					row[item] = 1
				elif type(row[item]) == type('A'):
					row[item] = 88
			row = list(map(int,row))
			self.data.append(row)
			##print(row)
		for x in range(0,3):
			row = sheet2.row_values(x)
			#print(row)
			#for item in range(len(row)-1,-1,-1):
			row = list(map(int,row))
			self.pointbk.extend(row)
		self.pointbk.sort()
		self.pointbk = self.pointbk[23:]
		#print(self.pointbk)
		self.databack = copy.deepcopy(self.data)
		
	def showMap(self):
		for item in self.data:
			print(item)
		return;
	def showPoint(self,x,y):
		print(self.data[x][y])
		return;
	
	def setMap(self,point):
		self.data[point.x][point.y] = self.pathTag
		return;
	def isPass(self, point):
		if (point.x < 0 or point.x > self.h-1 ) or (point.y < 0 or point.y > self.w - 1):
			return False;
		if (self.data[point.x][point.y] > 100) or (self.data[point.x][point.y] == 0):
			return True;
	def isSpace(self, point):
		if self.data[point.x][point.y] == 0:
			return True;

if __name__ == '__main__':
	map = mapcsv();
	##map.showMap();
'''
class map2d:
	""" 
	"""  
	def __init__(self):
		self.data = [list("####################"),
					 list("#*****#************#"),
					 list("#*****#*****#*####*#"),
					 list("#*########*##******#"),
					 list("#*****#*****######*#"),
					 list("#*****#####*#******#"),
					 list("####**#*****#*######"),
					 list("#*****#**#**#**#***#"),
					 list("#**#*****#**#****#*#"),
					 list("####################")]

		self.w = 20
		self.h = 10
		self.passTag = '*'
		self.pathTag = 'o'

	def showMap(self):
		for x in xrange(0, self.h):
			for y in xrange(0, self.w):
				print(self.data[x][y], end='')
			print(" ")
		return;

	def setMap(self, point):
		self.data[point.x][point.y] = self.pathTag
		return;

	def isPass(self, point):
		if (point.x < 0 or point.x > self.h - 1) or (point.y < 0 or point.y > self.w - 1):
			return False;

		if self.data[point.x][point.y] == self.passTag:
			return True;
'''