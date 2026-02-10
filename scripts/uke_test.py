import pygmu2 as pg
from pygmu2.asset_manager import AssetManager, GoogleDriveAssetLoader
import random

SAMPLE_RATE = 44100
pg.set_sample_rate(SAMPLE_RATE)

from pygmu2.logger import setup_logging, get_logger
setup_logging(level="INFO")
logger = get_logger(__name__)

# A clean, long reverb
IR_PATH = "data/assets/impulses/synthetic_ir_10.wav"
IR = pg.WavReaderPE(IR_PATH)

def s2s(seconds):
    return int(round(seconds * SAMPLE_RATE))

def make_uke_resource_name(pitch:int) -> str:
    return f'uke_{pitch:02d}'

def load_uke_notes() -> dict[str, pg.ProcessingElement]:
    """
    Load and cache all the single-pluck ukulele sound files from Andy Milburn's
    library at media/audio/ukes/A/uke_??.wav.  Create a stereo PE stream for
    each file via SpatialPE(WavReader(f)) and associate it with an asset name.
    """

    folder_id = '1d1h38mZyCZpCHewklJN_PW3uG01K29ON'   # Andy milburn media 
    # folder_id = '1qX5s1KCxAodHIA2sxxiHgybAHY_52LQn' # RDP GiantFish

    # oauth_client_secrets may be omitted if stored at the default config path.
    asset_loader = GoogleDriveAssetLoader(folder_id=folder_id)
    asset_manager = AssetManager(asset_loader=asset_loader)

    named_wav_files = {}

    def load_named_wav_file(name:str, wav_file_name:str):
        # Load the .wav file if not already cached locally
        path = asset_manager.load_asset(wav_file_name)

        # Create a WavReaderPE for the .wav file, coerce to stereo
        stream = pg.WavReaderPE(path=path)
        if stream.file_sample_rate != SAMPLE_RATE:
            logger.warn(f'Sample rate of {stream} does not match system sample rate of {SAMPLE_RATE}')
        else:
            logger.info(f'Reading {stream}')

        # Coerce to stereo
        stream = pg.SpatialPE(stream, method=pg.SpatialAdapter(channels=2))

        named_wav_files[name] = stream

    # load up all the uke files
    for i in range(21, 96):
        load_named_wav_file(f'uke_{i:02d}', f'media/audio/ukes/A/{i:02d}.wav')
    return named_wav_files

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

STACKS = [
    (53, 58, 66, 73),  # good
    (47, 54, 62, 67),  # okay
    (53, 58, 66, 74),  # okay
    (47, 52, 55, 63),  # okay
    # (54, 61, 64, 71),  # sweet sus 7
    (47, 53, 58, 63),  # good
    (53, 61, 66, 72),  # good
    (47, 55, 57, 62),  # sweet
    (49, 55, 63, 68),  # good
    (50, 57, 64, 70),  # okay
    (49, 55, 60, 66),  # okay
    (46, 53, 55, 63),  # tonal
    (52, 60, 63, 71),  # good
]


UKES = load_uke_notes()

def generate_stacked_chord(pitch_stack:list[int]):
    start_times = make_randomized_start_times(len(pitch_stack), max_start_time=2.0)
    notes = []
    for pitch, start_time in zip(pitch_stack, start_times):
        notes.append((UKES[make_uke_resource_name(pitch)], s2s(start_time)))
    stacked_notes = pg.SequencePE(*notes)
    return stacked_notes

def generate_stacked_chords(stacks):
    chords = []
    start = 0
    for stack in stacks:
        chords.append((generate_stacked_chord(stack), s2s(start)))
        start += 12
    return pg.SequencePE(*chords)

wet_chords = pg.ReverbPE(generate_stacked_chords(STACKS), ir=IR, mix=0.6)

pg.play_offline(wet_chords)

