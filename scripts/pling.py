import pygmu2 as pg
from pygmu2.karplus_strong_pe import rho_for_decay_db
import random

SAMPLE_RATE = 44100
pg.set_sample_rate(SAMPLE_RATE)

from pygmu2.logger import setup_logging, get_logger
setup_logging(level="INFO")
logger = get_logger(__name__)

def s2s(seconds):
    return int(round(seconds * SAMPLE_RATE))

"""
Generate stacked chords of four notes.  Rules:

Root is [45...54]
Top note is between 15 and 21 steps above root
"""

# A clean, long reverb
IR_PATH = "data/assets/impulses/synthetic_ir_10.wav"
IR = pg.WavReaderPE(IR_PATH)

def make_pitch_stack():
    n0 = random.randint(45, 54)
    n1 = n0 + random.randint(5, 8)
    n3 = n0 + random.randint(15, 21)
    n2 = n3 - random.randint(5, 8)
    return n0, n1, n2, n3

def make_good_pitches():
    while True:
        n0, n1, n2, n3 = make_pitch_stack()
        print(f"[{n0}, {n1}, {n2}, {n3}] ", end='')
        if (n0 + 12 == n2) or (n1 + 12 == n3) or (n1 + 24 == n3):
            print("internal octaves")
        elif (n1 + 1 >= n2 ):
            print("intenal semitone")
        else:
            print() 
            return n0, n1, n2, n3

def make_kp(pitch, seconds):
    freq = pg.pitch_to_freq(pitch)
    rho = rho_for_decay_db(
        seconds = seconds,
        frequency = freq,
        sample_rate = SAMPLE_RATE,
        db = -60)
    return pg.KarplusStrongPE(
        frequency = freq,
        rho = rho,
        amplitude = 1.0)


def make_instrument_stack(stack):
    plucks = pg.SequencePE([
        (make_kp(stack[0], 2.0), s2s(0)),
        (make_kp(stack[1], 2.0), s2s(0.6)),
        (make_kp(stack[2], 2.0), s2s(0.9)),
        (make_kp(stack[3], 2.0), s2s(1.0))]
    )
    # coerce to stereo
    plucks = pg.SpatialPE(plucks, method=pg.SpatialAdapter(channels=2))
    # wet_plucks = pg.ReverbPE(plucks, IR, mix=0.6)
    #return wet_plucks
    return plucks


if __name__ == "__main__":

    # while True:
    #     # choice = input("Hit return to hear a pling): ").strip()
    #     wet_plucks = make_instrument_stack(make_good_pitches())
    #     pg.play_offline(pg.SetExtentPE(wet_plucks, 0, s2s(9)), SAMPLE_RATE)

    pitches = [52, 59, 68, 73]

    dry_chord = make_instrument_stack(pitches)
    wet_chord = pg.ReverbPE(make_instrument_stack(pitches), IR, mix=0.6)
    seq = pg.SequencePE([
        (dry_chord, s2s(0)),
        (wet_chord, s2s(3)),
        ])
    pg.play_offline(
        pg.SetExtentPE(seq, s2s(0), s2s(18)),
        path='blings.wav', 
        sample_rate=SAMPLE_RATE)
