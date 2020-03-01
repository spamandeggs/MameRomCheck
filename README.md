[ updated 1st of March 2020 ]

# MameRomCheck
yet another tool to manage Mame Roms - ui and api

it has a gui (tkinter or gtk) and an api. This is very early release, but non destructive,
since it only get informations and dont touch anything (for now..)

Goal is to Provide a 'simple' user interface and a python api to get efficient romset listing inside Mame
without weeks of self-education about how Mame work :
* check wether a rom is *really* playable (not only marked as *working*)
* check several romsets against several releases of Mame
* remove duplicates, move roms in the right place
* integrate into existing mame tools eco-system
* click on a romset and run the compatible Mame release.
* ...

Goal is not to compete with very powerful analysis tools like clrMamePro or romCenter.
But both needs a lot of self eductation about how Mame work, and so far I was not able to automatically check wether a romset 
is really playable or not / to only keep the playable romsets in my roms directories.

### environment(s) :
- Windows 10 for now

for GTK interface :
- python3.8.2 from mingw64
- the GTK library

for TKinter interface :
- python3.7+ for windows from python.org
- PIL (pip install pillow)

this should work in other context, provided you use a Python 3.7+ release, but didn't get the chance to test yet.

### installation :
- unzip master and open a cmd shell.
- it needs 3 files from the 7-zip project to run : these can be found in the 7zip 19.00 64-bit x64 version, on the 7-zip.org website :
[https://www.7-zip.org/download.html](https://www.7-zip.org/download.html). [direct download link](https://www.7-zip.org/a/7z1900-x64.exe)
- the 7z1900-x64.exe can be open as an archive with 7zip to get the files
- If you didnt have 7-zip then you should :). Install it (and uninstall winrar, winzip etc once confident).
- copy 7z.exe, 7z.dll and License.txt from in the ./bin directory
- cd to the top level of the directory then :

```
python bin
```
The GTK user interface will open

```
python bin/tk.py
```
The tkinter user interface will open. Please not I work first on the GTK ui for now, (2020/03/01)
so everything wont work as it should with tkinter.

#### add Mame installations
- click the add button under the Mame releases area and browse to your Mame64.exe runtime, 
- the guess release button should populate the name and version field (Version field is important you should let it as is)
- click ok : the Mame release is added. in the Romset folders view, the roms folder(s) defined in mame.ini should appear.
- the 'M' icon means the corresponding folder is used by the currently selected Mame release. Try to add another Mame release to get it.
- one can add additional romset folders which are not used by any Mame installation
- name and/or path MUST be different for Mame and folders, no duplicates.

#### list romsets
- click on a romset folder to see what it contains
- in the romsets view, click on a romset to populate some information. This makes use of the 7z.exe and dll files.
- the update button refresh the romset list if needed.
- the verify button test the romset with the currently selected Mame release.
- the verify all button test all the romsets of the current folder with the currently selected Mame release. this is multithreaded but this is uncompiled python code : is takes around 25 seconds for 800 romsets on a i7.
- use the save button to save the informations gathered.

#### run
- a romset will be ok if the driver is reported as 'good' in the romset view/driver column (but this need a couple more tests to be sure [bios tests, split romset etc...])
- try the 'Run with Mame xxx' button

#### important 
- when you close the application, you should see the python console. Type :
```
task.info()
```
if the tasks manager is stopped. you can
```
exit()
```
else wait a bit, the console will warn you when it's finished. or you can
```
task.stop()
```
then leave. If you don't, the python console will hang and you'll need to kill the python process from the task manager to close it.

### API

Actually the core code is apart from the interface so on could script operations or integrate in another python project.


to run and play from a python console :
```
python -i bin/mameromcheck.py
```

the ui's make use of the methods listed below, so can you.

```python
Mame.list()         # list your Mame Releases (ordered as in the conf.default.tab file and the ui)
Romdir.list()       # list your romset folders (ordered as in the conf.default.tab file and the ui)
m = Mame.get(0)     # get the first Mame installation you defined. Mame.get(name) also work.
m2 = Mame("C:\\ ... \\mame64.exe")  # create a new mame installation
m2.name = 'my Mame'                 # add a name if you want to save it later

m.run()             # run Mame
rd = Romdir.get(1)  # get the second romset folder you defined. with name also.
rd.romset.keys()    # romsets names in this folder
rd.populate()       # update the romset of this folder
rd.verify(0)        # silently run a -listxml Mame command on 
r = rd.romset['romsetname']  # get a romset
r.verify(0)         # verify it with the first Mame installation
m.activate()        # romsets will return verification results of the first Mame release ( since m = Mame.get(0) )
r.driver            # if 'good' is returned, then this should be ok for this release

r.verify(1)            # verify it with the second Mame installation
Mame.get(1).activate() # romsets will return verification results of the second installation
r.driver               # so this could be a different result than previously
r.run(0)               # run the romset with the first Mame release
r.description
r.roms              # dictionnary with rom information (crc)
...

task.info()     # infos about parrallel threads and current tasks
task.maxtasks   # max number of parrallel threads. used by ROmdir.verify(), default 5, use with caution (10 means 40% cpu on a i7 8gen. and is ok for me)
task.verbose    # True|False
...

cfg.save()      # save everything in conf/default.tab. file is human readable

[! WIP WIP WIP !]
