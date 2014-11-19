import pygame, math
from numpy import *
SAMPLE_RATE = 22050 ## This many array entries per 1 second of sound.


pygame.mixer.init(22050, -16, channels=2, buffer=SAMPLE_RATE*10)



def SineWave(freq=10,volume=16000,length=1):
    num_steps = int(length*SAMPLE_RATE)
    s = []
    for n in range(num_steps):
	t = float(n)/SAMPLE_RATE
        val = int(math.sin(t*freq*2*pi)*volume)
        s.append( [val, val] )
    x_arr = array(s)
    return x_arr

def SquareWave(freq=100,volume=100000,length=1):
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
    return pygame.sndarray.make_sound(arr)

def PlaySquareWave(freq=1000):
    MakeSound(SquareWave(freq)).play()

def PlaySineWave(freq=1000, volume=16000, length=1):
    MakeSound(SineWave(freq, volume, length)).play()


if __name__ == '__main__':
    PlaySquareWave()
    pygame.time.wait(3000)

