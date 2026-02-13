"""
The Worlds Shortest Romance Novel, a poem by Zachary Smith, set to music of
sorts.

Copyright (c) 2026 R. Dunbar Poor, Andy Milburn and pygmu2 contributors

MIT License
"""

import pygmu2 as pg
from named_assets import (
    get_named_irs, 
    get_wav_files, 
    get_named_slices, 
    get_uke_notes,
    highpass_4th_order
)
import random
random.seed(20260210)

SAMPLE_RATE = 44100
pg.set_sample_rate(SAMPLE_RATE)

from pygmu2.logger import setup_logging, get_logger
setup_logging(level="INFO")
logger = get_logger(__name__)

"""
BPM = 40

B   Event
0   foghorn_amp ramp in for 8
6   snores_amp ramp in for 12
12  bubbles_amp ramp in for 12
12  whalesong_amp ramp in for 12
20  drum / chord ostinato starts (0, 2, 4, rest)
34  "my half brother"

    crowd_amp
    crowd_wet_mix
    speech_wet_mix
"""

BEATS_PER_MINUTE = 40
SECONDS_PER_BEAT = 60.0 / BEATS_PER_MINUTE

def b2sec(beats):
    return beats * SECONDS_PER_BEAT

def b2samp(beats):
    return int(round(b2sec(beats) * SAMPLE_RATE))

def samp2b(samples):
    seconds = float(samples) / SAMPLE_RATE
    beats = seconds / SECONDS_PER_BEAT
    return beats

NAMED_IRS = get_named_irs()
NAMED_SLICES = get_named_slices()
UKE_NOTES = get_uke_notes()

IR_10_PATH = "data/assets/impulses/synthetic_ir_10.wav"
IR_10 = pg.WavReaderPE(IR_10_PATH)

# ------------------------------------------------------------------------------
# Control ramps for various tracks

bubbles_track = pg.ConstantPE(0)
foghorn_track = pg.ConstantPE(0)
snores_track = pg.ConstantPE(0)
whalesong_track = pg.ConstantPE(0)
drums_track = pg.ConstantPE(0)
plings_track = pg.ConstantPE(0)
voices_track = pg.ConstantPE(0)
crowd_track = pg.ConstantPE(0)

# ------------------------------------------------------------------------------
# bubbles_track

bubbles_stream = NAMED_SLICES['bubbles_0_125']
bubble_loop_1 = pg.LoopPE(bubbles_stream)
bubble_loop_2 = pg.DelayPE(pg.LoopPE(bubbles_stream), int(bubbles_stream.extent().end/2))
bubbles_left = pg.SpatialPE(bubble_loop_1, method=pg.SpatialLinear(azimuth=-75.0))
bubbles_right = pg.SpatialPE(bubble_loop_2, method=pg.SpatialLinear(azimuth=75.0))
bubbles_stereo = pg.MixPE(bubbles_left, bubbles_right)
bubbles_track = bubbles_stereo

# ------------------------------------------------------------------------------
# foghorn_track

foghorn_stream = pg.LoopPE(NAMED_SLICES['foghorns'])

foghorn_track = foghorn_stream

# ------------------------------------------------------------------------------
# snores_track

snoring_stream = highpass_4th_order(pg.LoopPE(NAMED_SLICES['snores']), 120)
snores_track = snoring_stream

# ------------------------------------------------------------------------------
# whalesong_track

def make_whalesong():
    delay = 0
    segments = []

    pe = NAMED_SLICES['jasper1_0_3']
    segments.append(pg.DelayPE(pe, delay))
    delay += pe.extent().duration + b2samp(3) # 3 beats of silence before next

    pe = NAMED_SLICES['jasper2_0_3']
    segments.append(pg.DelayPE(pe, delay))
    delay += pe.extent().duration + b2samp(3) # 3 beats of silence before next

    pe = NAMED_SLICES['jasper3_0_3']
    segments.append(pg.DelayPE(pe, delay))
    delay += pe.extent().duration + b2samp(3) # 3 beats of silence before next

    pe = NAMED_SLICES['jasper4_0_3']
    segments.append(pg.DelayPE(pe, delay))
    delay += pe.extent().duration + b2samp(3) # 3 beats of silence before next

    pe = NAMED_SLICES['jasper5_0_3']
    segments.append(pg.DelayPE(pe, delay))
    delay += pe.extent().duration + b2samp(3) # 3 beats of silence before next

    pe = NAMED_SLICES['jasper6_0_3']
    segments.append(pg.DelayPE(pe, delay))
    delay += pe.extent().duration + b2samp(3) # 3 beats of silence before next

    # keep the 3 beats of silence
    jaspers = pg.SetExtentPE(pg.MixPE(*segments), 0, delay)

    return jaspers

# pan uwing a random walk
wandering_whalesong = pg.SpatialPE(
    pg.LoopPE(make_whalesong()),
    method=pg.SpatialConstantPower(
        azimuth=pg.RandomPE(
            min_value=-80.0,
            max_value=80.0,
            mode=pg.RandomMode.WALK,
            slew=0.001))
    )

# wet_whalesong = pg.ReverbPE(wandering_whalesong, NAMED_IRS['large_plate'], mix = 0.8)
wet_whalesong = pg.ReverbPE(wandering_whalesong, IR_10, mix = 0.6)

whalesong_track = wet_whalesong

# ------------------------------------------------------------------------------
# drums_track

DRUMS = [
    NAMED_SLICES['taiko1'],
    NAMED_SLICES['taiko2'],
    NAMED_SLICES['taiko3'],
    NAMED_SLICES['taiko6'],
    NAMED_SLICES['taiko7'],
]

trigger_pattern = pg.PiecewisePE(
    [
    (b2samp(0), 1.0), (b2samp(2)-2, 1.0), (b2samp(2)-1, 0.0),
    (b2samp(2), 1.0), (b2samp(4)-2, 1.0), (b2samp(4)-1, 0.0),
    (b2samp(4), 1.0), (b2samp(6)-2, 1.0), (b2samp(6)-1, 0.0),
    (b2samp(14)-1, 0.0)],
    transition_type=pg.TransitionType.STEP,
    )
drums_chosen = pg.RandomSelectPE(
    trigger=pg.LoopPE(trigger_pattern),
    inputs=DRUMS, 
    trigger_mode=pg.TriggerMode.RETRIGGER
    )
drums_loop = pg.LoopPE(pg.SetExtentPE(drums_chosen, 0, b2samp(14)))

drums_track = pg.SetExtentPE(drums_loop, 0, None)

# ------------------------------------------------------------------------------
# plings_track

PLING_STACKS = [
    (53, 58, 66, 73),  # good
    (47, 54, 62, 67),  # okay
    (53, 58, 66, 74),  # okay
    (47, 52, 55, 63),  # okay
    (47, 53, 58, 63),  # good
    (53, 61, 66, 72),  # good
    # (49, 55, 63, 68),  # good
    (49, 55, 63, 74),  # good

    (52, 60, 63, 71),  # good
    (47, 55, 57, 73),  # too sweet
    (50, 57, 64, 70),  # okay
    (49, 55, 60, 66),  # okay
    (46, 53, 55, 63),  # tonal
]

def make_randomized_start_times(n:int, max_start_time:float = 1.0) -> list[float]:
    """
    Return a list of N floats, representing the start time of each of N notes.
    The first start time is always 0, the last start time is always less than
    or equal to max_start_time
    """
    start_times = [0.0]
    max_delta = max_start_time / float(n)
    for _ in range(n-1):
        start_times.append(start_times[-1] + (random.random() * max_delta))

    print(f'Start times = {start_times}')
    return start_times

def make_uke_resource_name(pitch):
    return f'uke_{pitch:02d}'

def generate_stacked_chord(pitch_stack:list[int]):
    start_times = make_randomized_start_times(len(pitch_stack), max_start_time=2.0)
    notes = []
    for pitch, start_time in zip(pitch_stack, start_times):
        notes.append((UKE_NOTES[make_uke_resource_name(pitch)], b2samp(start_time)))
    stacked_notes = pg.SequencePE(*notes)
    return stacked_notes

def generate_stacked_chords(stacks):
    chords = []
    start = 0
    for stack in stacks:
        chords.append((generate_stacked_chord(stack), b2samp(start)))
        start += 14
    return pg.SequencePE(*chords)

wet_chords = pg.ReverbPE(generate_stacked_chords(PLING_STACKS), ir=IR_10, mix=0.6)

plings_track = wet_chords

# ------------------------------------------------------------------------------
# voices_track

def trio(n1, n2, n3):
    # mix three slice names, panning left, center, right
    # return a duple of (mix, max_dur)
    p1 = NAMED_SLICES[n1]
    p2 = NAMED_SLICES[n2]
    p3 = NAMED_SLICES[n3]
    max_dur = max(p1.extent().duration,
                  p2.extent().duration,
                  p3.extent().duration)
    return (max_dur, p1, p2, p3)

def make_voices():
    delay = 0
    segments1 = []
    segments2 = []
    segments3 = []
    print(f"My half brother ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 my half brother", "r1 my half brother", "n2 my half brother")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"His house is ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 his house is", "r1 his house is", "n2 his house is")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"Most days ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 most days", "r1 most days", "n2 most days")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration
    print(f"Tethered only by ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 tethered only by", "r1 tethered only by", "n2 tethered only by")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"At night, far off ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 at night, far off", "r1 at night, far off", "n2 at night, far off")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"Once a fish swam ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 once a fish swam", "r1 once a fish swam", "n2 once a fish swam")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"Once his breathing ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 once his breathing", "r1 once his breathing", "n2 once his breathing")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"He put something ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 he put something", "r1 he put something", "n2 he put something")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"Here, hold this ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 here, hold this", "r1 here, hold this", "n2 here, hold this")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"A while or maybe ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 a while or maybe", "r1 a while or maybe", "n2 a while or maybe")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"We were standing ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 we were standing", "r1 we were standing", "n2 we were standing")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"This is the skull ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 this is the skull", "r1 this is the skull", "n2 this is the skull")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.0)
    print(f"If you put it up ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 if you put it up", "r1 if you put it up", "n2 if you put it up")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration
    print(f"You can hear ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 you can hear", "r1 you can hear", "n2 you can hear")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration + b2samp(1.5)
    print(f"To Be Born ({samp2b(delay):0.2f} beats)")
    duration, p1, p2, p3 = trio(
        "n1 to be born", "r1 to be born", "n2 to be born")
    segments1.append(pg.DelayPE(p1, delay))
    segments2.append(pg.DelayPE(p2, delay))
    segments3.append(pg.DelayPE(p3, delay))

    delay += duration

    v1_compressed = pg.CompressorPE(pg.MixPE(*segments1))
    v2_compressed = pg.CompressorPE(pg.MixPE(*segments2))
    v3_compressed = pg.CompressorPE(pg.MixPE(*segments3))
    v3_attenuated = pg.GainPE(v3_compressed, 0.5)

    v1_panned = pg.SpatialPE(v1_compressed, method=pg.SpatialLinear(azimuth=-75.0))
    v2_panned = pg.SpatialPE(v2_compressed, method=pg.SpatialLinear(azimuth=0.0))
    v3_panned = pg.SpatialPE(v3_attenuated, method=pg.SpatialLinear(azimuth=75.0))

    return pg.MixPE(v1_panned, v2_panned, v3_panned)

voices_dry = make_voices()
voices_wet = pg.ReverbPE(voices_dry, NAMED_IRS['small_prehistoric_cave'], mix = 0.3)

voices_track = voices_wet

# ------------------------------------------------------------------------------
# crowd_track

crowd = NAMED_SLICES['crowd']
crowd_wet = pg.ReverbPE(
    crowd,
    NAMED_IRS['small_plate'],
    mix = 0.6
    )

crowd_track = crowd_wet

# ------------------------------------------------------------------------------
# submixes:
#
# individual tracks are delayed until their start time
# ramp breakpoints, etc, are expressed in absolute time.

bubbles_dly = pg.DelayPE(bubbles_track, b2samp(0))
bubbles_gain_db = pg.PiecewisePE([
    (b2samp(0), -30.0),   # holdoff
    (b2samp(10), 0.0),    # complete ramp up
    (b2samp(38+37.5), 0.0),    # here, hold this (duck)
    (b2samp(38+38), -10.0),    
    (b2samp(38+43), 0.0),    
    (b2samp(38+68), -20.0),   # ramp down
    (b2samp(110), -20.0),   # start ramp down
    (b2samp(115), -60),   # complete ramp down
    ])
bubbles_mix = pg.GainPE(
    bubbles_dly, 
    gain=pg.TransformPE(bubbles_gain_db, func=pg.db_to_ratio)
    )

foghorn_dly = pg.DelayPE(foghorn_track, b2samp(5))
foghorn_gain_db = pg.PiecewisePE([
    (b2samp(0), -30.0),   # holdoff
    (b2samp(5), -30),     # start ramp up
    (b2samp(10), 0.0),    # complete ramp up
    (b2samp(38+37.5), 0.0),    # here, hold this (duck)
    (b2samp(38+38), -10.0),    
    (b2samp(38+43), 0.0),    
    (b2samp(110), 0.0),   # start ramp down
    (b2samp(115), -60),   # complete ramp down
    ])
foghorn_mix = pg.GainPE(
    foghorn_dly, 
    gain=pg.TransformPE(foghorn_gain_db, func=pg.db_to_ratio)
    )

snores_dly = pg.DelayPE(snores_track, b2samp(5))
snores_gain_db = pg.PiecewisePE([
    (b2samp(0), -40.0),   # holdoff
    (b2samp(5), -40),     # start ramp up
    (b2samp(20), -20.0),    # complete ramp up
    (b2samp(38+37.5), -20.0),    # here, hold this (start duck)
    (b2samp(38+38), -60.0),    # ramp down, stay down for rest of piece
    (b2samp(115), -60),   # complete ramp down
    ])
snores_mix = pg.GainPE(
    snores_dly, 
    gain=pg.TransformPE(snores_gain_db, func=pg.db_to_ratio)
    )

whalesong_dly = pg.DelayPE(whalesong_track, b2samp(10))
whalesong_gain_db = pg.PiecewisePE([
    (b2samp(0), -30.0),   # holdoff
    (b2samp(10), -30),    # start ramp up
    (b2samp(15), 0.0),    # complete ramp up
    (b2samp(38+37.5), 0.0),    # here, hold this (duck)
    (b2samp(38+38), -10.0),    
    (b2samp(38+43), 0.0),    
    (b2samp(110), 0.0),   # start ramp down
    (b2samp(115), -60),   # complete ramp down
    ])
whalesong_mix = pg.GainPE(
    whalesong_dly, 
    gain=pg.TransformPE(whalesong_gain_db, func=pg.db_to_ratio)
    )

drums_dly = pg.DelayPE(drums_track, b2samp(15))
drums_mix = pg.SetExtentPE(drums_dly, b2samp(15), b2samp(90))

plings_dly = pg.DelayPE(plings_track, b2samp(22.5))
plings_mix = plings_dly

voices_dly = pg.DelayPE(voices_track, b2samp(38))
voices_mix = voices_dly

# start fading in before "this is the skull" at 38 + 54.6 beats"
# fade out fast at "to be born" at 38 + 65.5
crowd_dly = pg.DelayPE(crowd_track, b2samp(38+52))
crowd_gain_db = pg.PiecewisePE([
    (b2samp(0), -60.0),       # holdoff
    (b2samp(38+52), -60.0),   # 
    (b2samp(38+54), -20.0),   # this is the skull
    (b2samp(38+64), 4.0),     # (complete ramp to full)
    (b2samp(38+68), -20.0),   # ramp down
    (b2samp(115), -60.0),     # end
    ])
crowd_mix = pg.GainPE(
    crowd_dly, 
    gain=pg.TransformPE(crowd_gain_db, func=pg.db_to_ratio)
    )

# ------------------------------------------------------------------------------
# Final mix

mix = pg.MixPE(
    bubbles_mix,
    foghorn_mix,
    snores_mix,
    whalesong_mix,
    drums_mix,
    plings_mix,
    voices_mix,
    crowd_mix,
    )
duration = b2samp(115)
# Save mix to file "mix.wav" and open sound file browser to play it
pg.browse(
    pg.CropPE(mix, 0, duration),
    path = "mix.wav", 
    )
