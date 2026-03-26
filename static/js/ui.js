// Global notification system
window.showToast = function(text, tag) {
    if (!text) return;
    
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

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
};

document.addEventListener('DOMContentLoaded', function () {
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

  // --- Tab Session Isolation Guard ---
  (function () {
    const path = window.location.pathname;
    const isProtected = path.includes('/buyer/') || 
                        path.includes('/seller/') || 
                        path.includes('/messages/') || 
                        path.includes('/profile/');

    if (isProtected) {
      if (!sessionStorage.getItem('tab_verified')) {
        console.warn('New tab detected. Redirecting to sign-in for security.');
        window.location.href = "/signin/?reason=new_tab";
      }
    }
  })();
});
