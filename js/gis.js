/* GIS Marine Explorer - interactive map, filters, layer controls and record table */
(function () {
  'use strict';
  var ALL = window.SITE_DATA.sightings;
  var esc = window.SITE.escapeHtml;

  var speciesSel = document.getElementById('gis-species');
  var regionSel = document.getElementById('gis-region');
  var fromSel = document.getElementById('gis-from');
  var toSel = document.getElementById('gis-to');
  var tableBody = document.getElementById('gis-table');
  var countEl = document.getElementById('gis-count');
  var resetBtn = document.getElementById('gis-reset');

  var COLORS = { 'humpback-whale': '#1b6ca8', 'spinner-dolphin': '#17a2b8' };
  var LABELS = { 'humpback-whale': 'Humpback whale', 'spinner-dolphin': 'Spinner dolphin' };

  /* ---- build filter options ---- */
  var speciesIds = {};
  var years = {};
  ALL.forEach(function (s) {
    speciesIds[s.speciesId] = LABELS[s.speciesId] || s.species;
    var y = parseInt(s.date.slice(0, 4), 10);
    if (!isNaN(y)) years[y] = true;
  });
  Object.keys(speciesIds).forEach(function (id) {
    var o = document.createElement('option');
    o.value = id; o.textContent = speciesIds[id];
    speciesSel.appendChild(o);
  });
  var yearList = Object.keys(years).map(Number).sort(function (a, b) { return a - b; });
  yearList.forEach(function (y) {
    [fromSel, toSel].forEach(function (sel) {
      var o = document.createElement('option');
      o.value = y; o.textContent = y;
      sel.appendChild(o);
    });
  });

  /* ---- region classifier from coordinates ---- */
  function regionOf(lat, lon) {
    if (lat < -35) return 'Southern Ocean';
    if (lon < -30) return 'Atlantic';
    if (lon > 130) return 'Pacific';
    if (lat >= 5 && lat <= 25 && lon >= 50 && lon <= 78) return 'Arabian Sea';
    if (lat >= 5 && lat <= 23 && lon >= 79 && lon <= 98) return 'Bay of Bengal';
    return 'Indian Ocean';
  }

  /* ---- map setup ---- */
  var map = L.map('map', { scrollWheelZoom: true }).setView([4, 62], 3);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  var markerLayer = L.layerGroup().addTo(map);
  var densityLayer = L.layerGroup();
  var markers = [];

  function filtered() {
    var sp = speciesSel.value;
    var rg = regionSel.value;
    var from = fromSel.value ? parseInt(fromSel.value, 10) : null;
    var to = toSel.value ? parseInt(toSel.value, 10) : null;

    return ALL.filter(function (s) {
      if (sp && s.speciesId !== sp) return false;
      if (rg && regionOf(s.lat, s.lon) !== rg) return false;
      var y = parseInt(s.date.slice(0, 4), 10);
      if (!isNaN(y)) {
        if (from && y < from) return false;
        if (to && y > to) return false;
      }
      return true;
    });
  }

  function renderDensity(list) {
    densityLayer.clearLayers();
    var bins = {};
    list.forEach(function (s) {
      var key = Math.floor(s.lat / 5) + '_' + Math.floor(s.lon / 5);
      bins[key] = (bins[key] || 0) + 1;
    });
    Object.keys(bins).forEach(function (k) {
      var parts = k.split('_');
      var lat = (parseInt(parts[0], 10) + 0.5) * 5;
      var lon = (parseInt(parts[1], 10) + 0.5) * 5;
      var n = bins[k];
      L.circle([lat, lon], {
        radius: 60000 + n * 9000,
        color: '#d68910',
        weight: 0,
        fillColor: '#e0a100',
        fillOpacity: Math.min(0.42, 0.08 + n * 0.012)
      }).addTo(densityLayer);
    });
  }

  function render() {
    var list = filtered();
    markerLayer.clearLayers();
    markers = [];

    var showH = document.getElementById('lyr-humpback').checked;
    var showS = document.getElementById('lyr-spinner').checked;

    list.forEach(function (s) {
      if (s.speciesId === 'humpback-whale' && !showH) return;
      if (s.speciesId === 'spinner-dolphin' && !showS) return;
      var mk = L.circleMarker([s.lat, s.lon], {
        radius: 4.5,
        color: '#ffffff',
        weight: 1,
        fillColor: COLORS[s.speciesId] || '#647d90',
        fillOpacity: 0.9
      });
      mk.bindPopup(
        '<strong>' + esc(s.species) + '</strong><br>' +
        esc(s.lat.toFixed(3)) + '&deg;, ' + esc(s.lon.toFixed(3)) + '&deg;<br>' +
        'Date: ' + esc(s.date) + '<br>' +
        'Individuals: ' + (s.count == null ? 'not recorded' : s.count) + '<br>' +
        'Region: ' + esc(regionOf(s.lat, s.lon))
      );
      mk.addTo(markerLayer);
      markers.push(mk);
    });

    if (document.getElementById('lyr-heat').checked) {
      renderDensity(list);
      if (!map.hasLayer(densityLayer)) densityLayer.addTo(map);
    } else if (map.hasLayer(densityLayer)) {
      map.removeLayer(densityLayer);
    }

    countEl.textContent = list.length.toLocaleString('en-US') + ' records match the current filters';

    var rows = list.slice(0, 250).map(function (s, i) {
      return '<tr data-i="' + i + '" style="cursor:pointer">' +
        '<td>' + esc(s.species) + '</td>' +
        '<td>' + s.lat.toFixed(3) + '</td>' +
        '<td>' + s.lon.toFixed(3) + '</td>' +
        '<td>' + esc(s.date) + '</td>' +
        '<td>' + (s.count == null ? '&ndash;' : s.count) + '</td></tr>';
    }).join('');
    tableBody.innerHTML = rows || '<tr><td colspan="5">No records match these filters.</td></tr>';

    Array.prototype.forEach.call(tableBody.querySelectorAll('tr[data-i]'), function (tr) {
      tr.addEventListener('click', function () {
        var mk = markers[parseInt(tr.dataset.i, 10)];
        if (!mk) return;
        map.setView(mk.getLatLng(), 6);
        mk.openPopup();
      });
    });
  }

  [speciesSel, regionSel, fromSel, toSel].forEach(function (el) {
    el.addEventListener('change', render);
  });
  ['lyr-humpback', 'lyr-spinner', 'lyr-heat'].forEach(function (id) {
    document.getElementById(id).addEventListener('change', render);
  });
  resetBtn.addEventListener('click', function () {
    speciesSel.value = ''; regionSel.value = ''; fromSel.value = ''; toSel.value = '';
    document.getElementById('lyr-humpback').checked = true;
    document.getElementById('lyr-spinner').checked = true;
    document.getElementById('lyr-heat').checked = false;
    render();
  });

  render();
})();
