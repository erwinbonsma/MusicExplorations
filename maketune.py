import math
import wave
import struct
from enum import Enum

frate = 22050.0  # framerate as a float
channel_range = 256
min_val = -int(channel_range/2)
max_val = int(channel_range/2) - 1
eps = 0.0001

max_volume = 7
wave_table_size = 256

# Number of samples per volume step to ramp up (down) the volume at start (end) of a note
border_samples = 16

samples_per_note = int(frate / 7.5)

triangle_table = []
triangle_table.extend(range(min_val, max_val))
triangle_table.extend(range(max_val, min_val, -1))

wave_forms = [
    triangle_table, # 0
]

# Starts with A4
note_freqs = {
    "A":  440.00,
    "A#": 466.16,
    "B":  493.88,
    "C":  523.25,
    "C#": 554.37,
    "D":  587.33,
    "D#": 622.25,
    "E":  659.25,
    "F":  698.46,
    "F#": 739.99,
    "G":  783.99,
    "G#": 830.61
}

class Effect(Enum):
    NONE = 0
    DROP = 3

silence = ("", 0, 0, Effect.NONE)

# SFX 17 in Repair.p8
tune_volume = max_volume
sfx17 = [
    ("D#", 2, tune_volume, Effect.NONE),
    ("D#", 1, tune_volume, Effect.NONE),
    ("A#", 1, tune_volume - 1, Effect.NONE),
    ("D#", 1, tune_volume, Effect.NONE),
    ("F#", 2, tune_volume - 2, Effect.NONE),
    silence,
    ("F#", 2, tune_volume - 4, Effect.NONE),
    silence,

    ("D#", 2, tune_volume, Effect.NONE),
    ("D#", 1, tune_volume, Effect.NONE),
    ("A#", 1, tune_volume - 1, Effect.NONE),
    ("D#", 1, tune_volume, Effect.NONE),
    ("F#", 2, tune_volume - 2, Effect.NONE),
    silence,
    ("F#", 2, tune_volume - 4, Effect.NONE),
    silence,

    ("D#", 2, tune_volume, Effect.NONE),
    ("D#", 1, tune_volume, Effect.NONE),
    ("A#", 1, tune_volume - 1, Effect.NONE),
    ("D#", 1, tune_volume, Effect.NONE),
    ("F#", 2, tune_volume - 2, Effect.NONE),
    ("D#", 1, tune_volume, Effect.NONE),
    ("F#", 2, tune_volume - 4, Effect.NONE),
    ("D#", 1, tune_volume, Effect.NONE),

    ("D#", 2, tune_volume, Effect.NONE),
    ("D#", 1, tune_volume, Effect.NONE),
    ("A#", 1, tune_volume - 1, Effect.NONE),
    ("D#", 1, tune_volume, Effect.NONE),
    ("F#", 2, tune_volume - 2, Effect.NONE),
    silence,
    ("F#", 2, tune_volume - 4, Effect.NONE),
    silence,
]

sfx26 = [
    ("C", 1, 7, Effect.DROP), # TODO: Add drop (also everywhere else)
    silence,
    ("C", 1, 5, Effect.DROP),
    silence,
    ("C", 2, 5, Effect.DROP), # TODO: Make noise with fade out
    silence,
    ("C", 1, 5, Effect.DROP),
    ("C", 1, 5, Effect.DROP),

    ("C", 1, 7, Effect.DROP),
    silence,
    ("C", 1, 5, Effect.DROP),
    silence,
    ("C", 2, 5, Effect.DROP), # TODO: Make noise with fade out
    ("C", 1, 5, Effect.DROP),
    ("C", 1, 4, Effect.DROP),
    ("C", 0, 4, Effect.DROP),

    ("C", 1, 7, Effect.DROP),
    silence,
    ("C", 1, 5, Effect.DROP),
    silence,
    ("C", 2, 5, Effect.DROP), # TODO: Make noise with fade out
    silence,
    ("C", 1, 5, Effect.DROP),
    ("C", 1, 5, Effect.DROP),

    ("C", 1, 7, Effect.DROP),
    silence,
    ("C", 1, 5, Effect.DROP),
    silence,
    ("C", 2, 5, Effect.DROP), # TODO: Make noise with fade out
    ("C", 1, 5, Effect.DROP),
    ("C", 1, 4, Effect.DROP),
    ("C", 0, 4, Effect.DROP)
]

# Input is float value in range [-1, 1]
# Output is integer value in range [-channel_range/2, channel_range/2>
def make_discrete(x):
    return math.floor(x * (channel_range / 2 - eps))

def lerp(x0, x1, t):
    return (x1 - x0) * t + x0

# Surprisingly, this sounds pretty crap
sine_table = [
    make_discrete(math.sin(2 * math.pi * t / wave_table_size)) for t in range(wave_table_size)
]

silence_table = [0]

def make_tune(notes):
    samples = []
    for note in notes:
        name, octave, volume, effect = note
        if name == "":
            wave_table = silence_table
            period = 1
        else:
            wave_table = triangle_table
            period = frate / (note_freqs[name] * 2**(octave - 4 + 1))
        if effect == Effect.DROP:
            period_end = period * 2
        else:
            period_end = period

        for t in range(samples_per_note):
            p = lerp(period, period_end, t/samples_per_note)
            sample = wave_table[ int(t * len(wave_table) / p) % len(wave_table) ]
            boundary_delta = min(t, samples_per_note - 1 - t)
            v = volume * min(border_samples, boundary_delta) / border_samples
            samples.append(int(sample * (v / max_volume)))
    return samples

def write_wav(samples, fname):
    nchannels = 1
    sampwidth = 2
    framerate = int(frate)
    nframes = len(samples)
    comptype = "NONE"
    compname = "not compressed"

    wav_file = wave.open(fname, "w")
    wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))

    for sample in samples:
        wav_file.writeframes(struct.pack('h', sample * 64))

    wav_file.close()

# write_wav(make_tune(sfx17), "sfx17.wav")
write_wav(make_tune(sfx26), "sfx26.wav")