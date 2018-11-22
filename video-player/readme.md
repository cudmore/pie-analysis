## Video player

This is a Python based video player that allows frames to be annotated.

**Disclaimer**. As of November 2018, this is a work in progress and is updated daily.

## Screenshot

Video files are listed on top, annotations of current video on the left. Selecting an annotation from the list will snap the video to the frame of the annotation.

<IMG SRC="img/v2-interface.png" width=800>

## Keyboard commands

Controlling video

| Keyboard	| Action 
| -----		| -----
| space		| play/pause
| left/right arrows	| Backward/forward in video
| shift + left/right arrows	| Larger backward/forward in video
| +				| Play video faster, sets interval (ms)
| -				| Play video slower, sets interval (ms)

Editing annotations

| Keyboard	| Action 
| -----		| -----
| 1..9			| Create new annotation at current frame
| f				| Set first frame of selected event
| l				| Set last frame of selected event
| n				| Set note of current selected annotation

There are currently 9 different annotation types corresponding to keyboard 1, 2, 3, 4, 5, 6, 7, 8, 9.

## Saving annotations

All annotations are saved in a text file (.txt) with the same base name as the video file. For example

```
#
index,path,cseconds,type,frame,note,
0,/Users/cudmore/Dropbox/PiE/homecage-movie.mp4,1542328413.412974,1,367,,,
1,/Users/cudmore/Dropbox/PiE/homecage-movie.mp4,1542328419.127083,1,538,,,
2,/Users/cudmore/Dropbox/PiE/homecage-movie.mp4,1542328420.329067,2,574,,,
3,/Users/cudmore/Dropbox/PiE/homecage-movie.mp4,1542328422.295312,3,633,,,
4,/Users/cudmore/Dropbox/PiE/homecage-movie.mp4,1542330941.973472,2,788,,,
5,/Users/cudmore/Dropbox/PiE/homecage-movie.mp4,1542330942.505339,3,804,,,
```

## Install on macOS

Requires Python 3.7, Open CV 3, Pillow (PIL), Numpy

```
git clone https://github.com/cudmore/pie-analysis.git
cd pie-analysis
python3 -m env
source env/bin/activate
pip install -r requirements.txt
```

## Run

```
python player.py
```

## Detailed installation

	# install homebrew
	ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

	# upgrade to Python 3.7
	brew upgrade python
	
	# check Python 3.7 is installed, should return Python 3.7.1
	python3 --version
	
	# check pip3, should return
	# pip 18.1 from /usr/local/lib/python3.7/site-packages/pip (python 3.7)
	pip3 --version
	
	# add the following to profile using 'pico ~/.profile'
	# assuming username is 'cudmore', change as neccessary
	export PATH="$PATH:/Users/cudmore/Library/Python/3.7/bin"

	# activate the changes made to path
	source ~/.profile
	
	# clone repository
	git clone https://github.com/cudmore/pie-analysis.git
	
	# create a python 3 virtual environment 'env' and activate it
	# once activated, command line should begin with '(env)'
	cd pie-analysis/video-player
	python3 -m env
	source env/bin/activate
	
    # install with pip
    pip install -r requirements.txt

	# if needed, install opencv with brew
	brew install opencv3 --with-python3
    
Current working system has 'pip freeze'

```
numpy==1.15.4
opencv-python==3.4.3.18
Pillow==5.3.0
```

	
## Known bugs

 - Has some problems when it reaches end of file.
 - Resizing window will sometimes cause a crash
 
## To Do

 - Highlight most recent annotation in list as video is played.
 - Finish sorting annotation columns when clicked. Need to insert str(), int(), float() to do this.
 - Add note to video file by putting it in event list header. 
 - Running video faster/slower using +/- increments frame interval, it should increment frames per second (+/- 5 fps). This way user can get back to original fps. 

 - [done] Implement saving/loading options via JSON file. Include window geometry, show/hide, (MAYBE) mapping of annotation event numbers to names.
 - [done] toggle 'play' button to reflect state e.g. play and pause
 - [done] Add information about video file to saved event list .txt file, e.g. (path=xxx, numframes=yyy, fps=zzz)
 - [done] Expand code to open a folder of video files. Right now it is one hard-coded video file.
 - [done] Add standard video control buttons like play/pause/forward/backward/large-forward/large-backward.
 - [done] Finish setting annotation notes with keyboard 'n'.
 - [done] Write recipe for installation into Python virtual environment.
 - [done] Design system where annotations can have start/stop frames or start frame and number of frames (duration). Right now annotations only have single (start) frame.

 
## Learning Tkinter

https://www.inoreader.com/article/3a9c6e79a229d841-stack-abuse-gui-development-with-python-tkinter-an-introduction

https://www.pyimagesearch.com/2016/05/23/opencv-with-tkinter/

https://www.pyimagesearch.com/2016/05/30/displaying-a-video-feed-with-opencv-and-tkinter/

https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
