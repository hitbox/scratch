import argparse
import math
import random

class SoundGenerator:

    def __init__(
        self,
        volume = 0.3,
        sample_rate = 44100,
    ):
        self.volume = volume
        self.sample_rate = sample_rate

    def build_samples(
        self,
        volume = 1,
        randomness = 0.05,
        frequency = 220,
        attack = 0,
        sustain = 0,
        release = 0.1,
        shape = 0,
        shape_curve = 1,
        slide = 0,
        delta_slide = 0,
        pitch_jump = 0,
        pitch_jump_time = 0,
        repeat_time = 0,
        noise = 0,
        modulation = 0,
        bit_crush = 0,
        delay = 0,
        sustain_volume = 1,
        decay = 0,
        tremolo = 0,
        filter_ = 0,
    ):
        slide *= 500 * math.tau / self.sample_rate / self.sample_rate
        startSlide = slide
        frequency *= (1 + randomness*2*random.random() - randomness) * math.tau / self.sample_rate
        startFrequency = frequency
        tm = 0
        j = 1
        r = 0
        c = 0
        s = 0

        # biquad LP/HP filter
        quality = 2
        w = math.tau * abs(filter_) * 2 / self.sample_rate
        cosw = math.cos(w)
        alpha = math.sin(w) / 2 / quality
        a0 = 1 + alpha
        a1 = -2*cosw / a0
        a2 = (1 - alpha) / a0
        b0 = (1 + sign(filter_) * cosw) / 2 / a0
        b1 = -(sign(filter_) + cosw) / a0
        b2 = b0
        x2 = 0
        x1 = 0
        y2 = 0
        y1 = 0

        # scale by sample rate
        attack = attack * self.sample_rate + 9 # minimum attack to prevent pop
        decay *= self.sample_rate
        sustain *= self.sample_rate
        release *= self.sample_rate
        delay *= self.sample_rate
        delta_slide *= 500 * math.tau / self.sample_rate ** 3
        modulation *= math.tau / self.sample_rate
        pitch_jump *= math.tau / self.sample_rate
        pitch_jump_time *= self.sample_rate
        repeat_time = repeat_time * self.sample_rate
        volume *= self.volume

        shape_func = shape_funcs[shape]

        b = []
        t = 0
        length = attack + decay + sustain + release + delay
        for i in range(int(length)):
            c += 1
            if bit_crush and (c + 1) % (bit_crush * 100) == 0:
                s = process_sample(c, bit_crush, shape, t, i, repeat_time,
                                   tremolo, shape_curve, attack, decay,
                                   sustain, sustain_volume, length, delay,
                                   release, b, volume, filter_, b0, b1, b2, a1,
                                   a2, x1, x2, y1, y2)
            slide += delta_slide
            frequency += slide

            f = frequency * math.cos(modulation * tm)
            t += f + f * noise * math.sin(i ** 5)

            tm += 1
            b.append(s * volume)

        return b


def triangle(t):
    return 1 - 4 * abs(round(t / math.tau) - t / math.tau)

def saw(t):
    return 1 - (2 * t / math.tau % 2 + 2) % 2

def tan(t):
    max(min(math.tan(t), 1), -1)

def noise(t):
    return math.sin(t ** 3)

shape_funcs = {
    0: math.sin,
    1: triangle,
    2: saw,
    3: tan,
    4: noise,
}

def process_sample(c, bit_crush, shape, t, i, repeat_time, tremolo,
                   shape_curve, attack, decay, sustain, sustain_volume, length,
                   delay, release, b, volume, filter_, b0, b1, b2, a1, a2, x1,
                   x2, y1, y2):
    # Bit Crush Effect

    # Wave Shape Calculation
    if shape > 3:
        s = math.sin(t ** 3)
    elif shape > 2:
        s = max(min(math.tan(t), 1), -1)
    elif shape > 1:
        s = 1 - ((2 * t / math.tau) % 2 + 2) % 2
    elif shape > 0:
        s = 1 - 4 * abs(round(t / math.tau) - t / math.tau)
    else:
        s = math.sin(t)

    # Apply Tremolo Effect
    if repeat_time:
        tremolo_effect = (1 - tremolo + tremolo * math.sin(math.tau * i / repeat_time))
    else:
        tremolo_effect = 1
    s = tremolo_effect * (math.copysign(1, s) * (abs(s) ** shape_curve))

    # Envelope Calculation
    if i < attack:
        s *= i / attack
    elif i < attack + decay:
        s *= 1 - ((i - attack) / decay) * (1 - sustain_volume)
    elif i < attack + decay + sustain:
        s *= sustain_volume
    elif i < length - delay:
        s *= (length - i - delay) / release * sustain_volume
    else:
        s *= 0

    # Delay Effect
    if delay:
        if i < delay:
            s = s / 2
        else:
            release_delay = (1 if i < length - delay else (length - i) / delay)
            s = s / 2 + release_delay * b[int(i - delay)] / (2 * volume)

    # Apply Filter
    if filter_:
        # FIXME
        #y1 = b2 * x2 + b1 * (x2 = x1) + b0 * (x1 = s) - a2 * y2 - a1 * (y2 = y1)
        #s = y1
        pass

    return s

def sign(v):
    if v < 0:
        return -1
    else:
        return 1

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    sg = SoundGenerator()
    bytes_ = sg.build_samples()

if __name__ == '__main__':
    main()

# 2024-08-11 Sun.
# - Reading this:
#   https://frankforce.com/space-huggers-how-i-made-a-game-in-13-kilobytes/
# - Mentions this:
#   https://github.com/KilledByAPixel/ZzFX/tree/master
# - Want to make a Python version.
