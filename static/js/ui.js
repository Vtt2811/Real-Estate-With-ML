document.addEventListener('DOMContentLoaded', function () {
  // Create toast container
  var container = document.createElement('div');
  container.className = 'toast-container';
  document.body.appendChild(container);

  // Read hidden messages container inserted by templates
  var msgs = document.querySelectorAll('#messages .django-message');
  msgs.forEach(function (el) {
    var text = el.textContent.trim();
    var classes = el.className || '';
    var tag = 'info';
    if (classes.indexOf('error') !== -1) tag = 'error';
    if (classes.indexOf('success') !== -1) tag = 'success';
    if (classes.indexOf('warning') !== -1) tag = 'error';

    showToast(text, tag);
  });

  function showToast(text, tag) {
    if (!text) return;
    var t = document.createElement('div');
    t.className = 'toast ' + tag;
    t.textContent = text;
    container.appendChild(t);
    // force reflow to allow transition
    void t.offsetWidth;
    t.classList.add('show');
    setTimeout(function () {
      t.classList.remove('show');
      setTimeout(function () { t.remove(); }, 300);
    }, 4000);
  }
});
