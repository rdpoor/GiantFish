#!/usr/bin/env python3
import argparse
import math
import os
import wave

import numpy as np

SAMPLE_RATE = 44100


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a stereo exponentially decaying noise impulse response."
    )
    parser.add_argument(
        "duration",
        type=float,
        help="Length in seconds.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="data/assets/synthetic_ir.wav",
        help="Output wav path (default: data/assets/synthetic_ir.wav).",
    )
    parser.add_argument(
        "--decay",
        type=float,
        default=None,
        help="Decay time constant in seconds (default: set to reach -16 dB at end).",
    )
    return parser.parse_args()


def _exp_decay_envelope(n_samples: int, tau_seconds: float) -> np.ndarray:
    t = np.arange(n_samples, dtype=np.float64) / SAMPLE_RATE
    return np.exp(-t / max(1e-9, tau_seconds))


def _to_int16(stereo: np.ndarray) -> bytes:
    stereo = np.clip(stereo, -1.0, 1.0)
    pcm = (stereo * 32767.0).astype(np.int16)
    return pcm.tobytes()


def main() -> None:
    args = _parse_args()
    duration = max(0.0, args.duration)
    n_samples = int(math.ceil(duration * SAMPLE_RATE))
    if n_samples <= 0:
        raise ValueError("Duration must be > 0.")

    if args.decay is None:
        # Choose tau so that the envelope reaches -60 dB at t=duration.
        target_db = -60.0
        target_linear = 10 ** (target_db / 20.0)
        tau = duration / max(1e-9, -math.log(target_linear))
    else:
        tau = args.decay

    env = _exp_decay_envelope(n_samples, tau)

    left = np.random.normal(0.0, 1.0, size=n_samples)
    right = np.random.normal(0.0, 1.0, size=n_samples)

    stereo = np.stack([left * env, right * env], axis=1)

    out_path = args.output
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)  # int16
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(_to_int16(stereo))

    print(f"Wrote {out_path} ({duration:.3f}s, {SAMPLE_RATE} Hz)")


if __name__ == "__main__":
    main()
