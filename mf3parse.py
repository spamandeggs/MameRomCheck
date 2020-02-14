## mf3parse.py
# ensemble de fonctions qui convertissent
# une liste readlines() raw en un dictionnaire python,
# et un dictionnaire python en une liste readlines() raw 
# python3
# 11/02/2016
# 24/10/2017 sauts de lignes apres un nest, maj mfl2Odict, cleaning

'''
# tests depuis la console :
p = "D:\\documents\\projets\\3d\\bge\\mainframe\\mf4\\webui\\data\\lib\\testparsing.mf3"
f = open(p,'r')
cfg = f.readlines()
f.close()
from mf3parse import *

d,s = mfl2Odict(cfg)
print(d)
'''

from collections import OrderedDict as Odict
try :
	from mathutils import Vector, Euler, Color
except :
	def Vector(var) : return var
	def Euler(var) : return var

nestaslist = [ 'blocks','mf3','ifthen','reactions','mapto','mapto2','atinit','atend','atloop','atmin','atmax' ]	

# tabulation count + line instruction
def gettabulation(line) :
	# print('mf3Line : \n %s\n %s\n %s'%(line,len(line),type(line)))
	
	tabs = 0
	while len(line) > 0 and line[0] == '\t' :
		tabs += 1
		line = line[1:]
	line = line.strip()
	return tabs,line

# read a raw line and returns it cleaned with its tab position
def mf3Line(line) :
	# print('mf3Line : \n %s\n %s\n %s'%(line,len(line),type(line)))
	
	# tabulation count
	tabs = 0
	# get rid of eol's
	# if len(line) > 0 and line[-1] in ['\r','\n'] : line = line[:-1]
	# elif len(line) > 1 and line[-2:] == '\r\n' : line = line[:-2]

	# tabs count
	tabs,line = gettabulation(line)
	
	# file odd header ... ? todo : check to be sure its a DOM header
	if line[:3] == "ï»¿" : line = line[3:]

	# blank line actually
	if line == '' : return tabs,''
	
	# removes inner lines tab duplis and start/end blanks
	while '\t\t' in line : line = line.replace('\t\t','\t')

	# ignore eol comments
	if '#' in line :
		di = line.index('#')
		if di==0 or line[di-1] != "\\" : line = line[:di].strip()
		# if '\t' not in line[di:] : line = line[:di].strip()
	
	# remove additionnal slashes, cases like var	string	another string
	args=line.split('\t')
	while len(args) > 2 :
		args[-2] += ' %s'%args[-1]
		del args[-1]
	line='\t'.join(args)
	
	# ignore empty and comments lines
	if line in [ '', '\t']  or line[0] == '#' or line [0:2] == '//' : return tabs,''
	
	return tabs,line

# converts a list of mf3 lines to a dictionnary
def LASTmfl2dict(cfg,dico=False,lasttab=0,pointer=-1) :
	# orderedkeys = [ 'if' ,'elif','exec','ifthen','then','else','set','trace','mapto','mapto2','atinit','atend','atloop' ]
	orderedkeys = [ 'if' ,'elif','exec','ifthen','then','else','set','trace' ]
	if dico == False : dico = {}
	try :
		typ = 'dict' if type(dico) == dict else 'list'
				
		while pointer+1 < len(cfg) :
			
			pointer += 1
			line = cfg[pointer]
			tab = 0
			nexttab = 0
			tab, line = mf3Line(cfg[pointer])
			if line == '' : continue
			if pointer+1 < len(cfg) : nexttab, nextline = mf3Line(cfg[pointer+1])
			else : nexttab = tab		

			# print(pointer,tab,lasttab)
			
			if tab == lasttab :
				#print('%s.%s.%s.%s.%s'%(' '*tab,pointer+1,line,lasttab,line == 'if'))
				
				# a prop with a value
				if '\t' in line :
					line,v = line.split('\t')
					line = line.strip()
					try : line = int(line)
					except : pass
					v = findType(v.strip())
					if typ == 'dict' :
						dico[line] = v
					else :
						dico.append({line:v})
				# a list item
				elif tab >= nexttab :
					if typ == 'dict' :
						try : line = int(line)
						except : pass
						dico[line] = 0
					else :
						line = findType(line)
						dico.append(line)
				# a  nested list or dict 
				else :

					if line[-2:] == '[]' or line in [ 'if' ,'elif','exec','ifthen','then','else','set','trace' ] :
					# if line[-2:] == '[]' or line in orderedkeys :
						styp = 'list'
						line = line.replace('[]','')
						try : line = int(line)
						except : pass
						if typ == 'dict' :
							dico[line] = []
						else :
							dico.append({line:[]})
					else :
						try : line = int(line)
						except : pass
						styp = 'dict'
						if typ == 'dict' :
							dico[line] = {}
						else :
							dico.append({line:{}})
			  
			elif tab < lasttab :
				return dico,pointer-1
			
			elif tab > lasttab :
				#print('%s.%s.%s.%s'%(' '*tab,pointer+1,line,lasttab))
				#if typ == 'lst' :
				#	dico[lastline] = []
				#else :
				#	dico[lastline] = {}
					

				#
				if styp == 'list' :
					#print('%sread list'%(' '*tab))
					subdico,pointer = mfl2dict(cfg,[],lasttab+1,pointer-1)
					if subdico == False : return False,pointer
					#print(subdico)
					#print(type(dico))
					#print(dico)
					#print(lastline)
					if typ == 'dict' : 
						#print('%sfeed dict with list'%(' '*tab))
						dico[lastline].extend(subdico)
					else :
						#print('%sfeed list with list'%(' '*tab))
						dico[-1][lastline] = subdico
				else :
					#print('%sread dict'%(' '*tab))
					subdico,pointer = mfl2dict(cfg,{},lasttab+1,pointer-1)
					if subdico == False : return False,pointer
					#print(subdico)
					#print(type(dico),typ)
					#print(dico)
					#print(lastline)
					if typ == 'dict' : 
						#print('%sfeed dict with dict'%(' '*tab))
						dico[lastline].update(subdico)
					else :
						#print('%sfeed list with dict'%(' '*tab))
						dico[-1][lastline] = subdico
						
				tab -= 1

			#print('%s%s'%(' '*tab,dico))
			lastline = line
			lasttab = tab

		return dico,pointer
	except :
		return False,pointer

def mfl2dict(cfg,dico=False,lasttab=0,pointer=-1) :
	if dico == False : dico = {}
	# try :
	typ = 'dict' if type(dico) == dict else 'list'
			
	while pointer+1 < len(cfg) :
		
		pointer += 1
		line = cfg[pointer]
		tab = 0
		nexttab = 0
		tab, line = mf3Line(cfg[pointer])
		if line == '' : continue
		
		npointer = pointer
		nextline = ''
		
		while nextline == '' and npointer+1 < len(cfg) :
			npointer += 1
			nexttab, nextline = mf3Line(cfg[npointer])
			if nextline == '' :
				nexttab = tab
				continue

		# print(pointer,line,tab,nexttab)

		# is a peer of the last element
		if tab == lasttab :
			#print('%s.%s.%s.%s.%s'%(' '*tab,pointer+1,line,lasttab,line == 'if'))
			
			# a key and a value
			if '\t' in line :
				line,v = line.split('\t')
				line = line.strip()
				try : line = int(line)
				except : pass
				v = findType(v.strip())
				if typ == 'dict' :
					dico[line] = v
				else :
					dico.append({line:v})
			# not a nest, but a word alone
			elif tab >= nexttab :
				# if nest is a dict, default value 
				if typ == 'dict' :
					try : line = int(line)
					except : pass
					dico[line] = 0
				# if nest is a list, append
				else :
					line = findType(line)
					dico.append(line)
			# a  nested list or dict, create it
			else :
				if line[-2:] == '[]' :
					line = line[:-2]
					islist = True
				else : 
					islist = False
				# nest is a list
				if islist or line in nestaslist :
					nesttype = 'list'
					try : line = int(line)
					except : pass
					if typ == 'dict' :
						dico[line] = []
					else :
						dico.append({line:[]})
				# nest is a dict
				else :
					try : line = int(line)
					except : pass
					nesttype = 'dict'
					if typ == 'dict' :
						dico[line] = {}
					else :
						dico.append({line:{}})
		# end of a nest, return
		elif tab < lasttab :
			return dico,pointer-1
		# first element of a nest, populate it
		elif tab > lasttab :
			#print('%s.%s.%s.%s'%(' '*tab,pointer+1,line,lasttab))
			#if typ == 'lst' :
			#	dico[lastline] = []
			#else :
			#	dico[lastline] = {}
				

			#
			if nesttype == 'list' :
				#print('%sread list'%(' '*tab))
				subdico,pointer = mfl2tuple(cfg,[],lasttab+1,pointer-1)
				if subdico == False : return False,pointer
				#print(subdico)
				#print(type(dico))
				#print(dico)
				#print(lastline)
				if typ == 'dict' : 
					#print('%sfeed dict with list'%(' '*tab))
					dico[lastline].extend(subdico)
				else :
					#print('%sfeed list with list'%(' '*tab))
					dico[-1][lastline] = subdico
			else :
				#print('%sread dict'%(' '*tab))
				subdico,pointer = mfl2dict(cfg,{},lasttab+1,pointer-1)
				if subdico == False : return False,pointer
				#print(subdico)
				#print(type(dico),typ)
				#print(dico)
				#print(lastline)
				if typ == 'dict' : 
					#print('%sfeed dict with dict'%(' '*tab))
					dico[lastline].update(subdico)
				else :
					#print('%sfeed list with dict'%(' '*tab))
					dico[-1][lastline] = subdico
					
			tab -= 1

		#print('%s%s'%(' '*tab,dico))
		lastline = line
		lasttab = tab

	return dico,pointer
	# except :
		# return False,pointer

## c'est la fonction parser utilisée en entrée (juillet 2018)
def mfl2Odict(cfg,dico=False,lasttab=0,pointer=-1) :
	if dico == False : dico = Odict()
	# try :
	typ = 'dict' if type(dico) == Odict else 'list'
	
	try :
		while pointer+1 < len(cfg) :
			
			pointer += 1
			line = cfg[pointer]
			tab = 0
			nexttab = 0
			tab, line = mf3Line(cfg[pointer])
			if line == '' : continue
			
			npointer = pointer
			nextline = ''
			
			while nextline == '' and npointer+1 < len(cfg) :
				npointer += 1
				nexttab, nextline = mf3Line(cfg[npointer])
				if nextline == '' :
					nexttab = tab
					continue
			# print(pointer,line,tab,nexttab)
			
			# is a peer of the last element
			if tab == lasttab :
				#print('%s.%s.%s.%s.%s'%(' '*tab,pointer+1,line,lasttab,line == 'if'))
				
				# a key and a value
				if '\t' in line :
					line,v = line.split('\t')
					line = line.strip()
					try : line = int(line)
					except : pass
					v = findType(v.strip())
					if typ == 'dict' :
						dico[line] = v
					else :
						dico.append({line:v})
				# not a nest, but a word alone
				elif tab >= nexttab :
					# if nest is a dict, default value 
					if typ == 'dict' :
						try : line = int(line)
						except : pass
						dico[line] = 0
					# if nest is a list, append
					else :
						line = findType(line)
						dico.append(line)
				# a  nested list or dict, create it
				else :
					if line[-2:] == '[]' :
						line = line[:-2]
						islist = True
					else : 
						islist = False
					# nest is a list
					if islist or line in nestaslist :
						nesttype = 'list'
						try : line = int(line)
						except : pass
						if typ == 'dict' :
							dico[line] = []
						else :
							dico.append({line:[]})
					# nest is a dict
					else :
						try : line = int(line)
						except : pass
						nesttype = 'dict'
						if typ == 'dict' :
							dico[line] = Odict()
						else :
							dico.append({line:Odict()})
			# end of a nest, return
			elif tab < lasttab :
				return dico,pointer-1
			# first element of a nest, populate it
			elif tab > lasttab :
				#print('%s.%s.%s.%s'%(' '*tab,pointer+1,line,lasttab))
				#if typ == 'lst' :
				#	dico[lastline] = []
				#else :
				#	dico[lastline] = {}
					

				#
				if nesttype == 'list' :
					#print('%sread list'%(' '*tab))
					subdico,pointer = mfl2tuple(cfg,[],lasttab+1,pointer-1)
					if subdico == False : return False,pointer
					#print(subdico)
					#print(type(dico))
					#print(dico)
					#print(lastline)
					if typ == 'dict' : 
						#print('%sfeed dict with list'%(' '*tab))
						dico[lastline].extend(subdico)
					else :
						#print('%sfeed list with list'%(' '*tab))
						dico[-1][lastline] = subdico
				else :
					#print('%sread dict'%(' '*tab))
					subdico,pointer = mfl2Odict(cfg,Odict(),lasttab+1,pointer-1)
					if subdico == False : return False,pointer
					#print(subdico)
					#print(type(dico),typ)
					#print(dico)
					#print(lastline)
					if typ == 'dict' : 
						#print('%sfeed dict with dict'%(' '*tab))
						dico[lastline].update(subdico)
					else :
						#print('%sfeed list with dict'%(' '*tab))
						dico[-1][lastline] = subdico
						
				tab -= 1

			#print('%s%s'%(' '*tab,dico))
			lastline = line
			lasttab = tab
	except :
		return False,(pointer+1,line)
	return dico,pointer
	# except :
		# return False,pointer

# converts a list of mf3 lines to a dictionnary-list
def mfl2tuple(cfg,dico=False,lasttab=0,pointer=-1) :
	# orderedkeys = [ 'if' ,'elif','exec','ifthen','then','else','set','trace','mapto','mapto2','atinit','atend','atloop' ]
	orderedkeys = [ 'if' ,'elif','exec','ifthen','then','else','set','trace' ]
	if dico == False : dico = []
	
	try :
		while pointer+1 < len(cfg) :
			
			pointer += 1
			line = cfg[pointer]
			tab = 0
			nexttab = 0
			tab, line = mf3Line(cfg[pointer])
			if line == '' : continue
			if pointer+1 < len(cfg) : nexttab, nextline = mf3Line(cfg[pointer+1])
			else : nexttab = tab

			# print(pointer,tab,lasttab)
				
			## nous sommes sur la même ligne qu'auparavant
			if tab == lasttab :
				#print('%s.%s.%s.%s.%s'%(' '*tab,pointer+1,line,lasttab,line == 'if'))
				
				# a key and a value
				if '\t' in line :
					line,v = line.split('\t')[:2]
					line = line.strip()
					try : line = int(line)
					except : pass
					v = findType(v.strip())
					dico.append([line,v])
					
				# a list item
				elif tab >= nexttab :
					line = findType(line)
					dico.append(line)
				# a nested list or dict 
				else :

					# if line[-2:] == '[]' or line in [ 'if' ,'elif','exec','ifthen','then','else','set','trace' ] :
					# if line[-2:] == '[]' or line in orderedkeys :
					styp = 'list'
					line = line.replace('[]','')
					try : line = int(line)
					except : pass
					dico.append([line,'__'])
					# dico.append((line,[]))
			  
			elif tab < lasttab :
				return dico,pointer-1
			
			elif tab > lasttab :
				#print('%s.%s.%s.%s'%(' '*tab,pointer+1,line,lasttab))
				#if typ == 'lst' :
				#	dico[lastline] = []
				#else :
				#	dico[lastline] = {}
					
				#print('%sread list'%(' '*tab))
				subdico,pointer = mfl2tuple(cfg,[],lasttab+1,pointer-1)
				if subdico == False : return False,pointer
				#print(subdico)
				#print(type(dico))
				#print(dico)
				#print(lastline)
				# dico.append((lastline,tuple(subdico)))
				dico[-1][1] = subdico
						
				tab -= 1

			#print('%s%s'%(' '*tab,dico))
			lastline = line
			lasttab = tab

		return dico,pointer
	except :
		return False,(pointer+1,line)

# converts a dictionnary to a list of mf3 lines
def dict2mfl(dico,tab=0) :

	lines = []
	dicotypes = [ dict , Odict ]
	if type(dico) == list :
	
		for v in dico :
			
			if type(v) not in dicotypes and type(v) != list :
				# new list element value
				if type(v) != str : v = repr(v)
				lines.append('%s%s\n'%('\t'*tab,v))
			else :
				# list element is a nested thingy
				lines.extend(dict2mfl(v,tab))
	else :
		for k,v in dico.items() :
			
			if type(v) not in dicotypes and type(v) != list :
				# new key and a single value
				# this for 'SystemError: Representation not overridden by object.' ie vehicleID
				try : test = repr(v) 
				except : v = 'BUG'
				if type(v) != str : v = repr(v)
				intertab = max(2,6 - int(len(str(k)) / 4))
				lines.append('%s%s%s%s\n'%('\t'*tab,str(k),'\t'*intertab,v))
					
			else :
				# empty containers
				if not(v) :
					if type(v) == list : listtag = '\t[]'
					elif type(v) in dicotypes : listtag = '\t{}'
					else : listtag = '\t()'
				# new key and its nested elements
				else :
					if type(v) == list : listtag = '[]'
					else : listtag = ''
				lines.append('%s%s%s\n'%('\t'*tab,k,listtag))
				lines.extend(dict2mfl(v,tab+1))
	return lines

def dumpTuple(t,tab=0) :
	# print(len(t),type(t))
	# if len(t) == 1 :
		# dumpTuple(t[0],tab+1)
		# return
	for tm in t :
		if type(tm) != tuple :
			print('%s%s'%('  '*tab,tm))
			continue
		# elif len(tm) == 2 :
		# print(tm)
		k,v = tm
		if type(v) != tuple :
			print('%s%s = %s'%('  '*tab,k,v))
		else :
			print('%s%s'%('  '*tab,k))
			dumpTuple(v,tab+1)
			# print('%s%s contains %s'%('  '*tab,k,type(v)))
		# else :
			# for i in range(20) : print('x'*20)
				
		
# display a whole nested dict/list in the console
# todo : role tres semblable a dict2mfl
def dumpDict(dico,tab=0,typ=False) :
	if type(dico) == list :
		for v in dico :
			if type(v) != dict and type(v) != list :
				print('%s.%s'%('  '*tab,v))
			else :
				#print('%s.%s %s :'%(' '*tab,v,type(v)))
				dumpDict(v,tab+1,typ)
	else :
		for k,v in dico.items() :
			if typ :
				if type(v) != dict and type(v) != list :
					print('%s%s = %s'%('  '*tab,k,v))
				else :
					print('%s%s :'%('  '*tab,k))
					dumpDict(v,tab+1,typ)
			else :
				if type(v) != dict and type(v) != list :
					print('%s%s = %s'%('  '*tab,k,v))
				else :
					print('%s%s :'%('  '*tab,k))
					dumpDict(v,tab+1)

# convert a string to it's type : list, dict, int, float, blender maths
def findType(var) :
	# if len(var) == 0 : return ''
	if var == 'None' : return None
	elif var[0:7] == 'Vector(' : return eval(var)
	elif var[0:6] == 'Euler(' : return eval(var)
	elif var[0:6] == 'Color(' : return eval(var)
	elif var in [ "''", '""' ] : return ''
	elif var[0]=='[' and var[-1]==']' : return eval(var)
	elif var[0]=='{' and var[-1]=='}' : return eval(var)
	elif var[0]=='+' :#or var[0]=='-' :
		return var
	elif var.lower()=="false" : return bool(0)
	elif var.lower()=="true" : return bool(1)
	try :
		try :
			test=var.index(".") 
			var=float(var)
		except :
			var=int(var)
	except :
		var=str(var)
	return var