# Author: Robert Cudmore
# Date: 20181101

##################################################################################
# Main
##################################################################################

from FileVideoStream import FileVideoStream
from VideoApp import VideoApp

path = '/Users/cudmore/Dropbox/PiE/video'
videoPath = '/Users/cudmore/Dropbox/PiE/video/homecage-movie.mp4'

#fvs = FileVideoStream(videoPath) #.start()
#fvs.start()

#pba = VideoApp(path, fvs)
pba = VideoApp(path)

# this still blocks, any updates to tk slider blocks video thread?
pba.root.after(10, pba.myUpdate)

pba.root.mainloop()

print('videoplayer after root.mainloop()')

