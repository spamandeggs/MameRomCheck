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

from ui_romdirs import *
from time import sleep

###################

class UI(UI_romdirs) :
	def __init__(self, master=None) :
		super().__init__(master)
		
		# print(ttk.Style().theme_names())
		# ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
		
		style = ttk.Style()
		style.theme_use("winnative")
		# style.configure(".", font=('Helvetica', 8), foreground="white")
		style.configure("Treeview", foreground='red')
		# style.configure("Treeview.Heading", bg="black", foreground='green')
			# # rowheight
			# # font ('Calibri', 10)
		# style.configure("Treeview", highlightthickness=10, bd=0, font=('Calibri', 10)) # Modify the font of the body
		# style.configure('Treeview', rowheight=20)

		# # style.configure("Treeview", highlightthickness=0, bd=0, font=('Calibri', 8))
		# # style.configure('Treeview', rowheight=14)

		# # style.configure("Treeview", background="#383838", foreground="white", fieldbackground="red")
		# style.configure("TButton", padding=6, relief="flat", background="#ccc")
		
		## icons
		self.icons = {}
		iconpth = os.path.join(pth_mrc,'icons')
		icons = {
			'mame' : 'mame16x16.gif',
			'blank' : 'blank16x16.gif',
			'new' : 'new16x16.gif',
			'missing' : 'missing16x16.gif',
			}
		for k,v in icons.items() :
			self.icons[k] = ImageTk.PhotoImage(Image.open(os.path.join(iconpth,v)))
		
		# get config
		self.lastdir = "D:\\Program Files Shared\\jeux\\Emulateurs\\arcades"
		
		self.newRomdirPathLast = ''
		
		self.mameExeActive = None
		self.romdirActive = None
		self.romsetActive = None
		
		## widgets
		
		###############
		# MAME   view #
		###############
		self.mameExeFrame = ttk.Frame(self)
		mameExeTreeLabel = ttk.Label(self.mameExeFrame, text=cfg.txt['mameExeFrameLabel'])
		
		treecols = odict({
			'name' : cfg.txt['colName'],
			'version' : cfg.txt['colVersion'],
			'path' : cfg.txt['colPath'],
			})
		self.mameExeTags = ['mameexe']
		self.mameExeTree = buildTree(self.mameExeFrame,Mame.getall('item'),treecols,self.mameExeTags)
		self.mameExeTree.bind('<ButtonRelease-1>', self.mameExeTreeClick)
		# self.mameExeTree.tag_configure('mameexe', font=('Helvetica', 6))
		# print('CLASS',self.mameExeTree.winfo_class())
		# self.mameExeTree.configure(bg='black')
		
		mameExeButtonFrame = ttk.Frame(self.mameExeFrame)
		mameExeRun = ttk.Button(mameExeButtonFrame, text=cfg.txt['run'], command=self.runMame)
		mameExeAdd = ttk.Button(mameExeButtonFrame, text=cfg.txt['add'], command=self.mameExeAddDialog)
		mameExeEdit = ttk.Button(mameExeButtonFrame, text=cfg.txt['edit'], command=self.mameExeEditDialog)
		mameExeDel = ttk.Button(mameExeButtonFrame, text=cfg.txt['del'], command=self.mameExeDelDialog)
		
		###############
		# ROMDIR view #
		###############
		# self.romdirFrame = ttk.Frame(self)
		# self.romdirTreeFrame = ttk.Frame(self.romdirFrame)
		romdirTreeLabel = ttk.Label(self.mameExeFrame, text=cfg.txt['romdirFrameLabel'])
		
		self.romdirHeaders = odict({
			'name' : cfg.txt['colName'],
			'path' : cfg.txt['colPath'],
			})
		self.romdirCols = list(self.romdirHeaders.keys())
		self.romdirTags = ['romdir']
		self.romdirTree = buildTree(self.mameExeFrame,Romdir.getall('item'),self.romdirHeaders,self.romdirTags)
		self.romdirTree.bind('<ButtonRelease-1>', self.romdirTreeClick)
		# background='#...' definitely DOES NOT WORK for Treeview items on windows 10
		# will just silently fooling you.
		# self.romdirTree.tag_configure('hasuser', font=('Helvetica', 10,'bold'), image=self.icons['mame'])
		self.romdirTree.tag_configure('romdir', image=self.icons['blank'])
		self.romdirTree.tag_configure('hasuser', image=self.icons['mame'])

		romdirButtonFrame = ttk.Frame(self.mameExeFrame)
		romdirAdd = ttk.Button(romdirButtonFrame, text=cfg.txt['add'], command=self.romdirAddDialog)
		romdirEdit = ttk.Button(romdirButtonFrame, text=cfg.txt['edit'], command=self.romdirEditDialog)
		romdirDel = ttk.Button(romdirButtonFrame, text=cfg.txt['del'], command=self.romdirDelDialog)
		
		
		################
		# ROMSETS view #
		################
		# all romsets of an active folder
		self.romsetsFrame = ttk.Frame(self)
		self.romsetsTreeLabel = ttk.Label(self.romsetsFrame, text=cfg.txt['romsetsFrameLabel'])
		
		treecols = odict({
			'name' : cfg.txt['colName'],
			'description' : cfg.txt['colDescription'],
			# 'status' : cfg.txt['colStatus'],
			'driver' : cfg.txt['colDriver'],
			'rommatch' : cfg.txt['colRommatch'],
			'size' : cfg.txt['colSize'],
			'comment' : cfg.txt['colComment'],
			'romscount' : cfg.txt['colRomscount'],
			'warnings' : cfg.txt['colWarning'],
			'error' : cfg.txt['colError'],
		})
		self.romsetsCols = list(treecols.keys())
		self.romsetsTags = ['romset']
		self.romsetsTree = buildTree(self.romsetsFrame,{},treecols,self.romsetsTags)
		self.romsetsTree.bind('<ButtonRelease-1>', self.romsetsTreeClick)
		self.romsetsTree.tag_configure('romset', image=self.icons['blank'])
		self.romsetsTree.tag_configure('new', image=self.icons['new'])
		self.romsetsTree.tag_configure('missing', image=self.icons['missing'])
		
		romsetButtonFrame = ttk.Frame(self.romsetsFrame)
		self.romsetVerifyButton = ttk.Button(romsetButtonFrame, text=cfg.txt['romsetMameNone'], command=self.romsetVerify)
		self.romsetVerifyButton.state(['disabled'])
		self.romsetVerifyAllButton = ttk.Button(romsetButtonFrame, text=cfg.txt['romsetMameNone'], command=self.romsetVerifyAll)
		self.romsetVerifyAllButton.state(['disabled'])
		self.romdirUpdateButton = ttk.Button(romsetButtonFrame, text=cfg.txt['romdirUpdate'], command=self.romdirUpdate)

		# romsetsAdd = ttk.Button(self, text=cfg.txt['add'], command=self.romsetsAddDialog)
		# romsetsEdit = ttk.Button(self, text=cfg.txt['edit'], command=self.romsetsEditDialog)
		# romsetsDel = ttk.Button(self, text=cfg.txt['del'], command=self.romsetsDelDialog)
		
		# 
		
		###############
		# ROMSET view #
		###############
		# info about an active romset
		self.romsetFrame = ttk.Frame(self)
		self.romsetTreeLabel = ttk.Label(self.romsetFrame, text=cfg.txt['romsetFrameLabel'])
		
		treecols = odict({
			'name' : cfg.txt['colName'],
			# 'size' : cfg.txt['colSize'],
			'crc' : cfg.txt['colCRC'],
			# 'comment' : cfg.txt['colComment'],
			'status' : cfg.txt['colStatus'],
		})
		self.romsetCols = list(treecols.keys())
		self.romsetTags = ['romset']
		self.romsetTree = buildTree(self.romsetFrame,{},treecols,self.romsetTags)
		self.romsetTree.bind('<ButtonRelease-1>', self.romsetTreeClick)
		
		self.romsetRunButton = ttk.Button(self, text=cfg.txt['romsetMameNone'], command=self.romsetRun)
		self.romsetRunButton.state(['disabled'])
		
		###############
		# COMMON/MAIN #
		###############
		save = ttk.Button(self, text=cfg.txt['saveConfig'], command=self.saveConfig)

		#########################
		# ui geometry / theming #
		#########################
		self.grid(column=0, row=0, sticky=(N, W, E, S))
		
		mameexecol = 0
		romdircol = 0
		romsetscol = 1
		romsetcol = 2
		# MAME
		row = rowaddfrom(0)
		self.mameExeFrame.grid(column=mameexecol, row=next(row), sticky=(N,W,E,S))
		self.mameExeFrame['padding']=(5, 5, 12, 12)
		mameExeTreeLabel.grid(column=mameexecol, row=next(row), padx=10, pady=5)
		
		self.mameExeTree.grid(column=mameexecol, row=next(row), sticky=(N,W,E,S))
		self.mameExeTree.column('#0', width=200, anchor='w')
		self.mameExeTree.column('version', width=50, anchor='w')
		self.mameExeTree['height'] = 5
		
		mameExeButtonFrame.grid(column=mameexecol, row=next(row), sticky=(N,W,E,S))
		mameExeButtonFrame['padding']=(5, 5, 12, 12)
		mameExeAdd.grid(column=mameexecol, row=0, sticky=(N,S,E,W))
		mameExeEdit.grid(column=mameexecol+1, row=0, sticky=(N,S,E,W))
		mameExeDel.grid(column=mameexecol+2, row=0, sticky=(N,S,E,W))
		mameExeRun.grid(column=mameexecol+3, row=0, sticky=(N,S,E,W))
		
		# ROMDIR
		# self.romdirFrame.grid(column=romdircol, row=0, sticky=(N,W,E,S))
		# self.romdirFrame['padding']=(5, 5, 12, 12)
		# self.romdirTreeFrame.grid(column=romdircol, row=next(row), sticky=(N,W,E,S))
		# self.romdirTreeFrame['padding']=(5, 5, 12, 12)
		romdirTreeLabel.grid(column=romdircol, row=next(row), padx=10, pady=5)
		
		self.romdirTree.grid(column=romdircol, row=next(row), sticky=(N,W,E,S))
		self.romdirTree.column('#0', width=200, anchor='w')
		self.romdirTree['height'] = 10
		
		romdirButtonFrame.grid(column=romdircol, row=next(row), sticky=(N,W,E,S))
		romdirButtonFrame['padding']=(5, 5, 12, 12)
		romdirAdd.grid(column=romdircol, row=1, sticky=(N,S,E,W))
		romdirEdit.grid(column=romdircol+1, row=1, sticky=(N,S,E,W))
		romdirDel.grid(column=romdircol+2, row=1, sticky=(N,S,E,W))
				
		# ROMSETS
		row = rowaddfrom(0)
		self.romsetsFrame.grid(column=romsetscol, row=next(row), sticky=(N,W,E,S))
		self.romsetsFrame['padding']=(5, 5, 12, 12)
		self.romsetsTreeLabel.grid(column=romsetscol, row=next(row), padx=10, pady=5)

		self.romsetsTree.grid(column=romsetscol, row=next(row), sticky=(N,W,E,S))
		self.romsetsTree['height'] = 20
		self.romsetsTree.column('#0', width=70, anchor='w')
		self.romsetsTree.column('description', width=200, anchor='w')
		# self.romsetsTree.column('status', width=200, anchor='w')
		self.romsetsTree.column('driver', width=50, anchor='w')
		self.romsetsTree.column('rommatch', width=50, anchor='w')
		self.romsetsTree.column('size', width=50, anchor='w')
		self.romsetsTree.column('comment', width=50, anchor='w')
		self.romsetsTree.column('romscount', width=50, anchor='w')
		self.romsetsTree.column('warnings', width=5, anchor='w')
		self.romsetsTree.column('error', width=5, anchor='w')
		
		romsetButtonFrame.grid(column=romsetscol, row=next(row), sticky=(N,W,E,S))
		self.romsetVerifyButton.grid(column=romsetscol, row=0, sticky=(N,S,E,W))
		self.romsetVerifyAllButton.grid(column=romsetscol+1, row=0, sticky=(N,S,E,W))
		self.romdirUpdateButton.grid(column=romsetscol+2, row=0, sticky=(N,S,E,W))
		
		# ROMSET
		self.romsetFrame['padding']=(5, 5, 12, 12)
		self.romsetFrame.grid(column=romsetcol, row=0, sticky=(N,W,E,S))
		self.romsetTreeLabel.grid(column=romsetcol, row=0, padx=10, pady=5)
		
		self.romsetTree.column('#0', width=100, anchor='w')
		# self.romsetTree.column('size', width=50, anchor='w')
		self.romsetTree.column('crc', width=50, anchor='w')
		# self.romsetTree.column('comment', width=50, anchor='w')
		self.romsetTree.column('status', width=50, anchor='w')
		self.romsetTree.grid(column=romsetcol, row=1, sticky=(N,W,E,S))
		self.romsetTree['height'] = 20
		
		self.romsetRunButton.grid(column=romsetcol, row=2, sticky=(N,S,E,W))
		
		# COMMON/MAIN
		save.grid(column=0, row=6, sticky=(N,S,E,W))
		
		print(self)
	
	def romdirUpdate(self) :
		if self.romdirActive :
			self.romdirActive.populate()
			self.romdirTreeClick(0)
	
	def romsetRun(self) :
		tkid,name,*args = selectedItem(self.romsetsTree)
		rset = self.romsetActive = self.romdirActive.romset[name]
		
		tkidm,MameName,*args = selectedItem(self.mameExeTree)
		rset.run(MameName)
	
	## verify stuff
	# selection of romset can/will be : active romset (focus), selected romsets, all romsets in the dir
	# verify runs are threaded whatever the selection : only for all romsets for now
	# ui tree must be updated little by little
	def romsetVerify(self) :
		tkid,name,*args = selectedItem(self.romsetsTree) # only active for now
		rset = self.romdirActive.romset[name]
		MameName = self.mameExeActive.name
		rset.verify(MameName)
		self.__romsetUpdateLine(tkid,rset)
		# self.__romsetVerify(tkid,rset)
		self.romsetsTreeClick(0)
		
	def romsetVerifyAll(self) :
	
		self.romdirPending = self.romdirActive
		MameName = self.mameExeActive.name
		self.romdirPending.verify(MameName) # all romsets : got a threaded method for it
		
		itms = [(tkid,self.romdirPending.romset[self.romsetsTree.item(tkid)['text']]) for tkid in self.romsetsTree.get_children()]
		# threading.Thread(target=self.check, args=(itms,)).start()
	
	## update ui tree
	# def check(self,itms) :
	
		while itms :
			if itms[0][1].driver != '-' :
				tkid,rset = itms.pop(0)
				if self.romdirPending == self.romdirActive :
					self.__romsetUpdateLine(tkid,rset)
			sleep(0.01)
		print('ui sync ok')
		self.romdirPending = False
		
	# def __romsetVerify(self,tkid,rset) :
		# tkidm,MameName,*args = selectedItem(self.mameExeTree)
		# rset.verify(MameName)
		# self.__romsetUpdateLine(tkid,rset)
		
	def __romsetUpdateLine(self,tkid,rset) :
		self.romsetsTree.set(tkid,'description',rset.description)
		self.romsetsTree.set(tkid,'driver',rset.driver)
		self.romsetsTree.set(tkid,'rommatch',rset.rommatch) # todo
		self.romsetsTree.set(tkid,'size',rset.size)
		self.romsetsTree.set(tkid,'comment',rset.comment)
		self.romsetsTree.set(tkid,'romscount',rset.romscount)
		self.romsetsTree.set(tkid,'warnings',rset.warnings)
		self.romsetsTree.set(tkid,'error',rset.error)
			
		# self.romsetsTree.update_idletasks()
		self.romsetsTree.update()
	
	##############
	# trees clic #
	##############
	def mameExeTreeClick(self,event) :
		tkid,name,*args = selectedItem(self.mameExeTree)
		# print(tkid,name,args)
		self.mameExeActive = Mame.get(name)
		# to access the right Mame version fields
		# in the Romset class we need this :
		self.mameExeActive.activate()
		print(self.mameExeActive.romdirs)
		rdnames = [rd.name for rd in self.mameExeActive.romdirs]
			# print('
		for tkid in self.romdirTree.get_children() :
			if self.romdirTree.item(tkid)['text'] in rdnames :
				self.romdirTree.item(tkid,tags='hasuser')
			else :
				self.romdirTree.item(tkid,tags='romdir')
				
		# self.romdirTree.tag_configure('hasuser', foreground='red')
		
		# self.romdirTree.insert('', 'end', text='button', tags=('ttk', 'simple'))
		# self.romdirTree.tag_configure('ttk', background='#000')
		
		# update the romsets tree with same romsets but
		# with info about the new selected release
		if self.romdirActive :
			# selected romset need to be to reselected
			# once the romsets tree has been rebuilt
			rsettkid,rsetname,*args = selectedItem(self.romsetsTree)
			populateTree(self.romsetsTree,self.romdirActive.romset,self.romsetsCols,self.romsetsTags)
			self.romsetsTree.focus(rsettkid)
			self.romsetsTree.selection_set(rsettkid)
			# then trigger the romset view
			# to see the roms status with this release
			self.romsetsTreeClick(0)
		# dis/enable buttons
		if tkid :
			self.romsetRunButton['text'] = cfg.txt['romsetRun']%name
			self.romsetRunButton.state(['!disabled'])
			self.romsetVerifyButton['text'] = cfg.txt['romsetVerify']%name
			self.romsetVerifyButton.state(['!disabled'])
			self.romsetVerifyAllButton['text'] = cfg.txt['romsetVerifyAll']%name
			self.romsetVerifyAllButton.state(['!disabled'])
		else :
			self.romsetRunButton['text'] = cfg.txt['romsetMameNone']
			self.romsetRunButton.state(['disabled'])
			self.romsetVerifyButton['text'] = cfg.txt['romsetMameNone']
			self.romsetVerifyButton.state(['disabled'])
			self.romsetVerifyAllButton['text'] = cfg.txt['romsetMameNone']
			self.romsetVerifyAllButton.state(['disabled'])
			
	def romdirTreeClick(self,event) :
		tkid,name,*args = selectedItem(self.romdirTree)
		# print(tkid,name,args)
		self.romdirActive = Romdir.get(name)
		print(self.romdirTree.item(tkid))
		print('%s romsets'%(len(self.romdirActive.romset)))
		populateTree(self.romsetsTree,self.romdirActive.romset,self.romsetsCols,self.romsetsTags)
		self.romsetsTreeLabel['text'] = cfg.txt['romsetsFrameLabel']%(self.romdirActive.name,len(self.romdirActive.romset))
		
	def romsetsTreeClick(self,event) :
		tkid,name,*args = selectedItem(self.romsetsTree)
		print('romset %s %s'%(tkid,name))
		if name :
			self.romsetTreeLabel['text'] = cfg.txt['romsetFrameLabel']%(name,self.romdirActive.name)
			rset = self.romsetActive = self.romdirActive.romset[name]
			if rset.roms == {} : 
				# print('-'*10)
				# print('populate')
				# print(tkid,name,args)
				# print(rset.name,rset.path)
				rset.populate()
				# print(rset.size)
				# print(list(rset.roms.keys()))
				# print('-'*10)
				self.__romsetUpdateLine(tkid,rset)
				# self.romsetsTree.set(tkid,'size',rset.size)
				# self.romsetsTree.set(tkid,'comment',rset.comment)
				# self.romsetsTree.set(tkid,'romscount',rset.romscount)
				# self.romsetsTree.set(tkid,'warnings',rset.warnings)
				# self.romsetsTree.set(tkid,'error',rset.error)
			rsetview = {}
			if self.mameExeActive and self.mameExeActive.version in rset.mame :
				for k,v in rset.roms.items() :
					rsetview[k] = {
						'crc' : v['crc'],
						'status' : rset.mame[self.mameExeActive.version]['romset'][k],
					}
			else :
				for k,v in rset.roms.items() :
					rsetview[k] = {
						'crc' : v['crc'],
						'status' : '-',
					}
				
			populateTree(self.romsetTree,rsetview,self.romsetCols,self.romsetTags)
	
	def romsetTreeClick(self,event) :
		tkid,name,*args = selectedItem(self.romsetTree)
		
		
	def saveConfig(self) :
		print('ask save')
		cfg.save()
		print('save done')
		
	def runMame(self) :
		idx,mameExeName,mameExeVersion,mameExePath = selectedItem(self.mameExeTree)
		Mame.get(mameExeName).run()
		os.chdir(mrcpath)


if __name__ == '__main__':

	root = Tk()
	root.title(title)
	app = UI(master=root)
	app.mainloop()