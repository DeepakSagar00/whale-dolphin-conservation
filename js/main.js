/* Shared behaviour for the Intelligent Whale & Dolphin Conservation Platform */
(function () {
  'use strict';

  /* ---------- mobile navigation ---------- */
  var toggle = document.querySelector('.nav__toggle');
  var nav = document.getElementById('primary-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', nav.classList.contains('open') ? 'true' : 'false');
    });
  }

  /* ---------- mark active nav item ---------- */
  var here = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  document.querySelectorAll('.nav a[href], .nav__menu a[href]').forEach(function (a) {
    var href = (a.getAttribute('href') || '').split('#')[0].toLowerCase();
    if (href && href === here) a.classList.add('active');
  });

  /* ---------- reveal on scroll ---------- */
  var revealables = document.querySelectorAll('.reveal');
  if (revealables.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealables.forEach(function (el) { io.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- helpers shared by pages ---------- */
  window.SITE = {
    data: window.SITE_DATA || { species: [], sightings: [], metrics: {}, gridRisk: {} },

    statusClass: function (s) {
      return { LC: 'badge--lc', VU: 'badge--vu', EN: 'badge--en', DD: 'badge--dd' }[s] || 'badge--dd';
    },

    speciesById: function (id) {
      return this.data.species.filter(function (s) { return s.id === id; })[0] || null;
    },

    escapeHtml: function (str) {
      return String(str == null ? '' : str)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    },

    /* weighted centre of a set of lat/lon points */
    centroid: function (points) {
      if (!points.length) return null;
      var x = 0, y = 0, z = 0;
      points.forEach(function (p) {
        var la = p.lat * Math.PI / 180, lo = p.lon * Math.PI / 180;
        x += Math.cos(la) * Math.cos(lo);
        y += Math.cos(la) * Math.sin(lo);
        z += Math.sin(la);
      });
      var n = points.length;
      x /= n; y /= n; z /= n;
      return {
        lat: Math.atan2(z, Math.sqrt(x * x + y * y)) * 180 / Math.PI,
        lon: Math.atan2(y, x) * 180 / Math.PI
      };
    },

    /* nice number formatting */
    fmt: function (n) {
      return Number(n).toLocaleString('en-US');
    }
  };

  /* ---------- footer year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
