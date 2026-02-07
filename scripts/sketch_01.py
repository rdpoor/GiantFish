from import_assets import create_named_slices, _play
import pygmu2 as pg

from pygmu2.logger import setup_logging, get_logger
setup_logging(level="INFO")
logger = get_logger(__name__)


TEMPO_BPM = 64
SECONDS_PER_BEAT = TEMPO_BPM/60
SAMPLE_RATE = 44100
NAMED_SLICES = create_named_slices()

def b2sec(beat):
    return beat * SECONDS_PER_BEAT

def b2s(beat):
    return int(round(b2sec(beat) * SAMPLE_RATE))

def drum_ostinato():
    duration = b2s(16)
    taiko = NAMED_SLICES['taiko1']
    drum_seq = pg.SequencePE(
        (taiko, b2s(0)),
        (taiko, b2s(4)),
        (taiko, b2s(12)),
    )
    return pg.LoopPE(pg.SequencePE(
            (taiko, b2s(0)), 
            (taiko, b2s(4)), 
            (taiko, b2s(8)),
            # rest...
        ),
        loop_start=b2s(0),
        loop_end=b2s(16)
    )
    return drums

drums = pg.CropPE(drum_ostinato(), pg.Extent(b2s(0), b2s(72)))
bay = NAMED_SLICES['foghorns_full']
whalesong = pg.TimeWarpPE(
    pg.GainPE(
        pg.SequencePE(
            (NAMED_SLICES['jasper_1'], b2s(11)),
            (NAMED_SLICES['jasper_2'], b2s(40)),
            (NAMED_SLICES['jasper_3'], b2s(50)),
            (NAMED_SLICES['jasper_4'], b2s(72)),
        ),
        gain = 0.1
    ),
    rate = 0.75
)
wet_mix = pg.ConvolvePE(pg.MixPE(whalesong, bay), NAMED_SLICES['long_ir'])

mix = pg.SequencePE(
    (wet_mix, 0),
    (drums, b2s(12))
)

_play(mix, 44100)
