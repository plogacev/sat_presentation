import array, math, numpy, struct, ctypes
import pygame
import time

sampling_rate=44100
size=16
pygame.mixer.quit()
pygame.mixer.init(sampling_rate, size=-size, channels=1)

channel = pygame.mixer.Channel(7)
channel.set_volume(1.0)

class Sine:

    def __init__(self, frequency, duration, duration_pause, repetitions):
		self.duration = repetitions*(duration+duration_pause)
		duration_in_samples = int(sampling_rate*duration)
		pause_duration_in_samples = int(sampling_rate*duration_pause)
		samples = [5000*math.sin(2.0 * math.pi * frequency * t / sampling_rate) for t in xrange(0, duration_in_samples)]
		samples_pause = [0 for t in xrange(0, pause_duration_in_samples)]
		samples.extend(samples_pause)
		samples = samples*repetitions
		#s = []
		#for n in range(len(samples)):
		#	s.append( [samples[n]] ) #, samples[n]
		samples = numpy.array(samples, dtype=numpy.int16)
		self.sound = pygame.sndarray.make_sound(samples)
		self.sound.set_volume(1.0)
		
	
    def play(self):
		channel.play(self.sound)
		pygame.time.wait(int(self.duration*1000)+10)
		i = 0
		while pygame.mixer.get_busy():
			pygame.time.wait(10)
			i = i + 10
		return i
	
#    def __del__(self):	
#	pygame.mixer.quit()



if __name__ == '__main__':
	Sine(1000, .1, .9, 3).play()

