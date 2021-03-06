import os
from threading import Thread, Lock, Event
from tc import *

#if os.name =="nt":
#	from sine_wave_pyaudio import Sine 
#else:
from sine_wave_pygame import Sine 


def debug(string, level=1):
	if level < 2:
		print ("AUDIO (%s): " % get_time())+string

class AudioDevice:
	def __init__(self, config):
		debug("__init__")
		self._doTerminate = False
		self.config = config
		self.evtStart = Event()
		self.evtStart.clear()
		self.audioProcLock = Lock()
		self.handler = None
		self.sound = None
		self.paramsSignalCycle = None
		self.paramsSignalsCnt = None
		self.sndFrequency = 0
		self.sndDuration = 0

	def __del__(self):
		debug("__del__")
		self.terminate()

	def registerHandler(self, handler):
		self.handler = handler
		params = handler.params()
		self.sndFrequency = params['sndFrequency']
		self.sndDuration = params['sndDuration']
		#if (not self.sndFrequency == params['sndFrequency']) or (not self.sndDuration == params['sndDuration']):
		self.sound = None
		while not self.sound:
			try:
				self.sound = Sine(params['sndFrequency'], float(params['sndDuration'])/1000,
						  float(params['signalCycle']-params['sndDuration'])/1000,
						  params['signalsCnt'])
			except:
				pass
		self.paramsSignalCycle = params['signalCycle']
		self.paramsSignalsCnt = params['signalsCnt']

	def detachHandler(self):
		self.handler = None
		self.sound = None
		self.paramsSignalCycle = None
		self.paramsSignalCnt = None

	def terminate(self):
		self._doTerminate = True
		self.evtStart.set()
		if hasattr(self, "_signalsThread"):
			self._signalsThread.join()
		debug("thread terminated")

	def startSignals(self, startTime):
		debug("start signals, at %d" % startTime, 1)
		self.startTime = startTime
		self.evtStart.set()

	def waitTillAudioStops(self):
		self.audioProcLock.acquire()
		self.audioProcLock.release()

	def checkIfAudioStopped(self):
		return not self.audioProcLock.locked()

	def start(self):
		self._signalsThread = Thread(target=self._presentSignals)
		self._signalsThread.daemon = 1
		self._signalsThread.start()

	def _presentSignals(self):
		debug("_presentSignals")
		while True:
			self.evtStart.wait()
			debug("got evtStart")
			self.audioProcLock.acquire()
			self.evtStart.clear()
			debug("audioProcLock acquired")
			if self._doTerminate == True:
				self.audioProcLock.release()
				return
			debug("sleeping till %d" % self.startTime)
			sleepTill(self.startTime)
			debug("sleep over, startig signals")
			self._handleOneTrial()
			debug("trial over")
			self.startTime = 0
			debug("finished signals")
			self.audioProcLock.release()
			debug("released audioProcLock")

	def _handleOneTrial(self):
		tc = TimeCorrection()
		tc.initIfIdle("audio-thread")
		debug("playing signals")
		delay = self.playSignal()
		debug("finished signals: delay <%d>" % delay)

	def handleSignalQueued(self):
		debug("PLAYING SIGNALS", 1)
		self.handler.handleSignalQueued()

	def handleSignalFinished(self):
		debug("PLAYED SIGNAL", 1)
		self.handler.handleSignalSignalFinished()

	def playSignal(self):
		self.handleSignalQueued()
		delay = self.sound.play()
		self.handleSignalFinished()
		return delay
