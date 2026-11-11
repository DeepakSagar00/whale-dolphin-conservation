/* Application shell behaviour: navigation rail, connection status, user chip,
   global search and scroll reveal. */
(function () {
  'use strict';

  /* ---------------- navigation rail ---------------- */
  var sidebar = document.getElementById('sidebar');
  var scrim = document.getElementById('sidebar-scrim');
  var toggle = document.getElementById('sidebar-toggle');

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    if (scrim) scrim.classList.remove('show');
  }

  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      if (scrim) scrim.classList.toggle('show', sidebar.classList.contains('open'));
    });
  }
  if (scrim) scrim.addEventListener('click', closeSidebar);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeSidebar();
  });

  /* ---------------- connection indicator ---------------- */
  function setConnection(online, label) {
    var box = document.getElementById('conn-status');
    if (!box) return;
    box.className = 'conn ' + (online ? 'conn--on' : 'conn--off');
    var span = box.querySelector('span');
    if (span) span.textContent = label || (online ? 'API connected' : 'API offline');
  }

  /* ---------------- user chip ---------------- */
  function paintUser() {
    var chip = document.getElementById('user-name');
    var initial = document.getElementById('user-initial');
    if (!chip) return;
    var user = null;
    try { user = JSON.parse(localStorage.getItem('wd_user') || 'null'); } catch (e) { user = null; }
    if (user && user.username) {
      chip.textContent = user.username;
      if (initial) initial.textContent = user.username.charAt(0).toUpperCase();
    } else {
      chip.textContent = 'Researcher';
      if (initial) initial.textContent = 'R';
    }
  }

  /* ---------------- global search ---------------- */
  function initSearch() {
    var input = document.getElementById('global-search');
    if (!input) return;
    input.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter') return;
      var q = (input.value || '').trim();
      if (!q) return;
      location.href = 'species.html?q=' + encodeURIComponent(q);
    });
  }

  /* ---------------- reveal on scroll ---------------- */
  function initReveal() {
    var items = document.querySelectorAll('.reveal');
    if (!items.length) return;
    if (!('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ---------------- boot ---------------- */
  document.addEventListener('DOMContentLoaded', function () {
    paintUser();
    initSearch();
    initReveal();

    if (window.API && typeof window.API.health === 'function') {
      window.API.health().then(function (h) {
        if (h) setConnection(true, 'API connected');
        else setConnection(false, 'API offline');
      }).catch(function () { setConnection(false, 'API offline'); });
    } else {
      setConnection(false, 'local mode');
    }
  });

  window.SHELL = { setConnection: setConnection, paintUser: paintUser };
})();
