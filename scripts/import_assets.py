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

def _time_slice48(wav_reader, start_seconds:float, end_seconds:float):
    """
    Extract a slice from a wav_reader PE.  Hack b/c some files are recorded
    at 48000.
    """
    start_samples = start_seconds * 48000
    end_samples = end_seconds * 48000
    duration_samples = end_samples - start_samples
    return pg.SlicePE(wav_reader, start_samples, duration_samples)

def highpass_2nd_order(stream, frequency):
    # highpass filters
    filtered_stream = pg.BiquadPE(
        stream, 
        frequency=frequency, 
        q=0.707, 
        mode=pg.BiquadMode.HIGHPASS)
    return filtered_stream

def highpass_4th_order(stream, frequency):
    # Chain two 2nd order highpass filters together for sharper rolloff
    filtered_stream = pg.BiquadPE(
        stream, 
        frequency=frequency, 
        q=0.707, 
        mode=pg.BiquadMode.HIGHPASS)
    filtered_stream = pg.BiquadPE(
        filtered_stream, 
        frequency=frequency, 
        q=0.707, 
        mode=pg.BiquadMode.HIGHPASS)
    return filtered_stream

def create_named_slices():
    """
    Load and cache sound files, create a dict that associates a names with
    slices of sound files.  

    Note to future self: Audacity File => Export Other => Export Labels produces
    a tab separated file of start, end, name.  Consider parsing these directly:
    0.588796    3.221062    my half-brother
    3.278787    6.742294    his house is
    7.157915    12.918883   most days
    ...
    """
    named_slices = {}

    # impulse responses
    wav_reader = _import_wav_reader('GiantFish/wav_sources/long_ir44.wav')
    named_slices['long_ir'] = wav_reader

    # voices
    wav_reader = _import_wav_reader('GiantFish/wav_sources/shortest_rdp.wav')
    named_slices['r1 my half-brother'] = _time_slice48(wav_reader, 0.588796, 3.221062)
    named_slices['r1 his house is'] = _time_slice48(wav_reader, 3.278787, 6.742294)
    named_slices['r1 most days'] = _time_slice48(wav_reader, 7.157915, 12.918883)
    named_slices['r1 tethered only by'] = _time_slice48(wav_reader, 12.965063, 17.952513)
    named_slices['r1 at night, far off'] = _time_slice48(wav_reader, 18.552855, 25.826220)
    named_slices['r1 once a fish swam'] = _time_slice48(wav_reader, 26.484287, 31.864268)
    named_slices['r1 once his breathing'] = _time_slice48(wav_reader, 31.806543, 35.062240)
    named_slices['r1 he put something'] = _time_slice48(wav_reader, 35.593311, 38.087036)
    named_slices['r1 here, hold this'] = _time_slice48(wav_reader, 38.087036, 40.938657)
    named_slices['r1 a while or maybe'] = _time_slice48(wav_reader, 41.700629, 46.018468)
    named_slices['r1 we were standing'] = _time_slice48(wav_reader, 46.711170, 51.756345)
    named_slices['r1 this is the skull'] = _time_slice48(wav_reader, 51.894886, 54.296251)
    named_slices['r1 if you put it up'] = _time_slice48(wav_reader, 54.515606, 57.263322)
    named_slices['r1 you can hear'] = _time_slice48(wav_reader, 57.309502, 61.419531)
    named_slices['r1 to be born'] = _time_slice48(wav_reader, 61.419531, 64.305787)

    wav_reader = _import_wav_reader('GiantFish/wav_sources/shortest-cnrp_a.wav')
    named_slices['n1 my half brother'] = _time_slice48(wav_reader, 3.641721, 6.921682)
    named_slices['n1 his house is'] = _time_slice48(wav_reader, 6.921682, 11.118102)
    named_slices['n1 most days'] = _time_slice48(wav_reader, 11.118102, 17.931256)
    named_slices['n1 tethered only by'] = _time_slice48(wav_reader, 17.931256, 22.923549)
    named_slices['n1 at night, far off'] = pg.SequencePE(
        (_time_slice48(wav_reader, 22.911789, 26.599905), None),
        (_time_slice48(wav_reader, 37.689513, 40.821886), None))  # 'each one lit'
    named_slices['n1 once a fish swam'] = _time_slice48(wav_reader, 40.821886, 47.364502)
    named_slices['n1 once his breathing'] = _time_slice48(wav_reader, 47.364502, 51.191554)
    named_slices['n1 he put something'] = _time_slice48(wav_reader, 51.191554, 55.372261)
    named_slices['n1 here, hold this'] = _time_slice48(wav_reader, 55.372261, 58.694091)
    named_slices['n1 a while or maybe'] = _time_slice48(wav_reader, 58.694091, 62.761123)
    named_slices['n1 we were standing'] = _time_slice48(wav_reader, 66.019801, 76.919952)
    named_slices['n1 this is the skull'] = _time_slice48(wav_reader, 76.919952, 79.951280)
    named_slices['n1 if you put it up'] = _time_slice48(wav_reader, 79.951280, 82.780520)
    named_slices['n1 you can hear'] = _time_slice48(wav_reader, 82.780520, 88.476891)
    named_slices['n1 to be born'] = _time_slice48(wav_reader, 88.476891, 91.533480)

    wav_reader = _import_wav_reader('GiantFish/wav_sources/shortest-cnrp_b.wav')
    named_slices['n2 my half brother'] = _time_slice48(wav_reader, 3.895042, 6.797230)
    named_slices['n2 his house is'] = _time_slice48(wav_reader, 6.797230, 9.966724)
    named_slices['n2 most days'] = _time_slice48(wav_reader, 9.966724, 18.240505)
    named_slices['n2 tethered only by'] = _time_slice48(wav_reader, 18.240505, 23.039299)
    named_slices['n2 at night, far off'] = _time_slice48(wav_reader, 23.039299, 29.556492)
    named_slices['n2 once a fish swam'] = _time_slice48(wav_reader, 29.951088, 34.711695)
    named_slices['n2 once his breathing'] = _time_slice48(wav_reader, 34.711695, 38.441261)
    named_slices['n2 he put something'] = _time_slice48(wav_reader, 38.441261, 43.010934)
    named_slices['n2 here, hold this'] = _time_slice48(wav_reader, 43.010934, 46.218615)
    named_slices['n2 a while or maybe'] = _time_slice48(wav_reader, 46.218615, 49.706332)
    named_slices['n2 we were standing'] = _time_slice48(wav_reader, 51.602937, 59.609412)
    named_slices['n2 this is the skull'] = _time_slice48(wav_reader, 59.609412, 61.798781)
    named_slices['n2 if you put it up'] = _time_slice48(wav_reader, 61.798781, 64.675511)
    named_slices['n2 you can hear'] = _time_slice48(wav_reader, 64.675511, 69.881629)
    named_slices['n2 to be born'] = _time_slice48(wav_reader, 69.881629, 72.794438)

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
    wav_reader = highpass_4th_order(wav_reader, 100.0)
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
    stream = highpass_4th_order(wav_stream, 1000.0)
    named_slices['fishtank_1_00'] = stream

    # NOTE: Timewarp must precede BiquadPE since biquad required sequential 
    # calls to render().
    stream = pg.TimeWarpPE(wav_stream, rate=0.25)
    stream = highpass_4th_order(stream, 250.0)
    named_slices['fishtank_0_25'] = stream

    stream = pg.TimeWarpPE(wav_stream, rate=0.125)
    stream = highpass_4th_order(stream, 125.0)
    named_slices['fishtank_0_125'] = stream

    return named_slices

if __name__ == "__main__":
    import sys

    def audition_slices(pe_dict):
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
    audition_slices(named_slices)

# chord ideas
# 52 59 63 70
# 50 57 64 68
# 53 59 64 69
# 48 55 62 66

