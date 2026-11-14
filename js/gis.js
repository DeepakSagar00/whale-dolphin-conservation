/* GIS Marine Map — visualisation of marine observations plus an on-map
   collection workflow for submitting new records. */
(function () {
  'use strict';

  var el = function (id) { return document.getElementById(id); };
  var esc = function (t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  var COLORS = {
    'Humpback whale': '#1b80c4',
    'Spinner dolphin': '#12a8b8',
    'Humpback Whale': '#1b80c4',
    'Spinner Dolphin': '#12a8b8'
  };
  var SUBMIT_COLOR = '#35d6c4';

  var state = {
    map: null,
    markerLayer: null,
    records: [],
    markers: [],
    layers: {},
    filter: { species: {}, region: '', from: '', to: '', q: '' },
    selected: null,
    collecting: false,
    fitted: false
  };

  function setText(id, value) {
    var node = el(id);
    if (node) node.textContent = value;
  }

  /* --------------------------------------------------------- geo helpers */
  function regionOf(lat, lon) {
    if (lat < -35) return 'Southern Ocean';
    if (lon < -30) return 'Atlantic';
    if (lon > 130) return 'Pacific';
    if (lat >= 5 && lat <= 25 && lon >= 50 && lon <= 78) return 'Arabian Sea';
    if (lat >= 5 && lat <= 23 && lon >= 79 && lon <= 98) return 'Bay of Bengal';
    return 'Indian Ocean';
  }

  /* ------------------------------------------------------------- data load */
  function mapDb(r) {
    return {
      id: r.id,
      species: r.common_name || 'Unidentified',
      scientific: r.scientific_name || '',
      lat: r.lat, lon: r.lon,
      date: r.event_date || '',
      count: r.individual_count,
      source: r.source || 'OBIS',
      region: regionOf(r.lat, r.lon),
      year: r.event_date ? parseInt(String(r.event_date).slice(0, 4), 10) : null,
      kind: 'db'
    };
  }

  function loadRecords() {
    var offline = false;
    return window.API.publicSightings({ limit: 4000 })
      .then(function (r) { return r.sightings || []; })
      .catch(function () {
        // the API is unreachable - fall back to the published database snapshot
        offline = true;
        return window.SITE_DATA.dbSightings || [];
      })
      .then(function (list) {
        state.records = list.map(mapDb);
        if (offline) { buildSpeciesList(); buildYearFilters(); render(); fitOnce(); return null; }
        return window.API.listObservations({ limit: 2000 }).catch(function () { return null; });
      })
      .then(function (obs) {
        if (obs && obs.observations) {
          obs.observations.forEach(function (o) {
            state.records.push({
              id: 'o' + o.id,
              obsId: o.id,
              species: o.common_name,
              scientific: o.scientific_name || '',
              lat: o.lat, lon: o.lon,
              date: o.observed_at,
              count: o.individuals,
              source: o.source || 'Platform submission',
              notes: o.notes,
              media: o.media_filename,
              confirmed: o.count_confirmed,
              region: regionOf(o.lat, o.lon),
              year: o.observed_at ? parseInt(String(o.observed_at).slice(0, 4), 10) : null,
              kind: 'submission'
            });
          });
        }
        buildSpeciesList();
        buildYearFilters();
        render();
        fitOnce();
      })
      .catch(function (err) {
        el('gis-count').textContent = 'unable to load records';
        if (window.SHELL) window.SHELL.setConnection(false, 'API offline');
      });
  }

  /* -------------------------------------------------------- filter widgets */
  function buildSpeciesList() {
    var counts = {};
    state.records.forEach(function (r) {
      counts[r.species] = (counts[r.species] || 0) + 1;
    });
    var host = el('gis-species-list');
    host.innerHTML = Object.keys(counts).sort().map(function (s) {
      var on = state.filter.species[s] !== false;
      var color = COLORS[s] || '#647d90';
      return '<label class="filterrow' + (on ? ' filterrow--on' : '') + '" data-species="' + esc(s) + '">' +
        '<input type="checkbox" ' + (on ? 'checked' : '') + '>' +
        '<span class="dot" style="background:' + color + '"></span>' +
        '<span>' + esc(s) + '</span><span class="n">' + counts[s] + '</span></label>';
    }).join('');

    Array.prototype.forEach.call(host.querySelectorAll('.filterrow'), function (row) {
      row.addEventListener('click', function () {
        var s = row.dataset.species;
        state.filter.species[s] = state.filter.species[s] === false;
        row.classList.toggle('filterrow--on', state.filter.species[s] !== false);
        row.querySelector('input').checked = state.filter.species[s] !== false;
        render();
      });
    });

    var sel = el('gis-species');
    sel.innerHTML = '<option value="">All species</option>' +
      Object.keys(counts).sort().map(function (s) {
        return '<option value="' + esc(s) + '">' + esc(s) + '</option>';
      }).join('');
  }

  function buildYearFilters() {
    var years = {};
    state.records.forEach(function (r) { if (r.year) years[r.year] = true; });
    var list = Object.keys(years).map(Number).sort(function (a, b) { return a - b; });
    ['gis-from', 'gis-to'].forEach(function (id) {
      var sel = el(id);
      var label = id === 'gis-from' ? 'From: any year' : 'To: any year';
      sel.innerHTML = '<option value="">' + label + '</option>' +
        list.map(function (y) { return '<option value="' + y + '">' + y + '</option>'; }).join('');
    });
  }

  function visibleRecords() {
    return state.records.filter(function (r) {
      if (state.filter.species[r.species] === false) return false;
      if (state.filter.region && r.region !== state.filter.region) return false;
      if (state.filter.from && r.year && r.year < parseInt(state.filter.from, 10)) return false;
      if (state.filter.to && r.year && r.year > parseInt(state.filter.to, 10)) return false;
      if (state.filter.q) {
        var hay = (r.species + ' ' + r.scientific + ' ' + r.region + ' ' + r.source).toLowerCase();
        if (hay.indexOf(state.filter.q.toLowerCase()) === -1) return false;
      }
      return true;
    });
  }

  /* -------------------------------------------------------------- rendering */
  function render() {
    if (!state.map) return;
    var list = visibleRecords();
    state.markerLayer.clearLayers();
    state.markers = [];

    list.forEach(function (r) {
      var color = r.kind === 'submission' ? SUBMIT_COLOR : (COLORS[r.species] || '#647d90');
      var mk = L.circleMarker([r.lat, r.lon], {
        radius: r.kind === 'submission' ? 6 : 4.5,
        color: '#ffffff', weight: 1,
        fillColor: color, fillOpacity: 0.92
      });
      mk.bindPopup(popupHtml(r));
      mk.on('click', function () { select(r, mk); });
      mk.addTo(state.markerLayer);
      state.markers.push({ rec: r, marker: mk });
    });

    el('gis-count').textContent = list.length.toLocaleString('en-US') + ' of ' +
      state.records.length.toLocaleString('en-US') + ' records shown';

    /* live context strip over the map */
    var species = {};
    var years = [];
    var sources = {};
    list.forEach(function (r) {
      species[r.species] = true;
      sources[r.source] = true;
      if (r.year) years.push(r.year);
    });
    years.sort(function (a, b) { return a - b; });
    setText('ms-records', list.length.toLocaleString('en-US'));
    setText('ms-species', Object.keys(species).length
      ? Object.keys(species).join(', ') : 'none');
    setText('ms-years', years.length ? years[0] + '–' + years[years.length - 1] : 'n/a');
    setText('ms-source', Object.keys(sources).join(', ') || 'n/a');

    var rows = list.slice(0, 300).map(function (r, i) {
      return '<tr class="row-click" data-i="' + i + '">' +
        '<td>' + esc(r.species) + (r.kind === 'submission' ? ' <span class="badge badge--info">new</span>' : '') + '</td>' +
        '<td>' + esc(r.date) + '</td>' +
        '<td class="mono">' + r.lat.toFixed(3) + '</td>' +
        '<td class="mono">' + r.lon.toFixed(3) + '</td>' +
        '<td class="num">' + (r.count == null ? '&ndash;' : r.count) + '</td>' +
        '<td><span class="badge ' + (r.kind === 'submission' ? 'badge--info' : 'badge--grey') + '">' + esc(r.source) + '</span></td>' +
        '</tr>';
    }).join('');
    el('gis-table').innerHTML = rows || '<tr><td colspan="6" class="empty">No records match the current filters.</td></tr>';

    Array.prototype.forEach.call(el('gis-table').querySelectorAll('tr[data-i]'), function (tr) {
      tr.addEventListener('click', function () {
        var item = state.markers[parseInt(tr.dataset.i, 10)];
        if (!item) return;
        state.map.setView(item.marker.getLatLng(), 6);
        item.marker.openPopup();
        select(item.rec, item.marker);
      });
    });
  }

  function popupHtml(r) {
    return '<strong>' + esc(r.species) + '</strong><br>' +
      (r.scientific ? '<em>' + esc(r.scientific) + '</em><br>' : '') +
      'Date: ' + esc(r.date) + '<br>' +
      'Position: ' + r.lat.toFixed(3) + '&deg;, ' + r.lon.toFixed(3) + '&deg;<br>' +
      'Individuals: ' + (r.count == null ? 'not recorded' : r.count) + '<br>' +
      'Region: ' + esc(r.region) + '<br>' +
      'Source: ' + esc(r.source);
  }

  function select(rec, marker) {
    state.selected = rec;
    el('gis-detail-panel').style.display = '';
    el('gis-detail-title').textContent = rec.species;
    el('gis-detail-sub').textContent = rec.scientific || rec.source;
    el('gis-detail').innerHTML =
      '<dl>' +
      '<div><dt>Date observed</dt><dd>' + esc(rec.date || 'not recorded') + '</dd></div>' +
      '<div><dt>Latitude</dt><dd>' + rec.lat.toFixed(4) + '&deg;</dd></div>' +
      '<div><dt>Longitude</dt><dd>' + rec.lon.toFixed(4) + '&deg;</dd></div>' +
      '<div><dt>Individuals</dt><dd>' + (rec.count == null ? 'not recorded' : rec.count) + '</dd></div>' +
      '<div><dt>Region</dt><dd>' + esc(rec.region) + '</dd></div>' +
      '<div><dt>Source</dt><dd>' + esc(rec.source) + '</dd></div>' +
      (rec.confirmed === false ? '<div><dt>Verification</dt><dd><span class="badge badge--vu">unverified count</span></dd></div>' : '') +
      (rec.notes ? '<div><dt>Notes</dt><dd style="text-align:left">' + esc(rec.notes) + '</dd></div>' : '') +
      (rec.media ? '<div><dt>Attachment</dt><dd>' + esc(rec.media) + '</dd></div>' : '') +
      '</dl>';
    if (marker) {
      marker.setStyle({ color: '#c0392b', weight: 2.5, radius: 8 });
      setTimeout(function () { marker.setStyle({ color: '#ffffff', weight: 1, radius: rec.kind === 'submission' ? 6 : 4.5 }); }, 2200);
    }
  }

  /* -------------------------------------------------------- collection mode */
  function startCollect() {
    state.collecting = true;
    el('gis-collect-panel').style.display = '';
    el('collect-step').textContent = 'Step 1 \u2014 click the map to place the record';
    el('btn-collect').classList.add('btn--active');
    el('btn-collect').textContent = 'Placing record\u2026';
    if (state.map) state.map.getContainer().style.cursor = 'crosshair';
  }

  function stopCollect() {
    state.collecting = false;
    el('gis-collect-panel').style.display = 'none';
    el('btn-collect').classList.remove('btn--active');
    el('btn-collect').textContent = '+ Add observation';
    if (state.map) state.map.getContainer().style.cursor = '';
  }

  function placePin(latlng) {
    el('cf-lat').value = latlng.lat.toFixed(4);
    el('cf-lon').value = latlng.lng.toFixed(4);
    el('collect-step').textContent = 'Step 2 \u2014 complete the record and store it';
    el('cf-date').focus();
    if (state.map) state.map.getContainer().style.cursor = '';
  }

  function validateCollect() {
    var ok = true;
    function mark(id, valid) {
      var field = el(id).closest('.field');
      if (field) field.classList.toggle('field--invalid', !valid);
      if (!valid) ok = false;
    }
    var lat = parseFloat(el('cf-lat').value);
    var lon = parseFloat(el('cf-lon').value);
    var date = el('cf-date').value;
    mark('cf-species', !!el('cf-species').value);
    mark('cf-lat', !isNaN(lat) && lat >= -90 && lat <= 90);
    mark('cf-lon', !isNaN(lon) && lon >= -180 && lon <= 180);
    mark('cf-date', !!date && !isNaN(Date.parse(date)));
    if (!ok) {
      showNotice('err', 'Please complete the highlighted fields before storing the record.');
      return false;
    }
    return true;
  }

  function showNotice(kind, msg) {
    var box = el('gis-notice');
    if (!box) {
      box = document.createElement('div');
      box.id = 'gis-notice';
      box.style.marginBottom = '12px';
      var body = el('gis-collect-panel').querySelector('.panel__body');
      body.insertBefore(box, body.firstChild);
    }
    box.className = 'notice notice--' + kind;
    box.textContent = msg;
    box.style.display = 'block';
  }

  function submitCollect(e) {
    e.preventDefault();
    if (!window.API.signedIn()) {
      showNotice('warn', 'Sign in with your researcher account to store an observation.');
      el('collect-auth').style.display = '';
      el('ca-user').focus();
      return;
    }
    if (!validateCollect()) return;
    var btn = el('collect-submit');
    btn.disabled = true;
    btn.textContent = 'Storing\u2026';

    var media = el('cf-media').files[0];
    var payload = {
      species: el('cf-species').value,
      lat: parseFloat(el('cf-lat').value),
      lon: parseFloat(el('cf-lon').value),
      observed_at: el('cf-date').value,
      individuals: parseInt(el('cf-count').value, 10) || 1,
      notes: el('cf-notes').value.trim(),
      media_type: media ? (media.type.indexOf('image') === 0 ? 'photo' : 'audio') : '',
      media_filename: media ? media.name : '',
      source: 'Platform submission',
      count_confirmed: el('cf-confirmed').checked
    };

    window.API.createObservation(payload).then(function (r) {
      btn.disabled = false;
      btn.textContent = 'Store observation';
      showNotice('ok', 'Observation stored in the platform database (record #' +
        (r.observation ? r.observation.id : '?') + '). It now appears on the map.');
      el('cf-notes').value = '';
      el('cf-media').value = '';
      stopCollect();
      return loadRecords();
    }).catch(function (err) {
      btn.disabled = false;
      btn.textContent = 'Store observation';
      showNotice('err', 'The record could not be stored: ' + err.message);
    });
  }

  /* --------------------------------------------------------------- filters */
  function initFilters() {
    el('gis-search').addEventListener('input', function () {
      state.filter.q = el('gis-search').value.trim();
      render();
    });
    el('gis-region').addEventListener('change', function () {
      state.filter.region = el('gis-region').value; render();
    });
    el('gis-species').addEventListener('change', function () {
      var v = el('gis-species').value;
      Object.keys(state.filter.species).forEach(function (k) { delete state.filter.species[k]; });
      if (v) state.filter.species[v] = true;
      buildSpeciesList();
      render();
    });
    el('gis-from').addEventListener('change', function () {
      state.filter.from = el('gis-from').value; render();
    });
    el('gis-to').addEventListener('change', function () {
      state.filter.to = el('gis-to').value; render();
    });
    el('gis-all').addEventListener('click', function () {
      state.filter.species = {};
      buildSpeciesList();
      render();
    });
  }

  function initMap() {
    state.map = L.map('map', { scrollWheelZoom: true }).setView([0, 60], 3);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18, attribution: '&copy; OpenStreetMap contributors'
    }).addTo(state.map);
    state.markerLayer = L.layerGroup().addTo(state.map);

    state.map.on('click', function (e) {
      if (state.collecting) placePin(e.latlng);
    });

    el('btn-collect').addEventListener('click', function () {
      if (state.collecting) stopCollect(); else startCollect();
    });
    el('collect-cancel').addEventListener('click', stopCollect);
    el('collect-form').addEventListener('submit', submitCollect);

    el('ca-login').addEventListener('click', function () {
      var btn = el('ca-login');
      btn.disabled = true;
      btn.textContent = 'Signing in\u2026';
      window.API.login(el('ca-user').value.trim(), el('ca-pass').value)
        .then(function () {
          btn.disabled = false;
          btn.textContent = 'Sign in';
          el('collect-auth').style.display = 'none';
          showNotice('ok', 'Signed in. Submit the observation to store it.');
          if (window.SHELL) window.SHELL.paintUser();
        })
        .catch(function (err) {
          btn.disabled = false;
          btn.textContent = 'Sign in';
          showNotice('err', 'Sign-in failed: ' + err.message +
            '. The demonstration account is researcher / researcher.');
        });
    });

    el('btn-fit').addEventListener('click', fitAll);
    el('map-fit').addEventListener('click', fitAll);
    el('map-recenter').addEventListener('click', function () {
      state.map.setView([2, 60], 3);
    });
    el('gis-detail-close').addEventListener('click', function () {
      el('gis-detail-panel').style.display = 'none';
    });
  }

  function fitAll() {
    var list = visibleRecords();
    if (!list.length || !state.map) return;
    var bounds = L.latLngBounds(list.map(function (r) { return [r.lat, r.lon]; }));
    state.map.fitBounds(bounds, { padding: [40, 40], maxZoom: 7 });
  }

  /* Fit the view to the data the first time it loads, so the map opens on the
     records rather than on an empty patch of ocean. */
  function fitOnce() {
    if (state.fitted) return;
    state.fitted = true;
    fitAll();
  }

  /* ------------------------------------------------------------------ init */
  document.addEventListener('DOMContentLoaded', function () {
    initMap();
    initFilters();

    // species options for the collection form
    var sel = el('cf-species');
    sel.innerHTML = '<option value="">Select a species</option>' +
      ['Humpback whale', 'Spinner dolphin', 'Blue whale', 'Fin whale',
       'Killer whale', 'Bottlenose dolphin'].map(function (s) {
        return '<option value="' + s + '">' + s + '</option>';
      }).join('');

    loadRecords();
  });
})();
