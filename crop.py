import sys
import numpy as np
from scipy.io import wavfile

def crop_audio(input_file, output_file, start_time, duration):
    """
    Ritaglia un file audio WAV a partire da un istante iniziale per una durata specificata.

    Parametri:
    - input_file: percorso del file WAV di input.
    - output_file: percorso del file WAV di output.
    - start_time: tempo di inizio del ritaglio in secondi.
    - duration: durata del ritaglio in secondi.
    """
    # Legge il file audio
    sample_rate, data = wavfile.read(input_file)
    print(f"Frequenza di campionamento: {sample_rate} Hz")
    
    # Calcola gli indici di inizio e fine in base al sample rate
    start_sample = int(start_time * sample_rate)
    end_sample = start_sample + int(duration * sample_rate)
    
    # Verifica che end_sample non superi la lunghezza del segnale
    if end_sample > len(data):
        print("Attenzione: il ritaglio supera la durata del file audio. Verrà ritagliato fino alla fine.")
        end_sample = len(data)
    
    # Esegue il ritaglio
    cropped_data = data[start_sample:end_sample]
    
    # Salva il file audio ritagliato
    wavfile.write(output_file, sample_rate, cropped_data)
    print(f"Audio ritagliato da {start_time} sec per una durata di {duration} sec salvato in '{output_file}'")

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Utilizzo: python crop.py input.wav output.wav inizio durata")
        print("Esempio: python crop.py input.wav output.wav 10 5")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    start_time = float(sys.argv[3])
    duration = float(sys.argv[4])
    
    crop_audio(input_file, output_file, start_time, duration)