import math
import wave
import struct

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

# SFX 17 in Repair.p8
tune_volume = max_volume
tune = [
    ("D#", 2, tune_volume),
    ("D#", 1, tune_volume),
    ("A#", 1, tune_volume - 1),
    ("D#", 1, tune_volume),
    ("F#", 2, tune_volume - 2),
    ("", 0, 0),
    ("F#", 2, tune_volume - 4),
    ("", 0, 0),

    ("D#", 2, tune_volume),
    ("D#", 1, tune_volume),
    ("A#", 1, tune_volume - 1),
    ("D#", 1, tune_volume),
    ("F#", 2, tune_volume - 2),
    ("", 0, 0),
    ("F#", 2, tune_volume - 4),
    ("", 0, 0),

    ("D#", 2, tune_volume),
    ("D#", 1, tune_volume),
    ("A#", 1, tune_volume - 1),
    ("D#", 1, tune_volume),
    ("F#", 2, tune_volume - 2),
    ("D#", 1, tune_volume),
    ("F#", 2, tune_volume - 4),
    ("D#", 1, tune_volume),

    ("D#", 2, tune_volume),
    ("D#", 1, tune_volume),
    ("A#", 1, tune_volume - 1),
    ("D#", 1, tune_volume),
    ("F#", 2, tune_volume - 2),
    ("", 0, 0),
    ("F#", 2, tune_volume - 4),
    ("", 0, 0),
]

# Input is float value in range [-1, 1]
# Output is integer value in range [-channel_range/2, channel_range/2>
def make_discrete(x):
    return math.floor(x * (channel_range / 2 - eps))

# Surprisingly, this sounds pretty crap
sine_table = [
    make_discrete(math.sin(2 * math.pi * t / wave_table_size)) for t in range(wave_table_size)
]

triangle_table = []
triangle_table.extend(range(min_val, max_val))
triangle_table.extend(range(max_val, min_val, -1))

silence_table = [0]

def make_tune(notes):
    samples = []
    for note in notes:
        name, octave, volume = note
        if name == "":
            wave_table = silence_table
            period = 1
        else:
            wave_table = triangle_table
            period = frate / (note_freqs[name] * 2**(octave - 4 + 1))

        for t in range(samples_per_note):
            sample = wave_table[ int(t * len(wave_table) / period) % len(wave_table) ]
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

samples = make_tune(tune)
write_wav(samples, "tune.wav")