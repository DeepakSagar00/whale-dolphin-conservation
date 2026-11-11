/* Species record detail page - renders from ?id= */
(function () {
  'use strict';
  var id = new URLSearchParams(location.search).get('id');
  var root = document.getElementById('spd-root');
  var s = window.SITE.speciesById(id);

  function esc(t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  if (!s) {
    root.innerHTML = '<div class="panel"><div class="panel__body">' +
      '<h3>Species not found</h3><p class="muted small mt-2">The requested species record does ' +
      'not exist in the directory.</p>' +
      '<a class="btn btn--ghost btn--sm mt-3" href="species.html">Back to the directory</a>' +
      '</div></div>';
    return;
  }

  document.title = s.name + ' | WhaleAI Conservation';

  var facts = [
    ['Scientific name', s.latin],
    ['Group', s.type],
    ['Conservation status', s.statusLabel],
    ['Estimated population', s.population],
    ['Length', s.length],
    ['Weight', s.weight],
    ['Diet', s.diet],
    ['Habitat', s.habitat],
    ['Distribution', s.distribution]
  ];

  root.innerHTML =
    '<div class="grid grid--2">' +
      '<div class="panel"><div class="panel__body">' +
        '<img src="assets/species/' + s.id + '.svg" alt="' + esc(s.name) + '" ' +
          'style="width:100%;border-radius:8px;background:linear-gradient(160deg,#e8f4f9,#d3e9f2)">' +
        '<div class="pill-row mt-3">' +
          '<span class="badge badge--info">' + esc(s.type) + '</span>' +
          '<span class="badge ' + window.SITE.statusClass(s.status) + '">' + esc(s.statusLabel) + '</span>' +
        '</div>' +
        '<h2 class="mt-3">' + esc(s.name) + '</h2>' +
        '<p class="muted small" style="font-style:italic">' + esc(s.latin) + '</p>' +
        '<p class="mt-2 muted">' + esc(s.description) + '</p>' +
        '<div class="mt-3" style="display:flex;gap:8px;flex-wrap:wrap">' +
          '<a class="btn btn--primary btn--sm" href="gis.html">View on the GIS map</a>' +
          '<a class="btn btn--ghost btn--sm" href="bioacoustics.html">Analyse its calls</a>' +
          '<a class="btn btn--ghost btn--sm" href="identify.html">Identify a photograph</a>' +
        '</div>' +
      '</div></div>' +

      '<div class="grid" style="gap:14px;align-content:start">' +
        '<div class="panel"><div class="panel__head"><h3>Species record</h3></div>' +
          '<div class="panel__body"><dl class="fact-list">' +
          facts.map(function (f) {
            return '<div><dt>' + esc(f[0]) + '</dt><dd>' + esc(f[1]) + '</dd></div>';
          }).join('') + '</dl></div></div>' +

        '<div class="panel"><div class="panel__head"><h3>Principal threats</h3></div>' +
          '<div class="panel__body"><ul class="small muted" style="padding-left:18px">' +
          s.threats.map(function (t) {
            return '<li style="margin-bottom:7px">' + esc(t) + '</li>';
          }).join('') + '</ul></div></div>' +

        '<div class="panel"><div class="panel__head"><h3>Related modules</h3></div>' +
          '<div class="panel__body"><div style="display:flex;gap:8px;flex-wrap:wrap">' +
            '<a class="btn btn--ghost btn--sm" href="analytics.html">Conservation analytics</a>' +
            '<a class="btn btn--ghost btn--sm" href="conservation.html">Conservation strategies</a>' +
            '<a class="btn btn--ghost btn--sm" href="species.html">All species</a>' +
          '</div></div></div>' +
      '</div>' +
    '</div>';
})();
