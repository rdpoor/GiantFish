import pygmu2 as pg
from pygmu2.asset_manager import AssetManager, GoogleDriveAssetLoader

SAMPLE_RATE = 44100
pg.set_sample_rate(SAMPLE_RATE)

from pygmu2.logger import setup_logging, get_logger
setup_logging(level="INFO")
logger = get_logger(__name__)

"""
Some of the .wav source files need filtering or compression, etc to be useful.
However, filtering requires congituous render access which means you cannot 
call TimeWarp or CompressPE with lookahead with an "upstream" filter.  The most
general thing to do is to pre-process the .wav file and write the result to a 
new file.

In our case, we act on files in the AssetManager cache.
"""

ASSET_NAME = 'GiantFish/wav_sources/Hummy Bubbles.wav'
PROCESSED_NAME = 'GiantFish/wav_sources/Bubbles.wav'

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

def write_stream_to_wav_file(stream, path):
    extent = stream.extent()
    writer = pg.WavWriterPE(stream, path, sample_rate=SAMPLE_RATE)
    renderer = pg.NullRenderer(sample_rate=SAMPLE_RATE)
    renderer.set_source(writer)

    with renderer:
        renderer.start()
        renderer.render(extent.start, extent.end - extent.start)
    logger.info(f"Wrote {path}")

def highpass_file(unprocessed_name, processed_name, freq):
    gdrive_folder_id = '1qX5s1KCxAodHIA2sxxiHgybAHY_52LQn'
    # oauth_client_secrets may be omitted if stored at the default config path.
    asset_loader = GoogleDriveAssetLoader(folder_id=gdrive_folder_id)
    asset_manager = AssetManager(asset_loader=asset_loader)
    cache_dir = asset_manager.cache_path()

    # load .wav file into cache from google drive if needed, return path...
    unprocessed_path = asset_manager.load_asset(unprocessed_name)

    # convert to a pygmu2 stream
    stream = pg.WavReaderPE(path=unprocessed_path)

    logger.info(f'Reading {stream}')
    if stream.file_sample_rate != SAMPLE_RATE:
        logger.warn(f'sample rate mismatch: file={stream.file_sample_rate}, system={SAMPLE_RATE}, ignoring...')

    # process file and write to cache directory...
    processed_stream = highpass_4th_order(stream, freq)

    write_stream_to_wav_file(processed_stream, cache_dir / processed_name)

def pitch_file(unprocessed_name, processed_name, rate):
    gdrive_folder_id = '1qX5s1KCxAodHIA2sxxiHgybAHY_52LQn'
    # oauth_client_secrets may be omitted if stored at the default config path.
    asset_loader = GoogleDriveAssetLoader(folder_id=gdrive_folder_id)
    asset_manager = AssetManager(asset_loader=asset_loader)
    cache_dir = asset_manager.cache_path()

    # load .wav file into cache from google drive if needed, return path...
    unprocessed_path = asset_manager.load_asset(unprocessed_name)

    # convert to a pygmu2 stream
    stream = pg.WavReaderPE(path=unprocessed_path)

    logger.info(f'Reading {stream}')
    if stream.file_sample_rate != SAMPLE_RATE:
        logger.warn(f'sample rate mismatch: file={stream.file_sample_rate}, system={SAMPLE_RATE}, ignoring...')

    # process file and write to cache directory...
    processed_stream = pg.TimeWarpPE(stream, rate)

    write_stream_to_wav_file(processed_stream, cache_dir / processed_name)


# highpass_file(
#     'GiantFish/wav_sources/Hummy Bubbles.wav',
#     'GiantFish/wav_sources/Bubbles.wav',
#     1000)
# highpass_file(
#     'GiantFish/wav_sources/Valparaiso St 5.wav',
#     'GiantFish/wav_sources/Foghorns.wav',
#     100)
# pitch_file(
#     'GiantFish/wav_sources/Bubbles.wav',
#     'GiantFish/wav_sources/Bubbles_0_125.wav',
#     0.125)
# pitch_file(
#     'GiantFish/wav_sources/jasper_1.wav',
#     'GiantFish/wav_sources/jasper1_0_3.wav',
#     0.3)
# pitch_file(
#     'GiantFish/wav_sources/jasper_2.wav',
#     'GiantFish/wav_sources/jasper2_0_3.wav',
#     0.3)
# pitch_file(
#     'GiantFish/wav_sources/jasper_3.wav',
#     'GiantFish/wav_sources/jasper3_0_3.wav',
#     0.3)
# pitch_file(
#     'GiantFish/wav_sources/jasper_4.wav',
#     'GiantFish/wav_sources/jasper4_0_3.wav',
#     0.3)
# pitch_file(
#     'GiantFish/wav_sources/jasper_5.wav',
#     'GiantFish/wav_sources/jasper5_0_3.wav',
#     0.3)
# pitch_file(
#     'GiantFish/wav_sources/jasper_6.wav',
#     'GiantFish/wav_sources/jasper6_0_3.wav',
#     0.3)
