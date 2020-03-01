# python3.8.2
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

#####################
## mameexe dialogs ##
#####################

if __name__ == 'bin.tk_mameexes' :
	from . tk_mameexes import *
	from . tk_helpers import *
else :	
	from mameromcheck import *
	from tk_helpers import *
	
class UI_mameexes(ttk.Frame) :

	def mameExeAddDialog(self) :
		self.mameExeAddEditDialog()
		self.mameExeAddDialogRoot.title(cfg.txt['addMameTitle'])
		self.mameExeInst = None
		self.treetag = None

		self.newMameExeNameLast = ''
		self.newMameExePathLast = ''
		self.newMameExeVersionLast = ''
			
	def mameExeEditDialog(self) :
		idx,mameExeName,mameExeVersion,mameExePath = selectedItem(self.mameExeTree)
		if idx != None :
			self.mameExeAddEditDialog()
			self.mameExeAddDialogRoot.title(cfg.txt['editMameTitle'])
			
			self.mameExeInst = Mame.get(mameExeName)
			
			self.newMameExeName.set(mameExeName)
			self.newMameExePath.set(mameExePath)
			self.newMameExeVersion.set(mameExeVersion)
			
			self.treetag = idx
		
			self.newMameExeNameLast = mameExeName
			self.newMameExePathLast = mameExePath
			self.newMameExeVersionLast = mameExeVersion
			
	def mameExeAddEditDialog(self) :
		self.mameExeAddDialogRoot = Toplevel(self)
		self.mameExeAddDialogRoot.grab_set()
		self.mameExeAddDialogRoot.resizable(FALSE,FALSE)
		
		mameExeAddDialogNameLabel = ttk.Label(self.mameExeAddDialogRoot, text=cfg.txt['addName']) # todo apparait pas
		
		self.newMameExeName = StringVar()
		mameExeAddDialogName = ttk.Entry(self.mameExeAddDialogRoot, textvariable=self.newMameExeName)
		mameExeAddDialogName.bind('<FocusIn>',self.newMameExeNameStore)
		mameExeAddDialogName.bind('<FocusOut>',self.newMameExeNameCheck)
		
		self.newMameExePath = StringVar()
		mameExeAddDialogPathLabel = ttk.Label(self.mameExeAddDialogRoot, text=cfg.txt['addPath'])
		mameExeAddDialogPath = ttk.Entry(self.mameExeAddDialogRoot, textvariable=self.newMameExePath)
		mameExeAddDialogPath.bind('<FocusIn>',self.newMameExePathStore)
		mameExeAddDialogPath.bind('<FocusOut>',self.newMameExePathCheck)
		mameExeAddDialogPathButton = ttk.Button(self.mameExeAddDialogRoot, text="browse", command=self.mameExeAddPathDialog )
		
		self.newMameExeVersion = StringVar()
		mameExeAddDialogVersionLabel = ttk.Label(self.mameExeAddDialogRoot, text=cfg.txt['addVersion'])
		mameExeAddDialogVersion = ttk.Entry(self.mameExeAddDialogRoot, textvariable=self.newMameExeVersion)
		
		mameExeAddDialogCancel = ttk.Button(self.mameExeAddDialogRoot, text=cfg.txt['cancel'], command=self.mameExeAddDialogClose )
		mameExeAddDialogGuess = ttk.Button(self.mameExeAddDialogRoot, text=cfg.txt['guess'], command=self.mameExeGuessVersion )
		mameExeAddDialogOk = ttk.Button(self.mameExeAddDialogRoot, text=cfg.txt['ok'], command=self.mameExeAddDialogNew )
		
		# ui geometry
		mameExeAddDialogNameLabel.grid(column=0, row=0, sticky=(N,S,E,W))
		
		mameExeAddDialogName['width']=40
		mameExeAddDialogName.grid(column=0, row=1, sticky=(N,S,E,W))
		mameExeAddDialogPathLabel.grid(column=0, row=2, sticky=(N,S,E,W))
		
		mameExeAddDialogPath['width']=40
		mameExeAddDialogPath.grid(column=0, row=3, sticky=(N,S,W))
		mameExeAddDialogPathButton.grid(column=1, row=3, sticky=(N,S,E))
		
		mameExeAddDialogVersionLabel.grid(column=0, row=4, sticky=(N,S,E,W))
		mameExeAddDialogVersion.grid(column=0, row=5, sticky=(N,S,E,W))
		
		mameExeAddDialogCancel.grid(column=0, row=6, sticky=(N,S,W))
		mameExeAddDialogGuess.grid(column=1, row=6, sticky=(N,S,W))
		mameExeAddDialogOk.grid(column=2, row=6, sticky=(N,S,E))
	
	# mame edit/add ok button : add value, or reinsert in the list when edit mode
	def mameExeAddDialogNew(self) :
		newMameExeName = self.newMameExeName.get().strip()
		# checks
		if not(newMameExeName) :
			messagebox.showerror(message=cfg.txt['errorNameEmptyMame'],icon='warning',title=cfg.txt['errorNameEmptyTitle'],parent=self.mameExeAddDialogRoot)
			return
		nmep = self.newMameExePath.get()
		if not(nmep) :
			messagebox.showerror(message=cfg.txt['errorPathEmptyMame'],icon='warning',title=cfg.txt['errorPathEmptyTitle'],parent=self.mameExeAddDialogRoot)
			return
		
		# update source dict
		# add
		if self.mameExeInst == None :
			self.mameExeActive = Mame(nmep,newMameExeName,self.newMameExeVersion.get())
			tag = self.mameExeTree.insert('', 'end', text=newMameExeName, tags=self.mameExeTags)
		# edit
		else :
			self.mameExeInst.name = newMameExeName
			self.mameExeInst.path = nmep
			self.mameExeInst.version = self.newMameExeVersion.get()
			self.mameExeInst = None
			tag = self.treetag
			self.mameExeTree.item(tag,text=newMameExeName)
			
		self.mameExeTree.set(tag,'path',nmep)
		self.mameExeTree.set(tag,'version',self.newMameExeVersion.get())
		
		populateTree(self.romdirTree,Romdir.getall('item'),self.romdirCols,self.romdirTags)

		self.treetag = None
		self.mameExeAddDialogClose()

	# mame edit/add cancel button
	# if edit mode, self.treetag is an index (int) : write back the original values
	def mameExeAddDialogClose(self) :
		self.mameExeAddDialogRoot.grab_release()
		self.mameExeAddDialogRoot.destroy()
	
	def mameExeAddPathDialog(self) :
		self.mameExeAddDialogRoot.withdraw()
		mameExePath = filedialog.askopenfilename(initialdir = self.lastdir,title = cfg.txt['addPathTitleMame'],filetypes = (("mame exe","*.exe"),("all files","*.*")))
		
		self.newMameExePathCheck(mameExePath)
			# self.newMameExePath.set(mameExePath)

		self.mameExeAddDialogRoot.deiconify()
			
	# store previous entries of add/edit dialogs in case of user error
	def newMameExeNameStore(self,event) :
		self.newMameExeNameLast = self.newMameExeName.get()
	
	def newMameExePathStore(self,event) :
		self.newMameExePathLast = self.newMameExePath.get()

	# check Mame Name and path when added
	def newMameExeNameCheck(self,event) :
		newMameExeName = self.newMameExeName.get().strip()
		nametest = [fld.lower() for fld in Mame.getall('name')]
		# print('check name %s Mame names : %s. edited instance is %s'%(newMameExeName,newMameExeName.lower() in nametest,'' if type(self.mameExeInst) == None else self.mameExeInst.name))
		if newMameExeName.lower() in nametest and (not(self.mameExeInst) or newMameExeName.lower() != self.mameExeInst.name.lower()) :
			messagebox.showerror(message=cfg.txt['errorNameExistMame'],icon='warning',title=cfg.txt['errorNameExistTitle'],parent=self.mameExeAddDialogRoot)
			self.newMameExeName.set(self.newMameExeNameLast)
			return False
		self.newMameExeName.set(newMameExeName)
		return True

	def newMameExePathCheck(self,newMameExePath) :
		if type(newMameExePath) != str : newMameExePath = self.newMameExePath.get().strip()
		if not(newMameExePath) : return False
		newMameExePath = pathconform(newMameExePath)
		nametest = [fld.lower() for fld in Mame.getall('path')]
		# if in add mode and path exist or if in edit mode and another path than the edited one exist
		if newMameExePath in nametest and (not(self.mameExeInst) or self.mameExeInst.path != newMameExePath):
			messagebox.showerror(message=cfg.txt['errorPathExistMame'],icon='warning',title=cfg.txt['errorPathExistTitle'],parent=self.mameExeAddDialogRoot)
			self.newMameExePath.set(self.newMameExePathLast)
			return False
		if not(os.path.isfile(newMameExePath)) :
			messagebox.showerror(message=cfg.txt['errorPathWrong'],icon='warning',title=cfg.txt['errorPathWrongTitle'],parent=self.mameExeAddDialogRoot)
			self.newMameExePath.set(self.newMameExePathLast)
			return False
		self.newMameExePath.set(newMameExePath)
		self.lastdir = os.path.dirname(newMameExePath)
		return True
	
	## mame delete dialog
	def mameExeDelDialog(self) :
		idx,mameExeName,mameExeVersion,mameExePath = selectedItem(self.mameExeTree)
		if idx != None and messagebox.askyesno(message=cfg.txt['confirmRemoveConf']%(mameExeName),icon='warning',title=cfg.txt['confirmRemoveConfTitle']%(mameExeName),parent=self) :
			self.mameExeTree.delete(idx)
			Mame.remove(mameExeName)
			
	def mameExeGuessVersion(self) :
		cnmen = self.newMameExeName.get()
		cnmev = self.newMameExeVersion.get()
		nmen, nmev = guessVersion(self.newMameExePath.get())
		if cnmev == '' or nmev != 'unknown' : self.newMameExeVersion.set(nmev)
		if cnmen == '' : self.newMameExeName.set(nmen)
		