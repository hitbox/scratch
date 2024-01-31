import argparse
import math
import struct
import wave

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    # Samples per second
    sampling_rate = 44100

    # Duration of the sound in seconds
    duration = 2

    # Frequency of the sine wave (440 Hz for A4)
    frequency = 440

    # Maximum amplitude for 16-bit audio
    amplitude = 32767
    amplitude = 2**14//4

    # Calculate the number of frames for the given duration
    num_frames = int(duration * sampling_rate)

    # Generate the waveform (sine wave)
    audio_data = []
    for i in range(num_frames):
        sample = int(amplitude * math.sin(math.tau * frequency * i / sampling_rate))
        audio_data.append(sample)

    # Convert the audio data into a bytes object
    audio_bytes = b''
    for sample in audio_data:
        # Pack as signed short integer (16-bit)
        audio_bytes += struct.pack('<h', sample)

    # Save the audio data as a wave file
    with wave.open('sine_wave.wav', 'wb') as wave_file:
        wave_file.setnchannels(1)  # Mono audio
        wave_file.setsampwidth(2)  # 2 bytes per sample for 16-bit audio
        wave_file.setframerate(sampling_rate)
        wave_file.writeframes(audio_bytes)

if __name__ == '__main__':
    main()
