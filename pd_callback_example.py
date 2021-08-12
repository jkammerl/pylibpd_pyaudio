import pyaudio
from pylibpd import *
import time
import numpy as np

class PdAudio:
    def __init__(self):
        self.sample_rate = 44100
        self.num_channel = 2
        self.pd = self.__InitPd(self.num_channel, self.sample_rate)
        self.py_audio = pyaudio.PyAudio()
        self.block_size = libpd_blocksize()
        self.stream = self.__InitAudio(self.num_channel, self.sample_rate,self.block_size)
        self.inbuf = array.array('h', range(self.block_size))
        print("Blocksize: %d" % self.block_size)

    def StartPatchInBackground(self, filename):
        self.patch = libpd_open_patch(filename, '.')

    def IsPlaying(self):
        return self.stream.is_active()

    def __InitAudio(self, num_channels, sample_rate, block_size):
        return self.py_audio.open(format = pyaudio.paInt16,
                                  channels = num_channels,
                                  rate = sample_rate,
                                  input = False,
                                  output = True,
                                  frames_per_buffer = block_size,
                                  stream_callback=self.__AudioCallback)

    def __InitPd(self, num_channels, sample_rate):
        return PdManager(1, num_channels, sample_rate, 1)

    def __AudioCallback(self, in_data,frame_count,time_info,status):
        outp = self.pd.process(self.inbuf)
        return (outp.tobytes(),pyaudio.paContinue)

    def __del__(self):
        self.stream.close()
        self.pd.terminate()
        libpd_release()

pd_audio = PdAudio()
pd_audio.StartPatchInBackground('bloopy.pd')

while pd_audio.IsPlaying():
    print("Sleeping in main thread")
    time.sleep(1.0)

