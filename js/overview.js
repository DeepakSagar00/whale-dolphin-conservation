/* Overview page — live platform snapshot and data provenance. */
(function () {
  'use strict';

  var el = function (id) { return document.getElementById(id); };
  var esc = function (t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  function renderSnapshot(d) {
    var t = d.totals || {};
    var stats = [
      { v: (t.sightings || 0).toLocaleString('en-US'), k: 'Observations' },
      { v: (t.incidents || 0).toLocaleString('en-US'), k: 'Incidents recorded' },
      { v: (t.grid_cells || 0).toLocaleString('en-US'), k: 'Risk cells modelled' },
      { v: (t.species || 0), k: 'Species covered' }
    ];
    el('hero-stats').innerHTML = stats.map(function (s) {
      return '<div class="hero__stat"><div class="v">' + esc(s.v) + '</div><div class="k">' + esc(s.k) + '</div></div>';
    }).join('');

    var rows = [
      ['Marine observations', (t.sightings || 0).toLocaleString('en-US') + ' records',
        'Sighting records loaded from the Ocean Biodiversity Information System'],
      ['Mortality incidents', (t.incidents || 0).toLocaleString('en-US') + ' records',
        'Historical incidents with cause and severity'],
      ['Ocean grid', (t.grid_cells || 0).toLocaleString('en-US') + ' cells',
        'Modelled cells carrying depth, temperature, vessel and fishing pressure'],
      ['Protected areas', (t.protected_areas || 0) + ' areas', 'Marine protected areas in the study region'],
      ['Platform submissions', (t.observations || 0).toLocaleString('en-US') + ' records',
        'Observations submitted through the GIS collection workflow on this site'],
      ['Source system', d.database_connected ? 'PostgreSQL connected' : 'published dataset',
        'The API reads the platform database directly']
    ];
    el('provenance').innerHTML =
      '<div class="tablewrap"><table><thead><tr><th>Dataset</th><th>Volume</th><th>Description</th></tr></thead><tbody>' +
      rows.map(function (r) {
        return '<tr><td><strong>' + esc(r[0]) + '</strong></td><td>' + esc(r[1]) + '</td><td class="muted">' + esc(r[2]) + '</td></tr>';
      }).join('') + '</tbody></table></div>';
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!window.API) return;
    window.API.dashboardOverview().then(renderSnapshot).catch(function () {
      el('hero-stats').innerHTML =
        '<div class="hero__stat"><div class="v">&mdash;</div><div class="k">API not reachable</div></div>';
      el('provenance').innerHTML =
        '<p class="muted small">The platform API could not be reached, so the live figures are ' +
        'unavailable. The published research artefacts remain downloadable from the Research page.</p>';
    });
  });
})();
