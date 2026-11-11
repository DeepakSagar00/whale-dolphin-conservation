/* AI Conservation - browser-side species classifier
   Reproduces the feature extraction and linear model used during training. */
(function () {
  'use strict';

  var MODEL = window.MODEL || null;
  var fileInput = document.getElementById('ai-file');
  var drop = document.getElementById('ai-drop');
  var result = document.getElementById('ai-result');
  var bars = document.getElementById('ai-bars');
  var verdict = document.getElementById('ai-verdict');
  var speciesBox = document.getElementById('ai-species');
  var esc = window.SITE.escapeHtml;

  /* ------------------------------------------------------------------ math */
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

  function extractFeatures(x) {
    var nfft = MODEL.n_fft, hop = MODEL.hop;
    var pad = nfft >> 1;
    var nFrames = Math.max(1, Math.ceil((x.length + 2 * pad - nfft) / hop) + 1);
    var needed = (nFrames - 1) * hop + nfft;
    var buf = new Float32Array(needed);
    buf.set(x, pad);

    var win = hann(nfft);
    var nBands = MODEL.bands.length;
    var vals = [];
    for (var b = 0; b < nBands; b++) vals.push([]);

    for (var f = 0; f < nFrames; f++) {
      var start = f * hop;
      var re = new Float32Array(nfft), im = new Float32Array(nfft);
      for (var i = 0; i < nfft; i++) re[i] = buf[start + i] * win[i];
      fft(re, im);
      for (var b2 = 0; b2 < nBands; b2++) {
        var a = MODEL.bands[b2][0], e = MODEL.bands[b2][1], s = 0;
        for (var k = a; k < e; k++) s += re[k] * re[k] + im[k] * im[k];
        vals[b2].push(s / (e - a));
      }
    }

    var feats = [];
    for (var b3 = 0; b3 < nBands; b3++) {
      var v = vals[b3], mean = 0, j;
      for (j = 0; j < v.length; j++) mean += v[j];
      mean /= v.length;
      var sd = 0;
      for (j = 0; j < v.length; j++) sd += (v[j] - mean) * (v[j] - mean);
      sd = Math.sqrt(sd / v.length);
      feats.push(Math.log1p(mean), Math.log1p(sd));
    }
    return feats;
  }

  function predict(feats) {
    var z = [];
    for (var i = 0; i < MODEL.classes.length; i++) {
      var s = MODEL.intercept[i];
      for (var j = 0; j < feats.length; j++) {
        s += MODEL.coef[i][j] * ((feats[j] - MODEL.mean[j]) / MODEL.std[j]);
      }
      z.push(s);
    }
    var max = Math.max.apply(null, z);
    var exps = z.map(function (v) { return Math.exp(v - max); });
    var sum = exps.reduce(function (a, c) { return a + c; }, 0);
    return exps.map(function (v) { return v / sum; });
  }

  /* --------------------------------------------------------------- rendering */
  var SPECIES_ID = {
    'blue_whale': 'blue-whale',
    'fin_whale': 'fin-whale',
    'humpback_whale': 'humpback-whale',
    'killer_whale': 'killer-whale',
    'bottlenose_dolphin': 'bottlenose-dolphin',
    'background': null
  };

  function showResult(probs) {
    var order = probs.map(function (p, i) { return { p: p, i: i }; })
      .sort(function (a, b) { return b.p - a.p; });

    bars.innerHTML = order.map(function (o, rank) {
      var pct = Math.round(o.p * 100);
      return '<div class="bar-row' + (rank === 0 ? ' top' : '') + '">' +
        '<span class="name">' + esc(MODEL.classes[o.i].replace(/_/g, ' ')) + '</span>' +
        '<div class="bar-track"><div class="bar-fill"></div></div>' +
        '<span class="bar-val">' + pct + '%</span></div>';
    }).join('');

    Array.prototype.forEach.call(bars.querySelectorAll('.bar-row'), function (row, i) {
      var pct = Math.round(order[i].p * 100);
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { row.querySelector('.bar-fill').style.width = pct + '%'; });
      });
    });

    var top = order[0];
    var label = MODEL.classes[top.i].replace(/_/g, ' ');
    verdict.innerHTML = 'Detected: <b>' + esc(label) + '</b> with ' +
      Math.round(top.p * 100) + '% confidence.';

    var sid = SPECIES_ID[MODEL.classes[top.i]];
    if (sid) {
      var sp = window.SITE.speciesById(sid);
      if (sp) {
        speciesBox.innerHTML =
          '<div class="card"><div class="card__body" style="display:flex;gap:16px;align-items:flex-start">' +
            '<img src="assets/species/' + sp.id + '.svg" alt="" style="width:88px;border-radius:10px">' +
            '<div><h3 style="font-size:1rem">' + esc(sp.name) + '</h3>' +
            '<p style="font-style:italic;font-size:.86rem;color:var(--ink-400)">' + esc(sp.latin) + '</p>' +
            '<p style="font-size:.88rem;margin-top:8px">' + esc(sp.description) + '</p>' +
            '<a class="btn btn--outline btn--sm mt-2" href="species-detail.html?id=' + sp.id + '">Species record</a>' +
            '</div></div></div>';
      }
    } else {
      speciesBox.innerHTML = '<p class="muted" style="font-size:.88rem">' +
        'Background class &mdash; no biological call detected in this window. ' +
        'This is the class used to train the model to recognise ship noise.</p>';
    }

    result.classList.add('show');
  }

  function runSignal(signal, sr) {
    if (!MODEL) {
      verdict.innerHTML = 'The model is still loading. Please try again in a moment.';
      result.classList.add('show');
      return;
    }
    var x = resample(signal, sr, MODEL.sr);
    showResult(predict(extractFeatures(x)));
  }

  /* ------------------------------------------------------------- file input */
  fileInput.addEventListener('change', function (e) {
    var file = e.target.files[0];
    if (!file) return;
    var AC = window.AudioContext || window.webkitAudioContext;
    var ctx = new AC();
    file.arrayBuffer()
      .then(function (buf) { return ctx.decodeAudioData(buf); })
      .then(function (audio) {
        runSignal(new Float32Array(audio.getChannelData(0)), audio.sampleRate);
        ctx.close();
      })
      .catch(function (err) {
        verdict.innerHTML = 'That audio file could not be decoded: ' + esc(err.message);
        result.classList.add('show');
      });
  });

  ['dragenter', 'dragover'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('dropzone--over'); });
  });
  ['dragleave', 'drop'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('dropzone--over'); });
  });
  drop.addEventListener('drop', function (e) {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      fileInput.files = e.dataTransfer.files;
      fileInput.dispatchEvent(new Event('change'));
    }
  });

  /* ------------------------------------------------- synthetic test samples */
  var _seed = 42;
  function rand() { _seed = (_seed * 9301 + 49297) % 233280; return _seed / 233280; }
  function randn() {
    var u = Math.max(rand(), 1e-9), v = rand();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }
  function chirp(f0, f1, dur) {
    var n = Math.floor(dur * MODEL.sr), out = new Float32Array(n), phase = 0;
    for (var i = 0; i < n; i++) {
      var t = i / MODEL.sr;
      var f = f0 + (f1 - f0) * (t / dur);
      phase += 2 * Math.PI * f / MODEL.sr;
      out[i] = Math.sin(phase) * 0.5 * (1 - Math.cos(2 * Math.PI * i / (n - 1)));
    }
    return out;
  }
  function makeClip(species) {
    var n = MODEL.sr * 5, y = new Float32Array(n), i;
    for (i = 0; i < n; i++) y[i] = randn() * 0.05;
    function add(call, start) {
      var e = Math.min(n, start + call.length);
      for (var j = 0; j < e - start; j++) y[start + j] += call[j];
    }
    if (species === 'background') {
      for (i = 0; i < n; i++) y[i] += randn() * 0.3;
    } else if (species === 'blue_whale') {
      add(chirp(16, 19, 2.5), Math.floor(rand() * 2 * MODEL.sr));
    } else if (species === 'fin_whale') {
      for (var k = 0; k < 3; k++) add(chirp(28, 18, 1.0), Math.floor((0.3 + k * 1.5) * MODEL.sr));
    } else if (species === 'humpback_whale') {
      var t0 = 0;
      for (i = 0; i < 3; i++) {
        var d = 0.5 + rand() * 0.5;
        add(chirp(300, 1200, d), Math.floor(t0 * MODEL.sr)); t0 += d + 0.3;
      }
    } else if (species === 'killer_whale') {
      var t1 = 0;
      for (i = 0; i < 3; i++) {
        var d2 = 0.4 + rand() * 0.4;
        add(chirp(1000, 2000, d2), Math.floor(t1 * MODEL.sr)); t1 += d2 + 0.4;
      }
    } else if (species === 'bottlenose_dolphin') {
      var t2 = 0;
      for (i = 0; i < 3; i++) {
        var d3 = 0.3 + rand() * 0.4, m = Math.floor(d3 * MODEL.sr);
        var call = new Float32Array(m), f0 = 4000 + rand() * 2000;
        for (var q = 0; q < m; q++) {
          call[q] = Math.sin(2 * Math.PI * f0 * q / MODEL.sr) *
                    0.5 * (1 - Math.cos(2 * Math.PI * q / (m - 1)));
        }
        add(call, Math.floor(t2 * MODEL.sr)); t2 += d3 + 0.3;
      }
    }
    var max = 0;
    for (i = 0; i < n; i++) max = Math.max(max, Math.abs(y[i]));
    if (max > 0) for (i = 0; i < n; i++) y[i] = y[i] / max * 0.9;
    return y;
  }

  document.querySelectorAll('[data-sample]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (!MODEL) { verdict.innerHTML = 'The model is still loading. Please try again in a moment.'; result.classList.add('show'); return; }
      _seed = 42;
      runSignal(makeClip(btn.dataset.sample), MODEL.sr);
    });
  });

  /* ------------------------------------------------------------------ init */
  if (!MODEL) {
    verdict.innerHTML = 'The model could not be loaded. Please reload the page.';
    result.classList.add('show');
  } else {
    document.getElementById('ai-classes').textContent =
      MODEL.classes.map(function (c) { return c.replace(/_/g, ' '); }).join('  ·  ') +
      '  — ' + MODEL.bands.length + ' frequency bands, ' + MODEL.mean.length + ' features per window.';
  }
})();
