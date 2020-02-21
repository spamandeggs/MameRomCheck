# python3.73
# coding=utf-8
'''
Mame Rom Check

Copyright 2020 Jérôme Mahieux

This file is part of Mame Rom Check.

Mame Rom Check is free software: you can redistribute it and/or 
modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

Mame Rom Check is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Mame Rom Check. If not, see http://www.gnu.org/licenses/.
'''

import threading
from threading import active_count
from queue import Queue, SimpleQueue
from time import sleep, perf_counter
import subprocess

class Tasks() :
	def __init__(self,maxtasks=5,eco=False) :
		self.queue = SimpleQueue()	
		self.__status = False
		self.__task = []			# running task ( as threads instance )
		self.__left = []			# list of tasks in queue (tskname,func,args,kwargs)
		self.__done = []			# list of tasks done (tskname,*perf[todo])
		self.__aborted = []			# list of tasks aborted when stop() issued and left items still in queue (tskname,func,args,kwargs)
		self.__stoppending = False	# True when we empty the remaining queue after a task.stop(), doing nothing.
		self.__reports = {}
		self.__polls = []
		self.__pollslatency = 1.0
		self.__pollslast = 0
		self.__eco = eco
		self.__verbose = False
		self.maxtasks = maxtasks
		if not(self.__eco) : self.start()
	
	@property
	def task(self) : 
		tsks = []
		for t in self.__task :
			tsks.append(t.getName())
		return tsks

	@property
	def left(self) : return self.__left
	
	@property
	def done(self) : return self.__done
	
	@property
	def aborted(self) : return self.__aborted
	
	@property
	def eco(self) : return self.__eco
	@eco.setter
	def eco(self,v) : self.__eco = bool(v)
	
	@property
	def maxtasks(self) : return self.__maxtasks-2
	
	@property
	def pollslatency(self) : return self.__pollslatency
	@pollslatency.setter
	def pollslatency(self,v) : self.__pollslatency = int(v)
	
	@property
	def verbose(self) : return self.__verbose
	@verbose.setter
	def verbose(self,v) : self.__verbose = bool(v)
		
	@maxtasks.setter
	def maxtasks(self,v) :
		self.__maxtasks = max(1,v)+2 # main process and task manager are alive, so add 2
	
	@property
	def status(self) :
		return self.__status

	def statusinfo(self) :
		if self.__status : print('tasks manager started and waiting.')
		else : print('tasks manager stopped.')
	
	def start(self) :
		if not(self.__status) :
			if self.__stoppending :
				print('tasks manager is leaving, can\'t start for now.')
			else :
				self.__status = True
				p = threading.Thread(target=self.__queue,name='TaskManager')
				p.start()
		else :
			print('tasks manager already started.')
		
	def stop(self) :
		if self.__stoppending :
			print('tasks manager is already leaving.')
		elif not(self.__status) :
			print('tasks manager already stopped.')
		else :
			self.__stoppending = True

	# task.report(task basename,number of tasks awaited)
	# prepare a train of tasks after the call on can
	# task.info(task basename) to known the current status of
	# these tasks
	def report(self,tskbasename,count=1,poll=False) :
		self.__reports[tskbasename] = {
			'total' : count,
			'count' : 0,
			'start' : -1,
			'time' : -1,
			'poll' : poll,
		}
		if poll :
			self.__polls.append(tskbasename)
	
	def add(self,tskname,func=None,*args,**kwargs) :
		self.queue.put((tskname,func,args,kwargs))
		self.__left.append(tskname)
		if self.__eco and not(self.status) and len(self.__left) == 1 : self.start()
	
	# task.info()
	# task.info(train task basename,rtn)
	# is train task basename is given, returns infos about a train defined by task.report()
	# if rtn is False (default), print information in the console
	# if True, returns a tuple with ( status, tasks done, total tasks, start time, end time )
	def info(self,tskbasename=False,rtn=False) :
		if tskbasename :
			train = "tasks train '%s'"%tskbasename
			if tskbasename in self.__reports :
				rep = self.__reports[tskbasename]
				since = perf_counter()-rep['start']
				if rep['start'] == -1 :
					trainstacli = '%s is waiting for first task'%(train)
					trainsta = 'waiting'
				elif rep['time'] != -1 :
					trainstacli = '%s done in %.3f secs'%(train,rep['time'])
					trainsta = 'done'
				else :
					trainstacli = '%s running since %.3f secs %s/%s'%(train,since,rep['count'],rep['total'])
					trainsta = 'running'
			else :
				trainstacli = '%s does not exist'%(train)
			if rtn : return ( trainsta,rep['count'],rep['total'],since,rep['time'] )
			print(trainstacli)
			
		else :
			self.statusinfo()
			print( 'tasks left    : %s (check : %s)'%(self.queue.qsize(),len(self.__left))) # qsize is reported as non-reliable
			print( 'current tasks : %s'%(','.join(self.task) if self.task else 'None'))
			print(f'total done    : {len(self.__done)}')
			print(f'total aborted : {len(self.__aborted)}')
			print(f'threads       : {active_count()}')

	def __taskwrapper(self,func,tskname,*args,**kwargs) :
		if 'callback' in kwargs : callback = kwargs.pop('callback')
		else : callback = False
		rtn = func(*args,**kwargs)
		self.__done.append((tskname,[rtn]))
		if callback : callback(tskname,rtn)

	def __queue(self) :
		self.statusinfo()
		while self.__status :
			# got something to do
			try :
				args = list(self.queue.get_nowait())
				tskname,func,args,kwargs = args
				tskbasename = tskname.split('.')[0] # for tasks trains
				tskcheck = self.__left.pop(0)
				
				if not(self.__stoppending) :
					if active_count() < self.__maxtasks :
						
						# active_count()-1 rather than -2 : the about to run thread is counted as already running
						if self.__verbose :
							print("run task '%s' (%s/%s tasks)"%(tskname,active_count()-1,self.__maxtasks-2))
							
						# counter of train of tasks
						if tskbasename in self.__reports :
							rep = self.__reports[tskbasename]
							if rep['start'] == -1 : 
								rep['start'] = perf_counter()
								if self.__verbose : self.info(tskbasename)	
							
						# t = Thread(target=lambda q, arg1: q.put(foo(arg1)), args=(que, 'world!'))
						# args.insert(self.returnsqueue)
						# t = threading.Thread(target=lambda q, *args, **kwargs: q.put(func(*args,**kwargs)), name=tskname, args=args, kwargs=kwargs)
						# t = threading.Thread(target=func, name=tskname, args=args, kwargs=kwargs)
						
						if not(args) : args = []
						args = list(args)
						args.insert(0,tskname)
						args.insert(0,func)
						t = threading.Thread(target=self.__taskwrapper, name=tskname, args=args, kwargs=kwargs)
						t.start()
						self.__task.append(t)
						
						while active_count() >= self.__maxtasks :
							sleep(0.25)
					else :
						print('SHOULD NEVER BE HERE !!') # well
				# stop is pending, abort queue
				else :
					self.__aborted.append((tskname,func,args,kwargs))
					if self.__verbose : print('task %s aborted'%(tskname))
			
			# empty queue
			except :
				# print('empty queue, left is %s'%self.__left) # check
				# print('empty queue, task is %s'%self.task)   # check
				if not(self.__task) :
					if self.__stoppending :
						self.__status = False
						self.__stoppending = False
					elif self.__eco : 
						self.__stoppending = True
						if self.__verbose : print('eco mode, ask for stop()')
				else : sleep(0.25)
			
			# task completion check
			if self.__task :
				tasknext = []
				for t in self.__task :
					if t not in threading.enumerate() :
						tskname = t.getName()
						tskbasename = tskname.split('.')[0]
						if self.__verbose : print("task '%s' ended."%tskname)
						# train
						if tskbasename in self.__reports :
							rep = self.__reports[tskbasename]
							rep['count'] += 1
							if rep['count'] == rep['total'] :
								rep['time'] = perf_counter() - rep['start']
							if self.__verbose :
								self.info(tskbasename)
					else :
						tasknext.append(t)
				self.__task = tasknext
			
			if self.__polls and perf_counter() - self.__pollslast >= self.__pollslatency :
				pollnext = []
				for tskbasename in self.__polls :
					rep = self.__reports[tskbasename]
					trainsta,count,total,since,duration = self.info(tskbasename,True)
					if trainsta == 'done' :
						func = rep['poll']
						t = threading.Thread(target=func, name='tasksTrain.%s.%s'%(tskbasename,trainsta), args=(tskbasename,trainsta,count,total,since,duration) )
						t.start()
						rep['poll'] = False
					else : pollnext.append(tskbasename)
				self.__pollslast = perf_counter()
				self.__polls = pollnext

		self.statusinfo()
		

# inst0 = Something('instance 0')
# inst1 = Something('instance 1')
# inst2 = Something('instance 2')

# t = Tasks()
# t.add('task0',inst0.work1,(1,2,3))
# t.add('task1',inst1.work1,'hey')
# t.add('task2',inst2.work2,name='james')
# t.add('task3',inst2.work2,name='james')
# t.add('task4',inst2.work2,name='james')
# t.add('task5',inst2.work2,name='james')
# t.add('task6',inst2.work2,name='james')
# t.add('task7',inst2.work2,name='james')
# t.add('task8',inst2.work2,name='james')
# t.add('task9',inst2.work2,name='james')
# t.add('task10',inst2.work2,name='james')

# sleep(1)
# t.info()

# for w in threading.enumerate() :
	# print(t.getName(),t.is_alive(),t)

