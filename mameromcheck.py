# python373
import os
from tasks import *
# import threading
# from threading import active_count as activetasks
from xml.dom import minidom
from collections import OrderedDict as odict
import weakref

from mf3parse import mfl2dict, mfl2Odict, dict2mfl

from version import version, lastrev

def getlocales(locale) :
	loc = {}
	loc.update(locales['en'])
	if locale in list(locales.keys()) :
		loc.update(locales[locale])
	else :
		print('locale file %s missing, use english.'%(locale))
	return loc

		
def guessVersion(pth) :
	os.chdir(os.path.dirname(pth))
	runmame = [ pth, '-help' ]
	MAME = subprocess.run(runmame, capture_output=True)
	os.chdir(mrcpath)
	
	nmen = os.path.basename(pth)
	nmev = 'unknown'
	
	if MAME.returncode == 0 :
		try :
			stdout = MAME.stdout.decode().split('\r\n')[0]
			if stdout[:5] == 'MAME ' :
				nmen = ' '.join(stdout.split(' ')[:2]).title()
				nmev = stdout.split(' ')[1]
			elif stdout[:9] == 'M.A.M.E. ' :
				nmen = ' '.join(stdout.split(' ')[:2])
				nmev = stdout.split(' ')[1]
			else :
				print('not an official mame build :')
				print('STDOUT')
				print(MAME.stdout.decode())
				print('STDERR')
				print(MAME.stderr.decode())
		except :
			print('failed parsing %s -help :'%(nmen))
			print('STDOUT')
			print(MAME.stdout.decode())
			print('STDERR')
			print(MAME.stderr.decode())
			
	else :
		print('returned an error : %s'%MAME.returncode)
		print('STDOUT')
		print(MAME.stdout.decode())
		print('STDERR')
		print(MAME.stderr.decode())
		
	return nmen, nmev

# pth is a string representing a path
# when path as input (load from file) set system separators : pathconform(pth)
# when path to output (save, socket etc) set 'nix separators : pathconform(pth,True)
# delete trailing seps in any case
def pathconform(pth,save=False) :
	if save :
		pth = pth.replace(os.sep,'/')
	else :
		pth = pth.replace('/',os.sep).replace('\\',os.sep).strip()
	while pth[-1] == os.sep : pth = pth[:-1]
	return pth

class Romset() :

	def __setsize(self,v) : self.__size = int(v)
	def __setcomment(self,v) : self.__comment = v
	def __settype(self,v) : self.__type = v
	# tailsize appears in 7z header fields when 
	# 'WARNINGS:\nThere are data after the end of archive'
	def __settailsize(self,v) : self.__tailsize = int(v)
	# available header keys :
		# Folder
		# Size
		# Packed Size
		# Modified
		# Created
		# Accessed
		# Attributes
		# Encrypted
		# Comment
		# CRC
		# Method
		# Characteristics
		# Host OS
		# Version
		# Volume Index
		# Offset
	__sevenzromkeys = [
		'Encrypted',
		'Comment',
		'CRC',
		'Size',
		'Modified',
		'Created',
		'Accessed'
	]
	__sevenzknownignore = [
		'WARNINGS:',
		'',
	]
	__sevenzknownwarnings = [
		'There are data after the end of archive'
	]
	
	def __init__(self,name,**kwargs) :
		self.__name = name.split('.')[0] # name arg. has an archive extension
		self.__path = pathconform(os.path.join(kwargs['path'],name)) # with file
		self.__file = name
		self.__description = '-'
		self.__roms = {}
		self.__crcs = {}
		self.__mame = {}
		self.__romscount = '-'
		self.__size = '-'
		self.__comment = ''
		self.__type = ''
		self.__tags = ''
		# warnings/errors fields
		self.__tailsize = '-'
		self.__warnings = '-'
		self.__warningsmessages = []
		self.__error = '-'
		## todo depend on active mame release
		self.__status = '-' # all system go (driver good, romsetmatch True, playable True)
		self.__driver = '-' # XML driver tag
		self.__rommatch = '-' # roms in XML = roms in romset file
		self.__playable = '-' # once driver good, rommatch True : - verifyrom

		# todo : like to @class or @staticmethod but this does not work
		self.__sevenzlookup = {
			'Physical Size' : self.__setsize,
			'Comment' : self.__setcomment,
			'Type' : self.__settype,
			'Tail Size' : self.__settailsize
		}
	
	@property
	def name(self) : return self.__name
	@property
	def path(self) : return self.__path
	@property
	def file(self) : return self.__file
	@property
	def roms(self) : return self.__roms
	@property
	def crcs(self) : return self.__crcs
	@property
	def romscount(self) : return self.__romscount
	@property
	def size(self) : return self.__size
	@property
	def comment(self) : return self.__comment
	@property
	def type(self) : return self.__type
	@property
	def tags(self) : return self.__tags
	@tags.setter
	def tags(self,v) : self.__tags = v
	@property
	def tailsize(self) : return self.__tailsize
	@property
	def warnings(self) : return self.__warnings
	@property
	def warningsmessages(self) : return self.__warningsmessages
	@property
	def error(self) : return self.__error


	@property
	def mame(self) :
		# if self.__mame == {} : print('nothing yet.')
		return self.__mame
		
	## returned values of the following differ depending on 
	## the active Mame release
	# romset romname:status in this mame
	# xml romname: crc,size,match (only rom which are not bios, and not parent)
	@property
	def description(self) : return self.__getMameProp('description')
	@property
	def status(self) : return self.__getMameProp('status')
	@property
	def driver(self) : return self.__getMameProp('driver')
	@property
	def rommatch(self) : return self.__getMameProp('rommatch')
	@property
	def playable(self) : return self.__getMameProp('playable')
	
	def __getMameProp(self,propname) :
		if cfg.activeMame :
			if cfg.activeMame.version in self.__mame :
				return self.__mame[cfg.activeMame.version][propname]
		return '-'
	
	def updateFromConfig(self,rsetconf) :
		self.__description = rsetconf['description'] # last descr red from a verify(mameversion)
		self.__roms = rsetconf['roms']
		self.__crcs = rsetconf['crcs']
		self.__romscount = rsetconf['romscount']
		self.__size = rsetconf['size']
		self.__comment = rsetconf['comment']
		self.__type = rsetconf['type']
		self.__tailsize = rsetconf['tailsize']
		self.__warnings = rsetconf['warnings']
		self.__warningsmessages = rsetconf['warningsmessages']
		self.__error = rsetconf['error']
		self.__mame = rsetconf['mame']
		
		
	# populate a romset with general infos, roms,
	# rom infos, and possibly errors/warnings
	# use 7z.exe
	def populate(self) :
		# print('-'*50)
		# print('getRoms %s'%(self.name))
		runcrc = [ pth_7z ]
		runcrc.extend([ 'l', '-slt', self.__path ])
		CRCRAW = subprocess.run(runcrc,timeout=10,capture_output=True)
		showstd = False
		self.__warnings = 0
		self.__error = 0
		if CRCRAW.returncode == 0 :
			rawlines = CRCRAW.stdout.decode().split('\r\n')
			debug = False
			# header parse
			i = rawlines.index('--') + 1
			while rawlines[i] != '----------' :
				fld = rawlines[i].split(' = ')
				if len(fld) == 2 :
					k,v = fld
					if k in list(self.__sevenzlookup.keys()) :
						self.__sevenzlookup[k](v)
					elif k != 'Path' : 
						print('UNKNOWN ZIP KEY IN %s : %s = %s'%(self.__name,k,v))
				elif fld != [''] :
					fld = fld[0]
					if fld in Romset.__sevenzknownwarnings :
						self.__warnings += 1
						self.__warningsmessages.append(fld)
					elif fld not in Romset.__sevenzknownignore :
						print('UNKNOWN MESSAGE IN %s HEADER : %s'%(self.__name,fld))
						debug = True
				i+=1

			if debug :
				print('STDOUT')
				print(CRCRAW.stdout.decode())
			
			# roms
			i += 1
			j = i + rawlines[i:].index('')
			
			rll = len(rawlines)-1
			while i < rll :
				keyfound = False
				zipinfos = {}
				if debug : print('* %s > %s'%(i,j))
				for li,line in enumerate(rawlines[i:j]) :
					if debug : print('%s/%s %s'%(i+li,rll,line))
					fld = line.split(' = ')
					if len(fld) == 2 :
						k,v = fld
						if k == 'Path' :
							# print(' %s'%v)
							self.__roms[v] = {}
							keyfound = v
						elif k in Romset.__sevenzromkeys :
							# print('  %s %s'%(k,v))
							zipinfos[k.lower()] = v.lower() if k in ['CRC'] else v
					else :
						fld = fld[0]
						print('MESSAGE WHILE PARSING %s ROMS : %s'%(self.__name,fld))
						debug = True
				if keyfound :
					self.__roms[keyfound].update(zipinfos)
					# for k,v in self.__roms[keyfound].items() :
						# self.__crcs[v['crc']] = k
					self.__crcs = { v['crc'] : k for k,v in self.__roms.items() }
				else :
					print('rom name not found ?')
					print(' line : %s'%(line))
					print(' infos : %s'%(zipinfos))
				i = j + 1
				j = i + rawlines[i:].index('')
				if j == i :
					break
					debug = True
			if debug :
				for li,line in enumerate(rawlines[i:]) :
					if line[:10] == 'Warnings: ' :
						if self.__warnings != int(line[9:]) :
							print('WARNING COUNT CONFLICT header %s, Warnings: last line %s'%(self.__warnings,int(line[9:])))
					elif line not in [''] :
						print('UNKNOWN LINE IN %s: %s/%s %s'%(self.__name,i+li,rll,line))

			if self.__warnings != 0 :
				pass
				# print('rom %s has %s warnings'%(self.__name,self.__warnings))
			else :
				self.__warnings = 0
			
			self.__romscount = len(self.__roms)
			self.__error = 0
			
			# print('%s has %s roms'%(self.name,self.romscount))
		else :
			self.__error = 1
			print('7Z MAIN ERROR %s WITH %s'%(CRCRAW.returncode,self.__name))
			print('STDERR')
			print(CRCRAW.stderr.decode())
	
	def checkxml(self,mameExeName=0) :
		mameInst = Mame.get(mameExeName)
		if mameInst :
			mameInst.verify(self)

	def __verify(self,mameExeName=0) :
		# p = Process(target=self.__verify, args=(self.name,mameExeName,))
		
		# p = threading.Thread(target=test, args=('un','deux'))
		p = threading.Thread(target=self.__verify, args=('mameExeName',))
		p.start()
		# p.join()
		return p
	
	# mame -listxml self.name
	# generates self.mame[version] fields
	def verify(self,mameExeName=0) :
		mameInst = Mame.get(mameExeName)
		if mameInst :
			compat = self.__mame[mameInst.version] = {
				'romset':{},
				'xml':{},
				'description':'-',
				'status':'-',
				'driver':'-',
				'rommatch':'-',
				'playable':'-',
			}
			romsetxmlstatuscode, stdout, stderr = mameInst.run(cmd=['-listxml',self.name])
			roms = []
			parentroms = {}
			
			# romset is in the mame XML list
			if romsetxmlstatuscode == 0 :
			
				romsetdata = stdout.decode()
				romsetdom = minidom.parseString(romsetdata)
				
				machines = romsetdom.getElementsByTagName('machine')
				for i in range(machines.length) :
					if machines.item(i).getAttribute('name') == self.name :
						romsetdescription = machines.item(i).getElementsByTagName('description')[0].childNodes[0].data
						if romsetdescription == '' : romsetdescription = '[ no description ]'
						romsetxmlstatus = machines.item(i).getElementsByTagName('driver')[0].getAttribute('status')
						if romsetxmlstatus != 'good' : romsetxmlstatuscode = 1
						for rom in machines.item(i).getElementsByTagName('rom') :
							# roms required from the set have no merge attribute
							if rom.getAttribute('merge')== '' :
								# roms[rom.getAttribute('name')] = (rom.getAttribute('crc').lower(),rom.getAttribute('size'))
								# roms.append( (rom.getAttribute('name'),rom.getAttribute('crc').lower(),rom.getAttribute('size')) )
								namexml, crcxml, sizexml = (rom.getAttribute('name'),rom.getAttribute('crc').lower(),rom.getAttribute('size'))
								compat['xml'][namexml] = { 'crc' : crcxml , 'size' : sizexml }
								
							# Mame will check ancestors/bios to find those
							else :
								# print('Parent %s'%rom.getAttribute('name'))
								parentroms[rom.getAttribute('name')] = rom.getAttribute('crc').lower()
							# todo : si 'bios' attr, lire > TagName 'biosset' name="bios_value"
						break
			
			# error: M.A.M.E. v0.37 'unknown option -listxml\nerror while parsing cmdline'
			# if romsetxmlstatuscode == 1 :
			
			# stderr 'Unknown system \...'
			elif romsetxmlstatuscode == 5 :
				romsetxmlstatus = "set not found in mame list"
				romsetdescription = ''
			
			else :
				# print('UNKNOWN XML STATUS RETURN CODE : %s'%romsetxmlstatuscode)
				romsetxmlstatus = 'unknown'
				romsetdescription = ''
				# print('STDOUT')
				# print(stdout.decode())
				# print('STDERR')
				# print(stderr.decode())
			
			compat['description'] = romsetdescription
			compat['driver'] = romsetxmlstatus
						
			## for each rom (with no 'merge' xml key)
			# perfect match : right name and crc
			# crc match  : wrong rom name, right crc
			# name match : right rom name, different crc
			# missing : no rom/crc match
			if self.roms == {} : self.populate()
			setmatch = True
			__xmlcrcs = {} # temp store crc found in xml, that were found in romset but under a different rom name
			
			for namexml, v in compat['xml'].items() :
				rommatch = 'ok'
				# print('*',romname,crc,romname in self.roms)
				if namexml in self.roms :
					# print(crc,self.roms[romname]['crc'])
					if v['crc'] != self.roms[namexml]['crc'] :
						rommatch = 'bad_crc:%s'%self.roms[namexml]['crc']
						setmatch = False
				elif v['crc'] in self.__crcs :
					rommatch = 'bad_name:%s'%(self.__crcs[v['crc']])
					__xmlcrcs[v['crc']] = namexml
					setmatch = False
				else :
					rommatch = 'missing'
					setmatch = False
				compat['xml'][namexml]['match'] = rommatch
				
				# print(namexml, v['crc'], compat['xml'][namexml]['match'])
				
			for name, v in self.roms.items() :
				rommatch = 'ok'
				if name in compat['xml'] :
					if compat['xml'][name]['match'] == 'ok' :
						rommatch = 'ok'
					else :
						rommatch = 'bad_crc:%s'%compat['xml'][name]['crc']
				elif v['crc'] in __xmlcrcs :
					rommatch = 'bad_name:%s'%__xmlcrcs[v['crc']]
				else :
					rommatch = 'unused'
				compat['romset'][name] = rommatch
					
				# print(name, v['crc'], compat['romset'][name])
			
			compat['rommatch'] = '%s/%s'%(len(self.roms),len(roms))
			
			# print('descr  : %s'%self.description)
			# print('driver : %s'%self.driver)
			# print('match  : %s'%self.rommatch)
			# print('roms   : %s'%(' '.join(list(roms.keys()))))
			# print('return code  : %s'%romsetxmlstatuscode)
			
			# retours / cas d'erreurs
			# mslug		returncode=0
			# notexist	returncode=5		
			# antiairc	returncode=0
			# 2020bbh	returncode=2		stderr xxxxxxxx.yy ROM NEEDS REDUMP
			
			# mame64.exe -listxml mslug > mslug.xml
			# mslugxml ="D:\documents\projets\emulateurs\mame\scripts\mslug.xml"
			# xmlfile = open(mslugxml,encoding='utf8',error='ignore')
			# data = minidom.parse(xmlfile)
			# print(,,,)
			# return (romsetdescription,romsetxmlstatus,romsetxmlstatuscode,roms,parentroms)
	
	def run(self,mameExeName=0) :
		mameInst = Mame.get(mameExeName)
		if mameInst :
			mameInst.run(self)
			
class MameCommon() :

	def __new__(cls,path,name='',**kwargs) :
		if type(name) != str :
			print(cfg.txt['errorArgNotString']%'name')
			return
		name = name.strip()
		if type(path) != str :
			print(cfg.txt['errorArgNotString']%'path')
			return
		path = path.strip()
		if kwargs['isfile'] and not(os.path.isfile(path)) :
			print(cfg.txt['errorPathWrong'])
			return
		elif not(kwargs['isfile']) and not(os.path.isdir(path)) :
			print(cfg.txt['errorPathWrong'])
			return
		# print(cls,cls.getall('name'))
		pths = [ n.lower() for n in cls.getall('path') ]
		pthtest = pathconform(path).lower()
		# print('* %s'%path)
		# print(pths)
		# print(path in pths)
		if pthtest in pths :
			print(cfg.txt['errorPathExistRomdir'])
			return pths.index(pthtest)
			# ?? with Mame.readonfig as a caller,
			# ?? Romdir.get() changes the name of the existing dir
			# return Romdir.get(pths.index(pthtest)) 
			
		names = [ n.lower() for n in cls.getall('name') ]
		if name != '' and name.lower() in names :
			print(cfg.txt['errorNameExistRomdir'])
			return
		else :
			return super().__new__(cls)

	def __init__(self,pth,name='',**kwargs) :
		pth = pathconform(pth)
		self.__path = pth
		self.__name = name
		if self.__name == '' :
			print(cfg.txt['warningNameEmptyMameApi'])
	
	@property
	def name(self) : return self.__name
	
	# member names must be unique or 
	@name.setter
	def name(self,name) :
		if type(name) != str : name = repr(name).strip()
		if name in ['','0'] :
			self.__name = ''
			print(cfg.txt['errorNameEmptyMameApi'])
			return
		names = [ n.lower() for n in self.getall('name') ]
		if name not in names :
			self.__name = name
		else :
			print(cfg.txt['errorNameExistMame'])
		
	@property
	def path(self) : return self.__path
		
	@path.setter
	def path(self,pth) :
		if type(pth) != str :
			print(cfg.txt['errorArgNotString']%pth)
		elif not(os.path.isfile(pth)) :
			print(cfg.txt['errorPathWrong'])
		else :
			self.__path = pth
		# todo : find a way to recognize a Mame binary
		# crc comply with prebuilds only I guess,
		# investigate existing other files in the folder ?
		
	# @version.deleter
	# def version(self) :
		# print("can't do that.")

	@classmethod
	def getActive(cls) :
		pass
		
	def activate(self) :
		cfg.activeMame = self
		
	@classmethod
	def get(cls,id,members,what=False) :
		inst = None
		if type(id) == str :
			for inst in members :
				if inst.name == id : break
		elif type(id) == int and id >=0 and id < len(members) :
			inst = members[id]
		if not(inst) : return None
		
		if not(what) : return inst
		elif what == 'item' : return {inst.name:inst}
		elif what == 'name' : return inst.name
		elif what in ['name','path','version'] : return getattr(inst,what)
		return None
		
	@classmethod
	def getall(cls,members,what=False) :
		if not(what) : return members
		elif what == 'item' : 
			rtn = odict()
			for inst in members :
				rtn[inst.name] = inst
		elif what in ['name','path','version'] and hasattr(cls,what):
			rtn = []
			for inst in members :
				rtn.append(getattr(inst,what))
		else : return None
		return rtn
	
	@classmethod
	def remove(cls,id,members) :
		inst = cls.get(id,members)
		print(inst)
		print(cls)
		print(isinstance(inst,cls))
		if isinstance(inst,cls) :
			if cfg.activeMame == inst :
				cfg.activeMame = None
			del(members[members.index(inst)])
			return True
		else :
			print(cfg.txt['errorArgNotExist'])
			return False
	
	# todo : print formatter with columns etc for subclass list() results
	# @classmethod
	# def list(cls) :
	
class Mame(MameCommon) :
	
	__members = []
	# __dict__ = {} __slots__ todo, learn
	
	# instance creation is forbidden if the given path is wrong
	# and other things
	# 'path' written like that just for error message if missing
	def __new__(cls,path,name='',version='',**kwargs) :
		return super().__new__(cls,path,name,isfile=True)

	def __init__(self,pth,name='',version='',**kwargs) :
		super().__init__(pth,name,**kwargs)
		# print('--mame--')
		# print('self',self)
		# print(pth)
		# print(name)
		# print('---------')
		self.__version = version if type(version) == str else ''
		self.__romdirs = []
		# if self.name :
		Mame.__members.append(self)
		# Mame.members.append(weakref.ref(self))
		self.readconfig()
		
	@property
	def version(self) : return self.__version
	
	@property
	def romdirs(self) : return self.__romdirs
		
	@version.setter
	def version(self,name) :
		self.__version = name
	
	@classmethod
	def get(cls,id,what=False) :
		return super().get(id,cls.__members,what=False)
	
	@classmethod
	def getall(cls,what=False) :
		return super().getall(cls.__members,what)
	
	@classmethod
	def list(cls) :
		for inst in cls.__members :
			print(inst.name,inst.version,inst.path)
	
	@classmethod
	def remove(cls,id) :
		rtn = super().remove(id,cls.__members)
		
	def run(self,rom=False,cmd=False) :
		capoutput = False
		os.chdir(os.path.dirname(self.path))
		runmame = [ self.path ]
		if rom :
			# todo : if romdir given...
			# if not(isinstance(rom,Romset)) :
				# if dir :
					# if not(isinstance(dir,Romdir)) :
				# else 
				# rom = 
			# todo : compare path see if its locl : if yes, remove .zip
			runmame.append(rom.path)
			
		elif cmd :
			runmame.extend(cmd)
			capoutput = True
		# print(' '.join(runmame))
		MAME = subprocess.run(runmame,capture_output=capoutput)
		
		return MAME.returncode, MAME.stdout, MAME.stderr
		
	# get used rom folders from the ini file
	# populate self.__romdirs
	def readconfig(self,ininame="mame.ini") :
		pth = os.path.join(os.path.dirname(self.path),ininame)
		inifile=open(pth,'r',encoding='utf8')
		inilines = inifile.readlines()
		inifile.close()
		rpth = False
		for l in mfl2dict(inilines)[0] :
			if l[:7] == 'rompath' : rpth = l ; break
		if rpth :
			romdirspth = rpth[7:].strip().replace('"','').replace("'","").split(';')
			i=0
			for rdpth in romdirspth :	
				rdpth = rdpth.strip()
				if rdpth.lower() == 'roms' :
					rdpth = os.path.join(os.path.dirname(self.path),'roms')
				# print('* %s romdir :'%('%s.%02d'%(self.name,i)))
				rd = Romdir(rdpth,'%s.%02d'%(self.name,i))
				# if type(rd) == int : print(Romdir.get(rd).name) # already existing romdir
				# else : print(rd.name)
				if isinstance(rd,Romdir) : i+=1
				else : rd=Romdir.get(rd)
				self.__romdirs.append(rd)

	def guessVersion(self) :
		nmen, nmev = guessVersion(self.path)
		if self.version == '' or nmev != 'unknown' : self.version = nmev
		if self.name == '' : self.name = nmen

class Romdir(MameCommon) :
	
	__members = []
	
	def __new__(cls,path,name='',*args,**kwargs) :
		return super().__new__(cls,path,name,isfile=False)
		
	def __init__(self,pth,name='',*args,**kwargs) :
		super().__init__(pth,name,**kwargs)
		
		self.__romset = odict()
		Romdir.__members.append(self)
		
		self.populate(args)
	
	# @property
	# def romsets(self,filter=False) : 
		# return self.__romsetnames
		
	@property
	def romset(self) :
		return self.__romset
		
	@romset.setter
	def romset(self,name) :
		pass
	
	def getromsets(self,filter=False) : 
		if not(filter) : return self.__romsetnames
		rtn = []
		for romsetname in self.__romsetnames :
			if filter in romsetname :
				rtn.append(romsetname)
		return rtn
	
	@classmethod
	def get(cls,id,what=False) :
		return super().get(id,cls.__members,what=False)

	@classmethod
	def getall(cls,what=False) :
		return super().getall(cls.__members,what)
		
	@classmethod
	def list(cls) :
		for inst in cls.__members :
			print(inst.name,inst.path)

	@classmethod
	def remove(cls,id) :
		rtn = super().remove(id,cls.__members)

	# get infos about romsets in this dir
	# create Romset instance
	def populate(self,knowfields=None) :
		romsets = self.__dirzip()
		
		currentromsets = len(self.__romset)
		newromsets = []
		missingromsets = []
		for rsetname,r in romsets :
			# already known romset
			if rsetname in self.__romset and r == self.__romset[rsetname].file :
				self.__romset[rsetname].tags = ''
			else :
				newromsets.append(rsetname)
				rset = Romset(r,path=self.path)
				self.__romset[rset.name] = rset
		
		for rsetname,r in self.__romset.items() :
			if (rsetname,r.file) not in romsets :
				missingromsets.append(rsetname)
				
		if currentromsets != 0 :
			if len(newromsets) :
				print('populate() %s/%s romsets added.'%(len(newromsets),len(romsets)))
				for rsetname in newromsets :
					print(rsetname)
					self.__romset[rsetname].tags = 'new'
			if len(missingromsets) :
				print('populate() %s romsets are missing.'%(len(missingromsets)))
				for rsetname in missingromsets :
					print(rsetname)
					self.__romset[rsetname].tags = 'missing'
		
		# when populate() is called from cfg,
		# it inputs romset informations
		if knowfields : 
			print('knowfields',type(knowfields),len(knowfields))
			print(len(knowfields[0]['romsets']))
			romsetsfields = knowfields[0]['romsets']
			for rsetname,rsetconf in romsetsfields.items() :
				if rsetname in self.__romset :
					self.__romset[rsetname].updateFromConfig(rsetconf)
				else :
					print('MISSING !',rsetname,r)
					
	def __dirzip(self) :
		romsets = []
		files=os.listdir(self.path)
		for r in files :
			if '.' in r and r.split('.')[-1] in zipformats :
				romsets.append((r.split('.')[0],r))
		return romsets

	# verify() each romset of the dir with the given mame release
	def verify(self,mameExeName=0) :
		task.report('verify',len(self.romset),self.__isdone)
		for rsetname, rset in self.romset.items() :
			task.add('verify.%s'%rsetname,rset.verify,mameExeName)
	
	def __isdone(self,*args) :
		tskbasename,trainsta,count,total,since,duration = args
		print('verified %s romsets in %.3f secs.'%(count,duration))

class Config() :
	def __init__(self,name='default',**kwargs) :
		global version
		self.name = name if type(name) == str else 'default'
		self.file = self.name+'.tab'
		self.version = version
		self.locale = 'en'
		self.txt = locales[self.locale]
		self.cache = os.path.join(pth_mrc,'cache',self.name)
		self.__activeMame = None
		self.__activeRomdir = None
		
	@property
	def activeMame(self) :
		return self.__activeMame
		
	@property
	def activeRomdir(self) :
		return self.__activeRomdir
	
	@activeMame.setter
	def activeMame(self,inst) :
		if isinstance(inst,Mame) or inst == None : self.__activeMame = inst
	
	@activeRomdir.setter
	def activeRomdir(self,inst) :
		if isinstance(inst,Romdir) or inst == None : self.__activeRomdir = inst
		
	def load(self) :
		confpath = os.path.join(os.getcwd(),'conf',self.file)
		if not(os.path.isfile(confpath)) : self.save()
			
		cfgfile = open(confpath,encoding='utf8')
		cfglines = cfgfile.readlines()
		cfgfile.close()
		cfg = mfl2Odict(cfglines)[0]
		
		if 'locale' in cfg :
			self.locale = cfg.pop('locale')
			self.txt = getlocales(self.locale)
		
		# read dirs first in order to keep user names :
		# Mame.init() creates romdirs defined in mame.ini
		# with predefined names. it wont create if path already exist
		romdirsDict = cfg.pop('romdirs')
		for k,v in romdirsDict.items() :
			Romdir(v['path'],k,v)
			
		mameExesDict = cfg.pop('mameExes')
		for k,v in mameExesDict.items() :
			Mame(v['path'],k,v['version'])


		del(mameExesDict)
		del(romdirsDict)
		
		if not(os.path.isdir(self.cache)) :
			os.makedirs(self.cache)
	
	def save(self) :
		print('saving conf %s'%self.file)
		mameExesDict = odict()
		romdirsDict = odict()
		for inst in Mame.getall() :
			if inst.name != '' :
				print(inst.name)
				mameExesDict[inst.name] = odict({
					'version':inst.version,
					'path':pathconform(inst.path,save=True)
				})
		romfields = ["path",
			"file",
			"description",
			"roms",
			"crcs",
			"romscount",
			"size",
			"comment",
			"type",
			"tailsize",
			"warnings",
			"warningsmessages",
			"error",
			"mame",]
		for inst in Romdir.getall() :
			if inst.name != '' :
				
				romsetsDict = {}
				for rname,rset in inst.romset.items() :
					romsetsDict[rname] = {}
					for fld in romfields :
						romsetsDict[rname][fld] = getattr(rset,fld)
						
				romdirsDict[inst.name] = odict({
					'path':pathconform(inst.path,save=True),
					'romsets':romsetsDict
				})
		cfg = odict({
			'version' : self.version,
			'locale' : self.locale,
			'mameExes' : mameExesDict,
			'romdirs' : romdirsDict
		})
		
		cfglines = dict2mfl(cfg)
		cfgpath = os.path.join(pth_mrc,'conf',self.file)
		print('in path %s'%cfgpath)
		if not(os.path.isdir(os.path.dirname(cfgpath))) :
			os.makedirs(os.path.dirname(cfgpath))
		
		cfgfile = open(cfgpath,'w',encoding='utf8')
		for l in cfglines : cfgfile.write(l)
		cfgfile.close()

def checkxml(romsetname) :

	runmame = [ os.path.join(pth_mame,mame_exe) ]
	
	runmame.extend([ '-listxml', romsetname ])
	MAME = subprocess.run(runmame,timeout=10,capture_output=True)
	romsetxmlstatuscode = MAME.returncode
	roms = {}
	
	# rom is here, in the list
	if MAME.returncode == 0 :
	
		# print('STDOUT')
		# print(MAME.stdout.decode())
		romsetdata = MAME.stdout.decode()
		romsetdom = minidom.parseString(romsetdata)
		# print('returncode')
		# print(MAME.returncode)
		# print('STDERR')
		# print(MAME.stderr.decode())
		machines = romsetdom.getElementsByTagName('machine')
		for i in range(machines.length) :
			if machines.item(i).getAttribute('name') == rset.split('.')[0] :
				romsetdescription = machines.item(i).getElementsByTagName('description')[0].childNodes[0].data
				if romsetdescription == '' : romsetdescription = '[ no description ]'
				romsetxmlstatus = machines.item(i).getElementsByTagName('driver')[0].getAttribute('status')
				if romsetxmlstatus != 'good' : romsetxmlstatuscode = 1
				for rom in machines.item(i).getElementsByTagName('rom') :
					roms[rom.getAttribute('name')] = rom.getAttribute('crc')
				break
				
	# stderr 'Unknown system \...'
	elif MAME.returncode == 5 :
		romsetxmlstatus = "missing"
		romsetdescription = ''
	
	# retours / cas d'erreurs
	# mslug		returncode=0
	# notexist	returncode=5		
	# antiairc	returncode=0
	# 2020bbh	returncode=2		stderr xxxxxxxx.yy ROM NEEDS REDUMP
	
	# mame64.exe -listxml mslug > mslug.xml
	# mslugxml ="D:\documents\projets\emulateurs\mame\scripts\mslug.xml"
	# xmlfile = open(mslugxml,encoding='utf8',error='ignore')
	# data = minidom.parse(xmlfile)
	return (romsetdescription,romsetxmlstatus,romsetxmlstatuscode,roms)

def verifyrom() :
	romset = {}
	for rset in romsetslist :
		
		if rset[-4:] == '.zip' : romsetname = rset[:-4]
		else : romsetname = rset
		
		romsetdescription,romsetxmlstatus,romsetxmlstatuscode,roms = checkxml(romsetname)
		print(romsetxmlstatuscode,type(romsetxmlstatuscode))
		if romsetxmlstatuscode == 0 :
			romsetstatus, romsetstatuscode = rungame(romsetname)
		else :
			if not(os.path.isfile(os.path.join(pth_roms,romsetname+'.zip'))) :
				romsetstatus = 'romset file not found'
				romsetstatuscode = 1
			else :
				romsetstatus = ''
				romsetstatuscode = 0
		
		print(romsetname,romsetdescription,romsetxmlstatus,romsetxmlstatuscode,romsetstatus,romsetstatuscode)
		
		# res.append([romsetname,romsetdescription,romsetxmlstatus,str(romsetxmlstatuscode),romsetstatus,str(romsetstatuscode)])
		romset[romsetname] = {
			'description':romsetdescription,
			'driver':romsetxmlstatus,
			'file':romsetstatus,
			'roms':roms
		}




# if __name__ == '__main__':

title = 'Mame Rom Check %s - %s'%(version,lastrev)

mrcpath = os.getcwd()
pth_mrc = os.getcwd()
pth_7z =  os.path.join(pth_mrc,'bin','7z.exe') # 7z1900
zipformats = ['zip','7z']

## get locales
# todo : english is default, fill the holes from it
files=os.listdir(os.path.join(os.getcwd(),'locales'))
locales = {}
for lf in files :
	if '.' in lf and lf.split('.')[-1] == 'tab' :
		locale = lf.split('.')[0]
		localepath = os.path.join(os.getcwd(),'locales',lf)
		localefile = open(localepath,encoding='utf8')
		config = localefile.readlines()
		localefile.close()
		locales[locale] = mfl2dict(config)[0][locale]
task = Tasks()
cfg = Config()
cfg.load()

# rd=Romdir.get(1)
# task.verbose = False
# rd.verify()
