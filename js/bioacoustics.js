/* Marine Bioacoustics page controller.
   Uploads a recording, analyses it (server-side when the API is reachable,
   otherwise with the identical model in the browser), renders the waveform and
   spectrogram, and drives the communication explorer and simulator. */
(function () {
  'use strict';

  var el = function (id) { return document.getElementById(id); };
  var esc = function (t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  var MAX_BYTES = 25 * 1024 * 1024;
  var ACCEPT = ['audio/wav', 'audio/x-wav', 'audio/wave', 'audio/flac', 'audio/x-flac',
    'audio/mpeg', 'audio/mp3', 'audio/ogg', 'audio/aiff', 'audio/x-aiff', 'audio/webm', ''];

  var state = {
    file: null,
    audioUrl: null,
    audioBuffer: null,
    analysis: null,
    busy: false
  };

  /* ------------------------------------------------------------ status banner */
  function setApiStatus(online, detail) {
    var box = el('api-status');
    if (!box) return;
    box.className = 'notice ' + (online ? 'notice--ok' : 'notice--warn');
    box.innerHTML = online
      ? '<strong>Backend connected.</strong> ' + esc(detail || 'Analysis is running on the server.')
      : '<strong>Backend unreachable.</strong> ' + esc(detail ||
        'Analysis is being performed entirely in your browser with the same trained model.');
    box.style.display = 'block';
  }

  /* -------------------------------------------------------------- rendering */
  function drawWaveform(canvas, wave) {
    if (!canvas || !wave || !wave.min) return;
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.getBoundingClientRect();
    var w = Math.max(1, Math.round(rect.width));
    var h = Math.max(1, Math.round(rect.height));
    canvas.width = w * dpr; canvas.height = h * dpr;
    var ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#0b1f3a';
    ctx.fillRect(0, 0, w, h);
    ctx.strokeStyle = 'rgba(255,255,255,.12)';
    ctx.beginPath(); ctx.moveTo(0, h / 2); ctx.lineTo(w, h / 2); ctx.stroke();

    var n = wave.min.length;
    ctx.strokeStyle = '#2dd4bf';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (var i = 0; i < n; i++) {
      var x = (i / (n - 1)) * w;
      var y1 = h / 2 - wave.max[i] * (h / 2) * 0.94;
      var y2 = h / 2 - wave.min[i] * (h / 2) * 0.94;
      ctx.moveTo(x, y1); ctx.lineTo(x, y2);
    }
    ctx.stroke();
  }

  function drawSpectrogram(canvas, spec) {
    if (!canvas || !spec || !spec.mels) return;
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.getBoundingClientRect();
    var w = Math.max(1, Math.round(rect.width));
    var h = Math.max(1, Math.round(rect.height));
    canvas.width = w * dpr; canvas.height = h * dpr;
    var ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);

    var mels = spec.mels, frames = mels[0].length;
    var max = 0;
    mels.forEach(function (row) { row.forEach(function (v) { if (v > max) max = v; }); });
    if (!max) max = 1;

    // draw into an offscreen canvas then scale (low -> high frequency upwards)
    var off = document.createElement('canvas');
    off.width = frames; off.height = mels.length;
    var octx = off.getContext('2d');
    var img = octx.createImageData(frames, mels.length);
    for (var b = 0; b < mels.length; b++) {
      var row = mels[b];
      var y = mels.length - 1 - b;           // low frequencies at the bottom
      for (var f = 0; f < frames; f++) {
        var v = Math.min(1, row[f] / max);
        var idx = (y * frames + f) * 4;
        img.data[idx] = Math.round(255 * Math.min(1, Math.max(0, (v - 0.25) / 0.75)));
        img.data[idx + 1] = Math.round(255 * Math.min(1, Math.max(0, (v - 0.05) / 0.95)) * 0.85);
        img.data[idx + 2] = Math.round(255 * Math.min(1, Math.max(0, (v - 0.0) / 0.6)));
        img.data[idx + 3] = 255;
      }
    }
    octx.putImageData(img, 0, 0);
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(off, 0, 0, w, h);

    ctx.strokeStyle = 'rgba(255,255,255,.18)';
    ctx.fillStyle = 'rgba(255,255,255,.8)';
    ctx.font = '11px system-ui, sans-serif';
    ctx.fillText('8 kHz', 6, 14);
    ctx.fillText('4 kHz', 6, h / 2);
    ctx.fillText('0 Hz', 6, h - 6);
  }

  function renderBars(container, probs) {
    container.innerHTML = probs.map(function (p, i) {
      var pct = Math.round(p.probability * 100);
      return '<div class="bar-row' + (i === 0 ? ' top' : '') + '">' +
        '<span class="name">' + esc(String(p.species).replace(/_/g, ' ')) + '</span>' +
        '<div class="bar-track"><div class="bar-fill"></div></div>' +
        '<span class="bar-val">' + pct + '%</span></div>';
    }).join('');
    Array.prototype.forEach.call(container.querySelectorAll('.bar-row'), function (row, i) {
      var pct = Math.round(probs[i].probability * 100);
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { row.querySelector('.bar-fill').style.width = pct + '%'; });
      });
    });
  }

  function setText(id, value) {
    var node = el(id);
    if (node) node.textContent = value;
  }

  function renderAnalysis(a, source) {
    el('analysis-empty').style.display = 'none';
    el('analysis-result').style.display = 'block';

    setText('a-species', a.detected_species);
    setText('a-confidence', Math.round(a.confidence * 100) + '%');
    setText('a-source', source);

    renderBars(el('a-bars'), a.probabilities);

    var p = a.pattern || {};
    setText('a-pattern-label', p.label || '-');
    setText('a-pattern-desc', p.description || p.short_description || '');
    setText('a-pattern-interpretation', p.interpretation ||
      'Research-based interpretation: call meaning is an active area of research and is not ' +
      'established for individual calls.');
    setText('a-dom-freq', (p.dominant_frequency_hz != null ? p.dominant_frequency_hz : '-') + ' Hz');
    setText('a-centroid', (p.spectral_centroid_hz != null ? p.spectral_centroid_hz : '-') + ' Hz');
    setText('a-bandwidth', (p.bandwidth_hz != null ? p.bandwidth_hz : '-') + ' Hz');
    setText('a-pulse', (p.pulse_rate_hz != null ? p.pulse_rate_hz : '-') + ' Hz');
    setText('a-flatness', p.spectral_flatness != null ? p.spectral_flatness : '-');
    setText('a-tonality', p.tonality != null ? p.tonality : '-');
    setText('a-snr', a.snr_db != null ? a.snr_db + ' dB' : '-');
    setText('a-duration', a.duration_seconds != null ? a.duration_seconds + ' s' : '-');
    setText('a-window', a.window_seconds != null ? a.window_seconds + ' s' : '-');
    setText('a-samplerate', a.sample_rate != null ? (a.sample_rate / 1000).toFixed(1) + ' kHz' : '-');

    if (a.spectrogram) drawSpectrogram(el('a-spectrogram'), a.spectrogram);
    if (a.waveform) drawWaveform(el('a-waveform'), a.waveform);
  }

  function showError(msg) {
    el('analysis-empty').style.display = 'none';
    el('analysis-result').style.display = 'block';
    el('a-species').textContent = 'Analysis unavailable';
    el('a-confidence').textContent = '-';
    el('a-bars').innerHTML = '';
    el('a-pattern-label').textContent = '-';
    el('a-pattern-desc').textContent = msg;
    el('a-pattern-interpretation').textContent = '';
  }

  /* -------------------------------------------------------------- decoding */
  function decode(file) {
    return file.arrayBuffer().then(function (buf) {
      var AC = window.AudioContext || window.webkitAudioContext;
      var ctx = new AC();
      return ctx.decodeAudioData(buf).then(function (audio) {
        ctx.close();
        return audio;
      });
    });
  }

  /* ------------------------------------------------------ local analysis */
  function analyseLocally(file) {
    return decode(file).then(function (audio) {
      state.audioBuffer = audio;
      var samples = audio.getChannelData(0);
      var x = window.DSP.resample(samples, audio.sampleRate, window.MODEL.sr);
      var window5 = x.subarray(0, Math.min(x.length, Math.round(window.MODEL.sr * 5)));
      if (window5.length < 1024) {
        var pad = new Float32Array(1024);
        pad.set(window5);
        window5 = pad;
      }
      var feats = window.DSP.extractFeatures(window5);
      var ranked = window.DSP.classify(feats);
      var pattern = window.DSP.analysePattern(window5);
      var spec = window.DSP.spectrogram(window5, window.MODEL, 48, 300);
      var wave = window.DSP.waveform(window5, 320);

      var energy = spec.mels.map(function (r) {
        return r.reduce(function (a, c) { return a + c; }, 0) / r.length;
      });
      var sorted = energy.slice().sort(function (a, b) { return a - b; });
      var lo = sorted[Math.floor(sorted.length * 0.1)];
      var hi = sorted[Math.floor(sorted.length * 0.95)];
      var snr = Math.round(10 * Math.log10((hi + 1e-9) / (lo + 1e-9)) * 100) / 100;

      return {
        detected_species: String(ranked[0].species).replace(/_/g, ' '),
        confidence: Math.round(ranked[0].probability * 10000) / 10000,
        probabilities: ranked.map(function (r) {
          return { species: String(r.species).replace(/_/g, ' '), probability: r.probability };
        }),
        pattern: Object.assign({}, pattern, {
          description: window.DSP.PATTERN_INFO[pattern.pattern][1],
          interpretation: 'Research-based interpretation: the semantic content of individual ' +
            'calls is not established. The pattern label above describes the measured ' +
            'acoustic structure, not a decoded message.'
        }),
        snr_db: snr,
        duration_seconds: Math.round(audio.duration * 1000) / 1000,
        sample_rate: audio.sampleRate,
        window_seconds: Math.min(5, audio.duration),
        spectrogram: spec,
        waveform: wave
      };
    });
  }

  /* ---------------------------------------------------------- API analysis */
  function analyseViaApi(file) {
    return window.API.analyzeAudio(file).then(function (a) {
      return { analysis: a, source: 'server (FastAPI + trained model)' };
    });
  }

  function runAnalysis(file) {
    if (state.busy) return;
    state.busy = true;
    el('analysis-empty').style.display = 'none';
    el('analysis-loading').style.display = 'block';

    var done = function () {
      el('analysis-loading').style.display = 'none';
      state.busy = false;
    };

    analyseViaApi(file)
      .then(function (r) {
        renderAnalysis(r.analysis, r.source);
        done();
      })
      .catch(function (err) {
        // fall back to the identical model running in the browser
        analyseLocally(file).then(function (a) {
          renderAnalysis(a, 'browser (local model - API unavailable)');
          setApiStatus(false, 'The server could not be reached, so the same trained model was ' +
            'applied locally in your browser. Results are equivalent.');
        }).catch(function (e2) {
          showError('Could not analyse this recording: ' + e2.message);
        }).then(done);
      });
  }

  /* ------------------------------------------------------------ file input */
  function handleFile(file) {
    if (!file) return;
    var name = file.name.toLowerCase();
    var okExt = /\.(wav|flac|ogg|oga|mp3|aiff|aif|au|m4a|webm)$/.test(name);
    if (!okExt) {
      showError('Unsupported file type. Please choose a WAV, FLAC, OGG, MP3 or AIFF recording.');
      return;
    }
    if (file.size > MAX_BYTES) {
      showError('That file is ' + (file.size / 1048576).toFixed(1) +
        ' MB. The limit is 25 MB.');
      return;
    }
    if (file.size < 1024) {
      showError('That file is too short to analyse.');
      return;
    }

    state.file = file;
    el('file-meta').style.display = 'grid';
    el('file-name').textContent = file.name;
    el('file-size').textContent = (file.size / 1024).toFixed(0) + ' KB';

    if (state.audioUrl) URL.revokeObjectURL(state.audioUrl);
    state.audioUrl = URL.createObjectURL(file);
    el('player').src = state.audioUrl;
    el('player-wrap').style.display = 'block';

    decode(file).then(function (audio) {
      state.audioBuffer = audio;
      setText('file-duration', audio.duration.toFixed(2) + ' s');
      setText('file-rate', (audio.sampleRate / 1000).toFixed(1) + ' kHz');
      setText('file-channels', audio.numberOfChannels === 1 ? 'mono' : 'stereo');
    }).catch(function () {
      setText('file-duration', 'unknown');
    });

    runAnalysis(file);
  }

  /* ------------------------------------------------------ explorer samples */
  function renderSamples(manifest) {
    var host = el('sample-list');
    if (!host) return;
    var labels = {
      blue_whale: 'Blue whale', fin_whale: 'Fin whale',
      humpback_whale: 'Humpback whale', killer_whale: 'Killer whale',
      bottlenose_dolphin: 'Bottlenose dolphin', background: 'Ship noise only'
    };
    var order = ['blue_whale', 'fin_whale', 'humpback_whale', 'killer_whale',
      'bottlenose_dolphin', 'background'];
    var html = '';
    order.forEach(function (key) {
      var files = (manifest.files && manifest.files[key]) || [];
      if (!files.length) return;
      var src = 'samples/audio/' + files[0].file;
      html += '<article class="sample-card" data-key="' + key + '">' +
        '<button class="sample-card__play" type="button" data-src="' + src + '" ' +
          'aria-label="Play ' + esc(labels[key]) + ' sample">&#9654;</button>' +
        '<div><h4>' + esc(labels[key]) + '</h4>' +
        '<p>' + esc(key.replace(/_/g, ' ')) + ' &middot; ' + files.length +
          ' reference recordings</p></div>' +
        '<audio class="sample-card__audio" preload="none" src="' + src + '"></audio>' +
        '</article>';
    });
    host.innerHTML = html;

    Array.prototype.forEach.call(host.querySelectorAll('.sample-card'), function (card) {
      var audio = card.querySelector('.sample-card__audio');
      var btn = card.querySelector('.sample-card__play');
      var src = audio.getAttribute('src');
      var filename = src.split('/').pop();

      btn.addEventListener('click', function () {
        if (!audio.paused) { audio.pause(); btn.innerHTML = '&#9654;'; }
        else {
          Array.prototype.forEach.call(host.querySelectorAll('.sample-card__audio'), function (a) {
            a.pause();
          });
          Array.prototype.forEach.call(host.querySelectorAll('.sample-card__play'), function (b) {
            b.innerHTML = '&#9654;';
          });
          audio.play();
          btn.innerHTML = '&#10073;&#10073;';
        }
      });
      audio.addEventListener('ended', function () { btn.innerHTML = '&#9654;'; });

      card.querySelector('h4').addEventListener('click', function () {
        fetch(src).then(function (r) { return r.blob(); }).then(function (blob) {
          var f = new File([blob], filename, { type: 'audio/wav' });
          handleFile(f);
          el('analysis-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
      });
    });
  }

  /* ----------------------------------------------------------- simulator */
  var SIM_LOCAL = {
    whale: {
      blue_whale: { name: 'Blue whale', latin: 'Balaenoptera musculus', band: [10, 40],
        rate: 0.3, structure: 'Long, repeated D-shaped sweeps, spaced by long silences.',
        fns: ['Long-range contact between animals separated by tens of kilometres',
              'Advertising of feeding grounds to distant conspecifics',
              'Maintaining group cohesion across a feeding aggregation'],
        notes: 'Blue whale calls propagate over hundreds of kilometres through the deep sound ' +
               'channel and are among the loudest sounds made by any animal.' },
      fin_whale: { name: 'Fin whale', latin: 'Balaenoptera physalus', band: [15, 100],
        rate: 0.5, structure: 'Sweeps followed by a downsweep, then a broadband pulse.',
        fns: ['Long-range contact across feeding areas',
              'Coordinating group spacing while travelling',
              'Sharing the location of prey patches'],
        notes: 'The 20 Hz fin whale call is the lowest-frequency reliably detected call of any ' +
               'large whale and travels considerable distances.' },
      humpback_whale: { name: 'Humpback whale', latin: 'Megaptera novaeangliae', band: [80, 4000],
        rate: 1.0, structure: 'A song of repeated phrases, each built from several units, ' +
        'repeated for many minutes and revised through a season.',
        fns: ['Attracting a mate at breeding grounds',
              'Defending a mate against competing males',
              'Maintaining group cohesion while feeding'],
        notes: 'Humpback song structure changes progressively through the breeding season and ' +
               'songs are heard over hundreds of kilometres.' },
      killer_whale: { name: 'Killer whale', latin: 'Orcinus orca', band: [100, 5000],
        rate: 2.0, structure: 'Short, discrete calls with a distinctive contour, used in ' +
        'call-and-response.',
        fns: ['Individual recognition of group members (dialects)',
              'Coordinating foraging behaviour',
              'Maintaining cohesion while travelling and feeding'],
        notes: 'Each resident population has a stable vocal dialect, and calves inherit their ' +
               'group\'s call repertoire.' }
    },
    dolphin: {
      bottlenose_dolphin: { name: 'Bottlenose dolphin', latin: 'Tursiops truncatus',
        band: [2000, 20000], rate: 8.0,
        structure: 'Signature whistles with a narrow, frequency-modulated contour, plus ' +
          'burst-pulsed clicks in echolocation.',
        fns: ['Signature whistle used to call a specific individual by name',
              'Burst-pulsed clicks for echolocation and prey capture',
              'Squawks and whistles in social and aggressive contexts'],
        notes: 'Each bottlenose dolphin develops a signature whistle that other individuals ' +
               'learn to associate with that specific animal.' },
      spinner_dolphin: { name: 'Spinner dolphin', latin: 'Stenella longirostris',
        band: [5000, 25000], rate: 12.0,
        structure: 'Highly repetitive echolocation clicks with a distinctive whistle that rises ' +
          'and falls in pitch.',
        fns: ['Echolocation during deep off-shore foraging at night',
              'Whistle used for contact while travelling in large groups',
              'Synchronised group movement in large pods'],
        notes: 'Spinner dolphins rest in sheltered bays by day and move offshore to feed at ' +
               'night, when their echolocation click rates rise sharply.' }
    }
  };

  function pseudo(seed) {
    var x = Math.sin(seed * 12.9898) * 43758.5453;
    return x - Math.floor(x);
  }

  function simulateLocally(group, speciesKey, turns) {
    var p = SIM_LOCAL[group][speciesKey];
    var utterances = [];
    for (var i = 0; i < turns; i++) {
      var r = pseudo(i * 7.13 + 3), r2 = pseudo(i * 3.77 + 1);
      var callType = group === 'dolphin'
        ? ['signature whistle', 'burst-pulsed click train', 'social whistle',
           'echolocation click train'][Math.floor(r * 4) % 4]
        : ['low-frequency sweep', 'song phrase', 'contact call',
           'multi-unit phrase'][Math.floor(r * 4) % 4];
      var fLo = p.band[0] * (0.85 + 0.3 * r), fHi = p.band[1] * (0.85 + 0.3 * r2);
      var dur = (callType.indexOf('click') > -1) ? 0.4 + 2.6 * r2
        : (callType.indexOf('phrase') > -1 ? 3 + 9 * r : 1 + 4 * r);
      var desc = callType.indexOf('click') > -1
        ? 'A train of short broadband impulses spaced at roughly ' + Math.round(p.rate) + '-' +
          Math.round(p.rate * 2) + ' pulses per second, centred near ' + Math.round(fLo) +
          '-' + Math.round(fHi) + ' Hz.'
        : callType.indexOf('phrase') > -1
          ? 'A structured phrase of several units spanning roughly ' + Math.round(fLo) + '-' +
            Math.round(fHi) + ' Hz, repeated several times in succession.'
          : 'A swept tone whose contour moves between approximately ' + Math.round(fLo) +
            ' and ' + Math.round(fHi) + ' Hz.';
      utterances.push({
        turn: i + 1,
        speaker: i % 2 === 0 ? 'Animal A' : 'Animal B',
        call_type: callType,
        frequency_hz: Math.round(fLo) + '-' + Math.round(fHi) + ' Hz',
        duration_s: Math.round(dur * 100) / 100,
        acoustic_description: desc,
        likely_function: p.fns[Math.floor(r2 * p.fns.length) % p.fns.length],
        basis: 'Drawn from published acoustic parameters for this species; not a decoded message.'
      });
    }
    return {
      group: group, species: speciesKey, species_name: p.name, scientific_name: p.latin,
      acoustic_profile: { call_band_hz: p.band, pulse_rate_hz: p.rate, structure: p.structure },
      utterances: utterances,
      scientific_context: p.notes,
      documented_functions: p.fns,
      disclaimer: 'AI-GENERATED EDUCATIONAL SIMULATION. This sequence was composed from ' +
        'published acoustic parameters for the species. It is not a recording, not a decoding ' +
        'of real animal communication, and no sentence content is claimed. The semantic ' +
        'meaning of individual calls remains an active area of research.',
      generator: 'rule-based acoustic model + research-grounded synthesis'
    };
  }

  function renderSimulation(sim, source) {
    el('sim-empty').style.display = 'none';
    el('sim-result').style.display = 'block';
    el('sim-species').textContent = sim.species_name;
    el('sim-latin').textContent = sim.scientific_name;
    el('sim-source').textContent = source;
    el('sim-structure').textContent = sim.acoustic_profile.structure;
    el('sim-band').textContent = sim.acoustic_profile.call_band_hz[0] + '-' +
      sim.acoustic_profile.call_band_hz[1] + ' Hz';
    el('sim-rate').textContent = sim.acoustic_profile.pulse_rate_hz + ' per second';
    el('sim-context').textContent = sim.scientific_context;
    el('sim-disclaimer').textContent = sim.disclaimer;

    el('sim-utterances').innerHTML = sim.utterances.map(function (u) {
      return '<article class="utterance">' +
        '<div class="utterance__head"><span class="utterance__turn">Turn ' + u.turn + '</span>' +
        '<span class="utterance__speaker">' + esc(u.speaker) + '</span>' +
        '<span class="badge badge--info">' + esc(u.call_type) + '</span></div>' +
        '<p class="utterance__desc">' + esc(u.acoustic_description) + '</p>' +
        '<dl class="utterance__meta">' +
          '<div><dt>Frequency</dt><dd>' + esc(u.frequency_hz) + '</dd></div>' +
          '<div><dt>Duration</dt><dd>' + u.duration_s + ' s</dd></div>' +
          '<div><dt>Likely function</dt><dd>' + esc(u.likely_function) + '</dd></div>' +
        '</dl>' +
        '<p class="utterance__basis">' + esc(u.basis) + '</p>' +
        '</article>';
    }).join('');

    el('sim-functions').innerHTML = sim.documented_functions.map(function (f) {
      return '<li>' + esc(f) + '</li>';
    }).join('');
  }

  function populateSimulator() {
    var speciesSel = el('sim-species');
    var groupSel = el('sim-group');
    function fill() {
      var g = groupSel.value;
      speciesSel.innerHTML = Object.keys(SIM_LOCAL[g]).map(function (k) {
        return '<option value="' + k + '">' + esc(SIM_LOCAL[g][k].name) + '</option>';
      }).join('');
    }
    groupSel.addEventListener('change', fill);
    fill();

    el('sim-run').addEventListener('click', function () {
      var g = groupSel.value, s = speciesSel.value;
      var turns = parseInt(el('sim-turns').value, 10) || 6;
      el('sim-empty').style.display = 'none';
      el('sim-result').style.display = 'block';
      el('sim-species').textContent = 'Generating...';
      window.API.simulate(g, s, turns).then(function (sim) {
        renderSimulation(sim, 'server (FastAPI)');
      }).catch(function () {
        renderSimulation(simulateLocally(g, s, turns), 'browser (local rule-based model)');
      });
    });
  }

  /* ----------------------------------------------------------------- init */
  document.addEventListener('DOMContentLoaded', function () {
    var drop = el('bio-drop');
    var input = el('bio-file');

    input.addEventListener('change', function () { handleFile(input.files[0]); });
    ['dragenter', 'dragover'].forEach(function (ev) {
      drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('dropzone--over'); });
    });
    ['dragleave', 'drop'].forEach(function (ev) {
      drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('dropzone--over'); });
    });
    drop.addEventListener('drop', function (e) {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
    });

    populateSimulator();

    fetch('samples/sample_manifest.json').then(function (r) { return r.json(); })
      .then(renderSamples).catch(function () {
        el('sample-list').innerHTML = '<p class="muted">Sample recordings are not available ' +
          'in this build.</p>';
      });

    window.API.health().then(function (h) {
      if (h) setApiStatus(true, 'Analysis runs on the FastAPI service with the trained model ' +
        'and every result is stored in the platform database.');
      else setApiStatus(false, 'The server could not be reached. Analysis will be performed ' +
        'locally in your browser using the same trained model.');
    });

    window.addEventListener('resize', function () {
      if (state.analysis) {
        if (state.analysis.spectrogram) drawSpectrogram(el('a-spectrogram'), state.analysis.spectrogram);
        if (state.analysis.waveform) drawWaveform(el('a-waveform'), state.analysis.waveform);
      }
    });
  });
})();
