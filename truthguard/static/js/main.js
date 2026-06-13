// TruthGuard - global UI micro-interactions
// NOTE: no backend changes. This file is safe to load on every page.

(function () {
  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    // Mobile navbar hamburger toggle
    var hamburger = document.getElementById('hamburger');
    var navMenu = document.getElementById('navMenu');

    if (hamburger && navMenu) {
      hamburger.addEventListener('click', function () {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
      });

      // Close menu when a link is clicked (mobile)
      navMenu.addEventListener('click', function (e) {
        var target = e.target;
        if (target && target.tagName === 'A') {
          hamburger.classList.remove('active');
          navMenu.classList.remove('active');
        }
      });
    }

    // Close results panels / modals helpers (progressive enhancement)
    // If a close button exists, hide the closest container.
    document.addEventListener('click', function (e) {
      var el = e.target;
      if (!el) return;

      // Generic: closeResults button
      if (el.id === 'closeResults') {
        var results = document.getElementById('resultsSection');
        if (results) results.style.display = 'none';

        // Some pages use inline style display:none; this ensures it stays hidden.
        var noResults = document.getElementById('noResultsSection');
        if (noResults) noResults.style.display = 'none';
      }

      // Generic: close modal buttons
      if (el.id === 'closeSuccessModal' || el.id === 'closeSuccessModalBtn') {
        var modal = document.getElementById('successModal');
        if (modal) modal.style.display = 'none';

        var backdrop = document.getElementById('modalBackdrop');
        if (backdrop) backdrop.style.display = 'none';
      }

      if (el.id === 'modalBackdrop') {
        var modal2 = document.getElementById('successModal');
        if (modal2) modal2.style.display = 'none';
        el.style.display = 'none';
      }
    });

    // Form input focus states: add data attribute for styling
    document.addEventListener('focusin', function (e) {
      var t = e.target;
      if (!t || !(t instanceof HTMLElement)) return;
      if (t.matches('input, select, textarea')) {
        t.dataset.focused = 'true';
      }
    });

    document.addEventListener('focusout', function (e) {
      var t = e.target;
      if (!t || !(t instanceof HTMLElement)) return;
      if (t.matches('input, select, textarea')) {
        delete t.dataset.focused;
      }
    });

    // Navbar glass effect on scroll
    var navbar = document.getElementById('navbar');
    if (navbar) {
      window.addEventListener('scroll', function () {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
      });
    }

    // Auto-dismiss messages
    document.querySelectorAll('.alert-message').forEach(function (msg) {
      setTimeout(function () {
        msg.style.opacity = '0';
        setTimeout(function () { msg.remove(); }, 300);
      }, 5000);
    });
  });
})();
