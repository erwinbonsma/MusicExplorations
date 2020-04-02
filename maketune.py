import math
import wave
import struct
import random
from enum import IntEnum

frate = 22050.0  # framerate as a float
channel_range = 256
min_val = -int(channel_range/2)
max_val = int(channel_range/2) - 1
eps = 0.0001

max_volume = 7
wave_table_size = 256

# Number of samples per volume step to ramp up (down) the volume at start (end) of a note
ramp_up_samples = 16
ramp_dn_samples = ramp_up_samples

default_samples_per_note = int(frate / 7.5)

triangle_table = []
triangle_table.extend(range(min_val, max_val))
triangle_table.extend(range(max_val, min_val, -1))

organ_table = []
organ_table.extend(range(min_val, max_val))
organ_table.extend(range(max_val, min_val, -1))
organ_table.extend([x/2 + min_val/2 for x in range(min_val, max_val)])
organ_table.extend([x/2 + min_val/2 for x in range(max_val, min_val, -1)])

silence_table = [0]

wave_forms = [
    triangle_table, # 0
    silence_table,  # 1
    organ_table,    # 2
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

class Effect(IntEnum):
    NONE = 0
    SLIDE = 1
    VIBRATO = 2
    DROP = 3
    FADE_IN = 4
    FADE_OUT = 5

class Wave(IntEnum):
    TRIANGLE = 0
    SILENCE = 1
    ORGAN = 2
    NOISE = 8

silence = ("", 0, Wave.SILENCE, 0, Effect.NONE)

sfx_test1 = [
    # Four equal notes. These should fully blend into one.
    ("C", 3, Wave.TRIANGLE, 5, Effect.NONE),
    ("C", 3, Wave.TRIANGLE, 5, Effect.NONE),
    ("C", 3, Wave.TRIANGLE, 5, Effect.NONE),
    ("C", 3, Wave.TRIANGLE, 5, Effect.NONE),
    silence,
    ("C", 3, Wave.TRIANGLE, 5, Effect.NONE),
    ("D", 3, Wave.TRIANGLE, 5, Effect.NONE),
    ("E", 3, Wave.TRIANGLE, 5, Effect.NONE),
    ("F", 3, Wave.TRIANGLE, 5, Effect.NONE),
    silence,
    ("C", 3, Wave.TRIANGLE, 5, Effect.NONE),
    ("C", 3, Wave.TRIANGLE, 4, Effect.NONE),
    ("C", 3, Wave.TRIANGLE, 3, Effect.NONE),
    ("C", 3, Wave.TRIANGLE, 2, Effect.NONE),
]

# SFX 17 in Repair.p8
tune_volume = max_volume - 2
sfx17 = [
    ("D#", 2, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("D#", 1, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("A#", 1, Wave.TRIANGLE, tune_volume - 1, Effect.NONE),
    ("D#", 1, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("F#", 2, Wave.ORGAN, tune_volume - 2, Effect.NONE),
    silence,
    ("F#", 2, Wave.ORGAN, tune_volume - 4, Effect.NONE),
    silence,

    ("D#", 2, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("D#", 1, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("A#", 1, Wave.TRIANGLE, tune_volume - 1, Effect.NONE),
    ("D#", 1, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("F#", 2, Wave.ORGAN, tune_volume - 2, Effect.NONE),
    silence,
    ("F#", 2, Wave.ORGAN, tune_volume - 4, Effect.NONE),
    silence,

    ("D#", 2, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("D#", 1, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("A#", 1, Wave.TRIANGLE, tune_volume - 1, Effect.NONE),
    ("D#", 1, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("F#", 2, Wave.ORGAN, tune_volume - 2, Effect.NONE),
    ("D#", 1, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("A#", 1, Wave.TRIANGLE, tune_volume - 1, Effect.NONE),
    ("D#", 1, Wave.TRIANGLE, tune_volume, Effect.NONE),

    ("D#", 2, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("D#", 1, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("A#", 1, Wave.TRIANGLE, tune_volume - 1, Effect.NONE),
    ("D#", 1, Wave.TRIANGLE, tune_volume, Effect.NONE),
    ("F#", 2, Wave.ORGAN, tune_volume - 2, Effect.NONE),
    silence,
    ("F#", 2, Wave.ORGAN, tune_volume - 4, Effect.NONE),
    silence,
]

sfx18 = [
    ("G", 3, Wave.TRIANGLE, 4, Effect.NONE),
    ("G", 3, Wave.TRIANGLE, 4, Effect.NONE),
    ("G", 3, Wave.TRIANGLE, 4, Effect.NONE),
    ("G", 3, Wave.TRIANGLE, 4, Effect.VIBRATO),
    ("G", 3, Wave.TRIANGLE, 4, Effect.VIBRATO),
    ("G", 3, Wave.TRIANGLE, 4, Effect.VIBRATO),
    ("G", 3, Wave.TRIANGLE, 4, Effect.VIBRATO),
    ("G#", 3, Wave.TRIANGLE, 4, Effect.NONE),

    ("G", 3, Wave.TRIANGLE, 4, Effect.NONE),
    ("G", 3, Wave.TRIANGLE, 4, Effect.VIBRATO),
    ("G", 3, Wave.TRIANGLE, 4, Effect.VIBRATO),
    ("G", 3, Wave.TRIANGLE, 4, Effect.VIBRATO),
    ("D#", 3, Wave.TRIANGLE, 4, Effect.NONE),
    ("D#", 3, Wave.TRIANGLE, 4, Effect.NONE),
    ("D#", 3, Wave.TRIANGLE, 4, Effect.VIBRATO),
    ("C", 3, Wave.TRIANGLE, 4, Effect.NONE),

    ("F#", 3, Wave.TRIANGLE, 4, Effect.NONE),
    ("F#", 3, Wave.TRIANGLE, 4, Effect.NONE),
    ("F#", 3, Wave.TRIANGLE, 3, Effect.SLIDE),
    ("F#", 3, Wave.TRIANGLE, 3, Effect.NONE),
    ("F#", 3, Wave.TRIANGLE, 2, Effect.SLIDE),
    ("F#", 3, Wave.TRIANGLE, 2, Effect.NONE),
    ("F#", 3, Wave.TRIANGLE, 2, Effect.NONE),
    ("F#", 3, Wave.TRIANGLE, 1, Effect.SLIDE),

    ("F#", 3, Wave.TRIANGLE, 1, Effect.NONE),
    ("F#", 3, Wave.TRIANGLE, 1, Effect.NONE),
    ("F#", 3, Wave.TRIANGLE, 1, Effect.FADE_OUT)
]

sfx26 = [
    ("C", 1, Wave.TRIANGLE, 7, Effect.DROP),
    silence,
    ("C", 1, Wave.TRIANGLE, 5, Effect.DROP),
    silence,
    ("C", 2, Wave.NOISE, 5, Effect.FADE_OUT),
    silence,
    ("C", 1, Wave.TRIANGLE, 5, Effect.DROP),
    ("C", 1, Wave.TRIANGLE, 5, Effect.DROP),

    ("C", 1, Wave.TRIANGLE, 7, Effect.DROP),
    silence,
    ("C", 1, Wave.TRIANGLE, 5, Effect.DROP),
    silence,
    ("C", 2, Wave.NOISE, 5, Effect.FADE_OUT),
    ("C", 1, Wave.TRIANGLE, 5, Effect.DROP),
    ("C", 1, Wave.TRIANGLE, 4, Effect.DROP),
    ("C", 0, Wave.TRIANGLE, 4, Effect.DROP),

    ("C", 1, Wave.TRIANGLE, 7, Effect.DROP),
    silence,
    ("C", 1, Wave.TRIANGLE, 5, Effect.DROP),
    silence,
    ("C", 2, Wave.NOISE, 5, Effect.FADE_OUT),
    silence,
    ("C", 1, Wave.TRIANGLE, 5, Effect.DROP),
    ("C", 1, Wave.TRIANGLE, 5, Effect.DROP),

    ("C", 1, Wave.TRIANGLE, 7, Effect.DROP),
    silence,
    ("C", 1, Wave.TRIANGLE, 5, Effect.DROP),
    silence,
    ("C", 2, Wave.NOISE, 5, Effect.FADE_OUT),
    ("C", 1, Wave.TRIANGLE, 5, Effect.DROP),
    ("C", 1, Wave.TRIANGLE, 4, Effect.DROP),
    ("C", 0, Wave.TRIANGLE, 4, Effect.DROP)
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

def make_tune(notes, samples_per_note = default_samples_per_note):
    samples = []

    for note_idx in range(len(notes)):
        name, octave, wave, volume, effect = notes[note_idx]
        if wave == Wave.NOISE:
            wave_table = wave_forms[Wave.TRIANGLE]
        else:
            wave_table = wave_forms[wave]
        if wave == Wave.SILENCE:
            period = 1
        else:
            period = frate / (note_freqs[name] * 2**(octave - 4 + 1))

        volume_start = volume
        volume_end = volume
        period_start = period
        period_end = period

        if effect == Effect.DROP:
            period_end = period * 2
        elif effect == Effect.FADE_OUT:
            volume_end = 0
        elif effect == Effect.FADE_IN:
            volume_start = 0
        elif effect == Effect.SLIDE:
            volume_start = prev_volume_end
            period_start = prev_period_end

        prev_wave = None
        next_wave = None
        if note_idx > 0:
            _, _, prev_wave, _, _ = notes[note_idx - 1]
        if note_idx < len(notes) - 1:
            _, _, next_wave, _, _ = notes[note_idx + 1]

        if wave == prev_wave:
            volume_ramp_up = prev_volume_end
        else:
            volume_ramp_up = 0
            t = 0

        if wave == next_wave:
            volume_ramp_dn = volume_end
        else:
            volume_ramp_dn = 0

        t_delta = 0
        vibrato_offset = 0
        vibrato_dir = 1

        for n in range(samples_per_note):
            p = lerp(period_start, period_end, n / samples_per_note)
            v = lerp(volume_start, volume_end, n / samples_per_note)

            if wave == Wave.NOISE:
                t_delta += (random.random() - 0.5) * len(wave_table) / 8
                if t_delta < 0:
                    t_delta += len(wave_table)

            if effect == Effect.VIBRATO:
                vibrato_offset += vibrato_dir / (12 * p)
                if abs(vibrato_offset) > 2:
                    vibrato_dir = -vibrato_dir

            t += len(wave_table) / (p * (1 + vibrato_offset / 100))
            if t >= len(wave_table):
                t -= len(wave_table)

            if t_delta == 0:
                sample = wave_table[ int(t) ]
            else:
                sample = wave_table[ int(t + t_delta) %  len(wave_table) ]

            if n < ramp_up_samples:
                v = lerp(volume_ramp_up, v, n / ramp_up_samples)
            elif n >= samples_per_note - ramp_dn_samples:
                v = lerp(volume_ramp_dn, v, (samples_per_note - 1 - n) / ramp_dn_samples)

            samples.append(int(sample * (v / max_volume)))

        prev_period_end = period_end
        prev_volume_end = volume_end
        prev_wave = wave
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

samples_test1 = make_tune(sfx_test1)
samples17 = make_tune(sfx17)
samples26 = make_tune(sfx26)
samples18 = make_tune(sfx18, 2 * default_samples_per_note)

#combined = [x[0] + x[1] for x in zip(samples17, samples26)]
#write_wav(samples_test1, "sfx_test1.wav")
#write_wav(samples17, "sfx17.wav")
write_wav(samples18, "sfx18.wav")
#write_wav(samples26, "sfx26.wav")
#write_wav(combined, "combined.wav")
