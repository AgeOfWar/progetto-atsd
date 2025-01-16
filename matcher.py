import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate2d, correlate, stft
import tempfile
import subprocess
import os

def convert(path, dest):
    subprocess.run(["ffmpeg", "-y", "-i", path, "-ab", "128k", "-ac", "1", "-ar", "22050", "-vn", dest])

class Matcher:
    def set_original(self, path):
        temp = os.path.join(tempfile.gettempdir(), 'temp2893438.wav')
        convert(path, temp)
        frequency, original = wavfile.read(temp)
        self.frequency = frequency
        original = original / np.max(np.abs(original))
        self.original = original
        self.clip = None

    def set_clip(self, path):
        temp = os.path.join(tempfile.gettempdir(), 'temp2893439.wav')
        convert(path, temp)
        _, clip = wavfile.read(temp)
        clip = clip / np.max(np.abs(clip))
        self.clip = clip

    def correlate(self):
        return correlate_signals(self.original, self.clip)
    

def correlate_stft(s1, s2, nperseg=512, stride=64):
    s1 = s1 - np.mean(s1)
    s1 = s1 / np.max(np.abs(s1))
    s2 = s2 - np.mean(s2)
    s2 = s2 / np.max(np.abs(s2))
    noverlap = nperseg - stride
    _, _, z1 = stft(s1, nperseg=nperseg, noverlap=noverlap)
    _, _, z2 = stft(s2, nperseg=nperseg, noverlap=noverlap)
    z1 = z1.T
    z2 = z2.T
    correlation = correlate2d(z1, z2, mode='valid')
    correlation = np.sum(np.abs(correlation), axis=1)
    print(correlation.shape)
    max_index = correlation.argmax()
    # max_correlation = correlation[max_index]
    # s1_energy = np.sum(z1[max_index:min(max_index + z2.shape[1], z1.shape[1])]**2)
    # s2_energy = np.sum(z2**2)
    return max_index * stride, 1 # max_correlation / (np.sqrt(s1_energy) * np.sqrt(s2_energy))


def correlate_signals(s1, s2):
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    correlation = correlate(s1, s2, mode='valid')
    max_index = correlation.argmax()
    max_correlation = correlation[max_index]
    s1_energy = np.sum(s1[max_index:min(max_index + len(s2), len(s1))]**2)
    s2_energy = np.sum(s2**2)
    return max_index, max_correlation / (np.sqrt(s1_energy) * np.sqrt(s2_energy))
