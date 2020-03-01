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

from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


# parent :
#	tkinter container
# datas :
#	dict/ordered dict {k:dict,k2:dict2}
#	with k displayed name of the 1st column 
#	and dict the infos that could be displayed
# columns :
#	ordered dict {'col internal name' : 'col displayed name'}
#	with col internal name corresponding to some of the keys in dict
# tags :
#	list of tree tags
def buildTree(parent,datas,columns,tags) :
	headers = list(columns.keys())
	tree = ttk.Treeview(parent, columns=headers[1:])
	tree.heading('#0', text=columns[headers[0]],command=treeColumnOrder)
	for k in headers[1:] :
		tree.heading(k, text=columns[k],command=treeColumnOrder)
	populateTree(tree,datas,headers,tags) 
	return tree

def populateTree(tree,datas,headers,tags,icon=False) :
	tree.delete(*tree.get_children())
	if len(datas.values()) :
		firstvalue = list(datas.values())[0]
		if isinstance(firstvalue,dict) :
			tkid=0
			for k,v in datas.items() :
				sid = str(tkid)
				if 'tags' in datas : 
					print('tags ! %s'%datas['tags'])
					thesetags = datas['tags']
				else : thesetags = tags
				tree.insert('',"end",tkid, text=k, tags=thesetags)
				# id = tree.insert('', 'end', text=k, tags=tags)
				for k2 in headers[1:] :
					tree.set(tkid, k2, v[k2])
				tkid+=1
		# datas as a class instance
		elif isinstance(type(firstvalue),type) :
			tkid=0
			for k,v in datas.items() :
				sid = str(tkid)
				if hasattr(v,'tags') and getattr(v,'tags') != '' :
					# print('tags ! %s'%getattr(v,'tags'))
					thesetags = getattr(v,'tags')
				else : thesetags = tags
				tree.insert('',"end",tkid, text=k, tags=thesetags)
				# id = tree.insert('', 'end', text=k, tags=tags)
				for k2 in headers[1:] :
					tree.set(tkid, k2, getattr(v,k2))
				if icon :
					tree.set(tkid, k2,'☺')
				tkid+=1
	
	return tree

# given a Listbox object, returns the id and the displayed string
# of the selected item
# given a Tree object, returns ...
def selectedItem(widget) :
	# print(type(widget))
	typw = type(widget)
	if typw == ttk.Treeview :
		sel = widget.focus()
		if sel != None :
			itm = widget.item(sel)
			rtn = [sel,itm['text']]
			rtn.extend(itm['values'])
			# print(rtn)
			return rtn
		return None
	elif typw == Listbox :
		idxs = widget.curselection()
		if not(idxs) : return (None, None)
		if len(idxs) == 1:
			return (idxs[0],widget.get(idxs[0]))
		else :
			print('todo, multiselect !')
			return (None, None)
	
def treeColumnOrder() :
	print('treeColumnOrder')

def rowaddfrom(start) :
	while True :
		yield start
		start += 1

# tag = tree.focus()
# tag = tree.selection()[0]
# x = tree.get_children()

## changer texte label :
# resultsContents = StringVar()
# label['textvariable'] = resultsContents
# resultsContents.set('New value to display')

## change label color
# from tkinter  import *
# def colourUpdate():
	# colour.set('red' if colour.get()!='red' else 'blue')
	# # print colour.get()
	# l.configure(fg=colour.get())

# root = Tk()
# colour = StringVar()
# colour.set('red')
	
# btn = Button(root, text = "Click Me", command = colourUpdate)
# l = Label(root, textvariable=colour, fg = colour.get())
# l.pack()
# btn.pack()
# root.mainloop()