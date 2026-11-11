/* API client for the Whale & Dolphin Conservation backend.
   Falls back to local, in-browser computation when the API is unreachable so
   the interface never shows a fake result or a dead state. */
(function () {
  'use strict';

  var CFG = window.APP_CONFIG || {};
  var BASE = (CFG.apiBaseUrl || '').replace(/\/$/, '');
  var TOKEN_KEY = 'wd_token';
  var USER_KEY = 'wd_user';

  var state = {
    base: BASE,
    online: null,          // null = not tested yet
    lastError: null
  };

  function token() {
    try { return localStorage.getItem(TOKEN_KEY); } catch (e) { return null; }
  }
  function setToken(t, user) {
    try {
      if (t) { localStorage.setItem(TOKEN_KEY, t); localStorage.setItem(USER_KEY, JSON.stringify(user || {})); }
      else { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); }
    } catch (e) { /* private mode */ }
  }
  function currentUser() {
    try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null'); } catch (e) { return null; }
  }

  function authHeaders(extra) {
    var h = extra || {};
    var t = token();
    if (t) h.Authorization = 'Bearer ' + t;
    return h;
  }

  function request(path, options) {
    options = options || {};
    var url = state.base + path;
    var opts = {
      method: options.method || 'GET',
      headers: authHeaders(options.headers),
      body: options.body
    };
    return fetch(url, opts).then(function (r) {
      var ct = r.headers.get('content-type') || '';
      if (ct.indexOf('application/json') > -1) {
        return r.json().then(function (data) {
          if (!r.ok) { var e = new Error(data.detail || ('Request failed (' + r.status + ')')); e.status = r.status; throw e; }
          return data;
        });
      }
      if (!r.ok) { var e2 = new Error('Request failed (' + r.status + ')'); e2.status = r.status; throw e2; }
      return r.text();
    }).catch(function (err) {
      state.online = false;
      state.lastError = err.message;
      throw err;
    });
  }

  function json(path, method, body) {
    return request(path, {
      method: method || 'GET',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    });
  }

  function multipart(path, file, extraFields) {
    var fd = new FormData();
    fd.append('file', file, file.name);
    if (extraFields) {
      Object.keys(extraFields).forEach(function (k) { fd.append(k, extraFields[k]); });
    }
    return request(path, { method: 'POST', body: fd });
  }

  var API = {
    state: state,

    isOnline: function () { return state.online !== false; },

    baseUrl: function () { return state.base; },

    setBaseUrl: function (url) {
      state.base = (url || '').replace(/\/$/, '');
      state.online = null;
    },

    token: token,
    currentUser: currentUser,
    logout: function () { setToken(null); },

    /* Probe the API so the UI can show an honest connection banner. */
    health: function () {
      return request('/api/health')
        .then(function (data) { state.online = true; return data; })
        .catch(function () { state.online = false; return null; });
    },

    login: function (username, password) {
      return json('/api/auth/login', 'POST', { username: username, password: password })
        .then(function (data) {
          setToken(data.token, { username: data.username, role: data.role });
          state.online = true;
          return data;
        });
    },

    register: function (username, email, password) {
      return json('/api/auth/register', 'POST', { username: username, email: email, password: password })
        .then(function (data) {
          setToken(data.token, { username: data.username, role: data.role });
          state.online = true;
          return data;
        });
    },

    /* ---------------- bioacoustics ---------------- */
    analyzeAudio: function (file) {
      return multipart('/api/audio/analyze', file);
    },

    classifyAudioPcm: function (pcmBuffer, filename) {
      var blob = new Blob([pcmBuffer], { type: 'application/octet-stream' });
      var fd = new FormData();
      fd.append('file', blob, filename || 'recording.f32');
      return request('/api/audio/classify', { method: 'POST', body: fd });
    },

    audioHistory: function () { return request('/api/audio/history'); },

    deleteAudioHistory: function (id) {
      return request('/api/audio/history/' + id, { method: 'DELETE' });
    },

    /* ---------------- image identification ---------------- */
    identifyImage: function (file) {
      return multipart('/api/image/identify', file);
    },

    imageHistory: function () { return request('/api/image/history'); },

    /* ---------------- simulator ---------------- */
    simulate: function (group, species, turns) {
      return json('/api/simulator/conversation', 'POST', { group: group, species: species, turns: turns });
    },

    simulatorSpecies: function () { return request('/api/simulator/species'); },

    /* ---------------- public reference data ---------------- */
    speciesDirectory: function () { return request('/api/species/directory'); },
    publicStats: function () { return request('/api/public/stats'); },
    publicSightings: function (params) {
      var q = [];
      if (params && params.limit) q.push('limit=' + params.limit);
      if (params && params.species_id) q.push('species_id=' + params.species_id);
      if (params && params.bbox) q.push('bbox=' + encodeURIComponent(params.bbox));
      return request('/api/public/sightings' + (q.length ? '?' + q.join('&') : ''));
    },
    modelsStatus: function () { return request('/api/models/status'); }
  };

  window.API = API;
})();
