/* Shared digital signal processing.
   The feature extraction here is byte-for-byte equivalent to the Python
   training pipeline (scripts/10 / website/train_web_model.py) and to the
   FastAPI service (backend/app/bioacoustics.py), so predictions agree
   whether they are produced in the browser or on the server. */
(function () {
  'use strict';

  var SR = 16000, N_FFT = 1024, HOP = 256;

  function hann(n) {
    var w = new Float32Array(n);
    for (var i = 0; i < n; i++) w[i] = 0.5 * (1 - Math.cos(2 * Math.PI * i / (n - 1)));
    return w;
  }

  function fft(re, im) {
    var n = re.length, i, j, bit, tmp;
    for (i = 1, j = 0; i < n; i++) {
      bit = n >> 1;
      for (; j & bit; bit >>= 1) j ^= bit;
      j ^= bit;
      if (i < j) {
        tmp = re[i]; re[i] = re[j]; re[j] = tmp;
        tmp = im[i]; im[i] = im[j]; im[j] = tmp;
      }
    }
    for (var len = 2; len <= n; len <<= 1) {
      var ang = -2 * Math.PI / len;
      var wr = Math.cos(ang), wi = Math.sin(ang);
      for (i = 0; i < n; i += len) {
        var cr = 1, ci = 0;
        for (var k = 0; k < len >> 1; k++) {
          var ar = re[i + k], ai = im[i + k];
          var br = re[i + k + (len >> 1)] * cr - im[i + k + (len >> 1)] * ci;
          var bi = re[i + k + (len >> 1)] * ci + im[i + k + (len >> 1)] * cr;
          re[i + k] = ar + br; im[i + k] = ai + bi;
          re[i + k + (len >> 1)] = ar - br; im[i + k + (len >> 1)] = ai - bi;
          tmp = cr * wr - ci * wi;
          ci = cr * wi + ci * wr; cr = tmp;
        }
      }
    }
  }

  function resample(x, fromSr, toSr) {
    if (fromSr === toSr) return x;
    var ratio = fromSr / toSr;
    var out = new Float32Array(Math.floor(x.length / ratio));
    for (var i = 0; i < out.length; i++) {
      var pos = i * ratio;
      var i0 = Math.floor(pos);
      var i1 = Math.min(i0 + 1, x.length - 1);
      var f = pos - i0;
      out[i] = x[i0] * (1 - f) + x[i1] * f;
    }
    return out;
  }

  /* Frame exactly like the Python training code: zero-pad nfft/2 samples at the
     start, pad the end so the last frame fits, slide a Hann window each hop. */
  function framed(signal, nfft, hop) {
    var pad = nfft >> 1;
    var nFrames = Math.max(1, Math.ceil((signal.length + 2 * pad - nfft) / hop) + 1);
    var needed = (nFrames - 1) * hop + nfft;
    var buf = new Float32Array(needed);
    buf.set(signal.subarray(0, Math.min(signal.length, needed - pad)), pad);
    var win = hann(nfft);
    var frames = [];
    for (var f = 0; f < nFrames; f++) {
      var re = new Float32Array(nfft), im = new Float32Array(nfft);
      var start = f * hop;
      for (var i = 0; i < nfft; i++) {
        var s = start + i < buf.length ? buf[start + i] : 0;
        re[i] = s * win[i];
      }
      fft(re, im);
      frames.push({ re: re, im: im });
    }
    return frames;
  }

  function powerSpectrum(re, im) {
    var half = (re.length >> 1) + 1;
    var p = new Float64Array(half);
    for (var i = 0; i < half; i++) p[i] = re[i] * re[i] + im[i] * im[i];
    return p;
  }

  /* 128 features: per band, log1p(mean) and log1p(std) of the raw band energy,
     interleaved (mean0, std0, mean1, std1, ...) - identical to training. */
  function extractFeatures(signal, model) {
    model = model || window.MODEL;
    var bands = model.bands;
    var frames = framed(signal, model.n_fft, model.hop);
    var nBands = bands.length;
    var sums = new Float64Array(nBands);
    var sqs = new Float64Array(nBands);
    for (var f = 0; f < frames.length; f++) {
      var power = powerSpectrum(frames[f].re, frames[f].im);
      for (var b = 0; b < nBands; b++) {
        var a = bands[b][0], e = bands[b][1], s = 0;
        for (var k = a; k < e; k++) s += power[k];
        var v = s / (e - a);
        sums[b] += v;
        sqs[b] += v * v;
      }
    }
    var n = frames.length;
    var feats = new Float64Array(2 * nBands);
    for (var b2 = 0; b2 < nBands; b2++) {
      var mean = sums[b2] / n;
      var variance = Math.max(0, sqs[b2] / n - mean * mean);
      feats[2 * b2] = Math.log1p(mean);
      feats[2 * b2 + 1] = Math.log1p(Math.sqrt(variance));
    }
    return feats;
  }

  function classify(feats, model) {
    model = model || window.MODEL;
    var z = [];
    for (var i = 0; i < model.classes.length; i++) {
      var s = model.intercept[i];
      for (var j = 0; j < feats.length; j++) {
        s += model.coef[i][j] * ((feats[j] - model.mean[j]) / model.std[j]);
      }
      z.push(s);
    }
    var max = Math.max.apply(null, z);
    var exps = z.map(function (v) { return Math.exp(v - max); });
    var sum = exps.reduce(function (a, c) { return a + c; }, 0);
    return model.classes.map(function (c, i) { return { species: c, probability: exps[i] / sum }; })
      .sort(function (a, b) { return b.probability - a.probability; });
  }

  /* Log-mel spectrogram for display: returns { mels: [][], freqs: [] }. */
  function spectrogram(signal, model, nMels, maxFrames) {
    model = model || window.MODEL;
    nMels = nMels || 48;
    maxFrames = maxFrames || 300;
    var bands = melEdges(nMels, model.sr, model.n_fft);
    var frames = framed(signal, model.n_fft, model.hop);
    var step = Math.max(1, Math.ceil(frames.length / maxFrames));
    var mels = [], freqs = new Array(nMels);
    for (var b = 0; b < nMels; b++) {
      var a = bands[b][0], e = bands[b][1];
      freqs[b] = Math.round(((a + e) / 2.0) * model.sr / model.n_fft);
      mels.push([]);
    }
    for (var f = 0; f < frames.length; f += step) {
      var power = powerSpectrum(frames[f].re, frames[f].im);
      for (var b2 = 0; b2 < nMels; b2++) {
        var a2 = bands[b2][0], e2 = bands[b2][1], s = 0;
        for (var k = a2; k < e2; k++) s += power[k];
        mels[b2].push(Math.log1p(s / (e2 - a2)));
      }
    }
    return { mels: mels, freqs: freqs, frames: frames.length, step: step };
  }

  function melEdges(nMels, sr, nfft) {
    var fmin = 10, fmax = sr / 2;
    var mMin = 2595 * Math.log10(1 + fmin / 700);
    var mMax = 2595 * Math.log10(1 + fmax / 700);
    var pts = [];
    for (var i = 0; i < nMels + 2; i++) {
      var m = mMin + (mMax - mMin) * i / (nMels + 1);
      var f = 700 * (Math.pow(10, m / 2595) - 1);
      pts.push(Math.round(f * nfft / sr));
    }
    var edges = [];
    for (var j = 0; j < nMels; j++) {
      var a = Math.max(0, Math.min(pts[j], pts[j + 1] - 1));
      var b = Math.max(a + 1, Math.min(pts[j + 1], (nfft >> 1) + 1));
      edges.push([a, b]);
    }
    return edges;
  }

  /* Min/max envelope for the waveform drawing. */
  function waveform(signal, points) {
    points = points || 320;
    var step = Math.max(1, Math.floor(signal.length / points));
    var mins = [], maxs = [];
    for (var i = 0; i + step <= signal.length; i += step) {
      var mn = Infinity, mx = -Infinity;
      for (var j = i; j < i + step; j++) {
        if (signal[j] < mn) mn = signal[j];
        if (signal[j] > mx) mx = signal[j];
      }
      mins.push(mn); maxs.push(mx);
    }
    return { min: mins, max: maxs };
  }

  /* Acoustic pattern interpretation from measured spectral properties.
     Mirrors the rule set in backend/app/bioacoustics.py. */
  var PATTERN_INFO = {
    tonal_whistle: ['Tonal whistle', 'A narrow-band, frequency-modulated tone.'],
    broadband_click: ['Broadband click train', 'A train of short, broadband transients.'],
    low_frequency_call: ['Low-frequency call', 'Energy concentrated below a few hundred hertz.'],
    harmonic_song: ['Harmonic / song-like structure', 'A stable harmonic series with repeated phrases.'],
    ambient_noise: ['Ambient / broadband noise', 'Broadband energy with no stable tonal structure.']
  };

  function analysePattern(signal, model) {
    model = model || window.MODEL;
    var frames = framed(signal, model.n_fft, model.hop);
    if (!frames.length) return null;

    var nBins = (model.n_fft >> 1) + 1;
    var meanPower = new Float64Array(nBins);
    var geoSum = 0, arithSum = 0, count = 0, energyTotal = 0, weighted = 0;

    for (var f = 0; f < frames.length; f++) {
      var power = powerSpectrum(frames[f].re, frames[f].im);
      var frameTotal = 0;
      for (var i = 0; i < nBins; i++) frameTotal += power[i];
      for (var b = 0; b < nBins; b++) {
        meanPower[b] += power[b];
        geoSum += Math.log(power[b] + 1e-12);
        arithSum += power[b];
        count++;
        weighted += (b * model.sr / model.n_fft) * power[b];
        energyTotal += power[b];
      }
    }
    for (var m = 0; m < nBins; m++) meanPower[m] /= frames.length;

    var centroid = energyTotal > 0 ? weighted / energyTotal : 0;
    var flatness = (arithSum > 0) ? Math.exp(geoSum / count) / (arithSum / count) : 0;

    var domIdx = 0;
    for (var d = 1; d < nBins; d++) if (meanPower[d] > meanPower[domIdx]) domIdx = d;
    var domHz = domIdx * model.sr / model.n_fft;

    var half = meanPower[domIdx] / 2;
    var lo = domIdx, hi = domIdx;
    while (lo > 0 && meanPower[lo] > half) lo--;
    while (hi < nBins - 1 && meanPower[hi] > half) hi++;
    var bandwidth = (hi - lo) * model.sr / model.n_fft;

    var meanSpec = 0;
    for (var s = 0; s < nBins; s++) meanSpec += meanPower[s];
    meanSpec /= nBins;
    var tonality = meanPower[domIdx] / (meanSpec + 1e-12);

    // pulse rate from the autocorrelation of the frame energy sequence
    var env = new Float64Array(frames.length);
    for (var e = 0; e < frames.length; e++) {
      var t = 0;
      for (var q = 0; q < nBins; q++) t += Math.pow(frames[e].re[q], 2) + Math.pow(frames[e].im[q], 2);
      env[e] = t;
    }
    var mEnv = 0;
    for (var e2 = 0; e2 < env.length; e2++) mEnv += env[e2];
    mEnv /= env.length;
    var ac = new Float64Array(env.length);
    for (var i2 = 0; i2 < env.length; i2++) {
      var acc = 0;
      for (var j2 = 0; j2 < env.length - i2; j2++) acc += (env[j2] - mEnv) * (env[j2 + i2] - mEnv);
      ac[i2] = acc;
    }
    var pulseRate = 0;
    if (ac[0] > 0) {
      var best = 0, bestLag = 0;
      var maxLag = Math.min(ac.length - 1, Math.round(model.sr / model.hop / 50));
      for (var lag = 1; lag <= maxLag; lag++) {
        var v = ac[lag] / ac[0];
        if (v > best) { best = v; bestLag = lag; }
      }
      if (bestLag > 0) pulseRate = (model.sr / model.hop) / bestLag;
    }

    var pattern;
    if (domHz < 200 && bandwidth < 400) pattern = 'low_frequency_call';
    else if (flatness < 0.05 && tonality > 40 && domHz > 400) pattern = 'tonal_whistle';
    else if (pulseRate > 40 && bandwidth > 800) pattern = 'broadband_click';
    else if (tonality > 25 && bandwidth < 1500) pattern = 'harmonic_song';
    else if (flatness > 0.25 && tonality < 12) pattern = 'ambient_noise';
    else pattern = tonality > 18 ? 'harmonic_song' : 'broadband_click';

    var info = PATTERN_INFO[pattern];
    return {
      pattern: pattern,
      label: info[0],
      short_description: info[1],
      dominant_frequency_hz: Math.round(domHz * 10) / 10,
      spectral_centroid_hz: Math.round(centroid * 10) / 10,
      spectral_flatness: Math.round(flatness * 10000) / 10000,
      bandwidth_hz: Math.round(bandwidth * 10) / 10,
      pulse_rate_hz: Math.round(pulseRate * 10) / 10,
      tonality: Math.round(tonality * 100) / 100
    };
  }

  window.DSP = {
    SR: SR, N_FFT: N_FFT, HOP: HOP,
    hann: hann, fft: fft, resample: resample,
    extractFeatures: extractFeatures, classify: classify,
    spectrogram: spectrogram, waveform: waveform,
    analysePattern: analysePattern, melEdges: melEdges,
    PATTERN_INFO: PATTERN_INFO
  };
})();
