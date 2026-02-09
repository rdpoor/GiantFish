#!/usr/bin/env python3
import pygmu2 as pg
from pygmu2.karplus_strong_pe import rho_for_decay_db

SAMPLE_RATE = 44100
pg.set_sample_rate(SAMPLE_RATE)


def _play(source, sample_rate):
    renderer = pg.AudioRenderer(sample_rate=sample_rate)
    renderer.set_source(source)
    with renderer:
        renderer.start()
        renderer.play_extent()

def _play_offline(source, sample_rate):
    renderer = pg.NullRenderer(sample_rate=sample_rate)
    renderer.set_source(source)
    extent = source.extent()
    if extent.start is None or extent.end is None:
        raise RuntimeError("Source must have finite extent for offline render.")
    with renderer:
        renderer.start()
        renderer.render(extent.start, extent.end - extent.start)


def main() -> None:
    # Karplus-Strong pluck
    freq = 220.0
    rho = rho_for_decay_db(
        seconds=2.0,
        frequency=freq,
        sample_rate=SAMPLE_RATE,
        db=-60.0,
    )
    pluck = pg.KarplusStrongPE(
        frequency=freq,
        rho=rho,
        amplitude=0.8,
    )
    pluck = pg.CropPE(pluck, 0, 2.0 * SAMPLE_RATE)
    pluck = pg.SpatialPE(pluck, method=pg.SpatialAdapter(channels=2))
    ir_path = "data/assets/impulses/synthetic_ir_10.wav"
    ir = pg.WavReaderPE(ir_path)
    reverb = pg.ReverbPE(pluck, ir, mix=0.5)

    # Play a short burst
    duration = int(12.0 * SAMPLE_RATE)
    pg.play_offline(pg.CropPE(reverb, 0, duration), SAMPLE_RATE)


if __name__ == "__main__":
    main()
