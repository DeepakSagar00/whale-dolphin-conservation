/* Species record detail page - renders from ?id= */
(function () {
  'use strict';
  var id = new URLSearchParams(location.search).get('id');
  var root = document.getElementById('spd-root');
  var s = window.SITE.speciesById(id);

  function esc(t) { return window.SITE.escapeHtml(t); }

  if (!s) {
    root.innerHTML = '<div class="panel"><h3>Species not found</h3>' +
      '<p class="muted mt-2">The requested species record does not exist in the directory.</p>' +
      '<a class="btn btn--outline mt-3" href="species.html">Back to Species Explorer</a></div>';
    return;
  }

  document.title = s.name + ' | Whale & Dolphin Conservation';

  var crumbs = document.querySelector('.breadcrumbs');
  if (crumbs) {
    crumbs.innerHTML = '<a href="index.html">Home</a><span>/</span>' +
      '<a href="species.html">Species Explorer</a><span>/</span>' + esc(s.name);
  }

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
  ].map(function (f) {
    return '<div><dt>' + esc(f[0]) + '</dt><dd>' + esc(f[1]) + '</dd></div>';
  }).join('');

  root.innerHTML =
    '<nav class="breadcrumbs" style="color:var(--ink-400)">' +
      '<a href="index.html">Home</a><span>/</span>' +
      '<a href="species.html">Species Explorer</a><span>/</span>' + esc(s.name) +
    '</nav>' +
    '<div class="detail">' +
      '<div>' +
        '<div class="detail__media"><img src="assets/species/' + s.id + '.svg" alt="' + esc(s.name) + '"></div>' +
        '<div class="pill-row mt-3">' +
          '<span class="badge badge--info">' + esc(s.type) + '</span>' +
          '<span class="badge ' + window.SITE.statusClass(s.status) + '">' + esc(s.statusLabel) + '</span>' +
        '</div>' +
        '<h1 class="mt-3">' + esc(s.name) + '</h1>' +
        '<p class="muted" style="font-style:italic">' + esc(s.latin) + '</p>' +
        '<p class="lead mt-2">' + esc(s.description) + '</p>' +
        '<div class="mt-4">' +
          '<a class="btn btn--primary" href="gis.html">View on the map</a> ' +
          '<a class="btn btn--outline" href="ai.html">Identify a recording</a>' +
        '</div>' +
      '</div>' +
      '<div>' +
        '<h3>Species record</h3>' +
        '<dl class="fact-list">' + facts + '</dl>' +
        '<h3 class="mt-4">Principal threats</h3>' +
        '<ul class="muted mt-2" style="padding-left:20px">' +
          s.threats.map(function (t) { return '<li style="margin-bottom:8px">' + esc(t) + '</li>'; }).join('') +
        '</ul>' +
        '<div class="divider"></div>' +
        '<a class="btn btn--outline btn--sm" href="species.html">&#8592; Back to directory</a>' +
      '</div>' +
    '</div>';
})();
