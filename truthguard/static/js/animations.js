// TruthGuard - animations
(function () {
  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    // Scroll reveal
    var revealNodes = document.querySelectorAll('.reveal, .scroll-reveal');
    if ('IntersectionObserver' in window && revealNodes.length) {
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            obs.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });
      revealNodes.forEach(function (n) { obs.observe(n); });
    } else {
      revealNodes.forEach(function (n) { n.classList.add('visible'); });
    }

    // Counter animations
    var counters = document.querySelectorAll('.counter');
    if ('IntersectionObserver' in window && counters.length) {
      var counterObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          var target = parseFloat(el.dataset.target || '0');
          var duration = 1500;
          var start = performance.now();
          var isFloat = target % 1 !== 0;

          function step(now) {
            var progress = Math.min((now - start) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = target * eased;
            el.textContent = isFloat ? current.toFixed(1) : Math.floor(current);
            if (progress < 1) requestAnimationFrame(step);
          }
          requestAnimationFrame(step);
          counterObs.unobserve(el);
        });
      }, { threshold: 0.5 });
      counters.forEach(function (c) { counterObs.observe(c); });
    }

    // Ripple effect
    document.querySelectorAll('.ripple').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        var rect = btn.getBoundingClientRect();
        var ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        ripple.style.left = (e.clientX - rect.left) + 'px';
        ripple.style.top = (e.clientY - rect.top) + 'px';
        btn.appendChild(ripple);
        setTimeout(function () { ripple.remove(); }, 600);
      });
    });
  });
})();

