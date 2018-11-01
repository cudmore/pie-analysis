## Video player

This needs a desktop environment which most of my Raspberry Pi's do not have. Use OSX instead.

## Install opencv

Debian

	sudo apt-get install python-opencv

OSX

	# takes a very long time to build
	brew install opencv3 --with-python3

	# install pillow
	pip3 install pillow
	
If having trouble, see this tutorial

	https://www.pyimagesearch.com/2016/12/19/install-opencv-3-on-macos-with-homebrew-the-easy-way/

## opencv is slow!!!

see this on threading the reading of video frames

https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/


## trying out tkinter

not sure how to install but is installed on work macOS python3 ?

following tutorial at

https://www.inoreader.com/article/3a9c6e79a229d841-stack-abuse-gui-development-with-python-tkinter-an-introduction

this tutorial seems to use both cv2 and tkinter?

https://www.pyimagesearch.com/2016/05/23/opencv-with-tkinter/

https://www.pyimagesearch.com/2016/05/30/displaying-a-video-feed-with-opencv-and-tkinter/

https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
