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

from trial import Trial
from config import globalScreen
from handler import DisplayUpdateStart, DisplayUpdateEnd, SPRResponse, ITISleepStart, ITISleepEnd

def debug(string, level=1):
	if level < 2:
		print ("TRIAL.SATSPR.BASE (%s): "%get_time())+string

def debugTextObjects(list):
	strings = []
	for elem in list:
		strings.append(elem.parameters.text)
	debug("%s"%strings)

class TrialScreen(Viewport):

	fixationCross = FixationCross(on=False)

	def __init__(self, config, text_phrases, masked_phrases, mode, indicators=[]):
		self.config = config
		self.text_phrases = text_phrases
		self.masked_phrases = masked_phrases
		self.current_index = -1
		stimuli = copy.copy(text_phrases)
		stimuli.extend(masked_phrases)
		stimuli.append(self.fixationCross)
		stimuli.extend(indicators)
		Viewport.__init__(self, screen=globalScreen, stimuli=stimuli)

		self.mode = mode	
		if mode == CPresentationMode.MovingWindow:
			self.hide_mask = config.sprHideMask

		elif mode == CPresentationMode.Centered:
			self.hide_mask = False

		else:
			raise "No other mode is implemented so far."

		# determine all necessary positions for the fixation cross
		self.fixationCross.parameters.size = (config.sprFixationCrossSize,)*2
		position = self.text_phrases[0].parameters.position
		size = self.text_phrases[0].parameters.size
		self.fixationCrossFirstWord = (position[0]+size[0]/2, position[1]+self.config.sprFixationCrossSize/4)
		self.fixationCrossCenter = (globalScreen.size[0]/2, position[1]+self.config.sprFixationCrossSize/4)

	def visiblePhrase(self):
		if self.current_index == -1:
			return ""
		return self.text_phrases[self.current_index].parameters.text

	def phrase_cnt(self):
		return len(self.text_phrases)

	def hidePhrase(self, idx):
		self.text_phrases[idx].parameters.on = 0
		if self.hide_mask:
			self.masked_phrases[idx].parameters.on = 1

	def showPhrase(self, idx):
		self.text_phrases[idx].parameters.on = 1
		if self.hide_mask:
			self.masked_phrases[idx].parameters.on = 0

	def hideCurrentPhrase(self):
		self.hidePhrase(self.current_index)

	def showCurrentPhrase(self):
		self.showPhrase(self.current_index)

	def next(self):
		idx = self.current_index
		debug("next: idx=%d, cnt=%d"%(idx, self.phrase_cnt()))
		if (idx+1) == self.phrase_cnt():
			return False
		if idx > -1:
			self.hidePhrase(idx)
		idx = idx + 1
		self.showPhrase(idx)
		self.current_index = idx
		return True

	def previous(self):
		# TODO: test this
		idx = self.current_index
		debug("prev: idx=%d, cnt=%d"%(idx, self.phrase_cnt()))
		if idx == 0:
			return False

		self.hidePhrase(idx)
		idx = idx - 1
		self.showPhrase(idx)
		self.current_index = idx
		return True

	def toggleMaskedPhases(self):
		for idx in range(0, len(self.masked_phrases)):
			self.masked_phrases[idx].parameters.on = not self.masked_phrases[idx].parameters.on

	def moveFixationCross2Center(self):
		self.fixationCross.parameters.position = self.fixationCrossCenter

	def moveFixationCross2FirstWord(self):
		self.fixationCross.parameters.position = self.fixationCrossFirstWord

	def toggleFixationCross(self):
		self.fixationCross.parameters.on = not self.fixationCross.parameters.on
		
	def removeFixationCross(self):
		self.fixationCross.parameters.on = False
		

class SATSPRTrialBase(Trial):

	def presentFixationCross(self, crossTime, blankTime):
		self.recordEvent('ITISleepStart',  ITISleepStart())

		self.screen.toggleMaskedPhases()
		self.screen.moveFixationCross2Center()
	
		tc = TimeCorrection()
		tc.initIfIdle('ITI')

		self.recordDisplayUpdateStart(0)
		self.screen.toggleFixationCross()
		self.display.updateDisplay()
		self.recordDisplayUpdateEnd(0)

		tc.sleep(crossTime*2)

		for i in range(0, self.args['ITICrossRepeat']):	
			debug("first loop")
			self.screen.toggleFixationCross()
			self.display.updateDisplay()
			tc.sleep(blankTime)

			self.screen.toggleFixationCross()
			self.display.updateDisplay()
			tc.sleep(crossTime)

		if self.mode == CPresentationMode.MovingWindow:
			self.screen.toggleMaskedPhases()

			self.screen.moveFixationCross2FirstWord()
			for i in range(1, self.args['ITICrossRepeat']):  
                        	self.screen.toggleFixationCross()
				self.display.updateDisplay()
       		                tc.sleep(blankTime)

	                        self.screen.toggleFixationCross()
        	                self.display.updateDisplay()
                	        tc.sleep(crossTime)

		if self.mode == CPresentationMode.MovingWindow:
                	self.screen.toggleFixationCross()
			self.display.updateDisplay()

		self.recordEvent('ITISleepEnd',  ITISleepEnd())

	def presentNextPhrase(self):
		if self.screen.next():
			debug("presentNextPhrase: presenting next phrase")
			self.display.updateDisplay()
			return True

		elif self.question:
			debug("presentNextPhrase: presenting question")
			self.resetContinue1()
			self.resetContinue2()
			self.question.present(self.feedback)
			return False
		else:
			debug("presentNextPhrase: NONE")
		return False

	def recordDisplayUpdateStart(self,  phrase):
		self.displayTime = get_time()
		self.displayPhrase = None
		self.recordEvent('displayUpdateStart',  DisplayUpdateStart(phrase))
		return True
		
	def recordDisplayUpdateEnd(self,  phrase):
		self.displayTime = get_time()
		self.displayPhrase = phrase
		self.recordEvent('displayUpdateEnd',  DisplayUpdateEnd(phrase))
		return True

	def writeHeader(self, file):
		pass
