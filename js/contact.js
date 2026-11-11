/* Contact form - client-side validation and confirmation */
(function () {
  'use strict';
  var form = document.getElementById('contact-form');
  if (!form) return;
  var error = document.getElementById('cf-error');
  var note = document.getElementById('cf-note');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = document.getElementById('cf-name').value.trim();
    var email = document.getElementById('cf-email').value.trim();
    var msg = document.getElementById('cf-msg').value.trim();
    var ok = name && email && msg && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    if (!ok) {
      error.style.display = 'block';
      note.style.display = 'none';
      return;
    }
    error.style.display = 'none';
    note.style.display = 'block';
    form.reset();
  });
})();
