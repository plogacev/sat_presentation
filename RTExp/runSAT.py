#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import threading, sys, os, re
from threading import Thread, Timer, Event, Lock

from pygame.locals import QUIT,KEYDOWN,MOUSEBUTTONDOWN

from feedback_device import *
from text_display import InstructionsDisplay, StimulusDisplay
from trial_sat import SATTrial
from trial_spr import SPRTrial
from config import Config
from stimuli import read_stimuli
from handler import ResponseHandler

from audio_device import *
import VisionEgg.GUI 

#import os
#os.environ['SDL_VIDEO_WINDOW_POS']="0,0"

def debug(string):
	print "runSAT.py: "+string

class FakeFD:
	def __init__(self):
		self.handler = None
		self.lock = Lock()
		self.evt = Event()

	def start(self):
	   	self.__inputThread = Thread(target=self.__handleInput)
		self.__inputThread.daemon = 1
	        self.__inputThread.start()


	def terminate(self):
		self.evt.set()
		if hasattr(self, "__inputThread"):
		        self.__inputThread.join()

	def registerHandler(self, x):
		self.lock.acquire()	
		self.handler = x
		self.lock.release()	
	
	def __handleInput(self):
		while True:
			self.lock.acquire()	
			if self.handler:
				self.handler.handleStart()
				self.handler.handleContinue1()
				self.handler.handleContinue2()
				self.handler.handleLeft()
				self.handler.handleRight()
			else:
				debug("NO HANDLER")
			self.lock.release()	
			if self.evt.is_set():
				return


	def detachHandler(self):
		self.lock.acquire()	
		self.handler = None
		self.lock.release()	

# TODO: get rid of this class
class InstructionsWaiter(ResponseHandler):
	def __init__(self):
		self.evtS = Event(); self.evtS.clear()
	def handleLeft(self):
		pass
	def handleRight(self):
		pass
	def handleS(self):
		self.evtS.set()
	def waitForS(self):
		self.evtS.wait()

def check_existence(name):
	try:
		os.lstat(name)
		return True
	except OSError:
		return False

# CONSTANTS
resultsDirName = "Results"
filePractice = "items_practice"
fileInstructions = "instructions"
fileBlock = "items_block_"

debug("reading config")

# READ CONFIG AND COMMAND LINE ARGUMENTS
config = Config()
print sys.argv[1:4]
mode, subject, experimentDir, targetBlock = sys.argv[1:5]
config.ParticipantSetup(subject)

resultsDir = os.path.join(experimentDir, resultsDirName)
resultsFilename = os.path.join(resultsDir, "%s.%s.dat" % (subject, targetBlock))
targetFilename = os.path.join(experimentDir, "items_"+targetBlock)
#presentationFilename = os.path.join(resultsDir, "%s.block_%s.presentation" % (subject, targetBlock))
instructionsFilename = os.path.join(experimentDir, fileInstructions)

# TODO: check for non-existence of resultsFilename, old results should not be overwritten. Except for practice. There they should be appended 

if not check_existence(experimentDir):
	print "Experiment directory %s does not exist." % experimentDir
	sys.exit(-1)

if not check_existence(resultsDir):
	os.mkdir(resultsDir)

### find the practice items and read them
##practiceFilename = os.path.join(experimentDir, filePractice)
##if not check_existence(practiceFilename):
##	print "Practice file %s does not exist." % filePractice
##	sys.exit(-1)
##stimuliPractice = read_stimuli(practiceFilename, config)

### find the experimental items
##blockFilenamesTemp = []
##for filename in os.listdir(experimentDir):
##	if re.match(fileBlock, filename):
##		blockFilenamesTemp.append(filename)
##
##blockFilenames = [0]*len(blockFilenamesTemp)
##fileBlockLen = len(fileBlock)
##for filename in blockFilenamesTemp:
##	fileNum = int(file[fileBlockLen:])
##	blockFilenames[fileNum-1] = os.path.join(experimentDir, filename)
##del blockFilenamesTemp

debug("starting fd")

if config.jsFakeInput:
	fd = FakeFD()
else:
#	try:
		fd = FeedbackDevice(config, mode)
#	except:
#		sys.exit(-1)


debug("init display")
# TODO: StimulusDisplay seems to be quite obsolete with the new implementation of SAT and SPR presentation. Maybe it should be merged with InstructionDisplay.
td = StimulusDisplay(config)
fd.start()
ad = AudioDevice(config)
ad.start()

### read the experimental items
##stimuliExperiment = []
##for i in range(0, len(blockFilenames)):
##	filename = blockFilename[i]
##	if filename == "0":
##		print "At least one experimental block is missing.\n"
##		print "Files recognized as experimental blocks are %s." % blockFilenames
##		sys.exit(-1)
##	stimuliExperiment.append(read_stimuli( filename, config))


debug("reading stimuli")
# run trials
stimuli = read_stimuli(targetFilename, config)

debug("finished reading stimiuli")
# records practice statistics
responsesBasicTotal   = 0
responsesBasicPresses = 0
responsesBasicHits    = 0
responsesSentencesTotal   = 0 
responsesSentencesPresses = 0
responsesSentencesLastHits = 0
responsesSentencesLastTotal = 0

results = open(resultsFilename, "w")
#presentation = open(presentationFilename, "w")
results.write(config.dataHeader())

debug("starting presentation")
for s in stimuli:
	if s.__class__ == SATTrial:
		misclassifiedSentence = s.present(td, fd, ad)
		s.saveResponses(results)
		#results.flush()
		results.close()
		results = open(resultsFilename, "a")
		if misclassifiedSentence:
			text = config.string_incorrect_response + " \""+misclassifiedSentence+"\""
			sentenceDisplay = InstructionsDisplay(config, text)
			sentenceDisplay.present(fd)

	# TODO: Merge these two presentation routines
	elif s.__class__ == SPRTrial:
		s.present(td, fd, ad)
		s.saveResponses(results)
		#results.flush()
		results.close()
		results = open(resultsFilename, "a")

	elif s.__class__ == InstructionsDisplay:
		s.present(fd)

	else:
		raise "Unknown stimulus type. No idea how to present it."
debug("finished presentation")
	
results.close()
ad.terminate()
fd.terminate()
print "alive: %d" % threading.activeCount()

if responsesBasicTotal != 0:
	print "BASIC PRACTICE STATISTICS"
	print "Press ratio: %d/%d (%f)" % (responsesBasicPresses, responsesBasicTotal, float(responsesBasicPresses)/responsesBasicTotal)
	print "Accuracy: %d/%d (%f)" % (responsesBasicHits, responsesBasicTotal, float(responsesBasicHits)/responsesBasicPresses)
	print "\n"
if responsesSentencesTotal != 0:
	print "SENTENCE PRACTICE STATISTICS"
	print "Press ratio: %d/%d (%f)" % (responsesSentencesPresses, responsesSentencesTotal, float(responsesSentencesTotal)/responsesSentencesTotal)
	print "Accuracy: %d/%d (%f)" % (responsesSentencesLastHits, responsesSentencesLastTotal, float(responsesSentencesLastHits)/responsesSentencesLastTotal)
	print "Accuracy (Eventually): %d/%d (%f)" % (responsesSentencesHits, responsesSentencesLastTotal, float(responsesSentencesHits)/responsesSentencesPresses)
	print "\n"


