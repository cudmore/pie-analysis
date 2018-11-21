    # see: https://stackoverflow.com/questions/16523128/resizing-tkinter-frames-with-fixed-aspect-ratio
	#def set_aspect(self, lower_right_frame, content_frame, pad_frame, video_control_frame, aspect_ratio):
	def _set_aspect(self, hPane, lower_right_frame, content_frame, pad_frame, video_control_frame, videoLabel, aspect_ratio=None):
		# a function which places a frame within a containing frame, and
		# then forces the inner frame to keep a specific aspect ratio

		def enforce_aspect_ratio(event):
			# when the pad window resizes, fit the content into it,
			# either by fixing the width or the height and then
			# adjusting the height or width based on the aspect ratio.

			print('0a')
			print('enforce_aspect_ratio() event:', event)
			try:
				if self.lastResizeWidth is None:
					# initialize
					print('enforce_aspect_ratio() init')
					self.lastResizeWidth = event.width
					self.lastResizeHeight = event.height
				else:
					if event.width == self.lastResizeWidth:
						# do nothing
						print('enforce_aspect_ratio() no change')
						return "break"
					else:
						# continue
						print('enforce_aspect_ratio() processing')
						pass

				try:
					buttonHeight = 36
				except:
					print('eeeee 0')
				#event.width = lower_right_frame.winfo_width()
				#event.height = lower_right_frame.winfo_height()
				
				# start by using the width as the controlling dimension
				try:
					desired_width = event.width - buttonHeight
					desired_height = int(desired_width * aspect_ratio)
				except:
					print('eeeee 1')
					
				# if the window is too tall to fit, use the height as
				# the controlling dimension
				try:
					if desired_height > event.height:
						desired_height = event.height - buttonHeight
						desired_width = int(desired_height / aspect_ratio)
				except:
					print('eeeee 2')

				try:
					self.currentWidth = desired_width
					self.currentHeight = desired_height
				except:
					print('eeeee 3')
			
				try:
					print('   desired_width:', desired_width, 'desired_height:', desired_height)
				except:
					print('eeeee 4')
				# place the window, giving it an explicit size
				print('   1a')
				#content_frame.place(in_=pad_frame, x=0, y=0, width=desired_width, height=desired_height)
				if 1:
					#content_frame.place(in_=pad_frame, x=0, y=0, width=desired_width, height=desired_height)
					#content_frame.place(in_=lower_right_frame, x=0, y=0, width=desired_width, height=desired_height)
					# laast attempt
					#videoLabel.place(in_=content_frame, x=0, y=0, width=desired_width, height=desired_height)
					pass
				# place the video controls just below the video frame
				print('   2a')
				#video_control_frame.place(in_=lower_right_frame, x=0, y=desired_height + buttonHeight, width=desired_width)
				if 1:
					#video_control_frame.place(in_=pad_frame, x=0, y=desired_height + buttonHeight, width=desired_width)
					#video_control_frame.place(in_=lower_right_frame, x=0, y=desired_height + buttonHeight, width=desired_width)
					#video_control_frame.place(x=0, y=desired_height + buttonHeight, width=desired_width)
					pass
					
				print('   3a')
				#print('winfo_geometry:', self.root.winfo_geometry())
			except:
				print('*** bingo: exception in enforce_aspect_ratio()')
			print('   4a')

		aspect_ratio = self.vs.streamParams['aspectRatio']
		
		# this works reasonably well but causes crash in editing note?
		#content_frame.bind("<Configure>", enforce_aspect_ratio)
		
		#pad_frame.bind("<Configure>", enforce_aspect_ratio)
		#lower_right_frame.bind("<Configure>", enforce_aspect_ratio)
		#hPane.bind("<Configure>", enforce_aspect_ratio)
		#self.root.bind("<Configure>", enforce_aspect_ratio)

