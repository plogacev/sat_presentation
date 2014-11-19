import pyaudio
import struct
import numpy
import ctypes

chunk = 2048/2 # 1024

class Sine:
  def __init__(self, freq=1000, duration=1, sampling_rate=44100):
    """ Outputs a numpy array to the audio port, using PyAudio.  """

    t = numpy.linspace(0,1,sampling_rate*duration) # 44100 numbers between 0 and 1
    data = numpy.sin(t*2*numpy.pi*freq) # A above Middle C

    # Make Buffer
    buffer_size = struct.calcsize('@f') * len(data)
    output_buffer = ctypes.create_string_buffer(buffer_size)

    # Fill Up Buffer
    #struct needs @fffff, one f for each float
    format = '@' + 'f'*len(data)
    struct.pack_into(format, output_buffer, 0, *data)

    self.sound_buffer = output_buffer

    self.audio = pyaudio.PyAudio()
    self.stream = self.audio.open(format = pyaudio.paFloat32, 
	                channels = 1, rate = sampling_rate, 
		        input = True, output = True, 
	        	frames_per_buffer = chunk)

  def __del__(self):
	self.stream.close()

  def play(self):
    # Shove contents of buffer out audio port
    self.stream.write(self.sound_buffer)

#Sine(1024, 0.15).play()

#while True:
#	pass

