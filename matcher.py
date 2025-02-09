import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate2d, correlate, stft
import tempfile
import subprocess  # To run shell commands
import os  # To handle file paths

# Converts the input audio file to a mono WAV file with specific parameters
# (bitrate: 128k, sample rate: 22050 Hz, mono).
def convert(path, dest):
    subprocess.run(["ffmpeg", "-y", "-i", path, "-ab", "128k", "-ac", "1", "-ar", "22050", "-vn", dest])

# Matcher class for handling and comparing audio signals
class Matcher:
    # Loads and preprocesses the original audio file
    def set_original(self, path):
        # Create a temporary file path for the converted audio
        temp = os.path.join(tempfile.gettempdir(), 'temp2893438.wav')
        # Convert the input file to WAV format with predefined settings
        convert(path, temp)
        # Read the WAV file and get the sampling frequency and data
        frequency, original = wavfile.read(temp)
        self.frequency = frequency  # Store the sampling frequency
        self.original = original
        self.clip = None
    
    # Loads and preprocesses the clip audio file
    def set_clip(self, path):
        # Create a temporary file path for the converted clip
        temp = os.path.join(tempfile.gettempdir(), 'temp2893439.wav')
        # Convert the input file to WAV format with predefined settings
        convert(path, temp)
        # Read the WAV file and get the data
        _, clip = wavfile.read(temp)
        self.clip = clip

    # Correlates the original audio with the clip to find the best match
    def correlate(self):
        return correlate_signals_sign(self.original, self.clip)


# Computes the cross-correlation of the Short-Time Fourier Transform (STFT)
# between two signals to find their best match in both time and frequency domains.
def correlate_stft(s1, s2, nperseg=1024, stride=256):
    # Ensure the first signal is the longer one
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    
    s1 = s1.astype(np.float64)
    s2 = s2.astype(np.float64)
    # Compute the STFT of both signals with overlapping segments
    noverlap = nperseg - stride
    _, _, z1 = stft(s1, nperseg=nperseg, noverlap=noverlap)  # STFT of signal 1
    _, _, z2 = stft(s2, nperseg=nperseg, noverlap=noverlap)  # STFT of signal 2
    z1 = z1.T  # Transpose for 2D correlation
    z2 = z2.T  # Transpose for 2D correlation
    # Perform 2D cross-correlation between the STFT representations
    correlation = np.repeat(np.abs(correlate2d(z1, z2, mode='valid').ravel()), stride)
    max_index = correlation.argmax()  # Find the index of the highest correlation
    return max_index, np.nan, correlation  # Return the time shift and a placeholder score


# Computes the cross-correlation of two 1D signals to find the best match
def correlate_signals(s1, s2):
    # Ensure the first signal is the longer one
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    
    s1 = s1.astype(np.float64)
    s2 = s2.astype(np.float64)
    
    # Compute the cross-correlation between the two signals
    correlation = correlate(s1, s2, mode='valid')
    max_index = correlation.argmax()  # Find the index of the highest correlation
    max_correlation = correlation[max_index]  # Get the maximum correlation value
    
    # Calculate the energy of the overlapping segments of both signals
    s1_energy = np.sum(s1[max_index:min(max_index + len(s2), len(s1))]**2)
    s2_energy = np.sum(s2**2)
    
    # Return the index of the best match and the normalized correlation coefficient
    return max_index, max_correlation / (np.sqrt(s1_energy) * np.sqrt(s2_energy)), correlation

# Computes the cross-correlation of two 1D signals to find the best match
def correlate_signals_sign(s1, s2):
    # Ensure the first signal is the longer one
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    
    s1 = s1.astype(np.float64)
    s2 = s2.astype(np.float64)

    s1 = np.sign(s1)
    s2 = np.sign(s2)
    
    # Compute the cross-correlation between the two signals
    correlation = correlate(s1, s2, mode='valid')
    max_index = correlation.argmax()  # Find the index of the highest correlation
    max_correlation = correlation[max_index]  # Get the maximum correlation value
    
    # Calculate the energy of the overlapping segments of both signals
    s1_energy = np.sum(s1[max_index:min(max_index + len(s2), len(s1))]**2)
    s2_energy = np.sum(s2**2)
    
    # Return the index of the best match and the normalized correlation coefficient
    return max_index, max_correlation / (np.sqrt(s1_energy) * np.sqrt(s2_energy)), correlation
