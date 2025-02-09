import numpy as np
from scipy.io import wavfile
import sys

def add_white_noise(audio, noise_level):
    """
    Aggiunge rumore bianco al segnale audio.

    Parametri:
    - audio: array NumPy contenente il segnale audio.
    - noise_level: fattore che controlla l'ampiezza del rumore in relazione
      all'ampiezza massima del segnale originale (ad esempio, 0.05 per il 5%).
      
    Ritorna:
    - audio_noisy: segnale audio distorto dal rumore bianco.
    """
    # Calcola la deviazione standard del rumore in funzione del livello desiderato
    std_dev = noise_level * np.max(np.abs(audio))
    # Genera rumore bianco con distribuzione normale (media 0, deviazione standard calcolata)
    noise = np.random.normal(0, std_dev, audio.shape)
    
    # Aggiunge il rumore al segnale originale
    audio_noisy = audio + noise

    # Se il segnale è in formato intero, effettua un clipping per evitare overflow
    if audio.dtype == np.int16:
        audio_noisy = np.clip(audio_noisy, -32768, 32767)
    elif audio.dtype == np.int32:
        audio_noisy = np.clip(audio_noisy, -2147483648, 2147483647)
    
    return audio_noisy.astype(audio.dtype)

def main(input_file, output_file, noise_level):
    # Legge il file audio
    rate, audio = wavfile.read(input_file)
    print("Frequenza di campionamento:", rate)
    print("Forma dell'audio:", audio.shape)

    # Aggiunge rumore bianco al segnale audio
    audio_noisy = add_white_noise(audio, noise_level)
    
    # Salva il segnale distorto in un nuovo file WAV
    wavfile.write(output_file, rate, audio_noisy)
    print("File output salvato in:", output_file)

if __name__ == "__main__":
    # Uso: python distorce_audio.py input.wav output.wav noise_level
    # Esempio: python distorce_audio.py input.wav output.wav 0.05
    if len(sys.argv) < 4:
        print("Utilizzo: python add_noise.py input.wav output.wav noise_level")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    noise_level = float(sys.argv[3])
    main(input_file, output_file, noise_level)