import pygmu2 as pg
from named_assets import get_named_irs, get_wav_files, get_named_slices, highpass_4th_order

SAMPLE_RATE = 44100
pg.set_sample_rate(SAMPLE_RATE)

from pygmu2.logger import setup_logging, get_logger
setup_logging(level="INFO")
logger = get_logger(__name__)


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


# ------------------------------------------------------------------------------
# spoken voice - three sources, sync'd to start each phrase at the same time

def trio(n1, n2, n3):
    # mix three slice names, panning left, center, right
    # return a duple of (mix, max_dur)
    p1 = pg.SpatialPE(NAMED_SLICES[n1], method=pg.SpatialLinear(azimuth=-75.0))
    p2 = pg.SpatialPE(NAMED_SLICES[n2], method=pg.SpatialLinear(azimuth=0.0))
    p3 = pg.SpatialPE(NAMED_SLICES[n3], method=pg.SpatialLinear(azimuth=75.0))
    max_dur = max(p1.extent().duration,
                  p2.extent().duration,
                  p3.extent().duration)
    return (max_dur, pg.MixPE(p1, p2, p3))

def voices():
    delay = 0
    segments = []
    duration, pe = trio(
        "n1 my half brother", "r1 my half brother", "n2 my half brother")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.5)
    duration, pe = trio(
        "n1 his house is", "r1 his house is", "n2 his house is")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.5)
    duration, pe = trio(
        "n1 most days", "r1 most days", "n2 most days")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration
    duration, pe = trio(
        "n1 tethered only by", "r1 tethered only by", "n2 tethered only by")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.5)
    duration, pe = trio(
        "n1 at night, far off", "r1 at night, far off", "n2 at night, far off")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.5)
    duration, pe = trio(
        "n1 once a fish swam", "r1 once a fish swam", "n2 once a fish swam")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.5)
    duration, pe = trio(
        "n1 once his breathing", "r1 once his breathing", "n2 once his breathing")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.5)
    duration, pe = trio(
        "n1 he put something", "r1 he put something", "n2 he put something")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.5)
    print(f"Here, hold this at {delay} ({samp2b(delay)} beats)")
    duration, pe = trio(
        "n1 here, hold this", "r1 here, hold this", "n2 here, hold this")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.5)
    print(f"A while or maybe at {delay} ({samp2b(delay)} beats)")
    duration, pe = trio(
        "n1 a while or maybe", "r1 a while or maybe", "n2 a while or maybe")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.5)
    duration, pe = trio(
        "n1 we were standing", "r1 we were standing", "n2 we were standing")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.7)
    print(f"This is the skull at {delay} ({samp2b(delay)} beats)")
    duration, pe = trio(
        "n1 this is the skull", "r1 this is the skull", "n2 this is the skull")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.5)
    duration, pe = trio(
        "n1 if you put it up", "r1 if you put it up", "n2 if you put it up")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration
    duration, pe = trio(
        "n1 you can hear", "r1 you can hear", "n2 you can hear")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration + b2samp(0.7)
    print(f"To Be Born at {delay} ({samp2b(delay)} beats)")
    duration, pe = trio(
        "n1 to be born", "r1 to be born", "n2 to be born")
    segments.append(pg.DelayPE(pe, delay))
    delay += duration

    return pg.MixPE(*segments)

voice_mix = voices()
wet_voice = pg.ReverbPE(
    voice_mix,
    NAMED_IRS['small_prehistoric_cave'],
    mix = 0.3
    )

# ------------------------------------------------------------------------------
# drums and tones

drums = [
    NAMED_SLICES['taiko1'],
    NAMED_SLICES['taiko2'],
    NAMED_SLICES['taiko3'],
    # NAMED_SLICES['taiko4'],
    # NAMED_SLICES['taiko5'],
    NAMED_SLICES['taiko6'],
    NAMED_SLICES['taiko7'],
    # NAMED_SLICES['taiko8'],
    # NAMED_SLICES['taiko9'],
]

trigger_pattern = pg.PiecewisePE(
    [
    (b2samp(0), 1.0), (b2samp(4)-2, 1.0), (b2samp(4)-1, 0.0),
    (b2samp(4), 1.0), (b2samp(8)-2, 1.0), (b2samp(8)-1, 0.0),
    (b2samp(8), 1.0), (b2samp(12)-2, 1.0), (b2samp(12)-1, 0.0),
    (b2samp(20), 0.0)],
    transition_type=pg.TransitionType.STEP,
    )
print(f"trigger_pattern extent = {trigger_pattern.extent()} ({samp2b(trigger_pattern.extent().duration)})")
pg.render_to_file(trigger_pattern, "pulses.wav")
random_drum = pg.RandomSelectPE(
    trigger=pg.LoopPE(trigger_pattern),
    inputs=drums, 
    trigger_mode=pg.TriggerMode.RETRIGGER
    )

wet_drum = pg.ReverbPE(
    random_drum,
    NAMED_IRS['small_plate'],
    mix = 0.3
    )

# chord ideas
# 52 59 63 70 <7><4><7>  <18>
# 50 57 64 68 <7><7><4>  <18>
# 53 59 64 69 <6><5><5>  <16>
# 48 55 62 66 <7><7><4>  <18>

# ------------------------------------------------------------------------------
# bubbles

# Create left and right channel loops
pitched_bubbles = NAMED_SLICES['bubbles_0_125']
bubble_loop_1 = pg.LoopPE(pitched_bubbles)
bubble_loop_2 = pg.DelayPE(pg.LoopPE(pitched_bubbles), int(pitched_bubbles.extent().end/2))
bubbles_left = pg.SpatialPE(bubble_loop_1, method=pg.SpatialLinear(azimuth=-75.0))
bubbles_right = pg.SpatialPE(bubble_loop_2, method=pg.SpatialLinear(azimuth=75.0))
stereo_bubbles = pg.MixPE(bubbles_left, bubbles_right)

# Fade in over 10 beats
bubble_db_ramp = pg.PiecewisePE(
    [(0.0, -60.0), (b2samp(10), 0.0)], 
    transition_type=pg.TransitionType.LINEAR,
    extend_mode = pg.ExtendMode.HOLD_LAST
    )
bubble_ratio_ramp = pg.TransformPE(bubble_db_ramp, func = pg.db_to_ratio)
ramped_bubbles = pg.GainPE(stereo_bubbles, bubble_ratio_ramp)

# ------------------------------------------------------------------------------
# snoring

# Snoring ramps up over 10 beats, loops forever
snoring = NAMED_SLICES['snores']
snoring_loop = pg.LoopPE(snoring)
filtered_snoring = highpass_4th_order(snoring_loop, 120)
snoring_db_ramp = pg.PiecewisePE(
    [(0.0, -60.0), (b2samp(10), 0.0)],
    transition_type=pg.TransitionType.LINEAR,
    extend_mode = pg.ExtendMode.HOLD_LAST
    )
snoring_ratio_ramp = pg.TransformPE(snoring_db_ramp, func = pg.db_to_ratio)
ramped_snoring = pg.GainPE(snoring_loop, snoring_ratio_ramp)

# ------------------------------------------------------------------------------
# foghorns

# Foghorns loop forever
foghorns = pg.LoopPE(NAMED_SLICES['foghorns'])

# ------------------------------------------------------------------------------
# jasper whalesong

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

    # extend mix out to delay for silence before next loop
    jaspers = pg.LoopPE(pg.CropPE(pg.MixPE(*segments), 0, delay))

    # pan uwing a random walk
    wandering_jasper = pg.SpatialPE(
        jaspers,
        method=pg.SpatialConstantPower(
            azimuth=pg.RandomPE(
                min_value=-80.0,
                max_value=80.0,
                mode=pg.RandomMode.WALK,
                slew=0.001))
        )
    return wandering_jasper


wet_jasper = pg.ReverbPE(make_whalesong(), NAMED_IRS['large_plate'], mix = 0.8)

# ------------------------------------------------------------------------------
# crowd crescendo - ramps up with abrubt drop

crowd = NAMED_SLICES['crowd']
crowd_db_ramp = pg.PiecewisePE(
    [(0.0, -60.0), (b2samp(20), 0.0), (b2samp(20)+1, -60.0)],
    transition_type=pg.TransitionType.LINEAR,
    extend_mode = pg.ExtendMode.HOLD_LAST
    )
crowd_ratio_ramp = pg.TransformPE(crowd_db_ramp, func = pg.db_to_ratio)
ramped_crowd = pg.GainPE(crowd, crowd_ratio_ramp)
wet_crowd = pg.ReverbPE(
    ramped_crowd,
    NAMED_IRS['small_plate'],
    mix = 0.6
    )

# ------------------------------------------------------------------------------
# Submixes and final mix

# ambient = bubbles + foghorn + snoring
dry_ambient = pg.SequencePE([
    (pg.GainPE(pg.CropPE(ramped_bubbles, 0, None), pg.db_to_ratio(-10)), b2samp(0)), 
    (pg.GainPE(foghorns, pg.db_to_ratio(-10)), b2samp(0)),
    ])
wet_ambient = pg.ReverbPE(
    dry_ambient, 
    NAMED_IRS['large_plate'],
    mix = 0.5)


# mix = pg.CropPE(wet_background_pad, 0, b2samp(180))


# We'll use SequencePE to control the starting time of each element.  Note that
# we crop them starting at zero in case they extend to negative infinity.
#
# mix_sans_voice has all parts except voice so we can ramp it separately
mix_sans_voice = pg.SequencePE([
    (pg.GainPE(pg.CropPE(wet_ambient, 0, None), 2.0), b2samp(0)),
    (pg.GainPE(pg.CropPE(ramped_snoring, 0, None), pg.db_to_ratio(-30)), b2samp(1)),
    (pg.GainPE(pg.CropPE(wet_drum, 0, None), 1.0), b2samp(14)),
    (pg.GainPE(pg.CropPE(wet_jasper, 0, None), 0.25), b2samp(20)),
    (pg.GainPE(pg.CropPE(wet_crowd, 0, None), 1.0), b2samp(67)) # 33 beats into voice
    ]
)

mix = pg.SequencePE([
    (mix_sans_voice, b2samp(0)),
    (pg.GainPE(pg.CropPE(wet_voice, 0, None), 0.5), b2samp(34)),    
    ])

duration = voice_mix.extent().end + b2samp(44+12)
pg.play_offline(pg.CropPE(mix, 0, duration), SAMPLE_RATE)
