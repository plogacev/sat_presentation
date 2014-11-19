# -*- coding: utf-8 -*-

# NOTE: Pressing both buttons at the same time can be a problem if the second button 
#	press (and they rarely come at the same time) comes after the following beep.
#	In that case we end up with a sequence of Y-N (or N-Y) responses instead of
#	one single response.
#	In this software we will use only Y or N.


from VisionEgg.Core import get_default_screen

import VisionEgg.GUI 
import os, string

#VisionEgg.config.VISIONEGG_MONITOR_WIDTH = 800
#VisionEgg.config.VISIONEGG_MONITOR_HEIGHT = 600
VisionEgg.config.VISIONEGG_MONITOR_WIDTH = 1152
VisionEgg.config.VISIONEGG_MONITOR_HEIGHT = 864
VisionEgg.config.VISIONEGG_FULLSCREEN = 1
VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ = 60.0
#VisionEgg.config.VISIONEGG_MONITOR_WIDTH = 1280
#VisionEgg.config.VISIONEGG_MONITOR_HEIGHT = 1024
#VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ = 75.0

#window = VisionEgg.GUI.GraphicsConfigurationWindow()
#window.mainloop() # All this does is adjust VisionEgg.config
#if not window.clicked_ok:
#	sys.exit() # User wants to quit
#VisionEgg.Configuration.save_settings()
VisionEgg.config.VISIONEGG_GUI_INIT = 1


globalScreen = get_default_screen()

# TODO: check which of these settings are used at the moment, get rid of the unnecessary ones

class Config:
	jsNumber = 0

	# (left, right, start, next, terminate)
	# left and right are used for responses to questions
	jsSetup = {#"WingMan Action Pad": (6, 7, 8, 8, (3,4,5)),
		   #"Microsoft": (5, 4, 0, 0, (100,100,100)),
		   #"PS  Converter    ": (4, 5, 2, 2, (100,100,100)),
		   #"Logitech(R) Precision(TM) Gamepad": (6, 7, 0, 0, (3,2,1)),
		   #"Generic   USB  Joystick  ": (6, 7, 0, 0, (3,2,1)),
		   "?": 
		   	{'left': 4, 'right': 5, 'start': 9, 
			 'continue': (8,9), 'terminate': (3,2,1)},
		   "DragonRise Inc.   Generic   USB  Joystick  ": 
		   	{'left': 4, 'right': 5, 'start': 9, 
			 'continue': (8,9), 'terminate': (3,2,1)},
		   "Generic   USB  Joystick  ": 
		   	{'left': 4, 'right': 5, 'start': 9, 
			 'continue': (8,9), 'terminate': (3,2,1)},
		   "USB Gamepad ":
		   	{'left': 4, 'right': 5, 'start': 0, 
			 'continue': (8,9), 'terminate': (3,4,5)}
		   }
	
	jsKeyYes = None
	jsKeyNo  = None
	jsKeyStart  = None

	kbKeyEsc  = 27#'ESC' 

	# normal keyboard
	kbKeyStart  = 32#' ' 
	kbKeyLeft  = 102#'f' 
	kbKeyRight = 106#'j'
	kbKeyContinue1 = 32#' '
	kbKeyContinue2 = 32#' '
	kbKeysTerminate = (0, 0, 0)

	# keypad
	#kbKeyStart  = 257#'1'
	#kbKeyLeft  = 263#'7'
	#kbKeyRight = 269#'-'
	#kbKeyContinue1 = 258#'2'
	#kbKeyContinue2 = 258#'2'

	# GeneralKeys/Ortek keypad
	# '.'=266, '/'=267, 'Enter'=271, '+'=270, '-'=269, '*'=268
	# 0=256, 1=257, 2=258, 3=259, 4=260, 5=261, 6=262, 7=263, 8=264, 9=265 
	#kbKeyStart  = 271#'Enter'
	#kbKeyLeft  = 263#'7'
	#kbKeyRight = 265#'9'
	#kbKeyContinue1 = 264#'8'
	#kbKeyContinue2 = 264#'8'

	jsFakeInput = False # ignore gamepad and keep sending random buttonpresses

	# mostly SAT settings
	textContinueDistance = 20
	textContinueSize = 20
	textStimulusSize = 80 
	textDisplayBorder = 20

	# both, SPR and SAT settings
	textInstructionsSize = 40
	textQuestionSize = 20
	textAnswerSize = 20

	# SPR Settings
	xPositionStart = 10 # pixels
	yPositionStart = globalScreen.size[1]/2 # pixels
	sprHideMask = False
	sprMaskHeight = 1
	sprContinueDistance = 10
	sprContinueSize = 10
	sprInstructionsSize = 10
	sprStimulusSize = 60 
	sprFixationCrossSize = 40
	sprFixationCrossCrossTime = 250 # TODO: implement this for SAT, too 
	sprFixationCrossBlankTime = 150 # TODO: implement this for SAT, too 

	# SAT settings
	dotsDistance = 10 # pixels
	mappingDotsVDistance = 20 # pixels
	mappingDotsHDistance = 20 # pixels
	mappingDotSize = 10.0 # pixels
	satDisplayUpdateFrequencyDuringFeedback = 5

	string_practiceExperiment = "practice"
	string_cueRight = ">>>"
	string_cueLeft  = "<<<"
	string_continue = u"Zum Fortsetzen '10' drücken."
	string_incorrect_response = u"Bei diesem Satz haben Sie einen Fehler gemacht:"

	# functions and variables determined automatically
	participantNumber = None
	buttonsMapping = None
	startbuttonsMapping = None

	#font = "/Library/Fonts/Arial.ttf"
	#font = "/Library/Fonts/Tahoma.ttf"
	if os.name == "nt":
		font = "c:\\windows\\fonts\\trebuc.ttf"
	elif os.name == "posix":
		#font = "/usr/share/fonts/truetype/Trebuchet_MS.ttf"
		font = "/usr/share/fonts/truetype/msttcorefonts/Trebuchet_MS.ttf"
		#font = "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"
	else:
		assert(False)
	
	# data recording
	records_header = ['time',  'event','RT', 'phraseNr', 'phrase', 
			  'button', 'answerLeft', 'answerRight', 
			  'answerCorrect', 'interval', 
			  'responseButton', 'responseGrammatical', 'responseCorrect']
	trial_header = ['subject', 'experiment', 'item', 'condition']
	
	def dataHeader(self):
		return string.join(self.trial_header+self.records_header)+'\n'

	def ParticipantSetup(self, participant):
		self.participantNumber = participant
		mapLR_YN = buttonsMapping = {'L':'Y', 'R':'N'}
		mapLR_NY = buttonsMapping = {'L':'N', 'R':'Y'}
		map12_LR = buttonsMapping = {'1':'L', '2':'R', 'R':'R', 'L':'L'}
		map21_LR = buttonsMapping = {'2':'L', '1':'R', 'R':'R', 'L':'L'}
		participant_class = int(participant) % 4
		if participant_class == 0:
			self.buttonsMapping = mapLR_YN
			self.startbuttonsMapping = map12_LR
		elif participant_class == 1:
			self.buttonsMapping = mapLR_YN
			self.startbuttonsMapping = map21_LR
		elif participant_class == 2:
			self.buttonsMapping = mapLR_NY
			self.startbuttonsMapping = map12_LR
		elif participant_class == 3:
			self.buttonsMapping = mapLR_NY
			self.startbuttonsMapping = map21_LR
		self.determineRightButtonMarker = '?' 

	def JoystickSetup(self, js):
		name = js.get_name()
		if not self.jsSetup.has_key(name):
			print "Unknown gamepad called <%s>!" % name
			raise ("Unknown gamepad called <%s>!" % name)

		jsSetup = self.jsSetup[name]
		self.jsKeyLeft  = jsSetup['left']
		self.jsKeyRight = jsSetup['right']
		self.jsKeyStart = jsSetup['start']
		self.jsKeysTerminate = jsSetup['terminate']

		if type(jsSetup['continue']) == tuple:
			self.jsKeyContinue1 = jsSetup['continue'][0]
			self.jsKeyContinue2 = jsSetup['continue'][1]
		else:
			self.jsKeyContinue1 = jsSetup['continue']
			self.jsKeyContinue2 = -1

		return True
