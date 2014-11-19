import VisionEgg
VisionEgg.start_default_logging(); 
VisionEgg.watch_exceptions()

from VisionEgg.Core import Viewport, FrameTimer, Screen, swap_buffers
#from VisionEgg.FlowControl import Presentation
from VisionEgg.Text import Text
from VisionEgg.WrappedText import WrappedText
from VisionEgg.MoreStimuli import FilledCircle

from threading import Event, Lock
from tc import get_time
from config import globalScreen
from handler import ResponseHandler



def debug(string, level=2):
	if level < 2:
		print ("DISPLAY (%s): "%get_time())+string


class IndicatorDot (FilledCircle):
	grey  = (0.5,0.5,0.5,1.0)
	red   = (1, 0, 0, 1.0)
	green = (0, 1, 0, 1.0)
	black = (0, 0, 0, 1.0)
	white = (1, 1, 1, 1.0)

	def __init__(self, position, radius=2.0):
		FilledCircle.__init__(self, color=self.grey, position=position, 
					    radius=radius)
		
	def setGrey(self):
		self.parameters.color = self.grey

	def setBlack(self):
		self.parameters.color = self.black

	def setRed(self):
		self.parameters.color = self.red

	def setGreen(self):
		self.parameters.color = self.green
	
	
def accuracy_dots(number, dotsDistance, startPosition):
	targets = []
	for i in range(0, number):
		target = IndicatorDot(position=(startPosition[0]+i*dotsDistance, startPosition[1])) 
		targets.append(target)
	return targets

def mapping_dots(config, screenSize):
	leftDot = IndicatorDot(position=(config.mappingDotsVDistance, 
					 config.mappingDotsHDistance), 
			       radius=config.mappingDotSize) 
	rightDot = IndicatorDot(position=(screenSize[0]-config.mappingDotsVDistance, 
					  config.mappingDotsHDistance), 
				radius=config.mappingDotSize) 

	# NOTE: actually, just one comparison is needed here. But this is a sanity check.
	if (config.buttonsMapping['L'] == 'Y' and
	    config.buttonsMapping['R'] == 'N'):
		leftDot.setGreen()
		rightDot.setRed()
	elif (config.buttonsMapping['L'] == 'N' and
	      config.buttonsMapping['R'] == 'Y'):
		leftDot.setRed()
		rightDot.setGreen()
	else:
		raise "Inconsistent mapping."
	
	return (leftDot, rightDot)


class Display:
	config = None

	def __init__(self, config):
		self.config = config
		self.generate_continue()
		
	def generate_continue(self):
		self._continue = Text(text=self.config.string_continue, 
				      color=(0.0,0.0,0.0),
          			      position=(globalScreen.size[0]/2, 
						self.config.textContinueDistance),
    				      font_size=self.config.textContinueSize,
  				      anchor='center',
				      on=1, font_name=self.config.font)


class StimulusDisplay(Display):
	def __init__(self, config):
		Display.__init__(self, config)
		globalScreen.parameters.bgcolor = (.8,.8,.8) # background white (RGB)

		# prepare continue instruction
		stimuli=[]

		self.baseViewport = Viewport(screen=globalScreen,
                			size=globalScreen.size,
                   		 	stimuli=stimuli) 

		self._textWords = ""
		self.notifier = None
		self.lastWordPresentend = None	
		self.updateLock = Lock()

	def registerNotifier(self, notifier):
		self.notifier = notifier

	def detachNotifier(self):
		self.notifier = None

	def notifyUpdateStart(self):
		word = self.stimulusViewport.visiblePhrase()
		if self.lastWordPresentend == word:
			return
		self.notifier.notifyTextUpdateStart(word)	

	def notifyUpdateFinished(self):
		word = self.stimulusViewport.visiblePhrase()
		if self.lastWordPresentend == word:
			return
		self.notifier.notifyTextUpdateFinished(word)	
		self.lastWordPresentend = word	

	def setContinue(self, on):
		debug("setContinue(), doing nothing")
		self._continue.parameters.on = on

	def updateDisplay(self):
		self.updateLock.acquire()
		self.notifyUpdateStart()
		globalScreen.clear()
		# TODO: check whether the next line has any negative effects on timing!!!
		#self.baseViewport.draw()
		self.stimulusViewport.draw()
		swap_buffers()
	  	# frame_timer.tick()
		self.notifyUpdateFinished()
		self.updateLock.release()

	def setStimulus(self, viewport):
		self.stimulusViewport = viewport



class InstructionsDisplay(Display,  ResponseHandler):

	def __init__(self, config, instruction):
		# TODO: delete all that is done in stimulusDisplay too and call its __init__
		self.instruction = instruction
		globalScreen.parameters.bgcolor = (.8,.8,.8) # background white (RGB)
		Display.__init__(self, config)
		ResponseHandler.__init__(self, config)
	
	def updateDisplay(self, viewport):
		globalScreen.clear()
		viewport.draw()
		swap_buffers()
	  	# frame_timer.tick()

	def setText(self, text):
		self.text.parameters.text = text

	def setTextOn(self):
		#self.text.parameters.on = True
		self.text.parameters.text = self._textWords

	def setTextOff(self):
		#self.text.parameters.on = False
		self._textWords = self.text.parameters.text
		self.text.parameters.text = " "

	def present(self, feedback):
		self.generate_continue()	
               	size=(globalScreen.size[0]-self.config.textDisplayBorder,
               	      globalScreen.size[1]-self.config.textDisplayBorder)

		debug("presenting screen")
		feedback.registerHandler(self)
		debug("instruction <%s>"% self.instruction)
		text = WrappedText(text=self.instruction,
			color=(0.0,0.0,0.0), # alpha is ignored (set with max_alpha_param)
          		position=(self.config.textDisplayBorder, 
				globalScreen.size[1]-self.config.textDisplayBorder),
                		size=size, font_size=self.config.textInstructionsSize,
				on=1, font_name=self.config.font)

		viewport = Viewport(screen=globalScreen, size=size,
                   		 	stimuli=[self._continue, text]) 

		self.updateDisplay(viewport)
		self.waitForResponse()
		feedback.detachHandler()

		viewport = Viewport(screen=globalScreen,
               			size=globalScreen.size,
               		 	stimuli=[])
		self.updateDisplay(viewport)


	def processStart(self):
		debug("processStart")
		self.gotResponse()

	def waitForStart(self):
		debug("waitForStart")
		self.waitForResponse()
		debug("/waitForStart")
