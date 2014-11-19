import VisionEgg
from VisionEgg.Core import Viewport, FrameTimer, Screen, swap_buffers
from VisionEgg.Text import Text
from VisionEgg.WrappedText import WrappedText
from VisionEgg.MoreStimuli import FilledCircle, Target2D
from VisionEgg.Textures import FixationCross
from threading import Event
import copy, string, time, math, threading

from tc import *
from definitions import *

from trial import Trial
from trial_satspr_base import *
from config import globalScreen
from handler import DisplayUpdateStart, DisplayUpdateEnd, SPRResponse
from handler import ITISleepStart, ITISleepEnd, SignalStart, SignalEnd, SATResponse 

from text_display import IndicatorDot, accuracy_dots, mapping_dots 
from log import LogCfg

def debug(string, level=LogCfg.TrialSAT):
	if level <= LogCfg:
		print ("TRIAL.SAT (%s): "%get_time())+string

class TrialScreenSAT(TrialScreen):
	
	def __init__(self, config, text_phrases, masked_phrases, mode, 
			   signals_cnt, feedback_indicators, mapping_indicators):
		stimuli = []

		# feedback dots
		self.feedback_indicators = accuracy_dots( signals_cnt, 
			     	config.dotsDistance, 
			     	(globalScreen.size[0]-config.dotsDistance*(signals_cnt+1), 
			      	globalScreen.size[1]-config.dotsDistance))
		stimuli.extend(self.feedback_indicators)
		self.red_indicators = []
		self.green_indicators = []
	
		# mapping dots
		self.mapping_indicators = mapping_dots(config, globalScreen.size)
		stimuli.extend(self.mapping_indicators)

		indicators = []
		indicators.extend(self.feedback_indicators)
		indicators.extend(self.mapping_indicators)

		TrialScreen.__init__(self, config, text_phrases, masked_phrases, mode, indicators)
		self.setFeedbackIndicators(feedback_indicators)
		self.setMappingIndicators(mapping_indicators)
		self.feedback_indicatorsLock = threading.Lock()

	def setMappingIndicators(self, on):
		for indicator in self.mapping_indicators:
			indicator.parameters.on = on

	def setFeedbackIndicators(self, on):
		for indicator in self.feedback_indicators:
			indicator.parameters.on = on

	def setIndicatorStatus(self, i, status):
		self.feedback_indicatorsLock.acquire()
		debug("setIndicatorStatus: <%s, %s>" % (i, status) )
		if not i < len(self.feedback_indicators):
			self. feedback_indicatorsLock.release()
			return
		if status == None:
			self.feedback_indicators[i].setGrey()
		elif status == True:
			self.feedback_indicators[i].setBlack()
			self.green_indicators.append(i)
		elif status == False:
			self.feedback_indicators[i].setBlack()
			self.red_indicators.append(i)
		self.feedback_indicatorsLock.release()

	def setIndicatorsColors(self):
		self.feedback_indicatorsLock.acquire()
		for i in self.red_indicators:
			self.feedback_indicators[i].setRed()
		for i in self.green_indicators:
			self.feedback_indicators[i].setGreen()
		self.feedback_indicatorsLock.release()
			

# TODO: Create a common base class for SATTrial and SPRTrial in order to:
#	- merge the functions __init__(), present(), etc., which have a lot of overlap
#	- prevent the presence processContinue1(), processContinue2() (July, 2012: I'm not sure what I meant by this.)

class SATTrial(SATSPRTrialBase):

	firstSignalStartTime = None
		
	def __init__(self, expparadigm, config, phrases, args):
		# TODO: add a 'question' argument
		debug("__init__")
		Trial.__init__(self, config, args['experiment'], args['item'], 
				args['condition'], args['mode'], 
				phrases, len(phrases)+1, question=None)
		if expparadigm == "MR-SAT":
			self.paradigm = "MR"	
		elif expparadigm == "SAT":
			self.paradigm = "SR"	
		else:	
			raise("Invalid experiment paradigm.")

		mode = args['mode']

		if not args.has_key('speededAcceptability'):
			args['speededAcceptability'] = False
		#if not args.has_key('lastFeedbackOffset'):
		#	args['lastFeedbackOffset'] = 0

		self.args = args

		self.displayPhrase = None
		self.lastPhraseRead = None
		self.lastResponseCorrect = None

		# create phrase chunks
		masked_phrases = []
		text_phrases  = []
		space = Text(text=" ", color=(0.0,0.0,0.0), position=(0,0),
    			     font_size=self.config.sprStimulusSize, anchor='left', 
			     on=0, font_name=self.config.font)
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
		self.sentence = ""
		for i in range(0, len(phrases)):
			if phrases[i] == "$":
				self.phraseSignalReference = i
				continue

			self.sentence = self.sentence +  " " + phrases[i]
			text = Text(text = phrases[i], color = (0.0,0.0,0.0),
          			position = (x_pos, y_pos),
    				font_size = self.config.sprStimulusSize,
  		     		anchor=anchor, on=0, font_name=self.config.font)

			if mode == CPresentationMode.MovingWindow:
				phrase_positions.append( (x_pos,y_pos) )
				x_pos = x_pos + text.parameters.size[0] + space_size

			text_phrases.append(text)
			# TODO: Fix y coordinates too. Necessary once the stimulus 
			#       becomes longer than one line.
		assert( hasattr(self, "phraseSignalReference"))
		self.sentence.strip()

		# create masks if the mode is moving window
		if mode == CPresentationMode.MovingWindow:
			for i in range(0, len(phrases)):
				text_size = text_phrases[i].parameters.size
				mask_size = (text_size[0], config.sprMaskHeight )
				mask_position = [ phrase_positions[i][0], 
						  phrase_positions[i][1] ]	
				mask_position[1] = mask_position[1]-(text_size[1]/2-mask_size[1]/2)

				phrase_mask = Target2D(color=(0.0,0.0,0.0),
						position=mask_position, 
						anchor='left',
						on=1, size=mask_size)

				masked_phrases.append(phrase_mask)

		self.screen = TrialScreenSAT(config, text_phrases, 
					  masked_phrases, mode, 
					  self.args['signalsCnt'],
					  self.args['feedbackIndicators'],
					  self.args['mappingIndicators'])

		if not self.args['speededAcceptability']:
			self.responses = [False]*self.args['signalsCnt']
		else:
			self.responses = [False]

		self._directionBeforeSignal = None
		self._directionAfterSignal = None

	def present(self, display, feedback, audio):
		debug("starting presentation of trial")

		# init
		self.display = display
		debug("registering audio handler")
		audio.registerHandler(self)
		debug("registering feedback handler")
		feedback.registerHandler(self)
		#display.setContinue(True)
		debug("registering display handler")
		display.registerNotifier(self)
		#display.setStimulus(self.screen)
		#display.updateDisplay()
		#display.setContinue(False)

		debug("starting fixation cross")
		# post-wait init
		phrases_cnt = self.screen.phrase_cnt()
		display.setStimulus(self.screen)
		self.presentFixationCross(self.args['ITICross'], self.args['ITIBlank'])

		# present stimulus
		if self.mode == CPresentationMode.Centered:
			self.screen.removeFixationCross()
		debug("finished fixation cross")


		tc = TimeCorrection()
		i = -1 
		for i in range(0, phrases_cnt):
			debug("presenting phrase %s" % i)
			if not i == 0:
				self._directionBeforeSignal = self.isGrammatical()
			self.recordDisplayUpdateStart(i)
			# present phase
			self.presentNextPhrase()
			self.recordDisplayUpdateEnd(i)
			self._directionAfterSignal = self.isGrammatical()
		
			tc.initIfIdle("main-thread")
			self.scheduleFeedbackIfIdle( audio, feedback )
			tc.sleep(self.args['SOA'])

			# present blank screen unless this is the last phrase
			if i < phrases_cnt-1:
				self.recordDisplayUpdateStart(i + 0.5)
				self.showBlankScreen()
				self.recordDisplayUpdateEnd(i + 0.5)
				tc.sleep(self.args['ISI'])

		# wait till the response phase is finished
		debug("waiting for audio")
		self.waitForAudioThreadButUpdateDisplay(display.updateDisplay)
		debug("sleep")
		tc.reset() # no time correction is needed from here on
		tc.sleepAndExecute(self.args['signalCycle'], 
			display.updateDisplay, self.evtUpdate)
		display.updateDisplay()

		self.acquireResponseLock()
		if not self.responses[-1]:
			self.resetResponseSignal()
		debug("RESPONSES <%s>"%self.responses)
		self.releaseResponseLock()

		# add empty events for all missed responses
		for interval_idx in range(0, len(self.responses)):
			if not self.responses[interval_idx]:
				s = SATResponse(interval_idx+1, 'NA', 'NA', 'NA', -1, -1)
				self.recordEvent('satResponse', s)
	
		# post-stimulus wait phase, needed only for practice trials 
		# for subjects to check out their performance
		if self.accuracyFeedbackDuration() > 0:
			tc.reset()
			self.screen.setIndicatorsColors()
			self.showBlankScreen()
			tc.sleep(self.accuracyFeedbackDuration())

		debug("feedback detach")
		feedback.detachHandler()
		audio.detachHandler()
		display.detachNotifier()

		
		if self.lastResponseCorrect == False and self.displaySentenceIfIncorrect():
			return self.sentence
		else:
			return None


	def accuracyFeedbackDuration(self):
		if self.args.has_key('accuracyFeedbackDuration'):
			return self.args['accuracyFeedbackDuration']
		return 0

	def displaySentenceIfIncorrect(self):
		if self.args.has_key('displaySentenceIfIncorrect'):
			return self.args['displaySentenceIfIncorrect']
		return False

	def setFirstSignalStartTime(self):
		soa_plus_isi = self.args['SOA'] + self.args['ISI']
		firstSignalStartTime = soa_plus_isi*self.phraseSignalReference + self.args['signalOnset']
		self.firstSignalStartTime = get_time()+firstSignalStartTime

	def timeSinceFirstSignal(self):
		if self.firstSignalStartTime:
			return get_time()-self.firstSignalStartTime
		else:
			return None

	def scheduleFeedbackIfIdle(self, audio, feedback):
		if not self.audio and not self.feedback:
		    if self.firstSignalStartTime == None:
			self.setFirstSignalStartTime()
			audio.startSignals(self.firstSignalStartTime)
			self.audio = audio
			self.feedback = feedback
		    	debug("starting audio, firstSignalStartTime %s" % str(self.firstSignalStartTime))

	def waitForAudioThread(self):
		if self.audio:
			self.audio.waitForSignals()

	def waitForAudioThreadButUpdateDisplay(self, update):
		""" This implementation's timing is quite imprecise. (TODO: fix this). """
		if self.audio:
			while not self.audio.checkIfAudioStopped():
				sleep(self.config.satDisplayUpdateFrequencyDuringFeedback)
				if self.evtUpdate.isSet():
					update()

	def showBlankScreen(self):
		self.screen.hideCurrentPhrase()
		self.display.updateDisplay()

	# TODO: test this function
	def mapTime2IntervalNum(self, t):
		t = self.timeSinceFirstSignal()
		if not t:
			return -1, -1, None
		if self.args['speededAcceptability']:
			if t > 0:
				return 0, t, t
			return -1, -1, t

		signals_cnt = self.args['signalsCnt']
		signal_onset = self.args['signalOnset']
		signal_cycle = self.args['signalCycle']
		debug("<%s, %s, %s, %s>" % (t, signals_cnt, signal_onset, signal_cycle) )

		max_interval_idx = signals_cnt-1
		if self.paradigm == "MR":
			interval_idx = min(math.floor((t+signal_onset/2)/signal_cycle), max_interval_idx)
		elif self.paradigm == "SR":
			interval_idx = min(math.floor(t/signal_cycle), max_interval_idx)
		RT = t - interval_idx*signal_cycle
		return int(interval_idx), RT, t

	def processLeftAndRight(self, button):
		t = time.time()
		interval_idx, RT, time_since_first_signal = self.mapTime2IntervalNum(t)
		debug("processLeftAndRight: interval_idx <%s>, RT <%s>, self.responses <%s>, time_since_first_signal <%s>" % 
			(interval_idx, RT, self.responses, time_since_first_signal))

		responseGrammatical = self.mapButtonToResponse(button)
		responseCorrect = (self.isGrammatical() == responseGrammatical or \
				   self._directionAfterSignal == responseGrammatical or \
				   self._directionBeforeSignal == responseGrammatical)

		if interval_idx < 0 or \
		   interval_idx > len(self.responses) or \
		   self.responses[interval_idx]:
			interval = 'NA'
		else:
			interval = interval_idx + 1
			self.responses[interval_idx] = True
	
			# SET INDICATOR 
			self.screen.setIndicatorStatus(interval_idx, responseCorrect)
			self.evtUpdate.set()

		self.lastResponseCorrect = responseCorrect		

		# RECORD BUTTON PRESS
		s = SATResponse(interval, button, responseGrammatical, responseCorrect, RT, t)
		self.recordEvent('satResponse', s)
		return True

	def processLeft(self):
		return self.processLeftAndRight('L')

	def processRight(self):
		return self.processLeftAndRight('R')

	def isGrammatical(self):
		if self.args['grammatical'] == self.config.determineRightButtonMarker:
			if self.screen.visiblePhrase() == '<':
				button = 'L'
			elif self.screen.visiblePhrase() == '>':
				button = 'R'
			else:
				return(None)
			return self.mapButtonToResponse(button)
		else:
			return self.args['grammatical']

	def mapButtonToResponse(self, button):
		return self.config.buttonsMapping[button]

	def handleSignalQueued(self):
		t = self.timeSinceFirstSignal()
		self.signals.append([t, None])
		self.recordEvent('signalStart',  SignalStart(len(self.signals)+1) )

	def handleSignalSignalFinished(self):
		t = self.timeSinceFirstSignal()
		self.signals[-1][1] = t
		self.recordEvent('signalEnd',  SignalEnd(len(self.signals)) )

	def params(self):
		return self.args


