import threading
from threading import active_count
from queue import SimpleQueue
from time import sleep, perf_counter
import subprocess


# class Something() :
	# def __init__(self,name) :
		# self.name = name
	
	# def work1(self,*args,**kwargs) :
		# # print('%s is doing work1'%self.name)
		# # print(args)
		# # print(kwargs)
		# sleep(3.0)
		# # print('%s work1 finished.'%self.name)
		
	# def work2(self,*args,**kwargs) :
		# # print('%s is doing work2'%self.name)
		# # print(args)
		# # print(kwargs)
		# sleep(5.0)
		# # print('%s work2 finished.'%self.name)
	
class Tasks() :
	def __init__(self,maxtasks=5) :
		self.queue = SimpleQueue()	
		self.__status = False
		self.__task = []
		self.__check = []
		self.__reports = {}
		self.__polls = []
		self.__pollslatency = 1.0
		self.__pollslast = 0
		self.__verbose = False
		self.maxtasks = maxtasks
		self.start()
	
	@property
	def task(self) : return self.__task
	
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
			self.__status = True
			p = threading.Thread(target=self.__queue,name='TaskManager')
			p.start()
		else :
			print('tasks manager already started.')
		
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
		
	def stop(self) :
		if self.__status :
			self.__status = False
			self.add('stop')
		else :
			print('tasks manager already stopped.')
		
	def add(self,tskname,func=None,*args,**kwargs) :
		self.queue.put((tskname,func,args,kwargs))
		self.__check.append(tskname)
	
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
			print('%s tasks in queue'%(self.queue.qsize())) # qsize is reported as non-reliable
			print('%s tasks in queue check'%(len(self.__check)))
			print('current tasks : %s'%(','.join(self.task) if self.task else 'None'))
			print('threads : %s'%(active_count()))
		
	def __queue(self) :
		self.statusinfo()
		running = []
		while self.__status :
			# got something to do
			try :
				args = list(self.queue.get_nowait())
				# print(args)
				tskname,func,args,kwargs = args
				tskbasename = tskname.split('.')[0]
				# print(tskname,func,args,kwargs)
				tskcheck = self.__check.pop(0)
				# print('next task : %s'%(tskname))
				# print('check : %s'%tskcheck)
				
				if tskname not in ['stop'] and func :
					if active_count() < self.__maxtasks :
						
						# active_count()-1 tather than -2 : the about to run thread is counted as if it was already running
						if self.__verbose :
							print("run task '%s' (%s/%s tasks)"%(tskname,active_count()-1,self.__maxtasks-2))
							
						# counter of train of tasks
						if tskbasename in self.__reports :
							rep = self.__reports[tskbasename]
							if rep['start'] == -1 : 
								rep['start'] = perf_counter()
							
								if self.__verbose : self.info(tskbasename)
								# print("%s tasks train %s/%s"%(tskbasename,rep['count'],rep['total']))							
							
						t = threading.Thread(target=func, name=tskname, args=args, kwargs=kwargs)
						self.__task.append(tskname)
						running.append(t)
						t.start()
						
						
						# if active_count() >= self.__maxtasks :
							# print('wait...')
						while active_count() >= self.__maxtasks :
							sleep(0.25)

			# empty queue
			except :
				sleep(0.25)
			
			# task completion check
			if running :
				runningnext = []
				tasknext = []
				for t in running :
					if t not in threading.enumerate() :
						tskname = t.getName()
						tskbasename = tskname.split('.')[0]
						if self.__verbose : print("task '%s' ended."%tskname)
						if tskbasename in self.__reports :
							rep = self.__reports[tskbasename]
							rep['count'] += 1
							if rep['count'] == rep['total'] :
								rep['time'] = perf_counter() - rep['start']
							if self.__verbose :
								self.info(tskbasename)
								# print("%s tasks train done in %s secs, %s/%s"%(tskbasename,ttime,rep['count'],rep['total']))
									
						
					else :
						runningnext.append(t)
						tasknext.append(t.getName())
				running = runningnext
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

