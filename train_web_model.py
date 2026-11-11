"""Train a compact species classifier and export it to model.json for the website.

The website runs the same feature extraction + logistic regression in JavaScript,
so the demo model is genuinely working (not simulated).
"""
import json
import numpy as np
import pandas as pd
from scipy.signal import stft
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

SR = 16000
N_FFT = 1024
HOP = 256
N_MELS = 64
CLASSES = ["blue_whale", "fin_whale", "humpback_whale",
           "killer_whale", "bottlenose_dolphin", "background"]

# mel-spaced band edges (proper mel scale gives low-frequency calls the
# resolution they need to be separated from each other)
def mel_band_edges(n_mels, sr, nfft, fmin=10.0, fmax=None):
    import math
    fmax = fmax or sr / 2.0
    m_min = 2595.0 * math.log10(1.0 + fmin / 700.0)
    m_max = 2595.0 * math.log10(1.0 + fmax / 700.0)
    pts = []
    for i in range(n_mels + 2):
        m = m_min + (m_max - m_min) * i / (n_mels + 1)
        f = 700.0 * (10 ** (m / 2595.0) - 1.0)
        pts.append(int(round(f * nfft / sr)))
    edges = []
    for i in range(n_mels):
        a = max(0, min(pts[i], pts[i + 1] - 1))
        b = max(a + 1, min(pts[i + 1], nfft // 2 + 1))
        edges.append((a, b))
    return edges


BANDS = mel_band_edges(N_MELS, SR, N_FFT)


def chirp(f0, f1, dur, sr=SR):
    t = np.arange(int(dur * sr)) / sr
    f = f0 + (f1 - f0) * (t / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / sr) * np.hanning(len(t))


def make_call(species, n):
    y = np.zeros(n)

    def add(call, start):
        end = min(n, start + len(call))
        y[start:end] += call[:end - start]

    if species == "blue_whale":
        add(chirp(16, 19, 2.5), int(np.random.uniform(0, 2) * SR))
    elif species == "fin_whale":
        for k in range(3):
            add(chirp(28, 18, 1.0), int((0.3 + k * 1.5) * SR))
    elif species == "humpback_whale":
        t0 = 0.0
        for _ in range(3):
            d = np.random.uniform(0.5, 1.0)
            add(chirp(300, 1200, d), int(t0 * SR))
            t0 += d + 0.3
    elif species == "killer_whale":
        t0 = 0.0
        for _ in range(3):
            d = np.random.uniform(0.4, 0.8)
            add(chirp(1000, 2000, d), int(t0 * SR))
            t0 += d + 0.4
    elif species == "bottlenose_dolphin":
        t0 = 0.0
        for _ in range(3):
            d = np.random.uniform(0.3, 0.7)
            t = np.arange(int(d * SR)) / SR
            f0 = np.random.uniform(4000, 6000)
            add(np.sin(2 * np.pi * f0 * t) * np.hanning(len(t)), int(t0 * SR))
            t0 += d + 0.3
    return y


def make_clip(species, dur=5.0):
    n = int(dur * SR)
    y = np.random.normal(0, 0.05, n)
    if species == "background":
        y += 0.3 * np.random.normal(0, 1, n)
    else:
        y += make_call(species, n)
    return (y / (np.abs(y).max() + 1e-9) * 0.9).astype(np.float32)


def _hann(n):
    return 0.5 * (1 - np.cos(2 * np.pi * np.arange(n) / (n - 1)))


def features(x, sr=SR):
    """log-mel band energies: mean and std over time -> 2*N_MELS features.

    Uses a plain rFFT with a Hann window and the same framing/padding as the
    JavaScript version in the website, so training and inference match exactly.
    """
    nfft, hop = N_FFT, HOP
    pad = nfft // 2
    nFrames = max(1, int(np.ceil((len(x) + 2 * pad - nfft) / hop)) + 1)
    needed = (nFrames - 1) * hop + nfft
    buf = np.zeros(needed)
    buf[pad:pad + len(x)] = x

    win = _hann(nfft)
    vals = [[] for _ in range(N_MELS)]
    for f in range(nFrames):
        frame = buf[f * hop:f * hop + nfft] * win
        power = np.abs(np.fft.rfft(frame)) ** 2
        for b, (a, e) in enumerate(BANDS):
            vals[b].append(power[a:e].mean())

    feats = []
    for b in range(N_MELS):
        v = np.array(vals[b])
        feats.append(np.log1p(v.mean()))
        feats.append(np.log1p(v.std()))
    return np.array(feats)


def main():
    np.random.seed(42)
    X, y = [], []
    for sp in CLASSES:
        for _ in range(60):
            X.append(features(make_clip(sp)))
            y.append(sp)
    X = np.array(X)
    y = np.array(y)
    print("features:", X.shape)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    mean = X_tr.mean(axis=0)
    std = X_tr.std(axis=0) + 1e-9
    X_tr_s = (X_tr - mean) / std
    X_te_s = (X_te - mean) / std

    clf = LogisticRegression(max_iter=3000, C=1.0).fit(X_tr_s, y_tr)
    y_pred = clf.predict(X_te_s)
    print("web model accuracy:", round(accuracy_score(y_te, y_pred), 4))
    print(classification_report(y_te, y_pred, zero_division=0))
    model = {
        "classes": [str(c) for c in clf.classes_],
        "bands": BANDS,
        "sr": SR,
        "n_fft": N_FFT,
        "hop": HOP,
        "mean": [round(float(v), 6) for v in mean],
        "std": [round(float(v), 6) for v in std],
        "coef": [[round(float(v), 6) for v in row] for row in clf.coef_],
        "intercept": [round(float(v), 6) for v in clf.intercept_],
    }
    out = r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation\website\model.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(model, f)
    import os
    print("saved:", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
