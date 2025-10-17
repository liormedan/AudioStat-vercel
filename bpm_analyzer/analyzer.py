from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import contextlib
import math
import struct
import wave
import io


@dataclass
class AnalyzerConfig:
    min_bpm: float = 60.0
    max_bpm: float = 200.0
    target_sr: int = 22050
    method: str = "acf"
    estimate_grid: bool = False
    top_k: int = 3
    max_duration: Optional[float] = None


def analyze_file(path: Path, cfg: AnalyzerConfig) -> Dict[str, object]:
    p = Path(path)
    result: Dict[str, object] = {
        "file": str(p),
        "status": "ok",
        "bpm": None,
        "offset": None,
        "confidence": 0.0,
        "method": cfg.method,
    }

    try:
        if p.suffix.lower() == ".wav":
            sr, mono = _read_wav_mono(p, max_seconds=cfg.max_duration)
            bpm, conf = _estimate_bpm_acf(mono, sr, cfg)
            result["bpm"] = round(bpm, 2) if bpm is not None else None
            result["confidence"] = float(conf)
            return result
        # Placeholder for other formats
        result["status"] = "unsupported_format"
        return result
    except Exception as e:  # pragma: no cover - defensive
        result["status"] = f"error: {e.__class__.__name__}: {e}"
        return result


def analyze_wav_bytes(data: bytes, cfg: AnalyzerConfig) -> Dict[str, object]:
    result: Dict[str, object] = {
        "file": "<bytes>",
        "status": "ok",
        "bpm": None,
        "offset": None,
        "confidence": 0.0,
        "method": cfg.method,
    }
    try:
        sr, mono = _read_wav_mono_bytes(data, max_seconds=cfg.max_duration)
        bpm, conf = _estimate_bpm_acf(mono, sr, cfg)
        result["bpm"] = round(bpm, 2) if bpm is not None else None
        result["confidence"] = float(conf)
    except Exception as e:  # pragma: no cover
        result["status"] = f"error: {e.__class__.__name__}: {e}"
    return result


def _read_wav_mono(path: Path, max_seconds: Optional[float]) -> (int, List[float]):
    with contextlib.closing(wave.open(str(path), "rb")) as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()

        if max_seconds is not None:
            n_frames = min(n_frames, int(max_seconds * framerate))

        raw = wf.readframes(n_frames)

    # Convert to floats in [-1, 1]
    if sampwidth == 1:
        fmt = f"{n_frames * n_channels}B"
        ints = struct.unpack(fmt, raw)
        scale = 1.0 / 127.5
        offset = -1.0
        samples = [(i * scale) + offset for i in ints]
    elif sampwidth == 2:
        fmt = f"{n_frames * n_channels}h"
        ints = struct.unpack(fmt, raw)
        scale = 1.0 / 32768.0
        samples = [i * scale for i in ints]
    elif sampwidth == 4:
        fmt = f"{n_frames * n_channels}i"
        ints = struct.unpack(fmt, raw)
        scale = 1.0 / 2147483648.0
        samples = [i * scale for i in ints]
    else:
        raise ValueError(f"unsupported WAV sample width: {sampwidth} bytes")

    # To mono
    if n_channels == 1:
        mono = samples
    else:
        mono = []
        for i in range(0, len(samples), n_channels):
            s = 0.0
            for c in range(n_channels):
                s += samples[i + c]
            mono.append(s / n_channels)

    return framerate, mono


def _read_wav_mono_bytes(data: bytes, max_seconds: Optional[float]) -> (int, List[float]):
    with contextlib.closing(wave.open(io.BytesIO(data), "rb")) as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()

        if max_seconds is not None:
            n_frames = min(n_frames, int(max_seconds * framerate))

        raw = wf.readframes(n_frames)

    # Convert to floats in [-1, 1]
    if sampwidth == 1:
        fmt = f"{n_frames * n_channels}B"
        ints = struct.unpack(fmt, raw)
        scale = 1.0 / 127.5
        offset = -1.0
        samples = [(i * scale) + offset for i in ints]
    elif sampwidth == 2:
        fmt = f"{n_frames * n_channels}h"
        ints = struct.unpack(fmt, raw)
        scale = 1.0 / 32768.0
        samples = [i * scale for i in ints]
    elif sampwidth == 4:
        fmt = f"{n_frames * n_channels}i"
        ints = struct.unpack(fmt, raw)
        scale = 1.0 / 2147483648.0
        samples = [i * scale for i in ints]
    else:
        raise ValueError(f"unsupported WAV sample width: {sampwidth} bytes")

    # To mono
    if n_channels == 1:
        mono = samples
    else:
        mono = []
        for i in range(0, len(samples), n_channels):
            s = 0.0
            for c in range(n_channels):
                s += samples[i + c]
            mono.append(s / n_channels)

    return framerate, mono


def _decimate(x: List[float], factor: int) -> List[float]:
    if factor <= 1:
        return x
    return x[::factor]


def _moving_average(x: List[float], win: int) -> List[float]:
    if win <= 1:
        return x
    out: List[float] = []
    s = 0.0
    for i, v in enumerate(x):
        s += v
        if i >= win:
            s -= x[i - win]
        if i >= win - 1:
            out.append(s / win)
    # Pad head to keep length similar
    pad = [out[0]] * (win - 1) if out else []
    return pad + out


def _estimate_bpm_acf(x: List[float], sr: int, cfg: AnalyzerConfig) -> (Optional[float], float):
    # Preprocess: high-level simplification
    target_sr = min(sr, max(2000, min(8000, cfg.target_sr)))
    decim = max(1, int(round(sr / target_sr)))
    x = _decimate(x, decim)
    env_sr = sr / decim

    # Onset-like envelope: absolute first difference, half-wave rectified
    env: List[float] = []
    prev = 0.0
    for v in x:
        diff = v - prev
        prev = v
        env.append(diff if diff > 0 else 0.0)
    # Smooth envelope
    smooth_win = max(1, int(round(0.05 * env_sr)))  # ~50 ms
    env = _moving_average(env, smooth_win)

    # Downsample envelope for ACF speed
    env_decim = max(1, int(round(env_sr / 200.0)))  # ~200 Hz
    env = _decimate(env, env_decim)
    env_sr = env_sr / env_decim

    # Normalize envelope
    max_env = max(env) if env else 0.0
    if max_env <= 0:
        return None, 0.0
    env = [v / max_env for v in env]

    # Lag bounds in samples
    min_lag = int(env_sr * 60.0 / cfg.max_bpm)
    max_lag = int(env_sr * 60.0 / cfg.min_bpm)
    min_lag = max(1, min_lag)
    max_lag = max(min_lag + 1, max_lag)

    # Autocorrelation (naive, normalized)
    def acf_at(lag: int) -> float:
        num = 0.0
        den = 0.0
        for i in range(lag, len(env)):
            a = env[i]
            b = env[i - lag]
            num += a * b
            den += a * a
        return (num / den) if den > 0 else 0.0

    best_lag = None
    best_val = -1.0
    vals: List[float] = []
    for lag in range(min_lag, max_lag + 1):
        v = acf_at(lag)
        vals.append(v)
        if v > best_val:
            best_val = v
            best_lag = lag

    if best_lag is None or best_val <= 0:
        return None, 0.0

    bpm = 60.0 / (best_lag / env_sr)
    # Simple confidence: peak prominence vs mean
    mean_val = sum(vals) / len(vals) if vals else 0.0
    conf = max(0.0, min(1.0, (best_val - mean_val) / (1.0 - mean_val + 1e-9)))
    return bpm, conf
