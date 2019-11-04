# coding: utf-8
#!/usr/bin/python3

import agvsocket
from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen

class LoginScreen(GridLayout):
	def __init__(self, **kwargs):
		super(LoginScreen, self).__init__(**kwargs)
		self.cols = 1
		self.add_widget(Label(text='User Name'))
		self.username = TextInput(multiline=False)
		self.add_widget(self.username)
		self.add_widget(Label(text='password'))
		self.password = TextInput(password=True, multiline=False)
		self.add_widget(self.password)

Builder.load_string(r'''
<OneScreen>
	BoxLayout:
		orientation: 'vertical'
		BoxLayout:
			padding:20
			spacing:20
			hight: 20
			size_hint_y: None
			#size_hint_x: None
			height: '48dp'
			Label:
				text: 'Connect AGV'
			TextInput:
				id: agv_ip
				#mutiline: False
				#size_hint: 1, None
				#valign: 'middle'
				#padding: 20
				#line_height: 1.0
				height: self.minimum_height
				width: self.height
				hint_text: "AGV Connnet IP"
				text: '127.0.0.1'
			Label:
				text: 'Port'
			TextInput:
				id: agv_port
				#valign: 'middle'
				#line_height: 1.0
				size_hint_x: None
				hint_text: "Port"
				text: '10001'
			Switch:

		BoxLayout:
			hight: 90
			#width: 40
			padding: 20
			spacing: 20
			#size_hint_y: None
			
			orientation: 'vertical'
			
			TextInput:
				id: goid
				hint_text: "AGV Go ID"
				text: ''
			Button:
				text: 'Status'
				size_hint_y: None
				size_hint_x: None
				height: '48dp'
				on_press: root.get_agv_status()
			Button:
				id: start_button
				text: 'go start'
				height: '48dp'
				size_hint_y: None
				on_press: root.agv_go_id()
			Button:
				text: 'Clear'
				#height: '48dp'
				size_hint_y: None
				on_press: root.ids.scrolltext.text = ''
			ScrollView:
				Label:
					id: scrolltext
					text: ''
					font_size: 30
					size_hint_x: 10
					size_hint_y: None
					text_size: self.width, None
					height: self.texture_size[1]

''')

class OneScreen(Screen):
	def __init__(self, **kwargs):
		self.author = 'touchmii'
		super(OneScreen, self).__init__(**kwargs)
		self.agv = agvsocket.agv()
	
	def do_something(self):
		print('Start pressed goid: '+str(self.ids['goid'].text))
		self.ids.scrolltext.text += self.ids.goid.text+'\n'
		#self.ids['scrooltext'].text =+ self.ids['goid'].text
		#self.ids['scrooltext'].text = 'hello'*10
		#self.ids['start_button'].text = 'hello'
	def get_agv_status(self):
		self.agv.getstatus()
		#print(self.agv.id)
		self.ids.scrolltext.text += self.agv.status_overview
	def agv_go_id(self):
		#self.agv.go_pos(int(self.ids.goid.text))
		self.path_rec = self.agv.go_pos(int(self.ids.goid.text))
		self.ids.scrolltext.text += str(self.path_rec) + '\n'

def do_something():
	print('do something')


class TestApp(App):
	def build(self):
		return OneScreen()

TestApp().run()