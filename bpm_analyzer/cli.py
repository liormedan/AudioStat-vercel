import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .io import collect_audio_files
from .exporters import write_csv, write_json
from .analyzer import AnalyzerConfig, analyze_file


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bpm-analyzer",
        description="Analyze audio files to estimate tempo (BPM)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="Analyze one or more files or folders")
    a.add_argument("paths", nargs="+", help="Files, folders, or glob patterns")
    a.add_argument("--min-bpm", type=float, default=60.0, dest="min_bpm", help="Minimum BPM to search")
    a.add_argument("--max-bpm", type=float, default=200.0, dest="max_bpm", help="Maximum BPM to search")
    a.add_argument("--sr", type=int, default=22050, help="Target sample rate for analysis")
    a.add_argument("--method", choices=["acf", "tempogram"], default="acf", help="Tempo method (stub)")
    a.add_argument("--grid", action="store_true", help="Estimate beat grid offset (stub)")
    a.add_argument("--candidates", type=int, default=3, help="Top tempo candidates to keep (stub)")
    a.add_argument("--export", choices=["csv", "json"], help="Export format")
    a.add_argument("--out", type=str, help="Output file path for export")
    a.add_argument("--jobs", type=int, default=1, help="Parallel jobs (stub)")
    a.add_argument("--duration", type=float, default=None, help="Analyze only first N seconds")

    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def _default_out_path(fmt: str) -> Path:
    if fmt == "csv":
        return Path("bpm_results.csv")
    if fmt == "json":
        return Path("bpm_results.json")
    raise ValueError("unknown export format")


def cmd_analyze(args: argparse.Namespace) -> int:
    files = collect_audio_files([Path(p) for p in args.paths])
    if not files:
        print("No audio files found.", file=sys.stderr)
        return 2

    cfg = AnalyzerConfig(
        min_bpm=args.min_bpm,
        max_bpm=args.max_bpm,
        target_sr=args.sr,
        method=args.method,
        estimate_grid=args.grid,
        top_k=args.candidates,
        max_duration=args.duration,
    )

    results = []
    for f in files:
        res = analyze_file(f, cfg)
        results.append(res)

    if args.export:
        out_path = Path(args.out) if args.out else _default_out_path(args.export)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if args.export == "csv":
            write_csv(out_path, results)
        else:
            write_json(out_path, results)
        print(f"Wrote {len(results)} result(s) to {out_path}")
    else:
        # Pretty-print to stdout
        for r in results:
            status = r.get("status", "ok")
            bpm = r.get("bpm")
            conf = r.get("confidence")
            print(f"{r['file']}\n  status: {status}\n  bpm: {bpm}\n  confidence: {conf:.3f}")

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "analyze":
        return cmd_analyze(args)
    parser.error("No command provided")
    return 2

