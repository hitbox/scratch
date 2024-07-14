import argparse
import io
import math
import struct
import wave

import pygamelib

from pygamelib import pygame

# Note names in an octave, in the order of their semitone positions
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# samples per second
sample_rate = 44100
# seconds
duration = 0.1
# frequency of the sine wave (A4 note)
A4_frequency = 440.0

def calculate_frequency(note_name, octave):
    note_index = NOTES.index(note_name)
    # Calculate the number of semitones from A4
    semitone_distance = note_index - NOTES.index('A') + (octave - 4) * 12
    # Calculate and return the frequency
    return A4_frequency * (2 ** (semitone_distance / 12.0))

def sine_sample(amplitude, frequency, n, sample_rate):
    return amplitude * math.sin(math.tau * frequency * n / sample_rate)

def generate_wav(duration, frequency, sample_func):
    num_samples = int(sample_rate * duration)

    amplitude = 32767
    data = bytearray()
    for n in range(num_samples):
        sample = sample_func(amplitude, frequency, n, sample_rate)
        data.extend(struct.pack('<h', int(sample)))

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data)

    wav_buffer.seek(0)
    return wav_buffer

def run(args):
    pygame.mixer.init()

    frequency = calculate_frequency(args.note, args.octave)
    wav_buffer = generate_wav(args.duration, frequency, sine_sample)
    sound = pygame.mixer.Sound(wav_buffer)

    screen = pygame.display.set_mode((800,)*2)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
                elif event.key == pygame.K_SPACE:
                    sound.play()

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'note',
        choices = NOTES,
    )
    parser.add_argument(
        'octave',
        type = int,
    )
    parser.add_argument(
        '--duration',
        type = float,
        default = 0.1,
    )
    args = parser.parse_args(argv)
    run(args)

if __name__ == '__main__':
    main()
