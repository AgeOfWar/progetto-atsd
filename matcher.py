import numpy as np
from scipy.io import wavfile
from scipy.signal import resample, correlate, stft, find_peaks
import tempfile
import subprocess
import os

def convert(path, dest):
    subprocess.run(["ffmpeg", "-y", "-i", path, "-ab", "128k", "-ac", "1", "-ar", "16384", "-vn", dest])

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
        original = fingerprint(self.original)
        clip = fingerprint(self.clip)
        index, precision = correlate_signals(original, clip)
        return index * len(self.original) // len(original), precision
    

def fingerprint(s, nperseg=256, stride=32):
    noverlap = nperseg - stride
    _ , _, z = stft(s, nperseg=nperseg, noverlap=noverlap)
    
    fingerprint = np.zeros(z.shape[1])
    for i in range(z.shape[1]):
        f = z[:, i]
        f = f / max(np.max(np.abs(f)), 1e-6)
        fingerprint[i] = np.sum(np.arange(len(f)) * np.abs(f)**2) / max(np.sum(np.abs(f)**2), 1e-6)
    return fingerprint


def correlate_signals(s1, s2):
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    correlation = correlate(s1, s2, mode='valid')
    max_index = correlation.argmax()
    max_correlation = correlation[max_index]
    s1_energy = np.sum(s1[max_index:min(max_index + len(s2), len(s1))]**2)
    s2_energy = np.sum(s2**2)
    return max_index, max_correlation / (np.sqrt(s1_energy) * np.sqrt(s2_energy))
