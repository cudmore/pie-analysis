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

## Menus

 - **File**. Open Folder, Open Chunks, Save Options, Quit
 - **Window**. Toggle interface on/off for: video files, events, video feedback, chunks
 
## Saving annotations

All events are automatically saved in a text file (.txt) with the same base name as the video file. One events .txt file per video file. The events file is saved when new events are created or edited (first/last frame, note, file video note).

First line in events file is comma separated parameters. Second line is column headers. Remaining lines in file are event with one event per line. For example:

```
#
path=/Users/cudmore/Dropbox/PiE/video/1-homecage-movie.mp4,fileName=1-homecage-movie.mp4,width=640.0,height=480.0,aspectRatio=0.75,fps=15.0,numFrames=4500,numSeconds=300.0,numEvents=68,videoFileNote=,
index,path,cseconds,type,frameStart,frameStop,note,
0,/Users/cudmore/Dropbox/PiE/video/1-homecage-movie.mp4,1542723509.0230012,1,21,21,xxx,,
1,/Users/cudmore/Dropbox/PiE/video/1-homecage-movie.mp4,1542724942.9451919,2,50,253,,,
2,/Users/cudmore/Dropbox/PiE/video/1-homecage-movie.mp4,1542814082.8857589,5,737,1020,,,
3,/Users/cudmore/Dropbox/PiE/video/1-homecage-movie.mp4,1542821655.198092,1,1407,,,,
4,/Users/cudmore/Dropbox/PiE/video/1-homecage-movie.mp4,1542821684.321075,1,1732,,,,
5,/Users/cudmore/Dropbox/PiE/video/1-homecage-movie.mp4,1542821768.373924,4,1274,,,,
```

## Blinding

<IMG SRC="img/chunks-interface.png" width=600>

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
 - Resizing window will sometimes cause a crash.
 
## To Do

 - [bug] frame slider gets corrupted and does not move during chunk editing
 - [bug] Make sure video controls (buttons and keyboard) stay within chunk when 'Limit Controls' is on.
 - Highlight most recent annotation in list as video is played.
 - Finish sorting annotation columns when clicked. Need to insert str(), int(), float() to do this.
 - Add note to video file by putting it in event list header. Finish 'right-click' popup menu in video list.
 - Add option to warn when event frame start/stop is out of order, e.g. frameStart>frameStop.
 - [big idea] Make a visual bar for each video file showing: duration (black) overlaid .with position of chunks (gray), and position of events (bright colors). 
 - [bug] Make sure chunk navigation is working: >, <, go to.
 - [bug] Make sure toggle of video file and event list do not trash interface on next run. Need to add code to HIDE video and event list, currently setting sashpos==0 (remove this).
 - [bug] When increasing/decreasing fps with +/-, sometimes can not get back to orignal fps. Fix this. This is now fixed but minimum fps is no longer 1 fps.

20181128

 - Recalculate chunkIndex when setting event startFrame with keyboard 'f'
 
## To Do (done)

 - [done] Need some way to 1) categorize/file each event into its chunk 2) detect events falling outside a chunk.
 - [done] During chunk editing, hijack ALL video controls (frame slider, play, >, >>, <, <<) to only allow scrolling through frames in current chunk.
 - [done] Add checkbox to activate/inactivate chunk editing.
 - [done] Running video faster/slower using +/- increments frame interval, it should increment frames per second (+/- 5 fps). Maximum fps for tkinter seems to be ~90 fps. 
 - [done] Implement saving/loading options via JSON file. Include window geometry, show/hide, (MAYBE) mapping of annotation event numbers to names.
 - [done] Toggle 'play' button to reflect state e.g. play and pause.
 - [done] Add option to hide video controls like we hide video file list and event list.
 - [done] Add information about video file to saved event list .txt file, e.g. (path=xxx, numframes=yyy, fps=zzz).
 - [done] Expand code to open a folder of video files. Right now it is one hard-coded video file.
 - [done] Add standard video control buttons like play/pause/forward/backward/large-forward/large-backward.
 - [done] Finish setting annotation notes with keyboard 'n'.
 - [done] Write recipe for installation into Python virtual environment.
 - [done] Design system where annotations can have start/stop frames or start frame and number of frames (duration). Right now annotations only have single (start) frame.

## Blinding algorithm

 - **video file duration (30 min)**
 - **pieceDur (10 min)** gives us numPieces = dur / pieceDur
 - **totalNumChunks (30)** is total number of chunks for one video
 - **chunkDur (10 sec)** is duration of each chunk
 1. split video into a large number of chunks numChunks = (dur/chunkDur)
 2. partition video into a number of 'pieces' numPieces = (dur/pieceDur)
 3. chunksPerPiece = totalNumChunks/numPieces
 4. for each 'piece', randomly choose chunksPerPiece without replacement. Can do this by stepping through all chunks and only considering chunks with a piece using chunksPerPiece.
 
 - Add 'pieceIndex' to each chunk in output chunk list
 
## Learning Tkinter

https://www.inoreader.com/article/3a9c6e79a229d841-stack-abuse-gui-development-with-python-tkinter-an-introduction

https://www.pyimagesearch.com/2016/05/23/opencv-with-tkinter/

https://www.pyimagesearch.com/2016/05/30/displaying-a-video-feed-with-opencv-and-tkinter/

https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
