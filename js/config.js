/* Application configuration.
   Single place to point the front end at the deployed API.

   The API base can be overridden at runtime with a query parameter, e.g.
   index.html?api=https://my-api.example.com
   which is remembered in localStorage. */
(function () {
  var DEFAULT_API = 'https://edition-scholars-times-dialogue.trycloudflare.com';
  var KEY = 'wd_api_base';

  var params = new URLSearchParams(location.search);
  var override = params.get('api');
  if (override) {
    try { localStorage.setItem(KEY, override); } catch (e) { /* private mode */ }
  }

  var stored = null;
  try { stored = localStorage.getItem(KEY); } catch (e) { stored = null; }

  var isLocal = /^(localhost|127\.0\.0\.1)$/i.test(location.hostname);
  var base = stored || (isLocal ? 'http://127.0.0.1:8000' : DEFAULT_API);

  window.APP_CONFIG = {
    apiBaseUrl: base.replace(/\/$/, ''),
    defaultApiBaseUrl: DEFAULT_API,
    apiFallbacks: [DEFAULT_API, 'http://127.0.0.1:8000'],
    localFallback: true,
    demoUser: { username: 'researcher', password: 'researcher' }
  };
})();


