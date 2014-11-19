import time
import pygame
from time import time as abs_time

def debug(string, level=2):
	if level < 2:
		print ("TC (%s): " % get_time())+string


tcClock = pygame.time.Clock()

def get_time():
	return pygame.time.get_ticks()

def sleep(t):
	return pygame.time.wait(t)


# TODO: use pygame.time

class TimeCorrection:
	""" This class is supposed to facilitate sleeping by correcting for the
	    assumption that every operation except for finishes immediately. The
	    reason for using initIfNotRunning() is that time correction should
	    start after the first presentation of a stimulus, and thus at a 
	    later point in the first loop iteration than in all subsequent.
	"""
	def __init__(self):
		self.time = None

	def get_time(self):
		#return time.time()
		return pygame.time.get_ticks()

	def wait(self, t):
		#return time.sleep(t)
		return pygame.time.wait(t)

	def initIfIdle(self, name):
		""" TODO: find out why I gave this function this name or rename
		    it to something more sensible otherwise. I guess the name
		    must have something to do with successive or recursive 
		    calls. """
		if not self.time:
			self.time = self.get_time()
			self.name = name

	def reset(self):
		self.time = self.get_time()

	def sleep(self, t, double=False):
		""" t: Time to sleep for. Counted since last call to reset()
		    double: Boolean. Set to True if the event that happened 
		    between reset() and sleep() will happen again after sleep().
		    This option is meant for occurences of lengthy events, like
		    display updates. """
		now = self.get_time()
		error = (now - self.time)
		if double:
			error = 2*error
		if error < t:
			debug("%s (%s): supposed to sleep for %s, sleeping for %s" % (self.name, get_time(), t, (t-error)))
			self.wait(int(t-error))
		else:
			debug("%s (%s): supposed to sleep for %s, not sleeping (error=%s, self.time=%s)" % (self.name, get_time(), t, error, self.time))
		self.time = self.time+t

	def sleepAndExecute(self, t, func, evt):
		now = self.get_time()
		error = (now - self.time)
		if error < t:
			debug("%s (%s): supposed to sleep and execute for %s, sleeping for %s" % (self.name, get_time(), t, (t-error)))
			while True:
				if evt.isSet():
					func()
					evt.clear()
				error = (self.get_time() - self.time)
				wait_interval = t-error
				if wait_interval <= 0:
					break
				evt.wait(wait_interval/1000)
		else:
			debug("%s (%s): supposed to sleep and execute for %s, not sleeping (error=%s)" % (self.name, get_time(), t, error))
		if evt.isSet():
			func()
			evt.clear()
		self.time = self.time+t
	

def sleepTill(t):
	sleep(t-get_time())



