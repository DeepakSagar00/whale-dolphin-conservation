/* Species Directory — rendering, search and filtering. */
(function () {
  'use strict';
  var D = window.SITE_DATA.species;
  var grid = document.getElementById('sp-grid');
  var search = document.getElementById('sp-search');
  var typeSel = document.getElementById('sp-type');
  var statusSel = document.getElementById('sp-status');
  var count = document.getElementById('sp-count');
  var empty = document.getElementById('sp-empty');

  function esc(t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function card(s) {
    return '<article class="card species-card reveal in">' +
      '<div class="species-card__media"><img src="assets/species/' + s.id + '.svg" alt="' +
        esc(s.name) + ' illustration"></div>' +
      '<div class="species-card__body">' +
        '<h3>' + esc(s.name) + '</h3>' +
        '<p class="species-card__latin">' + esc(s.latin) + '</p>' +
        '<div class="species-card__meta">' +
          '<span class="badge badge--info">' + esc(s.type) + '</span>' +
          '<span class="badge ' + window.SITE.statusClass(s.status) + '">' + esc(s.statusLabel) + '</span>' +
        '</div>' +
        '<p>' + esc(s.description) + '</p>' +
        '<a class="species-card__link" href="species-detail.html?id=' + s.id + '">Open species record &rarr;</a>' +
      '</div></article>';
  }

  function render() {
    var q = (search.value || '').trim().toLowerCase();
    var t = typeSel.value;
    var st = statusSel.value;
    var list = D.filter(function (s) {
      if (t && s.type !== t) return false;
      if (st && s.status !== st) return false;
      if (q) {
        var hay = (s.name + ' ' + s.latin + ' ' + s.habitat + ' ' + s.distribution).toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });
    grid.innerHTML = list.map(card).join('');
    count.textContent = list.length + (list.length === 1 ? ' species' : ' species');
    empty.style.display = list.length ? 'none' : 'block';
  }

  search.addEventListener('input', render);
  typeSel.addEventListener('change', render);
  statusSel.addEventListener('change', render);

  // global search hands over a query string
  var q0 = new URLSearchParams(location.search).get('q');
  if (q0) search.value = q0;
  render();
})();
