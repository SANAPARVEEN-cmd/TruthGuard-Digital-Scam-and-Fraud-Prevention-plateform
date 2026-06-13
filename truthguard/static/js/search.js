// TruthGuard - Search page interactions
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var input = document.getElementById('entityInput');
    var examples = document.querySelectorAll('.example-btn');
    examples.forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (input) input.value = btn.dataset.value;
      });
    });

    var progress = document.querySelector('.risk-progress');
    if (progress) {
      var score = parseInt(progress.dataset.score || '0', 10);
      var circumference = 2 * Math.PI * 54;
      progress.style.strokeDasharray = circumference;
      progress.style.strokeDashoffset = circumference - (score / 100) * circumference;
    }
  });
})();
