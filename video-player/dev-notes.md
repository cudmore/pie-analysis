## Development notes

### Other software

Take a look at [moviepy](https://zulko.github.io/moviepy/).

### Make a standalone application

## NOT GOOD [py2app](https://py2app.readthedocs.io/en/latest/)

App generated is too big, slow, and has some interface issues (leaving open folder dialog open)

The key here was to

 - don't use a virtual environment
 - pip3 uninstall opencv-python (it is experimental anyway)
 - brew install opencv
 - generate app with 'python3 setup.py py2app --packages=PIL'
 
#install
pip install py2app

#make setup.py
py2applet --make-setup src/VideoApp.py

#Setup file contains

```
from setuptools import setup

APP = ['src/VideoApp.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True}

setup(
    packages=['src'],
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

#remember to remove these before building
rm -rf build dist

#Compile development (not stand-alone)
python3 setup.py py2app -A

Compile distribution, fully stand-alone This did not work in a virtual environment (did not generate .app in dist/) but works fine without using virtualenv

# this had problems with 'from PIL import Image'
python3 setup.py py2app

# this worked
# after I uninstalled opencv-python and used 'brew install opencv'
python3 setup.py py2app --packages=PIL

#Run app from command line (to see errors)
dist/VideoApp.app/Contents/MacOS/VideoApp


## GOOD Using [pyinstaller](https://pythonhosted.org/PyInstaller/index.html)

Seems to work very well

```
cd src/
pyinstaller --windowed VideoApp.py 

# include an icon
# windows
pyinstaller --windowed --icon=app.ico VideoApp.py
# mac
# mac icons are ICNS: 128x128, 72 pixels/inch
pyinstaller --windowed --icon=videoapp.icns VideoApp.py

# remove previous before building
rm -rf build dist

# run from command line to see errors
dist/VideoApp.app/Contents/MacOS/VideoApp
```

Now, where to load/save options file?

VideoApp.app/Contents/MacOS

Now, how to make .app drag and drop

see: https://github.com/pyinstaller/pyinstaller/pull/3832

plutil -insert 'CFBundleURLTypes' -xml '<array><dict> <key>CFBundleURLName</key> <string>myscheme</string> <key>CFBundleURLSchemes</key> <array><string>myscheme</string></array> </dict></array>' -- dist/VideoApp.app/Contents/Info.plist

this makes drag and drop between tkinter window:
   https://svn.python.org/projects/python/trunk/Lib/lib-tk/Tkdnd.py
   
   
