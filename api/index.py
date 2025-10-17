from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from pathlib import Path
import io

# Import local analyzer package
from bpm_analyzer.analyzer import AnalyzerConfig, analyze_wav_bytes, analyze_file


app = FastAPI(title="BPM Analyzer API", version="0.1.0")

# CORS: safe default for same-origin; customize if developing separately
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "bpm-analyzer", "version": "0.1.0"}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    min_bpm: float = Form(60.0),
    max_bpm: float = Form(200.0),
    duration: Optional[float] = Form(None),
):
    """Analyze an uploaded audio file (WAV supported currently)."""
    cfg = AnalyzerConfig(min_bpm=min_bpm, max_bpm=max_bpm, max_duration=duration)

    filename = file.filename or "uploaded"
    suffix = Path(filename).suffix.lower()
    data = await file.read()

    if suffix == ".wav":
        result = analyze_wav_bytes(data, cfg)
        result["file"] = filename
        return result

    # Fallback: try by path (if any) or return unsupported
    return {
        "file": filename,
        "status": "unsupported_format",
        "bpm": None,
        "offset": None,
        "confidence": 0.0,
        "method": cfg.method,
    }

