/* Research & Insights - datasets, findings, references and downloads */
(function () {
  'use strict';
  var D = window.SITE_DATA;
  var esc = window.SITE.escapeHtml;

  /* ---------------- datasets ---------------- */
  var sightings = D.sightings;
  var years = sightings.map(function (s) { return parseInt(s.date.slice(0, 4), 10); })
    .filter(function (y) { return !isNaN(y); });
  var yMin = Math.min.apply(null, years);
  var yMax = Math.max.apply(null, years);

  var datasets = [
    {
      title: 'OBIS occurrence records',
      body: 'Species occurrence records for humpback whale (Megaptera novaeangliae) and spinner dolphin ' +
            '(Stenella longirostris), retrieved from the Ocean Biodiversity Information System. ' +
            'The explorer publishes a sample of ' + sightings.length + ' records; the working dataset holds ' +
            '10,000 and 1,500 respectively.',
      meta: sightings.length + ' records published &middot; ' + yMin + '&ndash;' + yMax
    },
    {
      title: 'Acoustic monitoring archive',
      body: 'Underwater recordings processed into 5-second windows and 128-band log-mel spectrograms. ' +
            'The classifier is trained on blue, fin, humpback and killer whale calls, bottlenose dolphin ' +
            'whistles and ship-noise-only background samples.',
      meta: '6 classes &middot; noise-mixed at 0&ndash;20 dB SNR'
    },
    {
      title: 'AIS vessel tracks',
      body: 'MarineCadastre vessel positions reduced to ship-kilometres per grid cell and per week, ' +
            'combined with a logistic lethality curve relating speed to strike probability.',
      meta: 'MarineCadastre &middot; Southern California Bight'
    },
    {
      title: 'Gridded risk features',
      body: 'A modelled ocean grid of depth, sea-surface temperature, vessel intensity, fishing ' +
            'intensity, noise proxy, protected-area membership and habitat suitability, with a ' +
            'conservation risk class assigned to every cell.',
      meta: D.gridRisk.total.toLocaleString('en-US') + ' grid cells'
    },
    {
      title: 'Environmental layers',
      body: 'Environmental context layers used to score habitat suitability for each species, ' +
            'including bathymetry and sea-surface temperature products.',
      meta: 'Depth, SST, habitat suitability'
    },
    {
      title: 'Model runs and metrics',
      body: 'Every training run records its parameters, metrics and model artefacts so results ' +
            'remain reproducible and comparable between experiments.',
      meta: 'MLflow-compatible tracking'
    }
  ];

  document.getElementById('res-datasets').innerHTML = datasets.map(function (d) {
    return '<article class="card reveal in"><div class="card__body">' +
      '<h3>' + d.title + '</h3>' +
      '<p class="mt-2">' + d.body + '</p>' +
      '<p class="mt-3" style="font-size:.82rem;color:var(--teal-500);font-weight:600">' + d.meta + '</p>' +
      '</div></article>';
  }).join('');

  /* ---------------- findings (real measured metrics) ---------------- */
  var m = D.metrics;
  var findings = [
    {
      title: 'Risk model separates risk classes reliably',
      body: 'The gradient-boosted risk classifier reaches ' + m.accuracy + '% accuracy and ' +
            m.f1 + ' weighted F1 across the four conservation risk classes on held-out grid cells, ' +
            'with a multi-class ROC AUC of ' + m.rocAuc + '.',
      stat: m.accuracy + '%', statLabel: 'Accuracy'
    },
    {
      title: 'Vessel traffic dominates the risk signal',
      body: 'Vessel intensity (' + (m.featureImportance.vessel_intensity * 100).toFixed(1) + '% of feature ' +
            'importance) and the noise proxy (' + (m.featureImportance.noise_proxy * 100).toFixed(1) + '%) ' +
            'explain far more of the risk variation than habitat suitability or species density.',
      stat: (m.featureImportance.vessel_intensity * 100).toFixed(1) + '%', statLabel: 'Top feature'
    },
    {
      title: 'Detection history predicts presence',
      body: 'Rolling detection rates over 7, 14 and 30 days, combined with day-of-year seasonality, ' +
            'allow the presence model to anticipate whether a species will be present in the following week.',
      stat: '7 / 14 / 30d', statLabel: 'Rate windows'
    }
  ];

  document.getElementById('res-findings').innerHTML = findings.map(function (f) {
    return '<article class="card reveal in"><div class="card__body">' +
      '<div style="font-size:1.6rem;font-weight:800;color:var(--teal-500)">' + f.stat + '</div>' +
      '<div style="font-size:.76rem;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-400);margin-bottom:10px">' +
        esc(f.statLabel) + '</div>' +
      '<h3>' + esc(f.title) + '</h3>' +
      '<p class="mt-2">' + f.body + '</p>' +
      '</div></article>';
  }).join('');

  /* ---------------- publications & references ---------------- */
  var pubs = [
    {
      title: 'Vanderlaan, J. M. &amp; Taggart, C. T. (2007) &mdash; Vessel collisions with whales: the probability of lethal injury based on vessel speed',
      meta: 'Marine Mammal Science 23(1) &middot; methods reference for the lethality curve used in the risk engine',
      body: 'The logistic relationship between vessel speed and the probability of a lethal strike, ' +
            'as implemented in the risk engine of this platform.'
    },
    {
      title: 'Ocean Biodiversity Information System (OBIS) &mdash; marine occurrence records',
      meta: 'Open-access data repository &middot; source of all sighting records published on this site',
      body: 'Aggregated and quality-controlled marine biodiversity occurrence data contributed by ' +
            'institutions worldwide, accessed through the OBIS API.'
    },
    {
      title: 'NOAA SanctSound daily presence products (ERDDAP)',
      meta: 'Acoustic detection datasets &middot; source of the daily presence format used for forecasting',
      body: 'Daily detection summaries per hydrophone site and species, forming the temporal ' +
            'observations the presence forecast is trained on.'
    },
    {
      title: 'MarineCadastre AIS vessel data',
      meta: 'National AIS archives &middot; source of the ship traffic exposure layer',
      body: 'Daily vessel position archives used to derive ship-kilometres and mean speed per grid cell.'
    }
  ];

  document.getElementById('res-pubs').innerHTML = pubs.map(function (p) {
    return '<article class="pub reveal in"><h4>' + p.title + '</h4>' +
      '<p class="meta">' + p.meta + '</p><p>' + p.body + '</p></article>';
  }).join('');

  /* ---------------- downloadable resources ---------------- */
  var downloads = [
    { title: 'Sighting records (CSV)', file: 'downloads/sightings_sample.csv', note: 'Sampled OBIS records in the published schema' },
    { title: 'Risk model metrics (JSON)', file: 'downloads/ml_metrics.json', note: 'Accuracy, F1, confusion matrix, feature importance' },
    { title: 'Gridded risk features (CSV)', file: 'downloads/features_grid_sample.csv', note: 'Sampled rows of the modelled ocean grid' },
    { title: 'Colab research notebook', file: 'downloads/Whale_Dolphin_Capstone_Colab.ipynb', note: 'Full reproducible pipeline notebook' }
  ];

  document.getElementById('res-downloads').innerHTML = downloads.map(function (d) {
    return '<article class="card reveal in"><div class="card__body">' +
      '<h3 style="font-size:1rem">' + esc(d.title) + '</h3>' +
      '<p class="mt-2" style="font-size:.86rem">' + esc(d.note) + '</p>' +
      '<a class="btn btn--outline btn--sm mt-3" href="' + d.file + '" download>Download</a>' +
      '</div></article>';
  }).join('');
})();
