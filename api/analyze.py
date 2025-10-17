from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
from pathlib import Path

from bpm_analyzer.analyzer import AnalyzerConfig, analyze_wav_bytes

app = FastAPI(title="BPM Analyze Endpoint", version="0.1.0")


@app.post("/")
async def analyze(
    file: UploadFile = File(...),
    min_bpm: float = Form(60.0),
    max_bpm: float = Form(200.0),
    duration: Optional[float] = Form(None),
):
    cfg = AnalyzerConfig(min_bpm=min_bpm, max_bpm=max_bpm, max_duration=duration)
    filename = file.filename or "uploaded"
    suffix = Path(filename).suffix.lower()
    data = await file.read()

    if suffix == ".wav":
        result = analyze_wav_bytes(data, cfg)
        result["file"] = filename
        return result

    return {
        "file": filename,
        "status": "unsupported_format",
        "bpm": None,
        "offset": None,
        "confidence": 0.0,
        "method": cfg.method,
    }

