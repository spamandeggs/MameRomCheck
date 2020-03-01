# mameromcheck specific
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
# with python mingw, the local path sep is \, while the inherited path are /
# with a static pyinstaller build, path ar \ as os.sep
# when generating static with pyinstaller, it zips the main python lib,
# and the first sys.path is static\base_library.zip
# so we need to go two levels up rather than one to load mrc bin
from sys import path as _spth
if _spth[0].split('\\')[-1] == 'base_library.zip' :
	pth='/'.join(_spth[0].split('\\')[:-2])
else :
	pth='/'.join(_spth[0].split('\\')[:-1])
_spth.append(pth)
print('python module paths :')
for pth in _spth :
	print(' ',pth)
import bin