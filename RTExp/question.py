from VisionEgg.Core import Viewport, FrameTimer, Screen, swap_buffers
from VisionEgg.WrappedText import WrappedText
from VisionEgg.Text import Text

from config import globalScreen
from text_display import Display
from handler import ResponseHandler,  EventRecorder,  QuestionResponse,  DisplayUpdateStart, DisplayUpdateEnd
from tc import get_time
import string

def debug(string, level=2):
	if level < 2:
		print ("QUESTION (%s): "%get_time())+string

class Question(Display,  ResponseHandler,  EventRecorder):
	def __init__(self, config, question):
		self.displayPhrase = False

		colorBlack = (0.0,0.0,0.0)
		answLeft,  answRight = question['answers']
		answ_correct = question['correct']
		question = question['question']

		self.textAnswLeft = answLeft
		self.textAnswRight = answRight
		self.textAnswCorrect = answ_correct
		
		border = config.textDisplayBorder
		size=(globalScreen.size[0]-border, globalScreen.size[1]-border)
		positionQuestion = [globalScreen.size[0]/2,  globalScreen.size[1]/2]
		positionAnswLeft = [border,  border]
		positionAnswRight = [globalScreen.size[0]-border,  border]
	
		self._question = Text(text=question, color=colorBlack, size=size, 
					on=1, font_size=config.textQuestionSize, 
					font_name=config.font)
		positionQuestion[0] = positionQuestion[0] - self._question.parameters.size[0]/2
		self._question.parameters.position = positionQuestion

		self._answLeft = Text(text=answLeft, color=colorBlack, size=size, 
					on=1, font_size=config.textAnswerSize,
					font_name=config.font)
		self._answLeft.parameters.position = positionAnswLeft

		self._answRight = Text(text=answRight, color=colorBlack, size=size,
					on=1, font_size=config.textAnswerSize,
					font_name=config.font)
		positionAnswRight[0] = positionAnswRight[0] - self._answRight.parameters.size[0]
		self._answRight.parameters.position = positionAnswRight

		self._viewport = Viewport(screen=globalScreen, size=size,
                   			stimuli=[self._question,  self._answLeft,  
						self._answRight]) 
		ResponseHandler.__init__(self,  config)
		EventRecorder.__init__(self)

	def present(self, feedback):
		feedback.registerHandler(self)

		self.recordQuestionDisplayStart()
		self.updateDisplay(self._viewport)
		self.recordQuestionDisplayEnd()
		
		self.waitForResponse()
		feedback.detachHandler()

	def updateDisplay(self, viewport):
		globalScreen.clear()
		viewport.draw()
		swap_buffers()
	
	def recordQuestionDisplayStart(self):
		self.displayTime = get_time()
		self.recordUniqueEvent('questionDisplayStart',  DisplayUpdateStart('question'))
		return True

	def recordQuestionDisplayEnd(self):
		self.displayTime = get_time()
		self.displayPhrase = True
		self.recordUniqueEvent('questionDisplayEnd',  DisplayUpdateEnd('question'))
		return True

	# TODO: add answers
	def recordButton(self,  button):
		# don't record button presses before question display
		if self.displayPhrase:
			t = get_time()
			self.recordUniqueEvent('questionResponse', 
				QuestionResponse(button,  
					self.textAnswLeft, 
					self.textAnswRight,  
					self.textAnswCorrect,  
					t-self.displayTime))
			return True
		else:
			return False

	def processLeft(self):
		return self.recordButton("L")

	def processRight(self):
		return self.recordButton("R")
