# coding: utf-8
#usr/bin/python3

import PySimpleGUI as sg
from queue import PriorityQueue
from queue import Queue
import asyncio
import random
import time
import threading
import agvsocket2 as agvsock


agv1IP = "192.168.10.139"
#agv1IP = "127.0.0.1"
agv2IP = "192.168.10.194"
#agv2IP = "127.0.0.1"
#agv2IP = "127.0.0.1"
#agv2Port = 10001
agv1Port = 10001
agv2Port = 10001

room_list = ['', '胶囊3', '压片2', '批料', '制粒', '容器清洗' , '容器存放', '批混', '包衣', '胶囊1', '胶囊2', '压片1', '铝塑1', '铝塑2', '铝塑3', '瓶装']

menu_def = [['&File', ['&Open', '&Save', 'E&xit', 'Properties']]]

new_task = [[sg.Combo(('AGV1#', 'AGV2#'), size=(8, 1), default_value='AGV1#'), sg.InputText('101', size=(8, 1)),sg.Button('选取', size=(3, 1)), sg.Combo((room_list), size=(8,1))],
[sg.CBox('接受自动排队', size=(10, 1)), sg.CBox('是否称重', size=(10, 1))],
[sg.Radio('取桶', "RADIO1", default=True, size=(10, 1)), sg.Radio('送桶', "RADIO1"), sg.Text('任务优先级'), sg.Spin(values=('0', '1', '2', '3'), initial_value='0')],
[sg.Cancel(), sg.OK(), sg.Button('Pop')],
[sg.Button('Debugger'), sg.Debug(key='Debug'), sg.Button('Enable'), sg.Button('Popout')]]

continer_select = [[sg.Button('ok', size=(3, 1))]]
#task_view():
task_view = [[sg.Text(' ', key='-TASK-', size=(20,5))]]

agv_control = [[sg.Combo(('AGV1#', 'AGV2#'), size=(8, 1), default_value='AGV1#'), sg.Button('Connect')]]

continer_select = []

agv_status = [[sg.Text(' ', key='-AGV1_STATUS-')],
[sg.Text(' ', key='-AGV2_STATUS-')]]

task_list = []
def add_task(values):
	pass
async def task():
	pass
async def worker(name, queue):
	while True:
		# Get a "work item" out of the queue.
		sleep_for = await queue.get()

		# Sleep for the "sleep_for" seconds.
#		await asyncio.sleep(sleep_for)
		await asyncio.sleep(3)

		# Notify the queue that the "work item" has been processed.
		queue.task_done()

		print(f'{name} has slept for {sleep_for:.2f} seconds')


async def main(pq, agv1, agv2):
	# Create a queue that we will use to store our "workload".
#	queue = asyncio.Queue()
	queue = pq
	while True:
		if not queue.empty():
			task = queue.get()
			print('task: %r' % task[2])
#			await agv.action('charge')
			if task[2][0] == 'AGV1#':
				await agv1.trans_task(int(task[2][1]))
			elif task[2][0] == 'AGV2#':
				await agv2.trans_task(int(task[2][1]))
			else:
				pass
#			await asyncio.sleep(3)
			print('finish one task %r' % str(queue.queue))
#			queue.task_done()
		await asyncio.sleep(.2)
	# Generate random timings and put them into the queue.
	total_sleep_time = 0
#	for _ in range(20):
#		sleep_for = random.uniform(0.05, 1.0)
#		total_sleep_time += sleep_for
#		queue.put_nowait(sleep_for)

	# Create three worker tasks to process the queue concurrently.
	tasks = []
	for i in range(3):
		task = asyncio.create_task(worker(f'worker-{i}', queue))
		tasks.append(task)

	# Wait until the queue is fully processed.
	started_at = time.monotonic()
	await queue.join()
	total_slept_for = time.monotonic() - started_at

	# Cancel our worker tasks.
	for task in tasks:
		task.cancel()
	# Wait until all worker tasks are cancelled.
	await asyncio.gather(*tasks, return_exceptions=True)

	print('====')
	print(f'3 workers slept in parallel for {total_slept_for:.2f} seconds')
	print(f'total expected sleep time: {total_sleep_time:.2f} seconds')
def main_task(pq, mes_pq):
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
#	agv1_local_port = random.randint(8000,9999)
	agv1_local_port = None
#	agv2_local_port = random.randint(10001,12000)
	agv2_local_port = None
	agv1 = agvsock.agv(agv1IP, agv2Port, loop, num=1, queue=mes_pq, local_port=agv1_local_port)
	agv2 = agvsock.agv(agv2IP, agv2Port, loop, num=2, queue=mes_pq, local_port=agv2_local_port)
#	loop.run_until_complete(main(pq))
	tasks = [asyncio.Task(agv1.creat_connect()), asyncio.Task(agv2.creat_connect()), asyncio.Task(main(pq, agv1, agv2))]
	loop.run_until_complete(asyncio.wait(tasks))
	loop.close()

def windoww(queue, mes_pq):
	pq = queue
#	pq = PriorityQueue(10)
	window = sg.Window('新建订单', new_task, debugger_enabled=False)
	window2 = sg.Window('订单列表', task_view)
#	window.enable_debugger()
#	sg.show_debugger_popout_window()
#	sg.show_debugger_window()
	counter = 0
	task_index = 0
#	asyncio.run(main())
	while True:
		event, values = window.read(timeout=100)
		if event in (None, 'Cancel'):
			break
		elif event == 'OK':
			print(values)
			task_list.append(list(values.values()))
			pq.put((int(values[7]),task_index, list(values.values())))
			print('priority : %r' % values[7])
			print(task_list)
			print('queue: %r' % pq.queue)
			window2['-TASK-'].update(task_list)
			task_index += 1
		elif event == 'Pop':
			pq.get()
			task_list.pop()
			window2['-TASK-'].update(task_list)
			print('queue: %r' % pq.queue)
		elif event == 'Enable':
			window.enable_debugger()
		elif event == 'Popout':
			# replaces old popout with a new one, possibly with new variables`
			sg.show_debugger_popout_window()
		elif event == 'Debugger':
			sg.show_debugger_window()
		event, values = window2.read(timeout=0)
		if not mes_pq.empty():
			print('mes_pq: %r' % mes_pq.get())
#		await asyncio.sleep(.1)
		counter += 1
#		window['-OUT-'].update(values['-IN-'])

	window.close()

if __name__ == '__main__':
	#	loop = asyncio.new_event_loop()
#	asyncio.set_event_loop(loop)
	loop2 = asyncio.get_event_loop()
#	asyncio.set_event_loop(loop2)
	pq = PriorityQueue(10)
	mes_pq = Queue()
	threading.Thread(target=main_task, args=(pq, mes_pq)).start()
	windoww(pq, mes_pq)
#	threading.Thread(target=windoww).start()
#	asyncio.run(windoww())
#	tasks = [asyncio.Task(main)]
#	loop.create_task(main())
#	loop.run_forever()
#	loop2.create_task(windoww())
#	loop2.run_until_complete(windoww())