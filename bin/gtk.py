import sys, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

import mameromcheck
from mameromcheck import *

def nextrow(start) :
	while True :
		yield start
		start += 1

class DialogAdd(Gtk.Dialog):

	def __init__(self, title, labels, extra_bts, parent):
		Gtk.Dialog.__init__(self, title, parent, 0)
		
		self.set_default_size(250, 100)
		self.set_border_width(10)
		
		self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		for bt, btresp in extra_bts :
			self.add_button(bt,btresp)
		self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)

		self.box = self.get_content_area()
		self.grid = Gtk.Grid()
		self.grid.set_row_spacing(5)
		self.grid.set_column_spacing(5)
		self.box.add(self.grid)
		
		self.entry = []
		
		row = nextrow(0)
		for lbl,default_text,checklist in labels :
			r = next(row)
			self.grid.attach(lbl,0,r,1,1)

			thisentry = Gtk.Entry()
			self.entry.append(thisentry)
			
			if default_text :
				thisentry.set_text(default_text)
			
			# thisentry.set_margin_top(10)
			# thisentry.set_margin_bottom(10)
			thisentry.set_has_frame(False)
			# print(thisentry.size_request)
			# thisentry.set_size_request(200,30)
			if checklist :
				thisentry.connect('activate',parent.check_entry,checklist)
				thisentry.connect('focus-out-event',parent.check_entry_event,checklist)
			
			self.grid.attach(thisentry,1,r,1,1)

		
class AppWindow(Gtk.ApplicationWindow):

	def __init__(self, app):
		Gtk.Window.__init__(self, title=title, application=app)
		
		self.set_default_size(250, 100)
		self.set_border_width(10)
		
		## icons
		self.icons = {}
		iconpth = os.path.join(pth_mrc,'icons')
		icons = {
			# file status
			'mame' : 'mame16x16.gif',
			'ok' : 'dot_green16x16.gif',
			'missing' : 'missing16x16.gif',
			'warning' : 'warning16x16.png',
			'error' : 'error16x16.png',
			'new' : 'new16x16.gif',
			# mame status
			'unknown' : 'dot_white16x16.gif',
			'-' : 'dot_white16x16.gif',
			'fixable' : 'fixable16x16.png',
			'wrong' : 'dot_red16x16.gif',
			'playable' : 'dot_green16x16.gif',
			}
		self.ico = {}
		for k,v in icons.items() :
			self.ico[k] = GdkPixbuf.Pixbuf.new_from_file(os.path.join(iconpth,v))

		buttons = {
				'run' : ['run',True],
				'add' : ['add',True],
				'edit' : ['edit',True],
				'del' : ['del',True],
				'addD' : ['add', True],
				'editD' : ['edit',True],
				'delD' : ['del',True],
				'verify' : ['romsetMameNone',False],
				'verifyAll' : ['romsetMameNone',False],
				'runR' : ['romsetMameNone',False],
				'save' : ['saveConfig',True],
				'guess' : ['guess',True],
			}
		self.bt = {}
		for k,v in buttons.items() :
			txt,state = v
			self.bt[k] = Gtk.Button(label=cfg.txt[txt])
			self.bt[k].connect("clicked", self.button_clicked,k)
			self.bt[k].set_sensitive(state)
			# button.set_can_focus(False)
			
		self.labels = {
			'mameTree' : 'mameExeFrameLabel',
			'romdirTree' : 'romdirFrameLabel',
			'romsetsTree' : 'romsetsFrameLabel',
			'romsetTree' : 'romsetFrameLabel',
			'tasks' : 'tasksFrameLabel',
			
			'addMameTitle' : 'addMameTitle',
			'editMameTitle' : 'editMameTitle',
			'addName' : 'addName',
			'addPath' : 'addPath',
			'addVersion' : 'addVersion',
			'guess' : 'guess',
		}
		self.lbl = {}
		for k,v in self.labels.items() :
			self.lbl[k] = Gtk.Label(
				label=cfg.txt[v],
				halign=Gtk.Align.START, # Gtk.Align.END,
				# angle=25, 
				)
		
		self.box = Gtk.Box(spacing=6)
		
		########
		# MAME #
		########
		
		## TREE
		coltypes = cfg.fields['mame']['coltypes']
		self.mameModel = Gtk.ListStore(*coltypes)
		self.mameTree = Gtk.TreeView(model=self.mameModel)

		for i, (colname,render) in enumerate(cfg.fields['mame']['colnames']):
			if render == 'text' :
				renderer = Gtk.CellRendererText()
				header = Gtk.TreeViewColumn(colname, renderer, text=i)
			elif render == 'icon' :
				renderer = Gtk.CellRendererPixbuf()
				header = Gtk.TreeViewColumn(colname,renderer)
				header.set_cell_data_func(renderer, self.get_tree_cell_pixbuf,i)
			self.mameTree.append_column(header)

		self.mame = self.mameTree.get_selection()
		self.mame.connect("changed", self.tree_select,Mame)
		
		## BUTTONS
		mameBt = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
		mameBt.set_layout(Gtk.ButtonBoxStyle.START)
		mameBt.set_spacing(5)
		for btname in ['add','edit','del','run'] :
			mameBt.add(self.bt[btname])
		
		##########
		# ROMDIR #
		##########
		
		## TREE
		self.romdirModel = Gtk.ListStore(str,str)
		self.romdirTree = Gtk.TreeView(model=self.romdirModel)

		for i, colname in enumerate([cfg.txt['colName'], cfg.txt['colPath']]):
			renderer = Gtk.CellRendererText()
			header = Gtk.TreeViewColumn(colname, renderer, text=i)
			self.romdirTree.append_column(header)

		romdirTreeSelect = self.romdirTree.get_selection()
		romdirTreeSelect.connect("changed", self.tree_select,Romdir)
		
		## BUTTONS
		romdirBt = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
		romdirBt.set_layout(Gtk.ButtonBoxStyle.START)
		romdirBt.set_spacing(5)
		for btname in ['addD','editD','delD'] :
			romdirBt.add(self.bt[btname])
		
		###########
		# ROMSETS #
		###########
		
		## TREE
		coltypes = cfg.fields['romsets']['coltypes']
		self.romsetsModel = Gtk.ListStore(*coltypes)
		self.romsetsTree = Gtk.TreeView(model=self.romsetsModel)

		for i, (colname,render) in enumerate(cfg.fields['romsets']['colnames']) :
			if render == 'text' :
				renderer = Gtk.CellRendererText()
				header = Gtk.TreeViewColumn(colname, renderer, text=i)
			elif render == 'icon' :
				renderer = Gtk.CellRendererPixbuf()
				header = Gtk.TreeViewColumn(colname,renderer)
				header.set_cell_data_func(renderer, self.get_tree_cell_pixbuf,i)
			self.romsetsTree.append_column(header)

		self.romsetsTreeSelect = self.romsetsTree.get_selection()
		self.romsetsTreeSelect.connect("changed", self.tree_select,Romdir,'romset')
		
		## BUTTONS
		romsetsBt = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
		romsetsBt.set_layout(Gtk.ButtonBoxStyle.START)
		romsetsBt.set_spacing(5)
		for btname in ['verify','verifyAll','runR'] :
			romsetsBt.add(self.bt[btname])		
			
		# Gtk.ButtonBoxStyle.START
		# Gtk.ButtonBoxStyle.EXPAND
		
		##########
		# ROMSET #
		##########
		
		## TREE
		self.romsetModel = Gtk.ListStore(str,str,str)
		self.romsetTree = Gtk.TreeView(model=self.romsetModel)
	
		for i, colname in enumerate([
			cfg.txt['colName'],
			# cfg.txt['colSize'],
			cfg.txt['colCRC'],
			# cfg.txt['colComment'],
			cfg.txt['colStatus'],
			]):
			renderer = Gtk.CellRendererText()
			header = Gtk.TreeViewColumn(colname, renderer, text=i)
			self.romsetTree.append_column(header)

		romsetTreeSelect = self.romsetTree.get_selection()
		romsetTreeSelect.connect("changed", self.tree_select,Romset,'roms')
		
		## BUTTONS
		romsetBt = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
		romsetBt.set_spacing(5)
		romsetBt.set_layout(Gtk.ButtonBoxStyle.START)
		# for btname in [...] :
			# romsetsBt.add(self.bt[btname])
			
		########
		# MAIN #
		########
		
		mainBt = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
		mainBt.set_layout(Gtk.ButtonBoxStyle.START)
		mainBt.set_spacing(5)
		for btname in ['save'] :
			mainBt.add(self.bt[btname])		
		
		#########
		# TASKS #
		#########
		
		self.tasks = odict()
		self.tasksbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
		
		########
		# GRID #
		########
		
		self.grid = Gtk.Grid()
		self.grid.set_row_spacing(10)
		self.grid.set_column_spacing(10)
		self.add(self.grid)
		
		col = 0
		row = nextrow(0)
		self.grid.attach(self.lbl['mameTree'],col,next(row),1,1)
		self.grid.attach(self.mameTree,col,next(row),1,1)
		self.grid.attach(mameBt,col,next(row),1,1)
		
		self.grid.attach(self.lbl['romdirTree'],col,next(row),1,1)
		self.grid.attach(self.romdirTree,col,next(row),1,1)
		self.grid.attach(romdirBt,col,next(row),1,1)
		
		self.tasksbox.pack_start(self.lbl['tasks'], True, True, 0)
		self.grid.attach(self.tasksbox,col,next(row),1,1)
		
		self.grid.attach(mainBt,0,next(row),1,1)
		
		col += 1
		row = nextrow(0)
		self.grid.attach(self.lbl['romsetsTree'],col,next(row),1,1)
		self.romsetsTreeScroll = Gtk.ScrolledWindow()
		# self.romsetsTreeScroll.set_vexpand(True)
		self.grid.attach(self.romsetsTreeScroll,col,next(row), 5, 4)
		self.romsetsTreeScroll.add(self.romsetsTree)
		row = nextrow(5)
		self.grid.attach(romsetsBt,col,next(row),1,1)

		col += 5
		row = nextrow(0)
		self.grid.attach(self.lbl['romsetTree'],col,next(row),1,1)
		self.romsetTreeScroll = Gtk.ScrolledWindow()
		# self.romsetsTreeScroll.set_vexpand(True)
		self.grid.attach(self.romsetTreeScroll,col,next(row), 5, 4)
		self.romsetTreeScroll.add(self.romsetTree)
		row = nextrow(5)
		self.grid.attach(romsetBt,col,next(row),1,1)
		
		# keep instance upon which tasks are running
		self.mamePending = None
		self.romdirPending = None
		self.romsetPending = None
		
		############
		# POPULATE #
		############
		
		## mame
		for m in Mame.getall() :
			self.mameModel.append(m.fields())
		## romdir
		for d in Romdir.getall() :
			self.romdirModel.append([d.name,d.path])
	
	## all tree actions
	def get_tree_cell_pixbuf(self, col, cell, model, iter, fieldid):
		cell.set_property('pixbuf', self.ico[model.get_value(iter, fieldid)])

	def tree_truncate(self,tree,elm=False) :
		treeModel = tree.get_model()
		if elm : elm.desactivate()
		if len(treeModel) != 0:
			for i in range(len(treeModel)):
				iter = treeModel.get_iter(0)
				treeModel.remove(iter)
		if elm : elm.activate()
		
	def tree_select(self,selection,cls,attr=False) :
		model, treeiter = selection.get_selected() # treeiter is a Gtk.TreeIter object 'copy', 'free', 'stamp', 'user_data', 'user_data2', 'user_data3'
		# when at a previous tic a tree was truncated,
		# 'changed' signals are sent to the child tree at each tree_truncate() iter
		# we want to ignore them with this update switch
		update = False
		if treeiter is not None:
			selname = model[treeiter][0]
			if not(attr) :
				update = True
				inst = cls.get(selname)
				print('tree_select : %s, class %s, inst %s'%(selname,cls,inst.name))
				lastinst = cls.getActive()
				if lastinst : print('previous selection was %s'%(lastinst.name))
				inst.activate()
				
				if isinstance(inst,Mame) and Romdir.getActive() :
					mameflds = cfg.fields['romsets']['mame']
					rd = Romdir.getActive()
					for r in self.romsetsModel :
						s = rd.romset[r[0]]
						for col,fld in mameflds :
							r[col] = getattr(s,fld)
						
					# treeiter = self.romsetsModel.get_iter((0,))
					# selname = self.romsetsModel[treeiter][0]
					# self.romsetsModel[treeiter][2] = 'yes'
			
				## when selection is a romdir, update romsets view
				if isinstance(inst,Romdir) :
					self.tree_truncate(self.romsetsTree,inst)
					for sn, s in inst.romset.items() :
						self.romsetsModel.append(s.fields())
					self.lbl['romsetsTree'].set_text(cfg.txt[self.labels['romsetsTree']]%(inst.name,len(self.romsetsModel)))
				
					self.tree_truncate(self.romsetTree)
					
			else :
				inst = cls.getActive()
				if inst :
					update = True
					dico = getattr(inst,attr)
					elm = dico[selname]
					
					if type(elm) == odict : elmname = selname # ie Romset.roms
					else : elmname = elm.name # ie Romdir.romset
					
					print('tree_select : %s, class %s, %s.%s, elm %s'%(selname,cls,inst.name,attr,elmname))
					
					## when selection is a romset (in romsetS view), update romset view
					if isinstance(elm,Romset) :
						# elm.desactivate()
						self.tree_truncate(self.romsetTree,elm)
						for rn,r in elm.roms.items() :
							self.romsetModel.append([
								rn,
								str(r['crc']),
								str(elm.status),
								])
						self.lbl['romsetTree'].set_text(cfg.txt[self.labels['romsetTree']]%(elm.name,inst.name))
						# elm.activate()
					## selection is a rom
					else :
						cfg.activeRom = elmname
				
		else :
			inst = cls.getActive()
			if not(attr) :
				update = True
				inst.desactivate()
				print('deselected class %s inst %s'%(cls,inst.name))
				if isinstance(inst,Romdir) :
					self.tree_truncate(self.romsetsTree,inst)
					self.tree_truncate(self.romsetTree)
					
			elif inst :
				update = True
				dico = getattr(inst,attr)
				if len(dico) :
					elm = dico[list(dico.keys())[0]]
					if type(elm) == odict : elmname = cfg.activeRom # ie Romset.roms
					else : elmname = elm.name # ie Romdir.romset
					print('deselected class %s inst %s elm %s'%(cls,inst.name,elmname))
					
					if isinstance(elm,Romset) :
						elm.desactivate()
						self.tree_truncate(self.romsetTree)
					else :
						cfg.activeRom = None
		
		if update :
			## button states and labels updates
			if Mame.getActive() and Romdir.getActive() and len(Romdir.getActive().romset) :
				self.bt['verify'].set_sensitive(True)
				self.bt['verifyAll'].set_sensitive(True)
				if Romset.getActive() :
					self.bt['verify'].set_sensitive(True)
					self.bt['runR'].set_sensitive(True)
				else :
					self.bt['verify'].set_sensitive(False)
					self.bt['runR'].set_sensitive(False)
			else :
				self.bt['verify'].set_sensitive(False)
				self.bt['verifyAll'].set_sensitive(False)
				self.bt['runR'].set_sensitive(False)
			if Mame.getActive() :
				self.bt['run'].set_sensitive(True)
				self.bt['edit'].set_sensitive(True)
				self.bt['del'].set_sensitive(True)
			else :
				self.bt['run'].set_sensitive(False)
				self.bt['edit'].set_sensitive(False)
				self.bt['del'].set_sensitive(False)
			if Romdir.getActive() :
				self.bt['editD'].set_sensitive(True)
				self.bt['delD'].set_sensitive(True)
			else :
				self.bt['editD'].set_sensitive(False)
				self.bt['delD'].set_sensitive(False)
		
			print('active mame	 %s'%Mame.getActive())
			print('active romdir %s'%Romdir.getActive())
			print('active romset %s'%Romset.getActive())
			print('active rom	 %s'%cfg.activeRom)
			
			# print('selection mode %s'%selection.props.mode)
			# print(dir(self.bt['runR'].props))
			
			# verify all romsets with ...
			if self.bt['verifyAll'].get_sensitive() : txt = cfg.txt['romsetVerifyAll']%(Mame.getActive().name)
			else : txt = cfg.txt['romsetMameNone']
			self.bt['verifyAll'].set_label(txt)
			
			# verify romset with ...
			if self.bt['verify'].get_sensitive() : txt = cfg.txt['romsetVerify']%(Mame.getActive().name)
			else : txt = cfg.txt['romsetMameNone']
			self.bt['verify'].set_label(txt)
			
			# run romset with ...
			if self.bt['runR'].get_sensitive() : txt = cfg.txt['romsetRun']%(Mame.getActive().name)
			else : txt = cfg.txt['romsetMameNone']
			self.bt['runR'].set_label(txt)
	
	## display callbacks
	def romset_verified(self,tskname,romset) :
		flds = tskname.split('\\')
		tskname = '\\'.join(flds[:-1])
		romsetname = flds[-1]
		self.tasks_update(tskname)
		if Romdir.getActive() == self.tasks[tskname]['romdir'] :
			for r in self.romsetsModel :
				if r[0] == romset.name :
					for col,fld in enumerate(cfg.fields['romsets']['public']) :
						r[col] = getattr(romset,fld)
					break
		
	def all_romset_verified(self,*args) :
		tskbasename,status,count,total,since,duration = args
		print('all_romset_verified : %s/%s %s'%(count,total,status))
		self.tasks_done(tskbasename,since,duration)
	
	## display callbacks subs about progressbars
	def tasks_add(self,mameinst,romdirinst,tsktype,total,*args) :
		# give it a unique temporary name.
		tskname = cfg.tasksname(tsktype,mameinst.name,romdirinst.name)
		tsk = self.tasks[tskname] = {
				'progress' : 0,
				'total' : total,
				'mame' : mameinst,
				'romdir' : romdirinst,
			}
		
		tsk['bar'] = Gtk.ProgressBar()
		if tsktype == 'verify' :
			pbartxt = cfg.txt['task.%s.wait'%tsktype]%(0,total,romdirinst.name,mameinst.name)
		tsk['bar'].set_text(pbartxt)
		tsk['bar'].set_show_text(True)
		tsk['bar'].set_fraction(0.0)
		self.tasksbox.pack_start(tsk['bar'], True, True, 0)
		tsk['bar'].show()

		# no active task, run it immediately
		if tskname == list(self.tasks.keys())[0] :
			self.tasks_run(tskname)
		
	def tasks_run(self,tskname,*args) :
		tsktype = tskname.split('\\')[0]
		if tsktype == 'verify' :
			print('run %s'%tskname)
			m = self.tasks[tskname]['mame']
			rd = self.tasks[tskname]['romdir']
			rd.verify(m.name,self.romset_verified,self.all_romset_verified)
		
	def tasks_update(self,tskname,*args) :
		tsk = self.tasks[tskname]
		tsk['progress'] += 1
		tsktype = tskname.split('\\')[0]
		pbartxt = cfg.txt['task.%s'%tsktype]%(tsk['progress'],tsk['total'],tsk['romdir'].name,tsk['mame'].name)
		tsk['bar'].set_text(pbartxt)
		v = tsk['progress']/tsk['total']
		tsk['bar'].set_fraction(v)
	
	def tasks_done(self,tskname,*args) :
		tsktype = tskname.split('\\')[0]
		tsk = self.tasks[tskname]
		pbartxt = cfg.txt['task.%s.done'%tsktype]%(tsk['progress'],tsk['total'],tsk['romdir'].name,tsk['mame'].name)
		tsk['bar'].set_text(pbartxt)
		print('task.%s verif : %s/%s'%(tskname,self.tasks[tskname]['progress'],self.tasks[tskname]['total']))
		tsk['bar'].set_sensitive(False)
		del(self.tasks[tskname])
		if len(self.tasks) :
			nexttaskname = list(self.tasks.keys())[0]
			self.tasks_run(nexttaskname)
	
	def check_entry_event(self,widget,event,existing) :
		print('check_entry event')
		self.check_entry(widget,existing)
		
	def check_entry(self,widget,existing) :
		print('check_entry %s %s'%(widget,existing))
		if widget.get_text().lower() in existing :
			print('exist')
			pass
		
	## all buttons actions
	def button_clicked(self, widget,btname,*args):
		print('button %s clicked'%(btname))
		if btname == 'run' :
			Mame.getActive().run()
		
		elif btname in ['add','edit'] :
			
			if btname == 'add' :
				dialog_title = cfg.txt['addMameTitle']
				Mamename = None
				Mamepath = None
				Mameversion = None
			else :
				dialog_title = cfg.txt['editMameTitle']
				m = Mame.getActive()
				Mamename = m.name
				Mamepath = m.path
				Mameversion = m.version
				
			self.existingmame = []
			self.existingmamepath = []
			for m in Mame.getall() :
				if Mamename != m.name : self.existingmame.append(m.name.lower())
				if Mamepath != m.path : self.existingmamepath.append(m.path.lower())
			
			dialog = DialogAdd(
					dialog_title,
					[
					[self.lbl['addName'],Mamename,self.existingmame],
					[self.lbl['addPath'],Mamepath,self.existingmamepath],
					[self.lbl['addVersion'],Mameversion,None]
					],
					[[cfg.txt['guess'],10]],
					self
				)

			select_mame_exe = Gtk.Button(label="...")
			select_mame_exe.connect("clicked", self.button_clicked,'mamefile',dialog.entry[1])
		
			dialog.grid.attach(select_mame_exe,2,1,1,1)
			
			dialog.show_all()
			
			destroy = False
			while not(destroy) :
				response = dialog.run()
				
				print('response %s'%response)
				
				if response == Gtk.ResponseType.OK:
					if btname == 'add' :
						newm = Mame(dialog.entry[1].get_text(),dialog.entry[0].get_text())
						newm.version = dialog.entry[2].get_text()
						print(newm.path)
						if isinstance(newm,Mame) :
							r = [getattr(newm,fld) for fld in cfg.fields['mame']['public']]
							self.mameModel.append(r)
							destroy = True
					else :
						m = Mame.getActive()
						mpreviousname = m.name
						# a name exist ? check is done in the Mame.name setter,
						# so this avoid a False positive
						if dialog.entry[0].get_text() != mpreviousname :
							m.name = dialog.entry[0].get_text()
						m.path = dialog.entry[1].get_text()
						m.version = dialog.entry[2].get_text()
						for r in self.mameModel :
							if r[0] == mpreviousname :
								for col,fld in enumerate(cfg.fields['mame']['public']) :
									r[col] = getattr(m,fld)
									destroy = True
									break
				
				elif response in [Gtk.ResponseType.CANCEL,-4]:
					print("The Cancel button was clicked")
					destroy = True
				elif response == 10:
					print("The guess button was clicked")
			
			dialog.destroy()
			
		elif btname == 'del' :			
			
			(model, iter) = self.mame.get_selected()
			if iter is not None:
				print("%s has been removed" % (model[iter][0]))
				self.mameModel.remove(iter)
				m = Mame.getActive()					
				Mame.remove(m.name)
			else:
				print("Select a title to remove")
			
		elif btname == 'mamefile' :
			dialog = Gtk.FileChooserDialog(title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN) #,

			dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
			dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)

			filter_mame = Gtk.FileFilter()
			filter_mame.set_name("Mame executable")
			filter_mame.add_pattern("mame*.exe")
			dialog.add_filter(filter_mame)

			filter_any = Gtk.FileFilter()
			filter_any.set_name("All")
			filter_any.add_pattern("*")
			dialog.add_filter(filter_any)
		
			response = dialog.run()
			if response == Gtk.ResponseType.OK:
				args[0].set_text(dialog.get_filename())
				self.check_entry(args[0],self.existingmamepath)
				
			elif response == Gtk.ResponseType.CANCEL:
				print("Cancel clicked")

			dialog.destroy()
		
		elif btname == 'addD' : 
			pass
		elif btname == 'editD' :
			pass
		elif btname == 'delD' : 
			pass
		elif btname == 'verify' :
			MameName = Mame.getActive().name
			s = Romset.getActive()
			print('ask to verify romset %s in %s'%(s.name,MameName))
			self.romsetnames = [ row[0] for row in self.romsetsModel ]
			s.verify(MameName)
			
		# a task is defined by the implicated instances and an action
		# self.tasks_add(Mame inst,Romdir inst,task.taskname,args)
		elif btname == 'verifyAll' :
			m = Mame.getActive()
			rd = Romdir.getActive()
			print('ask to verify all romsets in %s with %s'%(rd.name,m.name))
			self.tasks_add(m,rd,'verify',len(self.romsetsModel))
			
		elif btname == 'runR' :
			MameName = Mame.getActive().name
			s = Romset.getActive()
			print('ask to run romset %s in %s'%(s.name,MameName))
			s.run(MameName)

		elif btname == 'save' : 
			cfg.save()		
	
class App(Gtk.Application):

	def __init__(self):
		Gtk.Application.__init__(self)

	def do_activate(self):
		win = AppWindow(self)
		win.show_all()

	def do_startup(self):
		Gtk.Application.do_startup(self)

app = App()
exit_status = app.run(sys.argv)
sys.exit(exit_status)