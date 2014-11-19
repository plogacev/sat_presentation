
import VisionEgg
from VisionEgg.Core import Viewport, FrameTimer, Screen, swap_buffers
from VisionEgg.Text import Text
from VisionEgg.WrappedText import WrappedText
from VisionEgg.MoreStimuli import FilledCircle
from threading import Event

from config import globalScreen
from tc import *
from text_display import Display
from handler import ResponseHandler, EventRecorder, QuestionResponse  
from question import Question
import string

def debug(string, level=2):
	if level < 2:
		print ("TRIAL (%s): "%get_time())+string

# TODO: Implement intertrial stimuli like cues.

class Trial(ResponseHandler,  EventRecorder):

	trial_header = ['subject', 'experiment',  'item', 'condition']

	def __init__(self, config, experiment, item, condition, mode, phrases, responses, question=None):
		self.experiment = experiment
		self.item = item
		self.condition = condition
		self.audio = None
		self.feedback = None
		self.config = config
		self.mode = mode

		if question:
			self.question = Question(config, question)
		else:
			self.question = None

		# list for recording the actual signal timing, if necessary (not used in SPR)
		self.signals = []

		# list for recording the actual display timing 
		self.display_updates = []
	
		self.evtStart = Event()
		self.evtUpdate = Event()
		self.evtContinue = Event()
	
		self.phraseLast = None
		self.phraseCurrent = None
		
		EventRecorder.__init__(self)
		ResponseHandler.__init__(self,  config)
		
		self.trial_header_val = ""
		for name in self.config.trial_header:
			if name == 'subject':
				self.trial_header_val = self.trial_header_val+str(self.config.participantNumber)+' '
			elif name == 'experiment':
				self.trial_header_val = self.trial_header_val+str(self.experiment)+' '
			elif name == 'item':
				self.trial_header_val = self.trial_header_val+str(self.item)+' '
			elif name == 'condition':
				self.trial_header_val = self.trial_header_val+str(self.condition)+' '

	def saveResponses(self,  results):
		lines = self.__eventLines(self.config.records_header,  self.trial_header_val)
		results.write(lines)
		results.flush()

	def stimulusId(self):
		return {'experiment': self.experiment,  'item': self.item,  'condition': self.condition}

	def __eventRecords(self):
		header,  records = EventRecorder.eventRecords(self)
		headerQ,  recordsQ = {}, []
		if self.question:
			headerQ,  recordsQ = self.question.eventRecords()
		header.update(headerQ)
		records.extend(recordsQ)
		return header,  records

	def __eventLines(self,  columns,  prefix=''):
		fullHeader,  records = self.__eventRecords()
		allColumns = fullHeader.keys()
		lines = ""
		for record in records:
			line = prefix + self.__eventLine(record,  columns) + '\n'
			lines = lines + line
		return lines

	def __eventLine(self,  record,  columns):
		line = ""
		for column in columns:
			format = "%s"
			if column == "time":
				format = "%f"
				line = line + " " + (format % float(record[column]))
			elif record.has_key(column):
				line = line + " " + (format % record[column])

			else:
				line = line + " NA"
		return line

	def isPractice(self):
		if(self.experiment == "practiceSentences" or
		   self.experiment == "practiceBasic"):
			return True
		else:
			return False

	def isWordStimulus(self):
		if self.experiment == "practiceBasic":
			return False
		else:
			return True

	def notifyTextUpdateStart(self, word):
		debug("DISPLAY UPDATE START, word <%s>" % word)
		t = get_time()
		self.display_updates.append([word, t, None])
		
	def notifyTextUpdateFinished(self, word):
		debug("DISPLAY UPDATE FINISH, word <%s>" % word)
		if self.display_updates[-1][0] != word:
			raise "TextChangeFinish expected for a different word."

		t = get_time()
		self.display_updates[-1][2] = t
