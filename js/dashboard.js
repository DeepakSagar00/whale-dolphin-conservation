/* Researcher Dashboard - sign-in gate, statistics and charts */
(function () {
  'use strict';
  var D = window.SITE_DATA;
  var esc = window.SITE.escapeHtml;

  /* ------------------------------------------------------------- sign-in gate */
  var gate = document.getElementById('dash-gate');
  var app = document.getElementById('dash-app');
  var form = document.getElementById('dash-login');
  var error = document.getElementById('dl-error');

  var DEMO_EMAIL = 'researcher@whaleai.org';
  var DEMO_PASS = 'whale2026';

  function openDashboard() {
    gate.classList.add('hidden');
    app.classList.remove('hidden');
    try { sessionStorage.setItem('wd_session', '1'); } catch (e) { /* private mode */ }
    buildDashboard();
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = document.getElementById('dl-email').value.trim().toLowerCase();
    var pass = document.getElementById('dl-pass').value;
    if (email === DEMO_EMAIL && pass === DEMO_PASS) {
      error.style.display = 'none';
      openDashboard();
    } else {
      error.style.display = 'block';
    }
  });

  var restored = false;
  try { restored = sessionStorage.getItem('wd_session') === '1'; } catch (e) { restored = false; }
  if (restored) openDashboard();

  /* ---------------------------------------------------------------- charts */
  var built = false;

  function regionOf(lat, lon) {
    if (lat < -35) return 'Southern Ocean';
    if (lon < -30) return 'Atlantic';
    if (lon > 130) return 'Pacific';
    if (lat >= 5 && lat <= 25 && lon >= 50 && lon <= 78) return 'Arabian Sea';
    if (lat >= 5 && lat <= 23 && lon >= 79 && lon <= 98) return 'Bay of Bengal';
    return 'Indian Ocean';
  }

  function buildDashboard() {
    if (built) return;
    built = true;

    var sightings = D.sightings;
    var species = D.species;
    var m = D.metrics;

    /* stats */
    var stats = [
      { k: 'Sighting records', v: sightings.length.toLocaleString('en-US'), d: 'Published in the explorer dataset' },
      { k: 'Species monitored', v: species.length, d: 'Whales and dolphins in the directory' },
      { k: 'Risk model accuracy', v: m.accuracy + '%', d: 'Weighted F1 ' + m.f1 + ' on held-out cells' },
      { k: 'Modelled grid cells', v: D.gridRisk.total.toLocaleString('en-US'), d: 'Ocean cells scored for risk' }
    ];
    document.getElementById('dash-stats').innerHTML = stats.map(function (s) {
      return '<div class="stat"><div class="k">' + esc(s.k) + '</div>' +
        '<div class="v">' + esc(String(s.v)) + '</div>' +
        '<div class="d">' + esc(s.d) + '</div></div>';
    }).join('');

    if (typeof Chart === 'undefined') {
      document.querySelectorAll('.chart-box').forEach(function (b) {
        b.innerHTML = '<p class="muted">Chart library unavailable offline.</p>';
      });
      return;
    }

    Chart.defaults.font.family = '"Segoe UI", system-ui, sans-serif';
    Chart.defaults.color = '#647d90';
    var TEAL = '#17a2b8', OCEAN = '#1b6ca8', NAVY = '#10304f';

    /* records by year */
    var byYear = {};
    sightings.forEach(function (s) {
      var y = parseInt(s.date.slice(0, 4), 10);
      if (!isNaN(y) && y > 1950) byYear[y] = (byYear[y] || 0) + 1;
    });
    var years = Object.keys(byYear).map(Number).sort(function (a, b) { return a - b; });
    new Chart(document.getElementById('chart-years'), {
      type: 'bar',
      data: {
        labels: years,
        datasets: [{
          label: 'Records',
          data: years.map(function (y) { return byYear[y]; }),
          backgroundColor: TEAL, borderRadius: 4, maxBarThickness: 26
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, grid: { color: '#eef3f7' } }, x: { grid: { display: false } } }
      }
    });

    /* conservation status */
    var statusCount = {};
    species.forEach(function (s) { statusCount[s.statusLabel] = (statusCount[s.statusLabel] || 0) + 1; });
    new Chart(document.getElementById('chart-status'), {
      type: 'doughnut',
      data: {
        labels: Object.keys(statusCount),
        datasets: [{
          data: Object.keys(statusCount).map(function (k) { return statusCount[k]; }),
          backgroundColor: ['#c0392b', '#d68910', '#1e8449', '#647d90'],
          borderWidth: 0
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: '58%', plugins: { legend: { position: 'right' } } }
    });

    /* feature importance */
    var fi = m.featureImportance;
    var fiKeys = Object.keys(fi).sort(function (a, b) { return fi[b] - fi[a]; }).slice(0, 8);
    new Chart(document.getElementById('chart-features'), {
      type: 'bar',
      data: {
        labels: fiKeys.map(function (k) { return k.replace(/_/g, ' '); }),
        datasets: [{
          label: 'Importance',
          data: fiKeys.map(function (k) { return +(fi[k] * 100).toFixed(1); }),
          backgroundColor: OCEAN, borderRadius: 4, maxBarThickness: 18
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, grid: { color: '#eef3f7' }, ticks: { callback: function (v) { return v + '%'; } } },
          y: { grid: { display: false } }
        }
      }
    });

    /* risk classes */
    new Chart(document.getElementById('chart-risk'), {
      type: 'doughnut',
      data: {
        labels: Object.keys(D.gridRisk).filter(function (k) { return k !== 'total'; }),
        datasets: [{
          data: Object.keys(D.gridRisk).filter(function (k) { return k !== 'total'; })
            .map(function (k) { return D.gridRisk[k]; }),
          backgroundColor: ['#1e8449', '#d68910', '#c0392b', '#8e0a13'],
          borderWidth: 0
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: '58%', plugins: { legend: { position: 'right' } } }
    });

    /* distribution by region */
    var byRegion = {};
    sightings.forEach(function (s) {
      var r = regionOf(s.lat, s.lon);
      byRegion[r] = (byRegion[r] || 0) + 1;
    });
    new Chart(document.getElementById('chart-region'), {
      type: 'bar',
      data: {
        labels: Object.keys(byRegion),
        datasets: [{
          label: 'Records',
          data: Object.keys(byRegion).map(function (k) { return byRegion[k]; }),
          backgroundColor: NAVY, borderRadius: 4, maxBarThickness: 40
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, grid: { color: '#eef3f7' } }, x: { grid: { display: false } } }
      }
    });

    /* recent records */
    var recent = sightings.slice().sort(function (a, b) { return a.date < b.date ? 1 : -1; }).slice(0, 12);
    document.getElementById('dash-table').innerHTML = recent.map(function (s) {
      return '<tr><td>' + esc(s.species) + '</td><td>' + s.lat.toFixed(3) + '</td>' +
        '<td>' + s.lon.toFixed(3) + '</td><td>' + esc(s.date) + '</td>' +
        '<td>' + (s.count == null ? '&ndash;' : s.count) + '</td></tr>';
    }).join('');
  }
})();
