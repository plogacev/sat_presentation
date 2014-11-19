import time
import threading
from tc import get_time

def debug(string, level=2):
	if level < 2:
		print ("HANDLER (%s): "%get_time())+string


# TODO: Add class for audio handler.

# TODO: Change all inheriting classes' handleX() to processX()
class ResponseHandler:
	"""" Handles messages from the feedback thread. Add processX() methods to handle respective events."""
	def __init__(self,  config):
		self.config = config
		self.event = threading.Event()
		self.responseLock = threading.Lock()

		if hasattr(self, "processLeft"):
			self.handleLeft = self._processLeft
		else:
			self.handleLeft = self._ignoreLeft
	
		if hasattr(self, "processRight"):
			self.handleRight = self._processRight
		else:
			self.handleRight = self._ignoreRight

		if hasattr(self, "processContinue1"):
			self.handleContinue1 = self._processContinue1
		else:
			self.handleContinue1 = self._ignoreContinue1

		if hasattr(self, "processContinue2"):
			self.handleContinue2 = self._processContinue2
		else:
			self.handleContinue2 = self._ignoreContinue2

		if hasattr(self, "processStart"):
			self.handleStart = self._processStart
		else:
			self.handleStart = self._ignoreStart

	def acquireResponseLock(self):
		self.responseLock.acquire()
		
	def releaseResponseLock(self):
		self.responseLock.release()
		
	def _ignoreLeft(self):
		debug("ignoring left")
		return True

	def _processLeft(self):
		self.acquireResponseLock()
		if self.processLeft():
			self.releaseResponseLock()
			debug("processing left: OK")
			self.gotResponse()
			return True
		self.releaseResponseLock()
		debug("processing left: ERROR")
		return False

	def _ignoreRight(self):
		debug("ignoring right")
		return True

	def _processRight(self):
		self.acquireResponseLock()
		if self.processRight():
			self.releaseResponseLock()
			debug("processing right: OK")
			self.gotResponse()
			return True
		self.releaseResponseLock()
		debug("processing right: ERROR")
		return False

	def resetContinue1(self):
		self.handleContinue1 = self._ignoreContinue1

	def _ignoreContinue1(self):
		debug("ignoring continue1")
		return True

	def _processContinue1(self):
		self.acquireResponseLock()
		if self.processContinue1():
			self.releaseResponseLock()
			debug("processing continue1: OK")
			self.resetContinue2()
			self.gotResponse()
			return True
		self.releaseResponseLock()
		debug("processing continue1: ERROR")
		return False
		
	def resetContinue2(self):
		self.handleContinue2 = self._ignoreContinue2

	def _ignoreContinue2(self):
		debug("ignoring continue2")
		return True

	def _processContinue2(self):
		self.acquireResponseLock()
		if self.processContinue2():
			self.releaseResponseLock()
			debug("processing continue2: OK")
			self.resetContinue1()
			self.gotResponse()
			return True
		self.releaseResponseLock()
		debug("processing continue2: ERROR")
		return False
		
	def _ignoreStart(self):
		debug("ignoring start") 
		return True
		
	def _processStart(self):
		self.acquireResponseLock()
		if self.processStart():
			self.releaseResponseLock()
			debug("processing start: OK") 
			self.gotResponse()
			return True
		self.releaseResponseLock()
		debug("processing start: ERROR") 
		return False

	def gotResponse(self):
		debug("set event")
		self.event.set()

	def resetResponseSignal(self):
		debug("resetResponseSignal")
		self.event.clear()

	def waitForResponse(self, time=None):
		debug("waitForResponse")
		if not time:
			self.event.wait()
		else:
			self.event.wait(time)
		self.event.clear()


class EventRecorder:
	"""" Abstract class defining an interface to objects that record events."""
	def __init__(self):
		self.events = []

	def eventRecords(self):
		headers = {}
		records = []
		for evt in self.events:
			t,  name,  info = evt
			record = info.record() 
			records.append( record )
			for key in record.keys():
				headers[key] = 1
		return headers,  records

	def recordUniqueEvent(self,  name,  val=None):
		t = get_time()
		if self.hasEvent(name):
			debug("Tried to add an event which has already been recorded.")
			return False
		self.events.append( (t,  name,  val) )

	def recordEvent(self,  name,  val=None):
		t = time.time()
		#debug("time.time=%s" % t)
		self.events.append( (t,  name,  val) )

	def hasEvent(self,  name):
		evtRecord = self._getFirstEventRecord(name)
		return (evtRecord != None)

	def getUniqueEvent(self,  name):
		return self._getFirstEventRecord(name)

	def _getFirstEventRecord(self,  name):
		for evtTime, evtName, evtVal in self.events:
			if name == evtName:
				return (evtTime,  evtVal)
		return None

	def _getAllEventRecords(self,  name):
		results = []
		for evtTime, evtName, evtVal in self.events:
			if name == evtName:
				results.append( (evtTime, evtVal) )
		return results
		
	def eventsAsString(self):
		raise "Method needs to be instantiated!"
		
		
class Event:
	def record(self):
		raise "Method needs to be instantiated!"

class ITISleepStart(Event):
	def __init__(self,  t=None):
		if not t:
			t = time.time()
		self.time = t

	def record(self):
		return {'event': 'ITISleepStart', 'time': self.time}

class ITISleepEnd(Event):
	def __init__(self,  t=None):
		if not t:
			t = time.time()
		self.time = t

	def record(self):
		return {'event': 'ITISleepEnd', 'time': self.time}

class DisplayUpdateStart(Event):
	def __init__(self,  phraseNr,  t=None):
		self.phraseNr = phraseNr
		if not t:
			t = time.time()
		self.time = t

	def record(self):
		return {'event': 'displayUpdateStart', 'time': self.time, 'phraseNr': self.phraseNr}

class DisplayUpdateEnd(Event):
	def __init__(self,  phraseNr,  t=None):
		self.phraseNr = phraseNr
		if not t:
			t = time.time()
		self.time = t

	def record(self):
		return {'event': 'displayUpdateEnd', 'time': self.time, 'phraseNr': self.phraseNr}


class SignalStart(Event):
	def __init__(self,  signalNr,  t=None):
		self.signalNr = signalNr
		if not t:
			t = time.time()
		self.time = t

	def record(self):
		return {'event': 'signalStart', 
			'time': self.time, 
			'signalNr': self.signalNr}

class SignalEnd(Event):
	def __init__(self,  signalNr,  t=None):
		self.signalNr = signalNr
		if not t:
			t = time.time()
		self.time = t

	def record(self):
		return {'event': 'signalEnd', 
			'time': self.time, 
			'signalNr': self.signalNr}



class SPRResponse(Event):
	def __init__(self,  button,  phraseNr,  phrase, RT,  t=None):
		self.button = button
		self.phraseNr = phraseNr
		self.phrase = phrase
		self.RT = RT
		if not t:
			t = time.time()
		self.time = t

	def record(self):
		q = "\""
		return {'event': 'sprResponse',  'time': self.time, 'button':self.button, 'phraseNr': self.phraseNr,  'phrase': q+self.phrase+q, 'RT': self.RT}


class SATResponse(Event):
	def __init__(self, interval, button_side, button_grammaticality, button_correct, RT, t=None):
		self.interval = interval
		self.button_side = button_side
		self.button_grammaticality = button_grammaticality
		self.button_correct = button_correct
		self.RT = RT
		if not t:
			t = time.time()
		self.time = t

	def record(self):
		return {'event': 'satResponse',  
			'time': self.time, 
			'interval':self.interval, 
			'responseButton': self.button_side,  
			'responseGrammatical': self.button_grammaticality, 
			'responseCorrect': self.button_correct, 
			'RT': self.RT}



# TODO: add
class QuestionResponse(Event):
	def __init__(self,  button,  answerLeft,  answerRight,  answerCorrect, RT,  t=None):
		self.button = button
		self.answerLeft = answerLeft
		self.answerRight = answerRight
		self.answerCorrect = answerCorrect
		self.RT = RT
		if not t:
			t = time.time()
		self.time = t

	def record(self):
		q = "\""
		return {'event': 'questionResponse',  'time': self.time, 'button':self.button, 'answerLeft': q+self.answerLeft+q,  'answerRight': q+self.answerRight+q, 'answerCorrect': q+self.answerCorrect+q, 'RT': self.RT}
