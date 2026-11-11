/* AI Species Identification page controller. */
(function () {
  'use strict';

  var el = function (id) { return document.getElementById(id); };
  var esc = function (t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };
  var MAX_BYTES = 8 * 1024 * 1024;

  var SPECIES_ID = {
    'blue_whale': 'blue-whale', 'fin_whale': 'fin-whale',
    'humpback_whale': 'humpback-whale', 'killer_whale': 'killer-whale',
    'bottlenose_dolphin': 'bottlenose-dolphin', 'spinner_dolphin': 'spinner-dolphin',
    'blue-whale': 'blue-whale', 'fin-whale': 'fin-whale',
    'humpback-whale': 'humpback-whale', 'killer-whale': 'killer-whale',
    'bottlenose-dolphin': 'bottlenose-dolphin', 'spinner-dolphin': 'spinner-dolphin'
  };

  function setApiStatus(online, detail) {
    var box = el('api-status');
    if (!box) return;
    box.className = 'notice ' + (online ? 'notice--ok' : 'notice--warn');
    box.innerHTML = online
      ? '<strong>Backend connected.</strong> ' + esc(detail || 'The classifier runs on the server.')
      : '<strong>Backend unreachable.</strong> ' + esc(detail ||
        'Image classification requires the server-side model.');
    box.style.display = 'block';
  }

  function renderBars(container, ranked) {
    container.innerHTML = ranked.map(function (r, i) {
      var pct = r.probability == null ? 0 : Math.round(r.probability * 100);
      return '<div class="bar-row' + (i === 0 ? ' top' : '') + '">' +
        '<span class="name">' + esc(r.species) + '</span>' +
        '<div class="bar-track"><div class="bar-fill"></div></div>' +
        '<span class="bar-val">' + pct + '%</span></div>';
    }).join('');
    Array.prototype.forEach.call(container.querySelectorAll('.bar-row'), function (row, i) {
      var pct = ranked[i].probability == null ? 0 : Math.round(ranked[i].probability * 100);
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { row.querySelector('.bar-fill').style.width = pct + '%'; });
      });
    });
  }

  function showResult(r) {
    el('id-empty').style.display = 'none';
    el('id-loading').style.display = 'none';
    el('id-result').style.display = 'block';
    el('id-species').textContent = r.predicted_species;
    el('id-confidence').textContent = r.confidence == null ? '' :
      Math.round(r.confidence * 100) + '% confidence';
    el('id-source').textContent = r.source || '';
    el('id-latin').textContent = r.scientific_name || '';
    el('id-note').textContent = r.note || '';
    renderBars(el('id-bars'), r.ranked || []);
    var sid = SPECIES_ID[r.species_key];
    el('id-species-link').href = sid ? 'species-detail.html?id=' + sid : 'species.html';
  }

  function showError(msg) {
    el('id-empty').style.display = 'none';
    el('id-loading').style.display = 'none';
    el('id-result').style.display = 'block';
    el('id-species').textContent = 'Identification unavailable';
    el('id-confidence').textContent = '';
    el('id-source').textContent = '';
    el('id-latin').textContent = '';
    el('id-bars').innerHTML = '';
    el('id-note').textContent = msg;
  }

  function handleFile(file) {
    if (!file) return;
    if (!/^image\//.test(file.type) && !/\.(jpe?g|png|webp|bmp|gif|tiff?)$/i.test(file.name)) {
      showError('Unsupported file type. Please choose an image file.');
      return;
    }
    if (file.size > MAX_BYTES) {
      showError('That image is ' + (file.size / 1048576).toFixed(1) + ' MB. The limit is 8 MB.');
      return;
    }

    var url = URL.createObjectURL(file);
    el('id-preview').innerHTML = '<img src="' + url + '" alt="Uploaded specimen">';

    el('id-empty').style.display = 'none';
    el('id-result').style.display = 'none';
    el('id-loading').style.display = 'block';

    window.API.identifyImage(file).then(function (r) {
      r.source = 'server (FastAPI + trained classifier)';
      showResult(r);
    }).catch(function (err) {
      showError('The image could not be classified: ' + err.message);
    });
  }

  var REFERENCE = [
    { key: 'blue_whale', label: 'Blue whale', file: 'blue_whale_000.jpg' },
    { key: 'blue_whale', label: 'Blue whale', file: 'blue_whale_001.jpg' },
    { key: 'fin_whale', label: 'Fin whale', file: 'fin_whale_000.jpg' },
    { key: 'fin_whale', label: 'Fin whale', file: 'fin_whale_001.jpg' },
    { key: 'humpback_whale', label: 'Humpback whale', file: 'humpback_whale_000.jpg' },
    { key: 'humpback_whale', label: 'Humpback whale', file: 'humpback_whale_001.jpg' },
    { key: 'killer_whale', label: 'Killer whale', file: 'killer_whale_000.jpg' },
    { key: 'killer_whale', label: 'Killer whale', file: 'killer_whale_001.jpg' },
    { key: 'bottlenose_dolphin', label: 'Bottlenose dolphin', file: 'bottlenose_dolphin_000.jpg' },
    { key: 'bottlenose_dolphin', label: 'Bottlenose dolphin', file: 'bottlenose_dolphin_001.jpg' },
    { key: 'spinner_dolphin', label: 'Spinner dolphin', file: 'spinner_dolphin_000.jpg' },
    { key: 'spinner_dolphin', label: 'Spinner dolphin', file: 'spinner_dolphin_001.jpg' }
  ];

  function renderReference() {
    var host = el('id-reference');
    if (!host) return;
    host.innerHTML = REFERENCE.map(function (r) {
      return '<button class="card ref-card" type="button" data-file="' + r.file + '" ' +
        'style="border:none;padding:0;cursor:pointer;text-align:left">' +
        '<img src="samples/images/' + r.file + '" alt="' + esc(r.label) + '" ' +
        'style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:12px">' +
        '<div style="padding:10px 12px"><strong style="font-size:.9rem">' + esc(r.label) +
        '</strong></div></button>';
    }).join('');
    Array.prototype.forEach.call(host.querySelectorAll('.ref-card'), function (btn) {
      btn.addEventListener('click', function () {
        var file = btn.dataset.file;
        fetch('samples/images/' + file).then(function (r) { return r.blob(); })
          .then(function (blob) {
            handleFile(new File([blob], file, { type: 'image/jpeg' }));
            el('analysis-section') && el('analysis-section').scrollIntoView({ behavior: 'smooth' });
          });
      });
    });
  }

  /* ---------------- identification history ---------------- */
  function loadHistory() {
    var host = el('id-history');
    if (!host) return;
    if (!window.API || !window.API.isOnline()) {
      host.innerHTML = '<tr><td colspan="4" class="empty">Sign in to load your identification history.</td></tr>';
      return;
    }
    window.API.imageHistory().then(function (r) {
      var list = (r && r.predictions) || [];
      host.innerHTML = list.map(function (p) {
        return '<tr><td>' + esc(p.filename || 'image') + '</td>' +
          '<td>' + esc(p.predicted_species || '-') + '</td>' +
          '<td class="num">' + (p.confidence == null ? '&ndash;' : Math.round(p.confidence * 100) + '%') + '</td>' +
          '<td>' + esc(String(p.created_at || '').slice(0, 19).replace('T', ' ')) + '</td></tr>';
      }).join('') || '<tr><td colspan="4" class="empty">No identifications recorded yet.</td></tr>';
    }).catch(function () {
      host.innerHTML = '<tr><td colspan="4" class="empty">Sign in to load your identification history.</td></tr>';
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var drop = el('id-drop');
    var input = el('id-file');
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

    var toggle = el('id-history-toggle');
    var panel = el('id-history-panel');
    if (toggle && panel) {
      toggle.addEventListener('click', function () {
        var open = panel.style.display === 'none' || !panel.style.display;
        panel.style.display = open ? '' : 'none';
        toggle.textContent = open ? 'Hide history' : 'Show history';
        if (open) loadHistory();
      });
    }
    var close = el('id-history-close');
    if (close && panel) {
      close.addEventListener('click', function () {
        panel.style.display = 'none';
        if (toggle) toggle.textContent = 'Show history';
      });
    }

    renderReference();

    window.API.health().then(function (h) {
      if (h) setApiStatus(true, 'The classifier and the reference image set run on the platform API.');
      else setApiStatus(false, 'The API could not be reached, so image identification is currently ' +
        'unavailable. The rest of the platform still works.');
    });
  });
})();
