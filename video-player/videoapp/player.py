# Author: Robert Cudmore
# Date: 20181101

##################################################################################
# Main
##################################################################################

import videoapp.videoApp

#from FileVideoStream import FileVideoStream
#videoPath = '/Users/cudmore/Dropbox/PiE/video/homecage-movie.mp4'
#fvs = FileVideoStream(videoPath) #.start()
#fvs.start()

path = '/Users/cudmore/Dropbox/PiE/video0'

pba = videoapp.videoApp.VideoApp(path)

#pba.root.mainloop()

print('player is ending')

