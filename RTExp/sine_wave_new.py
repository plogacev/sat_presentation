import pygame, math
from numpy import *
SAMPLE_RATE = 44100


pygame.mixer.init(SAMPLE_RATE, -16, channels=2, buffer=SAMPLE_RATE*10)



def SineWave(freq=10,length=1,volume=16000):
    num_steps = int(length*SAMPLE_RATE)
    s = []
    for n in range(num_steps):
	t = float(n)/SAMPLE_RATE
        val = int(math.sin(t*freq*2*pi)*volume)
        s.append( [val, val] )
    x_arr = array(s)
    return x_arr

def SquareWave(freq=100,length=1,volume=100000):
    length_of_plateau = SAMPLE_RATE / (2*freq)
    s = []
    counter = 0
    state = 1
    for n in range(length*SAMPLE_RATE):
        if state == 1:
            value = volume
        else:
            value = -volume
        s.append( [value,value] )

        counter += 1
        if counter == length_of_plateau:
            counter = 0
            if state == 1:
                state = -1
            else:
                state = 1

    x_arr = array(s)
    return x_arr

def MakeSound(arr):
    print arr
    return pygame.sndarray.make_sound(arr)

def PlaySquareWave(freq=1000):
    MakeSound(SquareWave(freq)).play()

def PlaySineWave(freq=1000, volume=16000, length=1):
    MakeSound(SineWave(freq, volume, length)).play()

class Sine:

    def __init__(self, frequency, duration):
		self.sound = MakeSound(SineWave(frequency))
		#duration_in_samples = sampling_rate*duration
		#samples = [5000*math.sin(2.0 * math.pi * frequency * t / sampling_rate) for t in xrange(0, duration_in_samples)]
		#samples = numpy.array(samples, dtype=numpy.int16)
		#self.sound = pygame.sndarray.make_sound(samples)
		#self.sound.set_volume(1.0)
		
    def play(self):
		self.sound.play()
		while pygame.mixer.get_busy():
			pygame.time.wait(200)
	

if __name__ == '__main__':
    Sine(1000, .1).play()

