import argparse
import io
import math
import struct
import wave

import pygamelib

from pygamelib import pygame

# Note names in an octave, in the order of their semitone positions
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# frequency of the sine wave (A4 note)
A4_frequency = 440.0

beeps = {
    'beep1': 'T999 L9 C',
    'beep2': 'T999 L9 C#',
}

def parse_mml(mml, octave=4, length=0.25, tempo=120):
    """
    :param octave:
    :param length: default to quarter note
    :param tempo:
    """
    # music macro language
    notes = []
    i = 0
    while i < len(mml):
        char = mml[i]
        if char == 'T':
            i += 1
            tempo = int(mml[i:i+3])
            i += 2
        elif char == 'L':
            i += 1
            length = 4 / int(mml[i])
        elif char == 'O':
            i += 1
            octave = int(mml[i])
        elif char in 'CDEFGAB':
            note_name = char
            if i+1 < len(mml) and mml[i+1] == '#':
                note_name += '#'
                i += 1
            duration = length * 60 / tempo
            notes.append((note_name, octave, duration))
        i += 1
    return notes

def calculate_frequency(note_name, octave):
    note_index = NOTES.index(note_name)
    # Calculate the number of semitones from A4
    semitone_distance = note_index - NOTES.index('A') + (octave - 4) * 12
    # Calculate and return the frequency
    return A4_frequency * (2 ** (semitone_distance / 12.0))

def sine_sample(amplitude, frequency, n, sample_rate):
    return amplitude * math.sin(math.tau * frequency * n / sample_rate)

def generate_wav(sound_sequence, sample_func, sample_rate, amplitude=32767):
    data = bytearray()
    for note, octave, duration in sound_sequence:
        frequency = calculate_frequency(note, octave)
        num_samples = int(sample_rate * duration)
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

def run(notes_list, args):
    pygame.mixer.init()

    sounds = []
    for notes in notes_list:
        wav_buffer = generate_wav(notes, sine_sample, args.sample_rate)
        sound = pygame.mixer.Sound(wav_buffer)
        sounds.append(sound)

    screen = pygame.display.set_mode((800,)*2)

    font = pygamelib.monospace_font(20)
    printer = pygamelib.FontPrinter(font, 'azure')
    lines = [f'{key}: {beeps[key]}' for key in sorted(beeps)]
    surf = printer(lines)
    screen.blit(screen, (0,0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
                elif event.key == pygame.K_SPACE:
                    for sound in sounds:
                        sound.play()
        pygame.display.flip()

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mml',
        action = 'append',
    )
    parser.add_argument(
        '--duration',
        type = float,
        default = 0.1,
    )
    parser.add_argument(
        '--sample-rate',
        type = int,
        default = 44100,
    )
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)
    if args.mml:
        notes_list = [parse_mml(mml) for mml in args.mml]
        run(notes_list, args)

if __name__ == '__main__':
    main()
