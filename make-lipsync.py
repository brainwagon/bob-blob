#!/usr/bin/env python3
"""Build a lip-sync track for Bob's intro from a WAV file.

Usage: python3 make-lipsync.py [input.wav] [output.js]

The audio is analysed at 30 fps (RMS, spectral centroid, high-frequency
energy) and mapped onto the same 15-viseme vocabulary used by the viewer.
The result is a baked track of mouth parameters, so the browser just has to
interpolate between frames while the audio plays.

The included voice is a macOS `say` placeholder until the OpenRouter key is
renewed. Replace bob-intro.wav with the Kokoro-82M render, then rerun this.
"""

import sys
import wave
import math

import numpy as np

FPS = 30
WINDOW = 1024

# name, width, height, corner, teeth, tongue
VISEMES = [
    ("sil", 0.080, 0.008, 0.020, 0.00, 0.00),
    ("PP",  0.075, 0.006, 0.000, 0.00, 0.00),
    ("FF",  0.085, 0.022, 0.005, 0.90, 0.08),
    ("TH",  0.085, 0.036, 0.005, 0.20, 0.95),
    ("DD",  0.085, 0.048, 0.010, 0.55, 0.35),
    ("kk",  0.075, 0.040, 0.000, 0.15, 0.15),
    ("CH",  0.065, 0.045, 0.000, 0.20, 0.20),
    ("SS",  0.100, 0.026, 0.020, 0.95, 0.00),
    ("nn",  0.080, 0.020, 0.008, 0.10, 0.55),
    ("RR",  0.070, 0.030, 0.005, 0.20, 0.25),
    ("aa",  0.095, 0.072, 0.000, 0.10, 0.30),
    ("E",   0.105, 0.045, 0.020, 0.55, 0.08),
    ("I",   0.098, 0.030, 0.020, 0.70, 0.00),
    ("O",   0.062, 0.058, 0.000, 0.00, 0.18),
    ("U",   0.050, 0.048, 0.000, 0.00, 0.10),
]

TRANSCRIPT = (
    "Hi, I'm Bob! I'm a squishy gummy blob, built in one HTML file with "
    "OpenCode. My body is ray marched from signed distance functions, my face "
    "is drawn with cartoon decals and visemes, and this is my little velvet "
    "stage and microphone. Thanks for stopping by!"
)


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def analyse(path):
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        channels = w.getnchannels()
        raw = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        raw = raw.reshape(-1, channels).mean(axis=1)

    hop = max(1, round(sr / FPS))
    win = np.hanning(WINDOW).astype(np.float32)
    freqs = np.fft.rfftfreq(WINDOW, 1.0 / sr)

    rms, centroid, hf = [], [], []
    for start in range(0, len(raw) - WINDOW, hop):
        seg = raw[start:start + WINDOW] * win
        mag = np.abs(np.fft.rfft(seg))
        total = mag.sum() + 1e-9
        rms.append(float(np.sqrt(np.mean(seg * seg))))
        centroid.append(float((freqs * mag).sum() / total))
        hf.append(float(mag[freqs > 3000.0].sum() / total))

    rms = np.array(rms)
    centroid = np.array(centroid)
    hf = np.array(hf)

    # perceptual features, normalised so any voice or sample rate works
    open_raw = np.clip((rms - 0.012) / 0.080, 0.0, 1.0)
    bright = smoothstep(650.0, 2600.0, centroid)
    fric = np.clip((hf - 0.18) / 0.55, 0.0, 1.0)

    # envelope follower: quick attack, slower release
    env = np.zeros_like(open_raw)
    for i in range(1, len(open_raw)):
        target = open_raw[i]
        coef = 0.65 if target > env[i - 1] else 0.28
        env[i] = env[i - 1] + (target - env[i - 1]) * coef

    # smooth the spectral descriptors
    bright_s = np.convolve(bright, np.ones(3) / 3.0, mode="same")
    fric_s = np.convolve(fric, np.ones(3) / 3.0, mode="same")

    frames = []
    cur = np.array(VISEMES[0][1:], dtype=float)
    counts = {v[0]: 0 for v in VISEMES}

    for i in range(len(env)):
        o = float(env[i])
        br = float(bright_s[i])
        fr = float(fric_s[i])
        active = (o > 0.05) or (fr > 0.45 and fr > 0.0)

        if not active:
            name = "sil"
        elif fr > 0.48 and o < 0.30:
            name = "FF" if o < 0.16 else "SS"
        elif o > 0.60:
            name = "aa" if br < 0.50 else "E"
        elif o > 0.32:
            name = "O" if br < 0.28 else ("I" if br > 0.66 else "DD")
        elif o > 0.14:
            name = "nn" if br < 0.42 else ("I" if br > 0.66 else "DD")
        else:
            name = "PP"

        preset = next(v for v in VISEMES if v[0] == name)
        counts[name] += 1

        # louder syllables open a little wider
        amp = 0.58 + 0.42 * o
        target = np.array([
            preset[1] * (0.94 + 0.06 * o),
            max(0.004, preset[2] * amp),
            preset[3],
            preset[4],
            preset[5],
        ], dtype=float)

        # low-pass the mouth pose; close a little faster than it opens
        alpha = 0.50 if target[1] < cur[1] else 0.34
        cur += (target - cur) * alpha
        frames.append([
            round(float(cur[0]), 4),
            round(float(cur[1]), 4),
            round(float(cur[2]), 4),
            round(float(cur[3]), 3),
            round(float(cur[4]), 3),
        ])

    duration = len(raw) / sr
    return sr, duration, frames, counts


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "bob-intro.wav"
    dst = sys.argv[2] if len(sys.argv) > 2 else "bob-lipsync.js"
    sr, duration, frames, counts = analyse(src)

    lines = []
    lines.append("// Generated by make-lipsync.py from %s" % src.split("/")[-1])
    lines.append("// Placeholder voice: macOS say (Eddy, en_US). Regenerate with Kokoro-82M.")
    lines.append("// Frames are [mouth width, height, corner lift, teeth, tongue] at 30 fps.")
    lines.append("const BOB_LIPSYNC = {")
    lines.append("  fps: %d," % FPS)
    lines.append("  duration: %.3f," % duration)
    lines.append("  transcript: %s," % repr(TRANSCRIPT))
    lines.append("  frames: [")
    for i in range(0, len(frames), 4):
        lines.append("    " + ", ".join(
            "[%s]" % ", ".join("%g" % v for v in f) for f in frames[i:i + 4]
        ) + ",")
    lines.append("  ]")
    lines.append("};")
    lines.append("")
    with open(dst, "w") as f:
        f.write("\n".join(lines))

    print("source: %s (%d Hz, %.2fs)" % (src, sr, duration))
    print("frames: %d at %d fps -> %s" % (len(frames), FPS, dst))
    print("visemes used:", ", ".join("%s:%d" % (k, v) for k, v in counts.items() if v))


if __name__ == "__main__":
    main()
