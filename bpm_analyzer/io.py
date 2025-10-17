from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
import glob


AUDIO_EXTS = {
    ".wav",
    ".mp3",
    ".flac",
    ".aif",
    ".aiff",
    ".ogg",
    ".m4a",
    ".aac",
    ".wma",
}


def _is_audio(path: Path) -> bool:
    return path.suffix.lower() in AUDIO_EXTS


def _walk_dir(d: Path) -> List[Path]:
    files: List[Path] = []
    for p in d.rglob("*"):
        if p.is_file() and _is_audio(p):
            files.append(p)
    return files


def collect_audio_files(inputs: Iterable[Path]) -> List[Path]:
    out: List[Path] = []
    for inp in inputs:
        p = Path(str(inp))
        # Glob pattern support
        if any(ch in str(p) for ch in ["*", "?", "["]):
            for g in glob.glob(str(p), recursive=True):
                gp = Path(g)
                if gp.is_file() and _is_audio(gp):
                    out.append(gp)
                elif gp.is_dir():
                    out.extend(_walk_dir(gp))
            continue
        if p.is_file() and _is_audio(p):
            out.append(p)
        elif p.is_dir():
            out.extend(_walk_dir(p))
    # Deduplicate preserving order
    seen = set()
    uniq: List[Path] = []
    for f in out:
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    return uniq

