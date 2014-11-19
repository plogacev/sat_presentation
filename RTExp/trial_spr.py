import VisionEgg
from VisionEgg.Core import Viewport, FrameTimer, Screen, swap_buffers
from VisionEgg.Text import Text
from VisionEgg.WrappedText import WrappedText
from VisionEgg.MoreStimuli import FilledCircle, Target2D
from VisionEgg.Textures import FixationCross
from threading import Event
import copy, string

from tc import *
from definitions import *
import time

from trial_satspr_base import *
from config import globalScreen
from handler import DisplayUpdateStart, DisplayUpdateEnd, SPRResponse, ITISleepStart, ITISleepEnd

def debug(string, level=2):
	if level < 2:
		print ("TRIAL.SPR (%s): "%get_time())+string

class SPRTrial(SATSPRTrialBase):

	def __init__(self, config, experiment, item, condition, mode, phrases, question=None):
		debug("__init__")
		Trial.__init__(self, config, experiment, item, condition, mode, phrases, len(phrases)+1, question)
		self.displayPhrase = None
		self.lastPhraseRead = None

		# create phrase chunks
		masked_phrases = []
		text_phrases = []
		i = 0
		signalReference = -1
		space = Text(text=" ", color=(0.0,0.0,0.0), position=(0,0),
    			     font_size=self.config.sprStimulusSize, 
			     anchor='left', on=0, font_name=self.config.font)
		space_size = space.parameters.size[0]

		# set initial word coordinates
		phrase_positions = []
		if mode == CPresentationMode.MovingWindow:
			x_pos = self.config.xPositionStart
			y_pos = globalScreen.size[1]/2
			anchor = "left"

		elif mode == CPresentationMode.Centered:
			x_pos = globalScreen.size[0]/2
			y_pos = globalScreen.size[1]/2
			anchor = "center"
		
		# create phrases
		for i in range(0, len(phrases)):
			if phrases[i] == "$":
				raise "There should not be a '$' in an SPR stimulus."

			text = Text(text = phrases[i], color = (0.0,0.0,0.0),
          			position = (x_pos, y_pos),
    				font_size = self.config.sprStimulusSize,
  		     		anchor=anchor, on=0, font_name=self.config.font)

			if mode == CPresentationMode.MovingWindow:
				phrase_positions.append( (x_pos,y_pos) )
				x_pos = x_pos + text.parameters.size[0] + space_size

			text_phrases.append(text)

			# TODO: Fix y coordinates too. Necessary once the stimulus becomes longer than one line.


		# create masks if the mode is moving window
		if mode == CPresentationMode.MovingWindow:
			for i in range(0, len(phrases)):
				text_size = text_phrases[i].parameters.size
				mask_size = (text_size[0], config.sprMaskHeight )
				mask_position = [phrase_positions[i][0], phrase_positions[i][1]]	
				mask_position[1] = mask_position[1]-(text_size[1]/2-mask_size[1]/2)

				phrase_mask = Target2D(color=(0.0,0.0,0.0),
						position=mask_position, 
						anchor='left',
						on=1, size=mask_size)

				masked_phrases.append(phrase_mask)

		self.screen = TrialScreen(config, text_phrases, masked_phrases, mode)


	def present(self, display, feedback, audio=None):
		debug("present")

		# init
		self.display = display
		self.feedback = feedback
		feedback.registerHandler(self)
		display.setMode(self.isPractice(), self.isWordStimulus())
		display.registerNotifier(self)

		display.setStimulus(self.screen)
		self.presentFixationCross(self.config.sprFixationCrossCrossTime,
					  self.config.sprFixationCrossBlankTime)

		# post-wait init
		phrases_cnt = self.screen.phrase_cnt()

		i = -1 
		self.recordDisplayUpdateStart(i)
		while True:
			self.recordDisplayUpdateEnd(i)
			i = i + 1
			self.waitForResponse()
			if self.mode == CPresentationMode.Centered:
				self.screen.removeFixationCross()

			self.recordDisplayUpdateStart(i)
			if not self.presentNextPhrase():
				break

		debug("feedback detach")
		feedback.detachHandler()
		display.detachNotifier()

	
	def recordButton(self,  button):
		# ensure that a button is not pressed immaturely and that a buttonpress is recorded
		# only once per phrase
		debug("recordButton: displayPhrase=%s, lastPhraseRead=%s" % 
				   (self.displayPhrase, self.lastPhraseRead))
		if self.displayPhrase != None and self.displayPhrase != self.lastPhraseRead:
			self.recordEvent('response',  SPRResponse(button,  self.displayPhrase, 
								  self.screen.visiblePhrase(), 
								  get_time()-self.displayTime))
			self.lastPhraseRead = self.displayPhrase
			return True
		else:
			debug("recordButton FAILED.")
			return False

		
	def processContinue1(self):
		return self.recordButton("C1")
	
	def processContinue2(self):
		return self.recordButton("C2")
	
	def mapButtonToResponse(self, response):
		return self.config.buttonsMapping[response]
