# Mix three segmented voices: left, center and right

import pygmu2 as pg
pg.set_sample_rate(44100)
from pygmu2.logger import get_logger
from pygmu2.asset_manager import AssetManager, GoogleDriveAssetLoader

logger = get_logger(__name__)
logger = logger if logger.handlers else None


def cache_voice_segments():
    folder_id = "1qX5s1KCxAodHIA2sxxiHgybAHY_52LQn"
    # oauth_client_secrets may be omitted if stored at the default config path.
    asset_loader = GoogleDriveAssetLoader(
        folder_id=folder_id,
    )
    asset_manager = AssetManager(asset_loader=asset_loader)

    # List all remote assets that match wildcard spec
    asset_spec = "GiantFish/SegmentedVoice/*_??.wav"
    remote_assets = asset_manager.list_remote_assets(asset_spec)
    print(f"Found {len(remote_assets)} remote assets")
    for asset in remote_assets:
        print(f"  - remote: {asset}")
        path = asset_manager.load_asset(str(asset))
        print(f"  - loaded: {path}")

def ingest_voice_segment(filename):
    # read wavfile and compress.
    wav_stream = pg.WavReaderPE(filename)
    compressed_stream = pg.CompressorPE(wav_stream, threshold=-20, ratio=4)
    return compressed_stream

def mix_trio(f1, f2, f3):
    # mix three sound files, panning left, center, right
    # return a duple of (mix, max_dur)
    c1 = ingest_voice_segment(f1)
    c2 = ingest_voice_segment(f2)
    c3 = ingest_voice_segment(f3)

    p1 = pg.SpatialPE(c1, method=pg.SpatialConstantPower(azimuth=-90))
    p2 = pg.SpatialPE(c2, method=pg.SpatialConstantPower(azimuth=0))
    p3 = pg.SpatialPE(c3, method=pg.SpatialConstantPower(azimuth=90))

    max_dur = max(p1.extent().duration,
                  p2.extent().duration,
                  p3.extent().duration)
    return (max_dur, pg.MixPE(p1, p2, p3))

def peace():
    """
    Concatenate 16 trio segments by delaying each segment to start after the 
    previous one.
    """
    prefix = pg.AssetManager().cache_path() / "GiantFish" / "SegmentedVoice"
    delay = 0
    segments = []
    for i in range(1, 17):
        duration, pe = mix_trio(
            str(prefix) + f"/N_{i:02d}.wav", 
            str(prefix) + f"/R_{i:02d}.wav", 
            str(prefix) + f"/N2_{i:02d}.wav")
        segments.append(pg.DelayPE(pe, delay))
        delay += duration
    return pg.MixPE(*segments)

if __name__ == "__main__":

    # can we load relative names?
    # test = "GiantFish/SegmentedVoice/R_15.wav"
    # asset_manager = pg.AssetManager() # asset must be local...
    # xyz = asset_manager.load_asset(test)
    # print(f"xyz = {xyz}")

    SAMPLE_RATE = 44100
    cache_voice_segments()  # make sure all voice segments are cached locally
    mix = peace()

    # renderer = pg.AudioRenderer(sample_rate=SAMPLE_RATE)
    # renderer = pg.NullRenderer()
    # renderer.set_source(mix)
    # with renderer:
    #     renderer.start()
    #     renderer.play_extent()

    print(f"rendered duration = {mix.extent().duration/SAMPLE_RATE} seconds")
    renderer = pg.NullRenderer()
    renderer.set_source(mix)
    renderer.start()
    renderer.render(mix.extent().start, mix.extent().duration)
    renderer.stop()