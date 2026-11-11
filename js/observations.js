/* Observation Management — structured submission form with validation, plus a
   live table of everything stored. */
(function () {
  'use strict';

  var el = function (id) { return document.getElementById(id); };
  var esc = function (t) {
    return String(t == null ? '' : t)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  };

  var SPECIES = [
    'Humpback whale', 'Spinner dolphin', 'Blue whale', 'Fin whale',
    'Killer whale', 'Bottlenose dolphin'
  ];

  function mark(id, valid) {
    var field = el(id).closest('.field');
    if (field) field.classList.toggle('field--invalid', !valid);
    return valid;
  }

  function validate() {
    var ok = true;
    var lat = parseFloat(el('of-lat').value);
    var lon = parseFloat(el('of-lon').value);
    var date = el('of-date').value;
    var count = parseInt(el('of-count').value, 10);

    if (!mark('of-species', !!el('of-species').value)) ok = false;
    if (!mark('of-lat', !isNaN(lat) && lat >= -90 && lat <= 90)) ok = false;
    if (!mark('of-lon', !isNaN(lon) && lon >= -180 && lon <= 180)) ok = false;
    if (!mark('of-date', !!date && !isNaN(Date.parse(date)))) ok = false;
    if (!mark('of-count', !isNaN(count) && count >= 1 && count <= 5000)) ok = false;
    return ok;
  }

  function notice(kind, msg) {
    var box = el('obs-notice');
    if (!box) {
      box = document.createElement('div');
      box.id = 'obs-notice';
      box.style.marginBottom = '12px';
      el('obs-form').parentElement.insertBefore(box, el('obs-form'));
    }
    box.className = 'notice notice--' + kind;
    box.textContent = msg;
    box.style.display = 'block';
  }

  function loadObservations() {
    return window.API.listObservations({ limit: 500 }).then(function (r) {
      var list = (r && r.observations) || [];
      el('obs-count').textContent = list.length +
        (list.length === 1 ? ' record stored in the platform database' : ' records stored in the platform database');
      el('obs-table').innerHTML = list.map(function (o) {
        return '<tr>' +
          '<td>' + esc(o.observed_at) + '</td>' +
          '<td>' + esc(o.common_name) + '</td>' +
          '<td class="mono">' + Number(o.lat).toFixed(3) + '</td>' +
          '<td class="mono">' + Number(o.lon).toFixed(3) + '</td>' +
          '<td class="num">' + (o.individuals == null ? '&ndash;' : o.individuals) + '</td>' +
          '<td>' + (o.count_confirmed
            ? '<span class="badge badge--lc">verified</span>'
            : '<span class="badge badge--vu">unverified</span>') + '</td>' +
          '<td class="num"><button class="btn btn--quiet btn--sm" data-del="' + o.id + '" ' +
            'title="Delete this record">Delete</button></td>' +
          '</tr>';
      }).join('') || '<tr><td colspan="7" class="empty">No observations submitted yet.</td></tr>';

      Array.prototype.forEach.call(el('obs-table').querySelectorAll('[data-del]'), function (b) {
        b.addEventListener('click', function () {
          var id = b.dataset.del;
          b.disabled = true;
          window.API.deleteObservation(id).then(function () {
            notice('ok', 'Observation #' + id + ' deleted.');
            return loadObservations();
          }).catch(function (err) {
            b.disabled = false;
            notice('err', 'The record could not be deleted: ' + err.message);
          });
        });
      });
    }).catch(function (err) {
      el('obs-count').textContent = 'unable to load records';
      notice('err', 'The observation store could not be reached: ' + err.message);
    });
  }

  function submit(e) {
    e.preventDefault();
    if (!window.API.signedIn()) {
      notice('warn', 'Sign in with your researcher account to store an observation.');
      el('obs-auth').style.display = '';
      el('oa-user').focus();
      return;
    }
    if (!validate()) {
      notice('err', 'Please complete the highlighted fields.');
      return;
    }
    var btn = el('obs-submit');
    btn.disabled = true;
    btn.textContent = 'Storing\u2026';

    var media = el('of-media').files[0];
    var payload = {
      species: el('of-species').value,
      lat: parseFloat(el('of-lat').value),
      lon: parseFloat(el('of-lon').value),
      observed_at: el('of-date').value,
      individuals: parseInt(el('of-count').value, 10) || 1,
      notes: el('of-notes').value.trim(),
      media_type: media ? (media.type.indexOf('image') === 0 ? 'photo' : 'audio') : '',
      media_filename: media ? media.name : '',
      source: 'Platform submission',
      count_confirmed: el('of-confirmed').checked
    };

    window.API.createObservation(payload).then(function (r) {
      btn.disabled = false;
      btn.textContent = 'Store observation';
      notice('ok', 'Observation stored (record #' + (r.observation ? r.observation.id : '?') +
        '). It now appears on the GIS map.');
      el('of-notes').value = '';
      el('of-media').value = '';
      ['of-species', 'of-lat', 'of-lon', 'of-date'].forEach(function (id) {
        mark(id, true);
      });
      return loadObservations();
    }).catch(function (err) {
      btn.disabled = false;
      btn.textContent = 'Store observation';
      notice('err', 'The record could not be stored: ' + err.message);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    el('of-species').innerHTML = '<option value="">Select a species</option>' +
      SPECIES.map(function (s) { return '<option value="' + s + '">' + s + '</option>'; }).join('');
    el('of-date').value = new Date().toISOString().slice(0, 10);

    el('obs-form').addEventListener('submit', submit);
    el('oa-login').addEventListener('click', function () {
      var btn = el('oa-login');
      btn.disabled = true;
      btn.textContent = 'Signing in\u2026';
      window.API.login(el('oa-user').value.trim(), el('oa-pass').value)
        .then(function () {
          btn.disabled = false;
          btn.textContent = 'Sign in';
          el('obs-auth').style.display = 'none';
          notice('ok', 'Signed in. Submit the observation to store it.');
          if (window.SHELL) window.SHELL.paintUser();
        })
        .catch(function (err) {
          btn.disabled = false;
          btn.textContent = 'Sign in';
          notice('err', 'Sign-in failed: ' + err.message +
            '. The demonstration account is researcher / researcher.');
        });
    });
    ['of-species', 'of-lat', 'of-lon', 'of-date', 'of-count'].forEach(function (id) {
      el(id).addEventListener('input', function () { mark(id, true); });
    });
    el('obs-refresh').addEventListener('click', loadObservations);

    loadObservations();
  });
})();
