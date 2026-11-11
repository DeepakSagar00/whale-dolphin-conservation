/* Conservation — threats, strategies and priority species. */
(function () {
  'use strict';
  var esc = function (t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  var THREATS = [
    { icon: '&#9875;', title: 'Ship strikes',
      body: 'Vessel traffic overlaps migratory routes and feeding grounds. Strikes remain a leading cause of mortality for several large whale species, with risk concentrated in a small number of high-traffic cells.' },
    { icon: '&#129361;', title: 'Entanglement and bycatch',
      body: 'Drifting nets, lines and traps entangle whales and dolphins. For dolphin populations, interaction with coastal fisheries is a persistent source of mortality.' },
    { icon: '&#9836;', title: 'Ocean noise',
      body: 'Engine noise and low-frequency shipping tones mask the calls animals use to communicate, raising energy demands and disrupting feeding and social behaviour.' },
    { icon: '&#9851;', title: 'Plastic and chemical pollution',
      body: 'Plastic debris and chemical contaminants enter the food chain, and marine mammals accumulate pollutants to levels that affect health and reproduction.' },
    { icon: '&#127760;', title: 'Climate change',
      body: 'Warming seas shift the distribution of prey and push species poleward, while changing prey abundance and habitat quality at the range edges.' },
    { icon: '&#127758;', title: 'Habitat degradation',
      body: 'Coastal development, dredging and altered prey distributions degrade the shallow-water habitat that dolphins depend on for feeding and resting.' }
  ];

  var STRATEGIES = [
    { icon: '&#9878;', title: 'Dynamic speed management',
      body: 'Speed restrictions are placed where the model shows whales and fast-moving vessels will overlap, and relaxed where risk is low.' },
    { icon: '&#128197;', title: 'Seasonal protection windows',
      body: 'Forecast models identify the weeks each species is most likely present, so protections can follow the migration instead of the calendar.' },
    { icon: '&#9635;', title: 'Protected area review',
      body: 'Cells with high habitat suitability and recorded presence but no current protection are surfaced as candidates for designation.' },
    { icon: '&#128266;', title: 'Quiet zones and noise reduction',
      body: 'Shipping corridors overlapping important habitat are candidates for engine restrictions, slow steaming and targeted noise monitoring.' },
    { icon: '&#129419;', title: 'Fishery mitigation',
      body: 'Where fishing effort overlaps predicted habitat, seasonal gear restrictions and bycatch mitigation measures are advised for that cell.' },
    { icon: '&#128209;', title: 'Open monitoring and reporting',
      body: 'Observation records, models and advisory outputs are published openly so other agencies can verify, reuse and extend the results.' }
  ];

  function card(c) {
    return '<article class="card reveal in"><div class="card__body">' +
      '<h3><span style="font-size:1.1rem;margin-right:6px">' + c.icon + '</span>' + esc(c.title) + '</h3>' +
      '<p class="small muted" style="margin-top:7px">' + esc(c.body) + '</p>' +
      '</div></article>';
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('cons-threats').innerHTML = THREATS.map(card).join('');
    document.getElementById('cons-strategies').innerHTML = STRATEGIES.map(card).join('');

    var order = { EN: 0, VU: 1, DD: 2, LC: 3 };
    var list = window.SITE_DATA.species.slice().sort(function (a, b) {
      return (order[a.status] - order[b.status]) || a.name.localeCompare(b.name);
    }).slice(0, 3);

    document.getElementById('cons-species').innerHTML = list.map(function (s) {
      return '<article class="card species-card reveal in">' +
        '<div class="species-card__media"><img src="assets/species/' + s.id + '.svg" alt="' +
          esc(s.name) + '"></div>' +
        '<div class="species-card__body">' +
          '<h3>' + esc(s.name) + '</h3>' +
          '<p class="species-card__latin">' + esc(s.latin) + '</p>' +
          '<div class="species-card__meta">' +
            '<span class="badge ' + window.SITE.statusClass(s.status) + '">' + esc(s.statusLabel) + '</span>' +
            '<span class="badge badge--grey">' + esc(s.population) + '</span>' +
          '</div>' +
          '<p>' + esc(s.description) + '</p>' +
          '<div class="pill-row mt-2">' +
            s.threats.map(function (t) { return '<span class="badge badge--grey">' + esc(t) + '</span>'; }).join('') +
          '</div>' +
          '<a class="species-card__link" href="species-detail.html?id=' + s.id + '">Open species record &rarr;</a>' +
        '</div></article>';
    }).join('');
  });
})();
