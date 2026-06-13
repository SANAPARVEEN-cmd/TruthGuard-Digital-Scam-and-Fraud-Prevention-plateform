// TruthGuard - Report form interactions
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var zone = document.getElementById('uploadZone');
    var input = document.getElementById('evidenceInput');
    var btn = document.getElementById('uploadBtn');
    var fileName = document.getElementById('fileName');
    var form = document.getElementById('reportForm');
    var progress = document.getElementById('progressFill');

    if (btn && input) {
      btn.addEventListener('click', function () { input.click(); });
    }

    if (input) {
      input.addEventListener('change', function () {
        if (fileName && input.files[0]) {
          fileName.textContent = input.files[0].name;
          if (progress) progress.style.width = '75%';
        }
      });
    }

    if (zone) {
      zone.addEventListener('dragover', function (e) {
        e.preventDefault();
        zone.classList.add('drag-over');
      });
      zone.addEventListener('dragleave', function () {
        zone.classList.remove('drag-over');
      });
      zone.addEventListener('drop', function (e) {
        e.preventDefault();
        zone.classList.remove('drag-over');
        if (input && e.dataTransfer.files.length) {
          input.files = e.dataTransfer.files;
          input.dispatchEvent(new Event('change'));
        }
      });
    }

    if (form && progress) {
      form.addEventListener('input', function () {
        var filled = 0;
        ['entity_type', 'entity_value', 'description'].forEach(function (name) {
          var el = form.querySelector('[name="' + name + '"]');
          if (el && el.value.trim()) filled++;
        });
        progress.style.width = (filled / 3 * 50) + '%';
      });
    }
  });
})();
