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
    fallbacks: (CFG.apiFallbacks || []).slice(),
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

  function fetchWith(base, path, options) {
    var opts = {
      method: options.method || 'GET',
      headers: authHeaders(options.headers),
      body: options.body
    };
    var timeout = options.timeout || 15000;
    var ctrl = ('AbortController' in window) ? new AbortController() : null;
    if (ctrl) opts.signal = ctrl.signal;
    var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, timeout) : null;

    return fetch(base + path, opts).then(function (r) {
      if (timer) clearTimeout(timer);
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
      if (timer) clearTimeout(timer);
      state.lastError = err.name === 'AbortError' ? 'request timed out' : err.message;
      throw err;
    });
  }

  /* Try the configured API, then any other known endpoint, so a moved or
     restarted backend does not take the interface down with it. */
  function withFailover(call) {
    var candidates = [state.base];
    if (state.fallbacks) {
      state.fallbacks.forEach(function (b) {
        if (b && b !== state.base && candidates.indexOf(b) === -1) candidates.push(b);
      });
    }
    var i = 0;
    function attempt() {
      var base = candidates[i];
      var prev = state.base;
      state.base = base;
      return call(base).then(function (result) {
        state.base = prev;
        state.online = true;
        return result;
      }).catch(function (err) {
        state.base = prev;
        i++;
        if (i < candidates.length) return attempt();
        state.online = false;
        throw err;
      });
    }
    return attempt();
  }

  function request(path, options) {
    options = options || {};
    return withFailover(function (base) { return fetchWith(base, path, options); });
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
    signedIn: function () { return !!token(); },
    logout: function () { setToken(null); },

    /* Probe the API so the UI can show an honest connection banner. */
    health: function () {
      return withFailover(function (base) {
        var ctrl = ('AbortController' in window) ? new AbortController() : null;
        var opts = { headers: authHeaders() };
        if (ctrl) { opts.signal = ctrl.signal; setTimeout(function () { ctrl.abort(); }, 6000); }
        return fetch(base + '/api/health', opts).then(function (r) { return r.json(); });
      }).then(function (data) { state.online = true; return data; })
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

    /* ---------------- observations (GIS collection workflow) ---------------- */
    listObservations: function (params) {
      var q = [];
      if (params) {
        if (params.limit) q.push('limit=' + params.limit);
        if (params.species) q.push('species=' + encodeURIComponent(params.species));
        if (params.region) q.push('region=' + encodeURIComponent(params.region));
        if (params.date_from) q.push('date_from=' + params.date_from);
        if (params.date_to) q.push('date_to=' + params.date_to);
      }
      return request('/api/observations' + (q.length ? '?' + q.join('&') : ''));
    },

    createObservation: function (payload) {
      return json('/api/observations', 'POST', payload);
    },

    deleteObservation: function (id) {
      return request('/api/observations/' + id, { method: 'DELETE' });
    },

    dashboardOverview: function () { return request('/api/dashboard/overview'); },

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
