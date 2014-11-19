import os, sys
import pygame
from pygame import locals
pygame.init()

from threading import Thread, Lock
from tc import *



def debug(string, level=1):
	if level < 2:
		print ("FEEDBACK (%s): "%get_time())+string


class FeedbackDevice:
	def __init__(self, config, mode):
		self.config = config
		self.mode = mode
		if mode == "-j":
			self.js = pygame.joystick.Joystick(config.jsNumber)
			self.js.init()
			config.JoystickSetup(self.js)
			self.mode = "joystick"

		elif mode == "-k":
			self.js = None
			self.mode = "keypad"

		else:
			raise "No input defined."

		self.keyProcLock = Lock()
		self.handler = None

	def __del__(self):
		debug("__del__")
		self.terminate()

	def terminate(self):
		debug("terminating thread", 1)
		pygame.event.post(pygame.event.Event(pygame.locals.QUIT))
		if hasattr(self, "_inputThread"):
			self._inputThread.join()
		debug("thread terminated", 1)

	def registerHandler(self, trial):
		self.handler = trial

	def detachHandler(self):
		debug("detachHandler")
		self.keyProcLock.acquire()
		self.handler = None
		self.keyProcLock.release()

	def start(self):
		self._inputThread = Thread(target=self._handleInput)
		self._inputThread.daemon = 1
		self._inputThread.start()
	
	def _handleInput(self):
		""" TODO: handle the problem of two events for a YesNo press."""
		keysTerminateSet = [False, False, False]
		if self.mode == "joystick":
			debug("mode: joystick")
			pygame.event.set_allowed(None)
			pygame.event.set_allowed([pygame.locals.QUIT, 
						  pygame.locals.JOYBUTTONDOWN, 
						  pygame.locals.JOYBUTTONUP])
			#pygame.event.set_blocked([pygame.locals.JOYAXISMOTION, 
			#			   pygame.locals.JOYBALLMOTION, 
			#			   pygame.locals.JOYHATMOTION])
			js = self.js
			keysTerminate = self.config.jsKeysTerminate

		elif self.mode == "keypad":
			debug("mode: keypad")
			pygame.event.set_allowed(None)
			pygame.event.set_allowed([pygame.locals.QUIT, pygame.KEYUP, pygame.KEYDOWN])
			keysTerminate = self.config.kbKeysTerminate

		else:
			debug("mode: none")

		while True:
		  	debug("waiting for event")
#			for e in pygame.event.get():
		  	e = pygame.event.wait()
			debug("got event, type %s, <%s>, <%s>" % (e.type, str(e), e.dict))
			self.keyProcLock.acquire()

			if e.type == pygame.locals.QUIT:
				self.keyProcLock.release()
				debug("quitting thread")
				return

			elif not self.handler:    
				self.keyProcLock.release()
				debug("no trial defined")
				continue

			elif e.type == pygame.KEYDOWN:
				debug("keyboard button")

				if e.key == self.config.kbKeyStart:
					self.__handleStart()

				if e.key == self.config.kbKeyContinue1:
					self.__handleContinue1()

				if e.key == self.config.kbKeyContinue2:
					self.__handleContinue2()

				if  e.key == self.config.kbKeyLeft:
					self.__handleLeft()

				elif e.key == self.config.kbKeyRight:
					self.__handleRight()

				elif e.key == self.config.kbKeyEsc:
					self.__handleTerminate()

			elif e.type == pygame.locals.JOYBUTTONDOWN:
				debug("joystick button")

				if e.button == self.config.jsKeyStart:
					self.__handleStart()

				if e.button == self.config.jsKeyContinue1:
					self.__handleContinue1()

				if e.button == self.config.jsKeyContinue2:
					self.__handleContinue2()

				if  e.button == self.config.jsKeyLeft:
					self.__handleLeft()

				elif e.button == self.config.jsKeyRight:
					self.__handleRight()
				elif e.button == keysTerminate[0]:
					debug("GOT TERM1")
					keysTerminateSet[0] = True
					debug("GOT TERM1: %s" % dir(e))
				elif e.button == keysTerminate[1]:
					debug("GOT TERM2")
					keysTerminateSet[1] = True
				elif e.button == keysTerminate[2]:
					debug("GOT TERM3")
					keysTerminateSet[2] = True
				debug("/joystick button")

			elif e.type == pygame.locals.JOYBUTTONUP:
				if e.button == keysTerminate[0]:
					debug("UNGOT TERM1")
					keysTerminateSet[0] = False
				elif e.button == keysTerminate[1]:
					debug("UNGOT TERM2")
					keysTerminateSet[1] = False
				elif e.button == keysTerminate[2]:
					debug("UNGOT TERM3")
					keysTerminateSet[2] = False

			if (keysTerminateSet[0] == True and
			    keysTerminateSet[1] == True and
			    keysTerminateSet[2] == True):
			
				debug("QUITTING" % keysTerminateSet, 1)
				self.__handleTerminate()

			debug("/proc")
			self.keyProcLock.release()

	def __handleTerminate(self):
		debug("QUITTING")
		if os.name == "nt":
			import win32api
			h = win32api.OpenProcess(1, False, os.getpid())
			win32api.TerminateProcess(h, -1)
			win32api.CloseHandle(h)
		elif os.name == "posix":
			os.system("kill -9 %d" % os.getpid())

	def __handleStart(self):
		if hasattr(self.handler, "handleStart"):
			self.handler.handleStart()
		else:
			debug("NO HANDLER FOR S", 1)

	def __handleContinue1(self):
		if hasattr(self.handler, "handleContinue1"):
			self.handler.handleContinue1()
		else:
			debug("NO HANDLER FOR C2", 1)

	def __handleContinue2(self):
		if hasattr(self.handler, "handleContinue2"):
			self.handler.handleContinue2()
		else:
			debug("NO HANDLER FOR C2", 1)

	def __handleLeft(self):
		if hasattr(self.handler, "handleLeft"):
			self.handler.handleLeft()
		else:
			debug("NO HANDLER FOR L", 1)

	def __handleRight(self):
		if hasattr(self.handler, "handleRight"):
			self.handler.handleRight()
		else:
			debug("NO HANDLER FOR R", 1)

