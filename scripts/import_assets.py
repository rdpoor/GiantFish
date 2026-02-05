# Importing and labeling .wav assets

import json
import pygmu2 as pg
from pygmu2.asset_manager import AssetManager, GoogleDriveAssetLoader

from pygmu2.logger import setup_logging, get_logger
setup_logging(level="INFO")
logger = get_logger(__name__)

SAMPLE_RATE = 44100

def _play(source, sample_rate):
    renderer = pg.AudioRenderer(sample_rate=sample_rate)
    renderer.set_source(source)
    with renderer:
        renderer.start()
        renderer.play_extent()

def _import_wav_reader(asset_name):
    """
    Download a remote .wav file and return a WavReaderPE for it, coercing to
    stero if not already stereo
    """
    folder_id = '1qX5s1KCxAodHIA2sxxiHgybAHY_52LQn'
    # oauth_client_secrets may be omitted if stored at the default config path.
    asset_loader = GoogleDriveAssetLoader(folder_id=folder_id)
    asset_manager = AssetManager(asset_loader=asset_loader)

    named_slices = {}

    # Assure the .wav file is available locally
    path = asset_manager.load_asset(asset_name)

    # Create a WavReaderPE for the .wav file, coerge to stereo
    wav_reader = pg.WavReaderPE(path=path)
    if wav_reader.file_sample_rate != SAMPLE_RATE:
        logger.warn(f'Sample rate of {wav_reader} does not match system sample rate of {SAMPLE_RATE}')
    else:
        logger.info(f'Reading {wav_reader}')

    # Coerce to stereo
    return pg.SpatialPE(wav_reader, method=pg.SpatialAdapter(channels=2))

def _time_slice(wav_reader, start_seconds:float, end_seconds:float):
    """
    Extract a slice from a wav_reader PE.
    """
    start_samples = start_seconds * SAMPLE_RATE
    end_samples = end_seconds * SAMPLE_RATE
    duration_samples = end_samples - start_samples
    return pg.SlicePE(wav_reader, start_samples, duration_samples)

def create_named_slices():
    """
    Load and cache sound files, create a dict that associates a names with
    slices of sound files.
    """
    named_slices = {}

    # Taiko drums
    wav_reader = _import_wav_reader('GiantFish/wav_sources/1601 CA-1 2.wav')
    # Create named slices into the .wav file.  Start and end times were derived
    # from Audacity => Get Info => Clips => JSON
    named_slices['taiko1'] = _time_slice(wav_reader, 2.42019, 7.51533)
    named_slices['taiko1'] = _time_slice(wav_reader, 2.42019, 7.51533)
    named_slices['taiko2'] = _time_slice(wav_reader, 7.45164, 12.8652)
    named_slices['taiko3'] = _time_slice(wav_reader, 12.8015, 18.1514)
    named_slices['taiko4'] = _time_slice(wav_reader, 18.2788, 23.1192)
    named_slices['taiko5'] = _time_slice(wav_reader, 23.1829, 28.0869)
    named_slices['taiko6'] = _time_slice(wav_reader, 30.8893, 35.9207)
    named_slices['taiko7'] = _time_slice(wav_reader, 35.7933, 41.0795)
    named_slices['taiko8'] = _time_slice(wav_reader, 41.0795, 45.6652)
    named_slices['taiko9'] = _time_slice(wav_reader, 45.6652, 51.2061)

    # Jasper howling
    wav_reader = _import_wav_reader('GiantFish/wav_sources/jasper_1.wav')
    named_slices['jasper_1'] = wav_reader # entire file
    wav_reader = _import_wav_reader('GiantFish/wav_sources/jasper_2.wav')
    named_slices['jasper_2'] = wav_reader # entire file
    wav_reader = _import_wav_reader('GiantFish/wav_sources/jasper_3.wav')
    named_slices['jasper_3'] = wav_reader # entire file
    wav_reader = _import_wav_reader('GiantFish/wav_sources/jasper_4.wav')
    named_slices['jasper_4'] = wav_reader # entire file
    wav_reader = _import_wav_reader('GiantFish/wav_sources/jasper_5.wav')
    named_slices['jasper_5'] = wav_reader # entire file
    wav_reader = _import_wav_reader('GiantFish/wav_sources/jasper_6.wav')
    named_slices['jasper_6'] = wav_reader # entire file

    # frogs
    wav_reader = _import_wav_reader('GiantFish/wav_sources/8 46th Ave 3.wav')
    named_slices['frogs_1'] = _time_slice(wav_reader, 17.0645, 41.0869)
    wav_reader = _import_wav_reader('GiantFish/wav_sources/Tompkins Ln 2.wav')
    named_slices['frogs_2'] = _time_slice(wav_reader, 4.93659, 117.212)

    # foghorns
    wav_reader = _import_wav_reader('GiantFish/wav_sources/Valparaiso St 5.wav')
    named_slices['foghorn_1'] = _time_slice(wav_reader, 11.874, 33.557)
    named_slices['foghorn_2'] = _time_slice(wav_reader, 72.0186, 90.8621)
    named_slices['foghorn_3'] = _time_slice(wav_reader, 111.513, 132.938)
    named_slices['foghorn_4'] = _time_slice(wav_reader, 132.421, 150.49)
    named_slices['foghorns_full'] = _time_slice(wav_reader, 5.93702, 235.932)
    
    # snoring
    wav_reader = _import_wav_reader('GiantFish/wav_sources/Lighthouse Ave.wav')
    named_slices['snores'] = _time_slice(wav_reader, 0.855376, 63.232)
 
    # bubbles (with pre-processing to clean up hum)
    wav_stream = _import_wav_reader('GiantFish/wav_sources/Hummy Bubbles.wav')
    filtered_stream = pg.BiquadPE(
        wav_stream, 
        frequency=1000.0, 
        q=0.707, 
        mode=pg.BiquadMode.HIGHPASS)
    filtered_stream = pg.BiquadPE(
        filtered_stream, 
        frequency=1000.0, 
        q=0.707, 
        mode=pg.BiquadMode.HIGHPASS)
    named_slices['fishtank_1_00'] = filtered_stream

    # NOTE: Timewarp must precede BiquadPE since biquad required sequential 
    # calls to render().
    stream = pg.TimeWarpPE(wav_stream, rate=0.25)
    stream = pg.BiquadPE(
        stream, 
        frequency=250.0, 
        q=0.707, 
        mode=pg.BiquadMode.HIGHPASS)
    stream = pg.BiquadPE(
        stream, 
        frequency=250.0, 
        q=0.707, 
        mode=pg.BiquadMode.HIGHPASS)
    named_slices['fishtank_0_25'] = stream

    stream = pg.TimeWarpPE(wav_stream, rate=0.125)
    stream = pg.BiquadPE(
        stream, 
        frequency=125.0, 
        q=0.707, 
        mode=pg.BiquadMode.HIGHPASS)
    stream = pg.BiquadPE(
        stream, 
        frequency=125.0, 
        q=0.707, 
        mode=pg.BiquadMode.HIGHPASS)
    named_slices['fishtank_0_125'] = stream

    return named_slices

if __name__ == "__main__":
    import sys

    def choose_and_play(pe_dict):
        """
        pe_dict: dict[str, ProcessingElement]
        Uses _play(pe) to audition the selected PE.
        """
        names = list(pe_dict.keys())

        def print_menu():
            print("Available PEs:")
            for i, name in enumerate(names, start=1):
                print(f"  {i}: {name}")
            print("  ?: show list")
            print("  q: quit")

        print_menu()
        while True:
            choice = input("Select PE (name or number): ").strip()
            if choice.lower() == "q":
                break
            if choice == "?":
                print_menu()
                continue

            # numeric choice
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(names):
                    name = names[idx - 1]
                    _play(pe_dict[name], SAMPLE_RATE)
                else:
                    print("Invalid number.")
                continue

            # name choice
            if choice in pe_dict:
                _play(pe_dict[choice], SAMPLE_RATE)
            else:
                print("Unknown name. Enter '?' for list.")

    named_slices = create_named_slices()
    choose_and_play(named_slices)

# chord ideas
# 52 59 63 70
# 50 57 64 68
# 53 59 64 69
# 48 55 62 66

# def get_raw_wav_assets():
#     '''
#     Load and cache raw .wav files, returning a dict naming the broad categories
#     followed by a list of the .wav paths.
#     '''
#     folder_id = '1qX5s1KCxAodHIA2sxxiHgybAHY_52LQn'
#     # oauth_client_secrets may be omitted if stored at the default config path.
#     asset_loader = GoogleDriveAssetLoader(
#         folder_id=folder_id,
#     )
#     asset_manager = AssetManager(asset_loader=asset_loader)
#     # Path is not serializable, so we return str(asset_mgr.load_asset())

#     d = {}
#     # drum beats
#     d['drum_beats'] = [
#         str(asset_manager.load_asset('GiantFish/wav_sources/1601 CA-1.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/1601 CA-1 2.wav')),
#     ]

#     # ambient voices and outdoors
#     d['ambient_voices'] = [
#         str(asset_manager.load_asset('GiantFish/wav_sources/080122-001.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/080122-003.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/080122-007.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/080122-009.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/080122-010.wav')),
#     ]

#     # not a mockingbird
#     d['night_bird'] = [
#         str(asset_manager.load_asset('GiantFish/wav_sources/506 21st St 16.wav')),
#     ]

#     # crazy toads
#     d['toads_and_frogs'] = [
#         str(asset_manager.load_asset('GiantFish/wav_sources/8 46th Ave 3.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/Tompkins Ln 2.wav')),
#     ]

#     # jasper (1 through 6)
#     d['jasper'] = [
#         str(asset_manager.load_asset('GiantFish/wav_sources/jasper_1.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/jasper_2.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/jasper_3.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/jasper_4.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/jasper_5.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/jasper_6.wav')),
#     ]

#     # snoring
#     d['snoring'] = [
#         str(asset_manager.load_asset('GiantFish/wav_sources/Lighthouse Ave.wav')),
#     ]

#     # Laguna Seca (36 and 37)
#     d['laguna_seca'] = [
#         str(asset_manager.load_asset('GiantFish/wav_sources/New Recording 36.wav')),
#         str(asset_manager.load_asset('GiantFish/wav_sources/New Recording 37.wav')),
#     ]

#     # SF Bay Foghorns
#     d['sf_bay_foghorns'] = [
#         str(asset_manager.load_asset('GiantFish/wav_sources/Valparaiso St 5.wav')),
#     ]

#     return d

# d = get_raw_wav_assets()
# print(json.dumps(d, indent=2, sort_keys=True))



