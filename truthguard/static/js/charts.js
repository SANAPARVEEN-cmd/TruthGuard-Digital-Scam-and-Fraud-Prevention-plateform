// TruthGuard - Dashboard Chart.js charts
(function () {
  var colors = {
    primary: '#00E5FF',
    secondary: '#6C63FF',
    accent: '#00FFB2',
    danger: '#FF4D6D',
    warning: '#FFC857',
    success: '#2ECC71',
    muted: '#AAB3C5',
  };

  var threatColors = {
    safe: colors.success,
    low: colors.accent,
    medium: colors.warning,
    high: '#FF8C42',
    critical: colors.danger,
  };

  function initCharts() {
    if (!window.dashboardData || typeof Chart === 'undefined') return;

    var data = window.dashboardData;
    Chart.defaults.color = colors.muted;
    Chart.defaults.borderColor = 'rgba(255,255,255,0.08)';

    var threatEl = document.getElementById('threatChart');
    if (threatEl && data.threatDistribution.length) {
      new Chart(threatEl, {
        type: 'doughnut',
        data: {
          labels: data.threatDistribution.map(function (d) { return d.threat_level; }),
          datasets: [{
            data: data.threatDistribution.map(function (d) { return d.count; }),
            backgroundColor: data.threatDistribution.map(function (d) {
              return threatColors[d.threat_level] || colors.muted;
            }),
            borderWidth: 0,
          }],
        },
        options: { plugins: { legend: { position: 'bottom' } }, cutout: '65%' },
      });
    }

    var typeEl = document.getElementById('entityTypeChart');
    if (typeEl && data.entityTypeDistribution.length) {
      new Chart(typeEl, {
        type: 'pie',
        data: {
          labels: data.entityTypeDistribution.map(function (d) { return d.entity_type; }),
          datasets: [{
            data: data.entityTypeDistribution.map(function (d) { return d.count; }),
            backgroundColor: [colors.primary, colors.secondary, colors.accent],
            borderWidth: 0,
          }],
        },
        options: { plugins: { legend: { position: 'bottom' } } },
      });
    }

    var timelineEl = document.getElementById('timelineChart');
    if (timelineEl) {
      new Chart(timelineEl, {
        type: 'line',
        data: {
          labels: data.reportsTimeline.map(function (d) { return d.date; }),
          datasets: [{
            label: 'Reports',
            data: data.reportsTimeline.map(function (d) { return d.count; }),
            borderColor: colors.primary,
            backgroundColor: 'rgba(0,229,255,0.1)',
            fill: true,
            tension: 0.4,
          }],
        },
        options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
      });
    }

    var alertEl = document.getElementById('alertChart');
    if (alertEl && data.alertSeverity.length) {
      new Chart(alertEl, {
        type: 'bar',
        data: {
          labels: data.alertSeverity.map(function (d) { return d.severity; }),
          datasets: [{
            data: data.alertSeverity.map(function (d) { return d.count; }),
            backgroundColor: data.alertSeverity.map(function (d) {
              return threatColors[d.severity] || colors.muted;
            }),
            borderRadius: 6,
          }],
        },
        options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
      });
    }
  }

  document.addEventListener('DOMContentLoaded', initCharts);
})();
