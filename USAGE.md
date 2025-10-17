Run the CLI using Python (no external dependencies required):

1) Analyze files or folders:

   python -m bpm_analyzer analyze "C:\\path\\to\\loops" --export csv --out results.csv

2) Options:

   --min-bpm / --max-bpm  Tempo search range (default 60–200)
   --sr                   Target analysis sample rate (default 22050)
   --duration             Analyze only first N seconds
   --export               csv or json; prints to stdout if omitted
   --out                  Output file for export

Notes:
- Current implementation supports WAV decoding for analysis. Other formats are detected but marked as unsupported for now.
- BPM estimation uses a simple autocorrelation on an onset-like envelope; accuracy is acceptable for steady, percussive material but is a starting point.

