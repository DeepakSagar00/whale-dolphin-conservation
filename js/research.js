/* Research and Insights — datasets, findings, references and downloads. */
(function () {
  'use strict';
  var D = window.SITE_DATA;
  var esc = function (t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  var sightings = D.sightings;
  var years = sightings.map(function (s) { return parseInt(s.date.slice(0, 4), 10); })
    .filter(function (y) { return !isNaN(y); });
  var yMin = Math.min.apply(null, years);
  var yMax = Math.max.apply(null, years);

  var datasets = [
    { title: 'OBIS occurrence records',
      body: 'Species occurrence records for humpback whale (Megaptera novaeangliae) and spinner dolphin (Stenella longirostris) from the Ocean Biodiversity Information System. The explorer publishes ' +
        sightings.length + ' records; the working dataset holds 10,000 and 1,500 respectively.',
      meta: sightings.length + ' records published · ' + yMin + '–' + yMax },
    { title: 'Acoustic monitoring archive',
      body: 'Underwater recordings processed into 5-second windows and 64 mel-spaced log-mel bands. The classifier separates blue, fin, humpback and killer whale calls, bottlenose dolphin whistles and ship-noise-only background, and is stress-tested with vessel noise mixed in at 0–20 dB SNR.',
      meta: '6 classes · noise-mixed at 0–20 dB SNR' },
    { title: 'Photographic reference set',
      body: 'Openly-licensed reference photographs retrieved from Wikimedia Commons for each of the six species, used to train the image classifier with histogram-of-oriented-gradients shape descriptors and colour statistics.',
      meta: '378 reference photographs · 6 species' },
    { title: 'AIS vessel tracks',
      body: 'MarineCadastre vessel positions reduced to ship-kilometres per grid cell and per week, combined with a logistic lethality curve relating speed to strike probability.',
      meta: 'Southern California Bight' },
    { title: 'Gridded risk features',
      body: 'A modelled ocean grid of depth, sea-surface temperature, vessel intensity, fishing intensity, noise proxy, protected-area membership and habitat suitability, with a conservation risk class assigned to every cell.',
      meta: (D.gridRisk.total || 0).toLocaleString('en-US') + ' grid cells' },
    { title: 'Model runs and metrics',
      body: 'Every training run records its parameters, metrics and model artefacts so results remain reproducible and comparable between experiments.',
      meta: 'MLflow-compatible tracking' }
  ];

  document.getElementById('res-datasets').innerHTML = datasets.map(function (d) {
    return '<article class="card reveal in"><div class="card__body">' +
      '<h3>' + esc(d.title) + '</h3>' +
      '<p class="small muted" style="margin-top:6px">' + esc(d.body) + '</p>' +
      '<p class="small mt-2" style="color:var(--teal-600);font-weight:650">' + esc(d.meta) + '</p>' +
      '</div></article>';
  }).join('');

  var m = D.metrics;
  var findings = [
    { stat: m.accuracy + '%', label: 'Accuracy',
      title: 'Risk model separates risk classes reliably',
      body: 'The gradient-boosted risk classifier reaches ' + m.accuracy + '% accuracy and ' + m.f1 +
        ' weighted F1 across the four conservation risk classes on held-out grid cells, with a ' +
        'multi-class ROC AUC of ' + m.rocAuc + '.' },
    { stat: (m.featureImportance.vessel_intensity * 100).toFixed(1) + '%', label: 'Top feature',
      title: 'Vessel traffic dominates the risk signal',
      body: 'Vessel intensity (' + (m.featureImportance.vessel_intensity * 100).toFixed(1) +
        '% of feature importance) and the noise proxy (' + (m.featureImportance.noise_proxy * 100).toFixed(1) +
        '%) explain far more of the risk variation than habitat suitability or species density.' },
    { stat: '7 / 14 / 30d', label: 'Rate windows',
      title: 'Detection history predicts presence',
      body: 'Rolling detection rates over 7, 14 and 30 days, combined with day-of-year seasonality, allow the presence model to anticipate whether a species will be present in the following week.' },
    { stat: '6 / 6', label: 'Classes separated',
      title: 'Acoustic classification separates the modelled calls',
      body: 'The audio classifier identifies the four whale call types, dolphin whistles and ship-noise-only background. It reproduces its training feature extraction exactly in the browser and on the server.' },
    { stat: '73%', label: 'Held-out accuracy',
      title: 'Photographic identification is reliable for whales, weaker for dolphins',
      body: 'The image classifier reaches about 73% accuracy on held-out photographs. The baleen whale classes score between 0.82 and 0.94 F1, while the two dolphin classes are regularly confused with one another. The limitation is reported in the interface rather than hidden.' },
    { stat: '12,856', label: 'Cells modelled',
      title: 'Risk is scored across the whole study grid',
      body: 'Every cell in the ocean grid carries a risk class, a confidence value and a set of recommended actions, so the output is a spatial table rather than an isolated point estimate.' }
  ];

  document.getElementById('res-findings').innerHTML = findings.map(function (f) {
    return '<article class="card reveal in"><div class="card__body">' +
      '<div style="font-size:1.5rem;font-weight:800;color:var(--teal-600)">' + esc(f.stat) + '</div>' +
      '<div class="small muted" style="text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">' +
        esc(f.label) + '</div>' +
      '<h3>' + esc(f.title) + '</h3>' +
      '<p class="small muted" style="margin-top:5px">' + esc(f.body) + '</p>' +
      '</div></article>';
  }).join('');

  var pubs = [
    { title: 'Vanderlaan, J. M. &amp; Taggart, C. T. (2007) — Vessel collisions with whales: the probability of lethal injury based on vessel speed',
      meta: 'Marine Mammal Science 23(1) · methods reference for the lethality curve used in the risk engine',
      body: 'The logistic relationship between vessel speed and the probability of a lethal strike, as implemented in the risk engine of this platform.' },
    { title: 'Ocean Biodiversity Information System (OBIS) — marine occurrence records',
      meta: 'Open-access data repository · source of all sighting records published on this site',
      body: 'Aggregated and quality-controlled marine biodiversity occurrence data contributed by institutions worldwide, accessed through the OBIS API.' },
    { title: 'NOAA SanctSound daily presence products (ERDDAP)',
      meta: 'Acoustic detection datasets · source of the daily presence format used for forecasting',
      body: 'Daily detection summaries per hydrophone site and species, forming the temporal observations the presence forecast is trained on.' },
    { title: 'MarineCadastre AIS vessel data',
      meta: 'National AIS archives · source of the ship traffic exposure layer',
      body: 'Daily vessel position archives used to derive ship-kilometres and mean speed per grid cell.' }
  ];

  document.getElementById('res-pubs').innerHTML = pubs.map(function (p) {
    return '<article class="pub reveal in"><h4>' + p.title + '</h4>' +
      '<p class="meta">' + p.meta + '</p><p>' + esc(p.body) + '</p></article>';
  }).join('');

  var downloads = [
    { title: 'Sighting records', file: 'downloads/sightings_sample.csv', note: 'Sampled OBIS records in the published schema' },
    { title: 'Risk model metrics', file: 'downloads/ml_metrics.json', note: 'Accuracy, F1, confusion matrix, feature importance' },
    { title: 'Gridded risk features', file: 'downloads/features_grid_sample.csv', note: 'Sampled rows of the modelled ocean grid' },
    { title: 'Research notebook', file: 'downloads/Whale_Dolphin_Capstone_Colab.ipynb', note: 'Full reproducible pipeline notebook' }
  ];

  document.getElementById('res-downloads').innerHTML = downloads.map(function (d) {
    return '<article class="card reveal in"><div class="card__body">' +
      '<h3>' + esc(d.title) + '</h3>' +
      '<p class="small muted" style="margin-top:5px">' + esc(d.note) + '</p>' +
      '<a class="btn btn--ghost btn--sm mt-2" href="' + d.file + '" download>Download</a>' +
      '</div></article>';
  }).join('');

  /* ---------------- complete dataset catalogue ---------------- */
  fetch('downloads/datasets/DATASET_CATALOG.json')
    .then(function (r) { return r.json(); })
    .then(function (cat) {
      var host = document.getElementById('res-catalogue');
      if (!host) return;
      host.innerHTML = cat.files.map(function (f) {
        return '<tr>' +
          '<td class="mono" style="font-size:.8rem">' + esc(f.name) + '</td>' +
          '<td><span class="badge badge--grey">' + esc(f.group) + '</span></td>' +
          '<td class="num">' + (typeof f.rows === 'number' ? f.rows.toLocaleString('en-US') : '&ndash;') + '</td>' +
          '<td class="muted small">' + esc(f.description) + '</td>' +
          '<td class="num"><a class="btn btn--quiet btn--sm" href="downloads/datasets/' +
            esc(f.name) + '" download>Get</a></td>' +
          '</tr>';
      }).join('');
      var total = document.getElementById('cat-total');
      if (total) {
        total.textContent = cat.total_files + ' files, ' +
          cat.total_rows.toLocaleString('en-US') + ' rows in total';
      }
    })
    .catch(function () {
      var host = document.getElementById('res-catalogue');
      if (host) host.innerHTML = '<tr><td colspan="5" class="empty">The catalogue could not be loaded.</td></tr>';
    });
})();
