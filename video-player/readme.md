## Video player

This is a Python based video player that allows frames to be annotated.

## Screenshot

Video files are listed in upper left. Annotations of current video are in upper right. Selecting an annotation from the list will snap the video to the frame of the annotation.

<IMG SRC="img/player-screenshot.png" width=550>

## Keyboard commands

Controlling video

```
space: play/pause
left/right arrows: Backward/forward in video
shift + left/right arrows: Larger backward/forward in video
f: Play video faster, sets interval (ms)
s: Play video slower, sets interval (ms)
```

Editing annotations

```
1/2/3/4/5: Create new annotation at current frame
n: Set note of current selected annotation
```

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

1)  [Brew](https://brew.sh/)

2) OpenCV (takes a long time to build)
	
	brew install opencv3 --with-python3

3) Pillow

	pip3 install pillow

4) Make sure you have required Python libraries

 - Numpy
 - TKInter
	
If having trouble, see this tutorial

	https://www.pyimagesearch.com/2016/12/19/install-opencv-3-on-macos-with-homebrew-the-easy-way/

## Run

	python3 player.py
	
## Learning TKInter

https://www.inoreader.com/article/3a9c6e79a229d841-stack-abuse-gui-development-with-python-tkinter-an-introduction

this tutorial seems to use both cv2 and tkinter?

https://www.pyimagesearch.com/2016/05/23/opencv-with-tkinter/

https://www.pyimagesearch.com/2016/05/30/displaying-a-video-feed-with-opencv-and-tkinter/

https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
