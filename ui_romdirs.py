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

#####################
## romdirs dialogs ##
#####################

from ui_mameexes import *



class UI_romdirs(UI_mameexes) :
	
	def romdirAddDialog(self) :
		self.romdirAddEditDialog()
		self.romdirAddDialogRoot.title(cfg.txt['addRomdirTitle'])
		self.romdirInst = None
		self.treetag = None

		self.newRomdirNameLast = ''
		self.newRomdirPathLast = ''
		
		

	def romdirEditDialog(self) :
		idx,romdirName,romdirPath = selectedItem(self.romdirTree)
		if idx != None :
			self.romdirAddEditDialog()
			self.romdirAddDialogRoot.title(cfg.txt['EditRomdirTitle'])
			
			self.romdirInst = Romdir.get(romdirName)
			
			# self.romdirEdited = romdirName
			# self.romdirKey = selectedRomdir(romdirName,'key')
			
			self.newRomdirName.set(romdirName)
			self.newRomdirPath.set(romdirPath)
			
			
			self.treetag = idx

			self.newRomdirNameLast = romdirName
			self.newRomdirPathLast = romdirPath
			
			
	def romdirAddEditDialog(self) :
		self.romdirAddDialogRoot = Toplevel(self)
		self.romdirAddDialogRoot.grab_set()
		self.romdirAddDialogRoot.resizable(FALSE,FALSE)
		
		romdirAddDialogNameLabel = ttk.Label(self.romdirAddDialogRoot, text=cfg.txt['addName']) # todo apparait pas
		
		self.newRomdirName = StringVar()
		romdirAddDialogName = ttk.Entry(self.romdirAddDialogRoot, textvariable=self.newRomdirName)
		romdirAddDialogName.bind('<FocusIn>',self.newRomdirNameStore)
		romdirAddDialogName.bind('<FocusOut>',self.newRomdirNameCheck)
		
		self.newRomdirPath = StringVar()
		romdirAddDialogPathLabel = ttk.Label(self.romdirAddDialogRoot, text=cfg.txt['addPath'])
		romdirAddDialogPath = ttk.Entry(self.romdirAddDialogRoot, textvariable=self.newRomdirPath)
		romdirAddDialogPath.bind('<FocusIn>',self.newRomdirPathStore)
		romdirAddDialogPath.bind('<FocusOut>',self.newRomdirPathCheck)
		romdirAddDialogPathButton = ttk.Button(self.romdirAddDialogRoot, text="browse", command=self.romdirAddPathDialog )
		
		
		
		
		
		romdirAddDialogCancel = ttk.Button(self.romdirAddDialogRoot, text=cfg.txt['cancel'], command=self.romdirAddDialogClose )
		romdirAddDialogOk = ttk.Button(self.romdirAddDialogRoot, text=cfg.txt['ok'], command=self.romdirAddDialogNew )
		
		# ui geometry
		romdirAddDialogNameLabel.grid(column=0, row=0, sticky=(N,S,E,W))
		
		romdirAddDialogName['width']=40
		romdirAddDialogName.grid(column=0, row=1, sticky=(N,S,E,W))
		romdirAddDialogPathLabel.grid(column=0, row=2, sticky=(N,S,E,W))
		
		romdirAddDialogPath['width']=40
		romdirAddDialogPath.grid(column=0, row=3, sticky=(N,S,W))
		romdirAddDialogPathButton.grid(column=1, row=3, sticky=(N,S,E))
		
		
		
		
		romdirAddDialogCancel.grid(column=0, row=6, sticky=(N,S,W))
		romdirAddDialogOk.grid(column=1, row=6, sticky=(N,S,E))
	
	# mame edit/add ok button : add value, or reinsert in the list when edit mode
	def romdirAddDialogNew(self) :
		newRomdirName = self.newRomdirName.get().strip()
		# checks
		if not(newRomdirName) :
			messagebox.showerror(message=cfg.txt['errorNameEmptyRomdir'],icon='warning',title=cfg.txt['errorNameEmptyTitle'],parent=self.romdirAddDialogRoot)
			return
		nmep = self.newRomdirPath.get()
		if not(nmep) :
			messagebox.showerror(message=cfg.txt['errorPathEmptyRomdir'],icon='warning',title=cfg.txt['errorPathEmptyTitle'],parent=self.romdirAddDialogRoot)
			return
		
		# update source dict
		# romdirs[newRomdirName] = {'path':nmep,'version':self.newRomdirVersion.get()}
		# add
		if self.romdirInst == None :
			Romdir(nmep,newRomdirName)
			tag = self.romdirTree.insert('', 'end', text=newRomdirName, tags=self.romdirTags)
		# edit
		else :
			self.romdirInst.name = newRomdirName
			self.romdirInst.path = nmep
			
			tag = self.treetag
			self.romdirTree.item(tag,text=newRomdirName)
			
		self.romdirTree.set(tag,'path',nmep)
		
		self.treetag = None
		self.romdirAddDialogClose()
	
	# mame edit/add cancel button
	# if edit mode, self.treetag is an index (int) : write back the original values
	def romdirAddDialogClose(self) :
		self.romdirAddDialogRoot.grab_release()
		self.romdirAddDialogRoot.destroy()
		
	def romdirAddPathDialog(self) :
		self.romdirAddDialogRoot.withdraw()
		romdirPath = filedialog.askdirectory(initialdir = self.lastdir,title = cfg.txt['addPathTitleRomdir'])
		
		if self.newRomdirPathCheck(romdirPath) :
			self.newRomdirPath.set(romdirPath)
		
		self.romdirAddDialogRoot.deiconify()

	# store previous entries of add/edit dialogs in case of user error
	def newRomdirNameStore(self,event) :
		self.newRomdirNameLast = self.newRomdirName.get()
	
	def newRomdirPathStore(self,event) :
		self.newRomdirPathLast = self.newRomdirPath.get()

	# check romdir Name and path when added
	def newRomdirNameCheck(self,event) :
		newRomdirName = self.newRomdirName.get().strip()
		nametest = [fld.lower() for fld in Romdir.getall('name')]
		# print('check name %s romdirs names : %s. edited is %s'%(newRomdirName,newRomdirName.lower() in nametest,'' if type(self.romdirInst) == None else self.romdirInst.name))
		if newRomdirName.lower() in nametest and (not(self.romdirInst) or newRomdirName.lower() != self.romdirInst.name.lower()) :
			messagebox.showerror(message=cfg.txt['errorNameExistRomdir'],icon='warning',title=cfg.txt['errorNameExistTitle'],parent=self.romdirAddDialogRoot)
			self.newRomdirName.set(self.newRomdirNameLast)
			return False
		self.newRomdirName.set(newRomdirName)
		return True

	def newRomdirPathCheck(self,newRomdirPath) :
		if type(newRomdirPath) != str : newRomdirPath = self.newRomdirPath.get().strip()
		if not(newRomdirPath) : return False
		newRomdirPath = pathconform(newRomdirPath)
		nametest = [fld.lower() for fld in Romdir.getall('path')]
		
		if newRomdirPath in nametest and (not(self.mameExeInst) or newRomdirPath.lower() != self.romdirInst.path.lower()) :
			messagebox.showerror(message=cfg.txt['errorPathExistRomdir'],icon='warning',title=cfg.txt['errorPathExistTitle'],parent=self.romdirAddDialogRoot)
			self.newRomdirPath.set(self.newRomdirPathLast)
			return False
		if not(os.path.isdir(newRomdirPath)) :
			messagebox.showerror(message=cfg.txt['errorPathWrong'],icon='warning',title=cfg.txt['errorPathWrongTitle'],parent=self.romdirAddDialogRoot)
			self.newRomdirPath.set(self.newRomdirPathLast)
			return False
		self.newRomdirPath.set(newRomdirPath)
		self.lastdir = os.path.dirname(newRomdirPath)
		if not(self.newRomdirName.get()) :
			self.newRomdirName.set(os.path.basename(newRomdirPath))
		return True

	## romdir delete dialog
	def romdirDelDialog(self) :
		idx,romdirName,romdirPath = selectedItem(self.romdirTree)
		if idx != None and messagebox.askyesno(message=cfg.txt['confirmRemoveConf']%(romdirName),icon='warning',title=cfg.txt['confirmRemoveConfTitle']%(romdirName),parent=self) :
			self.romdirTree.delete(idx)
			Romdir.remove(romdirName)