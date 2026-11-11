/* Professional Dashboard — live database aggregates, alerts, status and activity. */
(function () {
  'use strict';

  var el = function (id) { return document.getElementById(id); };
  var esc = function (t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  var STATUS_CLASS = { EN: 'badge--en', VU: 'badge--vu', LC: 'badge--lc', DD: 'badge--dd' };
  var SEVERITY_CLASS = { fatal: 'badge--en', severe: 'badge--vu', minor: 'badge--grey' };

  var charts = [];

  function paint(d) {
    var t = d.totals || {};

    var kpis = [
      { k: 'Total observations', v: (t.sightings || 0).toLocaleString('en-US'), c: '', m: 'sighting records in the database' },
      { k: 'Species detected', v: t.species || 0, c: 'kpi--teal', m: 'in the species reference table' },
      { k: 'Recorded incidents', v: (t.incidents || 0).toLocaleString('en-US'), c: 'kpi--amber', m: 'mortality events with cause and severity' },
      { k: 'Ocean cells modelled', v: (t.grid_cells || 0).toLocaleString('en-US'), c: 'kpi--green', m: 'scored for conservation risk' }
    ];
    el('dash-kpis').innerHTML = kpis.map(function (k) {
      return '<div class="kpi ' + k.c + '"><div class="kpi__label">' + esc(k.k) + '</div>' +
        '<div class="kpi__value">' + esc(String(k.v)) + '</div>' +
        '<div class="kpi__meta">' + esc(k.m) + '</div></div>';
    }).join('');

    /* alerts */
    var alerts = d.alerts || [];
    el('dash-alerts').innerHTML = alerts.map(function (a) {
      var icon = a.level === 'critical' ? '&#9888;' : (a.level === 'warning' ? '&#9889;' : '&#8505;');
      return '<div class="alert alert--' + esc(a.level) + '">' +
        '<span class="alert__icon">' + icon + '</span>' +
        '<div class="alert__body"><h4>' + esc(a.title) + '</h4>' +
        '<p>' + esc(a.detail) + '</p>' +
        '<div class="src">Source: ' + esc(a.source) + '</div></div></div>';
    }).join('') || '<div class="empty">No alerts raised from the current record.</div>';

    /* conservation status */
    el('dash-species').innerHTML = (d.species || []).map(function (s) {
      return '<tr><td><strong>' + esc(s.common_name) + '</strong><br>' +
        '<span class="small muted" style="font-style:italic">' + esc(s.scientific_name) + '</span></td>' +
        '<td class="num"><span class="badge ' + (STATUS_CLASS[s.iucn_category] || 'badge--dd') + '">' +
        esc(s.iucn_category || 'n/a') + '</span></td></tr>';
    }).join('') || '<tr><td class="empty">No species records.</td></tr>';

    /* recent sightings */
    el('dash-recent').innerHTML = (d.recent_sightings || []).map(function (s) {
      return '<tr><td>' + esc(s.common_name || 'Unidentified') + '</td>' +
        '<td>' + esc(s.event_date || '') + '</td>' +
        '<td class="mono">' + Number(s.lat).toFixed(3) + '</td>' +
        '<td class="mono">' + Number(s.lon).toFixed(3) + '</td>' +
        '<td class="num">' + (s.individual_count == null ? '&ndash;' : s.individual_count) + '</td></tr>';
    }).join('') || '<tr><td colspan="5" class="empty">No records.</td></tr>';

    /* recent incidents */
    el('dash-incidents').innerHTML = (d.recent_incidents || []).map(function (i) {
      return '<tr><td>' + esc(i.event_date || '') + '</td>' +
        '<td>' + esc(i.common_name || 'Unidentified') + '</td>' +
        '<td>' + esc(i.cause || 'unspecified') + '</td>' +
        '<td><span class="badge ' + (SEVERITY_CLASS[i.severity] || 'badge--grey') + '">' +
        esc(i.severity || 'n/a') + '</span></td>' +
        '<td class="mono">' + Number(i.lat).toFixed(3) + '</td>' +
        '<td class="mono">' + Number(i.lon).toFixed(3) + '</td></tr>';
    }).join('') || '<tr><td colspan="6" class="empty">No incidents recorded.</td></tr>';

    drawCharts(d);
  }

  function drawCharts(d) {
    if (typeof Chart === 'undefined') return;
    charts.forEach(function (c) { c.destroy(); });
    charts = [];

    Chart.defaults.font.family = '"Segoe UI", system-ui, sans-serif';
    Chart.defaults.color = '#6a8299';
    var TEAL = '#12a8b8', OCEAN = '#1b80c4', NAVY = '#102c47';

    var sev = d.incidents_by_severity || [];
    charts.push(new Chart(el('chart-severity'), {
      type: 'doughnut',
      data: {
        labels: sev.map(function (r) { return r.severity; }),
        datasets: [{
          data: sev.map(function (r) { return r.c; }),
          backgroundColor: ['#c0392b', '#d68910', '#92a7ba'], borderWidth: 0
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: '58%',
                 plugins: { legend: { position: 'right' } } }
    }));

    var cause = d.incidents_by_cause || [];
    charts.push(new Chart(el('chart-cause'), {
      type: 'bar',
      data: {
        labels: cause.map(function (r) { return r.cause; }),
        datasets: [{
          label: 'Incidents', data: cause.map(function (r) { return r.c; }),
          backgroundColor: OCEAN, borderRadius: 3, maxBarThickness: 22
        }]
      },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true, grid: { color: '#eef3f7' } }, y: { grid: { display: false } } }
      }
    }));
  }

  function openDashboard() {
    el('dash-gate').classList.add('hidden');
    el('dash-app').classList.remove('hidden');
    window.API.dashboardOverview().then(paint).catch(function (err) {
      el('dash-kpis').innerHTML = '<div class="kpi kpi--red"><div class="kpi__label">API unavailable</div>' +
        '<div class="kpi__value">-</div><div class="kpi__meta">' + esc(err.message) + '</div></div>';
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var form = el('dash-login');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var err = el('dl-error');
      err.style.display = 'none';
      var username = el('dl-email').value.trim();
      var pass = el('dl-pass').value;
      if (!username || !pass) {
        err.textContent = 'Enter your username and password.';
        err.style.display = 'block';
        return;
      }
      if (!window.API) {
        err.textContent = 'The API client is not available.';
        err.style.display = 'block';
        return;
      }
      var btn = form.querySelector('button[type=submit]');
      btn.disabled = true;
      btn.textContent = 'Signing in\u2026';
      window.API.login(username, pass).then(function () {
        btn.disabled = false;
        btn.textContent = 'Sign in';
        if (window.SHELL) window.SHELL.paintUser();
        openDashboard();
      }).catch(function (e2) {
        btn.disabled = false;
        btn.textContent = 'Sign in';
        err.textContent = 'Sign-in failed: ' + (e2.message || 'invalid credentials') +
          '. The demonstration account is researcher / researcher.';
        err.style.display = 'block';
      });
    });
  });
})();
