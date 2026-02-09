from giantfish.config import ASSETS_DIR
import json
import pygmu2 as pg
from pygmu2.asset_manager import AssetManager, GoogleDriveAssetLoader
from typing import Optional, Union

pg.set_sample_rate(44100)


from pygmu2.logger import setup_logging, get_logger
setup_logging(level="INFO")
logger = get_logger(__name__)

SAMPLE_RATE = 44100

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

def load_named_irs() -> dict[str, pg.ProcessingElement]:

    named_irs = {}

    impulse_dir = ASSETS_DIR / "impulses"
    def load_named_ir(name:str, filename:str):
        named_irs[name] = pg.WavReaderPE(impulse_dir / filename)


    load_named_ir("fat_plate", "480_Fat Plate.wav")
    load_named_ir("large_church", "480_Large Church.wav")
    load_named_ir("large_hall", "480_Large Hall.wav")
    load_named_ir("large_plate", "480_Large Plate.wav")
    load_named_ir("small_hall", "480_Small Hall.wav")
    load_named_ir("small_plate", "480_Small Plate.wav")
    load_named_ir("bottle_hall", "Bottle Hall.wav")
    load_named_ir("cement_blocks", "Cement Blocks 2.wav")
    load_named_ir("long_echo_hall", "Conic Long Echo Hall.wav")
    load_named_ir("north_stairwell", "CPMCNorthStairwell.wav")
    load_named_ir("five_columns", "Five Columns.wav")
    load_named_ir("hot_hall", "IR_HotHall.wav")
    load_named_ir("small_church", "IR_SmallChurch.wav")
    load_named_ir("large_bottle_hall", "Large Bottle Hall.wav")
    load_named_ir("large_wide_echo_hall", "Large Wide Echo Hall.wav")
    load_named_ir("masonic_lodge", "Masonic Lodge.wav")
    load_named_ir("portage_creek_tunnel", "PortageCreekTunnel.wav")
    load_named_ir("small_prehistoric_cave", "Small Prehistoric Cave.wav")
    load_named_ir("space_art_gallery", "Space4ArtGallery.wav")
    load_named_ir("st_nicolaes_church", "St Nicolaes Church.wav")
    load_named_ir("vox_plate", "VoxPlateNo2.wav")

    return named_irs

def load_named_wav_files() -> dict[str, pg.ProcessingElement]:

    folder_id = '1qX5s1KCxAodHIA2sxxiHgybAHY_52LQn'
    # oauth_client_secrets may be omitted if stored at the default config path.
    asset_loader = GoogleDriveAssetLoader(folder_id=folder_id)
    asset_manager = AssetManager(asset_loader=asset_loader)

    named_wav_files = {}

    def load_named_wav_file(name:str, wav_file_name:str):
        # Assure the .wav file is available locally
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

    load_named_wav_file('rdp_v1', 'GiantFish/wav_sources/shortest_rdp.wav')
    load_named_wav_file('cnrp_v1', 'GiantFish/wav_sources/shortest-cnrp_a.wav')
    load_named_wav_file('cnrp_v2', 'GiantFish/wav_sources/shortest-cnrp_b.wav')
    load_named_wav_file('taiko', 'GiantFish/wav_sources/1601 CA-1 2.wav')
    load_named_wav_file('jasper1', 'GiantFish/wav_sources/jasper_1.wav')
    load_named_wav_file('jasper2', 'GiantFish/wav_sources/jasper_2.wav')
    load_named_wav_file('jasper3', 'GiantFish/wav_sources/jasper_3.wav')
    load_named_wav_file('jasper4', 'GiantFish/wav_sources/jasper_4.wav')
    load_named_wav_file('jasper5', 'GiantFish/wav_sources/jasper_5.wav')
    load_named_wav_file('jasper6', 'GiantFish/wav_sources/jasper_6.wav')
    load_named_wav_file('jasper1_0_3', 'GiantFish/wav_sources/jasper1_0_3.wav')
    load_named_wav_file('jasper2_0_3', 'GiantFish/wav_sources/jasper2_0_3.wav')
    load_named_wav_file('jasper3_0_3', 'GiantFish/wav_sources/jasper3_0_3.wav')
    load_named_wav_file('jasper4_0_3', 'GiantFish/wav_sources/jasper4_0_3.wav')
    load_named_wav_file('jasper5_0_3', 'GiantFish/wav_sources/jasper5_0_3.wav')
    load_named_wav_file('jasper6_0_3', 'GiantFish/wav_sources/jasper6_0_3.wav')
    load_named_wav_file('frogs1', 'GiantFish/wav_sources/8 46th Ave 3.wav')
    load_named_wav_file('frogs2', 'GiantFish/wav_sources/Tompkins Ln 2.wav')
    load_named_wav_file('foghorns', 'GiantFish/wav_sources/Foghorns.wav')
    load_named_wav_file('snores', 'GiantFish/wav_sources/Lighthouse Ave.wav')
    load_named_wav_file('bubbles', 'GiantFish/wav_sources/Bubbles.wav')
    load_named_wav_file('bubbles_0_125', 'GiantFish/wav_sources/Bubbles_0_125.wav')
    load_named_wav_file('crowd2', 'GiantFish/wav_sources/080122-007.wav')

    return named_wav_files

def post_process_wav_files(named_wav_files:dict[str, pg.ProcessingElement]) -> dict[str, pg.ProcessingElement]:
    """
    Add gain, compression, etc to wave files 
    """
    # filter low-frequency rumble from foghorns
    # foghorns = named_wav_files['foghorns']
    # named_wav_files['foghorns'] = highpass_4th_order(foghorns, 100.0)

    return named_wav_files


def make_named_slices(named_wav_files:dict[str, pg.ProcessingElement]) -> dict[str, pg.ProcessingElement]:

    slices = {}

    def s2s(seconds, sample_rate):
        return int(round(seconds * sample_rate))

    def _make_slice(
        wav_name:str, 
        start:Optional[float] = None,
        end:Optional[float] = None,
        sample_rate:Optional[int] = None
    ):
        wav_stream = named_wav_files[wav_name]
        if start is None and end is None:
            return wav_stream
        else:
            if sample_rate is None:
                sample_rate = wav_stream.sample_rate
            extent = wav_stream.extent()
            start_sample = s2s(start, sample_rate) if start is not None else extent.start
            end_sample = s2s(end, sample_rate) if end is not None else extent.end_sample
            dur_samples = end_sample - start_sample
            return pg.SlicePE(wav_stream, start_sample, dur_samples)

    def make_slice(
        slice_name:str, 
        wav_name:str, 
        start:Optional[float] = None,
        end:Optional[float] = None,
        sample_rate:Optional[int] = None):
        """
        Extract a slice from the wav_name .wav file and add it to the dict of
        slice names
        """
        slices[slice_name] = _make_slice(wav_name, start, end, sample_rate)

    make_slice('r1 my half brother', 'rdp_v1',  0.588796, 3.221062, 48000)
    make_slice('r1 his house is', 'rdp_v1', 3.278787, 6.742294, 48000)
    make_slice('r1 most days', 'rdp_v1', 7.157915, 12.918883, 48000)
    make_slice('r1 tethered only by', 'rdp_v1', 12.965063, 17.952513, 48000)
    make_slice('r1 at night, far off', 'rdp_v1', 18.552855, 25.826220, 48000)
    make_slice('r1 once a fish swam', 'rdp_v1', 26.484287, 31.864268, 48000)
    make_slice('r1 once his breathing', 'rdp_v1', 31.806543, 35.062240, 48000)
    make_slice('r1 he put something', 'rdp_v1', 35.593311, 38.087036, 48000)
    make_slice('r1 here, hold this', 'rdp_v1', 38.087036, 40.938657, 48000)
    make_slice('r1 a while or maybe', 'rdp_v1', 41.700629, 46.018468, 48000)
    make_slice('r1 we were standing', 'rdp_v1', 46.711170, 51.756345, 48000)
    make_slice('r1 this is the skull', 'rdp_v1', 51.894886, 54.296251, 48000)
    make_slice('r1 if you put it up', 'rdp_v1', 54.515606, 57.263322, 48000)
    make_slice('r1 you can hear', 'rdp_v1', 57.309502, 61.419531, 48000)
    make_slice('r1 to be born', 'rdp_v1', 61.419531, 64.305787, 48000)

    make_slice('n1 my half brother', 'cnrp_v1', 3.641721, 6.921682, 48000)
    make_slice('n1 his house is', 'cnrp_v1', 6.921682, 11.118102, 48000)
    make_slice('n1 most days', 'cnrp_v1', 11.118102, 17.931256, 48000)
    make_slice('n1 tethered only by', 'cnrp_v1', 17.931256, 22.923549, 48000)
    slices['n1 at night, far off'] = \
        pg.SequencePE(
            (_make_slice('cnrp_v1', 22.911789, 26.599905, 48000), None),
            (_make_slice('cnrp_v1', 37.689513, 40.821886, 48000), None))
    make_slice('n1 once a fish swam', 'cnrp_v1', 40.821886, 47.364502, 48000)
    make_slice('n1 once his breathing', 'cnrp_v1', 47.364502, 51.191554, 48000)
    make_slice('n1 he put something', 'cnrp_v1', 51.191554, 55.372261, 48000)
    make_slice('n1 here, hold this', 'cnrp_v1', 55.372261, 58.694091, 48000)
    make_slice('n1 a while or maybe', 'cnrp_v1', 58.694091, 62.761123, 48000)
    make_slice('n1 we were standing', 'cnrp_v1', 66.019801, 76.919952, 48000)
    make_slice('n1 this is the skull', 'cnrp_v1', 76.919952, 79.951280, 48000)
    make_slice('n1 if you put it up', 'cnrp_v1', 79.951280, 82.780520, 48000)
    make_slice('n1 you can hear', 'cnrp_v1', 82.780520, 88.476891, 48000)
    make_slice('n1 to be born', 'cnrp_v1', 88.476891, 91.533480, 48000)

    make_slice('n2 my half brother', 'cnrp_v2', 3.895042, 6.797230, 48000)
    make_slice('n2 his house is', 'cnrp_v2', 6.797230, 9.966724, 48000)
    make_slice('n2 most days', 'cnrp_v2', 9.966724, 18.240505, 48000)
    make_slice('n2 tethered only by', 'cnrp_v2', 18.240505, 23.039299, 48000)
    make_slice('n2 at night, far off', 'cnrp_v2', 23.039299, 29.556492, 48000)
    make_slice('n2 once a fish swam', 'cnrp_v2', 29.951088, 34.711695, 48000)
    make_slice('n2 once his breathing', 'cnrp_v2', 34.711695, 38.441261, 48000)
    make_slice('n2 he put something', 'cnrp_v2', 38.441261, 43.010934, 48000)
    make_slice('n2 here, hold this', 'cnrp_v2', 43.010934, 46.218615, 48000)
    make_slice('n2 a while or maybe', 'cnrp_v2', 46.218615, 49.706332, 48000)
    make_slice('n2 we were standing', 'cnrp_v2', 51.602937, 59.609412, 48000)
    make_slice('n2 this is the skull', 'cnrp_v2', 59.609412, 61.798781, 48000)
    make_slice('n2 if you put it up', 'cnrp_v2', 61.798781, 64.675511, 48000)
    make_slice('n2 you can hear', 'cnrp_v2', 64.675511, 69.881629, 48000)
    make_slice('n2 to be born', 'cnrp_v2', 69.881629, 72.794438, 48000)

    make_slice('taiko1', 'taiko', 2.42019, 7.51533)
    make_slice('taiko1', 'taiko', 2.42019, 7.51533)
    make_slice('taiko2', 'taiko', 7.45164, 12.8652)
    make_slice('taiko3', 'taiko', 12.8015, 18.1514)
    make_slice('taiko4', 'taiko', 18.2788, 23.1192)
    make_slice('taiko5', 'taiko', 23.1829, 28.0869)
    make_slice('taiko6', 'taiko', 30.8893, 35.9207)
    make_slice('taiko7', 'taiko', 35.7933, 41.0795)
    make_slice('taiko8', 'taiko', 41.0795, 45.6652)
    make_slice('taiko9', 'taiko', 45.6652, 51.2061)

    make_slice('jasper1', 'jasper1', None, None)
    make_slice('jasper2', 'jasper2', None, None)
    make_slice('jasper3', 'jasper3', None, None)
    make_slice('jasper4', 'jasper4', None, None)
    make_slice('jasper5', 'jasper5', None, None)
    make_slice('jasper6', 'jasper6', None, None)
    make_slice('jasper1_0_3', 'jasper1_0_3', None, None)
    make_slice('jasper2_0_3', 'jasper2_0_3', None, None)
    make_slice('jasper3_0_3', 'jasper3_0_3', None, None)
    make_slice('jasper4_0_3', 'jasper4_0_3', None, None)
    make_slice('jasper5_0_3', 'jasper5_0_3', None, None)
    make_slice('jasper6_0_3', 'jasper6_0_3', None, None)

    make_slice('frogs1', 'frogs1', None, None)
    make_slice('frogs2', 'frogs2', None, None)

    make_slice('foghorn1', 'foghorns', 11.874, 33.557)
    make_slice('foghorn2', 'foghorns', 72.0186, 90.8621)
    make_slice('foghorn3', 'foghorns', 111.513, 132.938)
    make_slice('foghorn4', 'foghorns', 132.421, 150.49)
    make_slice('foghorns', 'foghorns', 5.93702, 235.932)

    make_slice('snores', 'snores', 0.855376, 63.232)

    make_slice('bubbles', 'bubbles', None, None)
    make_slice('bubbles_0_125', 'bubbles_0_125', None, None)

    make_slice('crowd', 'crowd2', None, None)

    return slices

def post_process_slices(named_slices):
    return named_slices

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

def get_named_irs():
    return load_named_irs()

def get_wav_files():
    return post_process_wav_files(load_named_wav_files())

def get_named_slices():
    return post_process_slices(make_named_slices(get_wav_files()))

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    SAMPLE_RATE = 44100

    def _play(source, sample_rate):
        renderer = pg.AudioRenderer(sample_rate=sample_rate)
        renderer.set_source(source)
        with renderer:
            renderer.start()
            renderer.play_extent()

    def _audition_named_assets(asset_dict):
        """
        asset_dict: dict[str, ProcessingElement]
        Uses _play(pe) to audition the selected PE.
        """
        names = list(asset_dict.keys())

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
                    _play(asset_dict[name], SAMPLE_RATE)
                else:
                    print("Invalid number.")
                continue

            # name choice
            if choice in asset_dict:
                _play(asset_dict[choice], SAMPLE_RATE)
            else:
                print("Unknown name. Enter '?' for list.")

    named_slices = get_named_slices()
    _audition_named_assets(named_slices)

