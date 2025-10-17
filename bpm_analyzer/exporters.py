from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable


FIELDS = [
    "file",
    "status",
    "bpm",
    "offset",
    "confidence",
    "method",
]


def write_csv(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in FIELDS})


def write_json(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    data = list(rows)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

