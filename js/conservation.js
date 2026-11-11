/* Conservation page - renders the priority species cards */
(function () {
  'use strict';
  var order = { EN: 0, VU: 1, DD: 2, LC: 3 };
  var list = window.SITE_DATA.species.slice().sort(function (a, b) {
    return (order[a.status] - order[b.status]) || a.name.localeCompare(b.name);
  }).slice(0, 3);

  var html = list.map(function (s) {
    return '<article class="card species-card reveal in">' +
      '<div class="species-card__media"><img src="assets/species/' + s.id + '.svg" alt="' +
        window.SITE.escapeHtml(s.name) + '"></div>' +
      '<div class="species-card__body">' +
        '<h3>' + window.SITE.escapeHtml(s.name) + '</h3>' +
        '<p class="species-card__latin">' + window.SITE.escapeHtml(s.latin) + '</p>' +
        '<div class="species-card__meta">' +
          '<span class="badge ' + window.SITE.statusClass(s.status) + '">' + window.SITE.escapeHtml(s.statusLabel) + '</span>' +
          '<span class="badge badge--info">' + window.SITE.escapeHtml(s.population) + '</span>' +
        '</div>' +
        '<p>' + window.SITE.escapeHtml(s.description) + '</p>' +
        '<div class="pill-row mt-2">' +
          s.threats.map(function (t) { return '<span class="badge badge--dd">' + window.SITE.escapeHtml(t) + '</span>'; }).join('') +
        '</div>' +
        '<a class="species-card__link" href="species-detail.html?id=' + s.id + '">View species &#8594;</a>' +
      '</div></article>';
  }).join('');

  document.getElementById('cons-species').innerHTML = html;
})();
