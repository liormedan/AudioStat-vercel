"use client";

import { useState } from "react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

export default function Page() {
  const [file, setFile] = useState<File | null>(null);
  const [minBpm, setMinBpm] = useState(60);
  const [maxBpm, setMaxBpm] = useState(200);
  const [duration, setDuration] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  function apiBase() {
    return process.env.NEXT_PUBLIC_API_BASE || '';
  }

  async function fileToWav(file: File, durationSec?: number): Promise<File> {
    // If already WAV, return as-is
    if (file.name.toLowerCase().endsWith(".wav") || file.type === "audio/wav") {
      return file;
    }
    const arrayBuf = await file.arrayBuffer();
    const AC = (window as any).AudioContext || (window as any).webkitAudioContext;
    const ctx = new AC();
    const audio = await ctx.decodeAudioData(arrayBuf.slice(0));

    // Optionally trim duration
    let length = audio.length;
    if (durationSec && durationSec > 0) {
      length = Math.min(length, Math.floor(audio.sampleRate * durationSec));
    }

    // Downmix to mono
    const mono = new Float32Array(length);
    const ch = audio.numberOfChannels;
    for (let c = 0; c < ch; c++) {
      const data = audio.getChannelData(c).subarray(0, length);
      for (let i = 0; i < length; i++) mono[i] += data[i] / ch;
    }

    const wavBlob = floatToWav(mono, audio.sampleRate);
    const out = new File([wavBlob], file.name.replace(/\.[^.]+$/, "") + ".wav", {
      type: "audio/wav",
      lastModified: Date.now(),
    });
    ctx.close?.();
    return out;
  }

  function floatToWav(samples: Float32Array, sampleRate: number): Blob {
    const bytesPerSample = 2; // 16-bit PCM
    const blockAlign = 1 * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = samples.length * bytesPerSample;
    const buffer = new ArrayBuffer(44 + dataSize);
    const view = new DataView(buffer);

    function writeString(offset: number, s: string) {
      for (let i = 0; i < s.length; i++) view.setUint8(offset + i, s.charCodeAt(i));
    }
    let offset = 0;
    writeString(offset, "RIFF"); offset += 4;
    view.setUint32(offset, 36 + dataSize, true); offset += 4;
    writeString(offset, "WAVE"); offset += 4;
    writeString(offset, "fmt "); offset += 4;
    view.setUint32(offset, 16, true); offset += 4; // Subchunk1Size
    view.setUint16(offset, 1, true); offset += 2;  // PCM
    view.setUint16(offset, 1, true); offset += 2;  // channels
    view.setUint32(offset, sampleRate, true); offset += 4;
    view.setUint32(offset, byteRate, true); offset += 4;
    view.setUint16(offset, blockAlign, true); offset += 2;
    view.setUint16(offset, 8 * bytesPerSample, true); offset += 2;
    writeString(offset, "data"); offset += 4;
    view.setUint32(offset, dataSize, true); offset += 4;

    // Write samples
    let i = 0;
    for (let s = 0; s < samples.length; s++, i += 2) {
      let v = Math.max(-1, Math.min(1, samples[s]));
      view.setInt16(44 + i, v < 0 ? v * 0x8000 : v * 0x7fff, true);
    }
    return new Blob([view], { type: "audio/wav" });
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!file) {
      setError("Please choose a WAV file.");
      return;
    }
    // Convert MP3/FLAC/etc. to WAV in browser if needed
    let uploadFile = file;
    try {
      uploadFile = await fileToWav(file, duration ? parseFloat(duration) : undefined);
    } catch (err) {
      // If conversion fails, fall back to original file (WAV-only backend may reject)
      console.warn("WAV conversion failed, uploading original:", err);
    }

    const form = new FormData();
    form.append("file", uploadFile);
    form.append("min_bpm", String(minBpm));
    form.append("max_bpm", String(maxBpm));
    if (duration) form.append("duration", duration);

    setLoading(true);
    try {
      const res = await fetch(`${apiBase()}/api/analyze`, { method: "POST", body: form });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setResult(json);
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">BPM Analyzer</h1>
        <p className="text-sm text-[var(--muted)]">Upload a WAV file to estimate its tempo.</p>
      </div>
      <form onSubmit={onSubmit} className="grid gap-4 max-w-xl">
        <input
          className="block w-full text-sm file:mr-4 file:rounded-md file:border-0 file:bg-cyan-500 file:px-3 file:py-2 file:text-sm file:font-medium hover:file:bg-cyan-400"
          type="file"
          accept="audio/*,.wav,.mp3,.flac,.aiff,.aif,.ogg,.m4a"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <div className="grid grid-cols-2 gap-3">
          <Label>
            <span className="text-[var(--muted)]">Min BPM</span>
            <Input type="number" value={minBpm} min={20} max={300} onChange={e => setMinBpm(parseFloat((e.target as HTMLInputElement).value))} />
          </Label>
          <Label>
            <span className="text-[var(--muted)]">Max BPM</span>
            <Input type="number" value={maxBpm} min={20} max={300} onChange={e => setMaxBpm(parseFloat((e.target as HTMLInputElement).value))} />
          </Label>
        </div>
        <Label>
          <span className="text-[var(--muted)]">Analyze first N seconds (optional)</span>
          <Input type="number" step="0.1" value={duration} onChange={e => setDuration((e.target as HTMLInputElement).value)} />
        </Label>
        <Button type="submit" disabled={loading}>{loading ? 'Analyzing…' : 'Analyze'}</Button>
      </form>
      {error && <p className="text-red-400 mt-3">{error}</p>}
      {result && (
        <pre className="bg-[var(--panel)] p-4 mt-4 overflow-x-auto rounded-md ring-1 ring-slate-800">
{JSON.stringify(result, null, 2)}
        </pre>
      )}
      <p className="mt-6 text-[var(--muted)] text-sm">
        UI uses Tailwind; I can add shadcn/ui components next.
      </p>
    </main>
  );
}
