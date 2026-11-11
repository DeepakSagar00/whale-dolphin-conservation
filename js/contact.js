/* Contact form — client-side validation and confirmation. */
(function () {
  'use strict';
  var form = document.getElementById('contact-form');
  if (!form) return;

  var note = document.getElementById('cf-note');

  function mark(id, valid) {
    var field = document.getElementById(id).closest('.field');
    if (field) field.classList.toggle('field--invalid', !valid);
    return valid;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = document.getElementById('cf-name').value.trim();
    var email = document.getElementById('cf-email').value.trim();
    var msg = document.getElementById('cf-msg').value.trim();

    var ok = true;
    if (!mark('cf-name', !!name)) ok = false;
    if (!mark('cf-email', !!email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))) ok = false;
    if (!mark('cf-msg', !!msg)) ok = false;

    if (!ok) {
      if (note) note.style.display = 'none';
      return;
    }
    if (note) note.style.display = 'block';
    form.reset();
  });

  ['cf-name', 'cf-email', 'cf-msg'].forEach(function (id) {
    var node = document.getElementById(id);
    if (node) node.addEventListener('input', function () { mark(id, true); });
  });
})();
