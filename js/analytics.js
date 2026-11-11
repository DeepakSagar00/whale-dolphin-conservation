/* Conservation Analytics — charts computed from the platform database. */
(function () {
  'use strict';

  var el = function (id) { return document.getElementById(id); };
  var esc = function (t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  var STATUS_CLASS = { EN: 'badge--en', VU: 'badge--vu', LC: 'badge--lc', DD: 'badge--dd' };

  function regionOf(lat, lon) {
    if (lat < -35) return 'Southern Ocean';
    if (lon < -30) return 'Atlantic';
    if (lon > 130) return 'Pacific';
    if (lat >= 5 && lat <= 25 && lon >= 50 && lon <= 78) return 'Arabian Sea';
    if (lat >= 5 && lat <= 23 && lon >= 79 && lon <= 98) return 'Bay of Bengal';
    return 'Indian Ocean';
  }

  var charts = [];

  function draw(d) {
    if (typeof Chart === 'undefined') return;
    charts.forEach(function (c) { c.destroy(); });
    charts = [];
    Chart.defaults.font.family = '"Segoe UI", system-ui, sans-serif';
    Chart.defaults.color = '#6a8299';
    var TEAL = '#12a8b8', OCEAN = '#1b80c4', NAVY = '#102c47';

    var years = (d.sightings_by_year || []).filter(function (r) { return r.year > 1950; });
    charts.push(new Chart(el('ana-years'), {
      type: 'bar',
      data: {
        labels: years.map(function (r) { return r.year; }),
        datasets: [{ label: 'Records', data: years.map(function (r) { return r.c; }),
          backgroundColor: OCEAN, borderRadius: 3, maxBarThickness: 22 }]
      },
      options: { responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: '#eef3f7' } } } }
    }));

    var cause = d.incidents_by_cause || [];
    charts.push(new Chart(el('ana-cause'), {
      type: 'bar',
      data: {
        labels: cause.map(function (r) { return r.cause; }),
        datasets: [{ label: 'Incidents', data: cause.map(function (r) { return r.c; }),
          backgroundColor: TEAL, borderRadius: 3, maxBarThickness: 22 }]
      },
      options: { responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: '#eef3f7' } } } }
    }));

    var sev = d.incidents_by_severity || [];
    charts.push(new Chart(el('ana-severity'), {
      type: 'doughnut',
      data: { labels: sev.map(function (r) { return r.severity; }),
        datasets: [{ data: sev.map(function (r) { return r.c; }),
          backgroundColor: ['#c0392b', '#d68910', '#92a7ba'], borderWidth: 0 }] },
      options: { responsive: true, maintainAspectRatio: false, cutout: '58%',
        plugins: { legend: { position: 'right' } } }
    }));

    var risk = d.risk_classes || [];
    var riskColors = { Critical: '#8e0a13', High: '#c0392b', Moderate: '#d68910', Low: '#1e8449' };
    charts.push(new Chart(el('ana-risk'), {
      type: 'doughnut',
      data: { labels: risk.map(function (r) { return r.risk_class; }),
        datasets: [{ data: risk.map(function (r) { return r.c; }),
          backgroundColor: risk.map(function (r) { return riskColors[r.risk_class] || '#92a7ba'; }),
          borderWidth: 0 }] },
      options: { responsive: true, maintainAspectRatio: false, cutout: '58%',
        plugins: { legend: { position: 'right' } } }
    }));

    var byRegion = {};
    (d.recent_sightings || []).forEach(function (s) {
      var r = regionOf(s.lat, s.lon);
      byRegion[r] = (byRegion[r] || 0) + 1;
    });
    charts.push(new Chart(el('ana-region'), {
      type: 'bar',
      data: {
        labels: Object.keys(byRegion),
        datasets: [{ label: 'Records', data: Object.keys(byRegion).map(function (k) { return byRegion[k]; }),
          backgroundColor: NAVY, borderRadius: 3, maxBarThickness: 34 }]
      },
      options: { responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: '#eef3f7' } } } }
    }));

    var top = d.top_species || [];
    charts.push(new Chart(el('ana-species'), {
      type: 'bar',
      data: {
        labels: top.map(function (r) { return r.common_name; }),
        datasets: [{ label: 'Records', data: top.map(function (r) { return r.c; }),
          backgroundColor: TEAL, borderRadius: 3, maxBarThickness: 34 }]
      },
      options: { responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: '#eef3f7' } } } }
    }));
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!window.API) return;
    window.API.dashboardOverview().then(function (d) {
      render(d);
    }).catch(function (err) {
      var snap = window.SITE_DATA.dashboard;
      if (snap && snap.totals) {
        render(snap);
      } else {
        el('ana-kpis').innerHTML = '<div class="kpi kpi--red"><div class="kpi__label">API unavailable</div>' +
          '<div class="kpi__value">-</div><div class="kpi__meta">' + esc(err.message) + '</div></div>';
      }
    });
  });

  function render(d) {
      var t = d.totals || {};
      var kpis = [
        { k: 'Sighting records', v: (t.sightings || 0).toLocaleString('en-US'), m: 'observation records', c: '' },
        { k: 'Incidents', v: (t.incidents || 0).toLocaleString('en-US'), m: 'mortality events', c: 'kpi--amber' },
        { k: 'Grid cells', v: (t.grid_cells || 0).toLocaleString('en-US'), m: 'cells scored for risk', c: 'kpi--green' },
        { k: 'Platform submissions', v: (t.observations || 0).toLocaleString('en-US'), m: 'submitted via the GIS map', c: 'kpi--teal' }
      ];
      el('ana-kpis').innerHTML = kpis.map(function (k) {
        return '<div class="kpi ' + k.c + '"><div class="kpi__label">' + esc(k.k) + '</div>' +
          '<div class="kpi__value">' + esc(String(k.v)) + '</div>' +
          '<div class="kpi__meta">' + esc(k.m) + '</div></div>';
      }).join('');

      var counts = {};
      (d.top_species || []).forEach(function (r) { counts[r.common_name] = r.c; });
      el('ana-species-table').innerHTML = (d.species || []).map(function (s) {
        return '<tr><td><strong>' + esc(s.common_name) + '</strong></td>' +
          '<td style="font-style:italic" class="muted">' + esc(s.scientific_name) + '</td>' +
          '<td><span class="badge ' + (STATUS_CLASS[s.iucn_category] || 'badge--dd') + '">' +
          esc(s.iucn_category || 'n/a') + '</span></td>' +
          '<td class="num">' + (counts[s.common_name] || 0) + '</td>' +
          '<td class="muted small">' + esc(s.conservation_note || '') + '</td></tr>';
      }).join('') || '<tr><td colspan="5" class="empty">No species records.</td></tr>';

      draw(d);
  }
})();
