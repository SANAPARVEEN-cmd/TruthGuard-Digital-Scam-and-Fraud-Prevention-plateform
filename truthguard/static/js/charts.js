/**
 * TruthGuard Analytics Charts
 * Fixes empty chart containers: Threat Level Distribution, Entity Types, Reports Timeline
 * Requires Chart.js — add to base.html or dashboard.html:
 *   <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
 */

document.addEventListener('DOMContentLoaded', function () {

  // ─── Common chart defaults (dark cybersecurity theme) ───────────────────────
  Chart.defaults.color = '#94a3b8';
  Chart.defaults.borderColor = 'rgba(255,255,255,0.07)';
  Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";

  // ─── 1. Threat Level Distribution — Doughnut chart ──────────────────────────
  const threatCtx = document.getElementById('threatLevelChart');
  if (threatCtx) {
    new Chart(threatCtx, {
      type: 'doughnut',
      data: {
        labels: ['Critical', 'High', 'Medium', 'Low'],
        datasets: [{
          data: [127, 342, 891, 2871],
          backgroundColor: [
            'rgba(220, 38, 38, 0.85)',   // critical — red
            'rgba(249, 115, 22, 0.85)',  // high     — orange
            'rgba(234, 179, 8, 0.85)',   // medium   — amber
            'rgba(34, 197, 94, 0.85)',   // low      — green
          ],
          borderColor: [
            '#dc2626',
            '#f97316',
            '#eab308',
            '#22c55e',
          ],
          borderWidth: 2,
          hoverOffset: 10,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 20,
              usePointStyle: true,
              pointStyle: 'rectRounded',
              font: { size: 13 },
              color: '#94a3b8',
            }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            borderColor: 'rgba(6, 182, 212, 0.4)',
            borderWidth: 1,
            titleColor: '#e2e8f0',
            bodyColor: '#94a3b8',
            padding: 12,
            callbacks: {
              label: (ctx) => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = ((ctx.parsed / total) * 100).toFixed(1);
                return `  ${ctx.label}: ${ctx.parsed.toLocaleString()} (${pct}%)`;
              }
            }
          }
        },
      }
    });
  }

  // ─── 2. Entity Types — Horizontal Bar chart ──────────────────────────────────
  const entityCtx = document.getElementById('entityTypesChart');
  if (entityCtx) {
    new Chart(entityCtx, {
      type: 'bar',
      data: {
        labels: ['Phone Numbers', 'Email Addresses', 'URLs', 'Domains', 'IP Addresses'],
        datasets: [{
          label: 'Count',
          data: [4231, 3124, 2876, 1543, 769],
          backgroundColor: [
            'rgba(6, 182, 212, 0.75)',
            'rgba(99, 102, 241, 0.75)',
            'rgba(236, 72, 153, 0.75)',
            'rgba(249, 115, 22, 0.75)',
            'rgba(34, 197, 94, 0.75)',
          ],
          borderColor: [
            '#06b6d4',
            '#6366f1',
            '#ec4899',
            '#f97316',
            '#22c55e',
          ],
          borderWidth: 1.5,
          borderRadius: 6,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',   // horizontal bars
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            borderColor: 'rgba(6, 182, 212, 0.4)',
            borderWidth: 1,
            titleColor: '#e2e8f0',
            bodyColor: '#94a3b8',
            padding: 12,
            callbacks: {
              label: (ctx) => `  ${ctx.parsed.x.toLocaleString()} entities`
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.06)' },
            ticks: { color: '#64748b' },
            border: { color: 'rgba(255,255,255,0.07)' }
          },
          y: {
            grid: { display: false },
            ticks: { color: '#94a3b8', font: { size: 12 } },
            border: { color: 'rgba(255,255,255,0.07)' }
          }
        }
      }
    });
  }

  // ─── 3. Reports Timeline (7 Days) — Line chart ───────────────────────────────
  const timelineCtx = document.getElementById('reportsTimelineChart');
  if (timelineCtx) {
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    new Chart(timelineCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Critical',
            data: [18, 22, 15, 31, 27, 19, 25],
            borderColor: '#dc2626',
            backgroundColor: 'rgba(220, 38, 38, 0.10)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#dc2626',
            pointRadius: 4,
            pointHoverRadius: 7,
            borderWidth: 2,
          },
          {
            label: 'High',
            data: [45, 60, 52, 70, 65, 48, 58],
            borderColor: '#f97316',
            backgroundColor: 'rgba(249, 115, 22, 0.08)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#f97316',
            pointRadius: 4,
            pointHoverRadius: 7,
            borderWidth: 2,
          },
          {
            label: 'Medium',
            data: [110, 95, 130, 120, 140, 105, 118],
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6, 182, 212, 0.08)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#06b6d4',
            pointRadius: 4,
            pointHoverRadius: 7,
            borderWidth: 2,
          },
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: {
              usePointStyle: true,
              pointStyle: 'circle',
              padding: 18,
              color: '#94a3b8',
              font: { size: 12 }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            borderColor: 'rgba(6, 182, 212, 0.4)',
            borderWidth: 1,
            titleColor: '#e2e8f0',
            bodyColor: '#94a3b8',
            padding: 12,
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: '#64748b' },
            border: { color: 'rgba(255,255,255,0.07)' }
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: '#64748b' },
            border: { color: 'rgba(255,255,255,0.07)' }
          }
        }
      }
    });
  }

  // ─── KPI counter animation (if not already in dashboard.js) ─────────────────
  document.querySelectorAll('.kpi-value[data-value]').forEach(el => {
    const target = parseInt(el.dataset.value, 10);
    if (!target) return;
    let current = 0;
    const step = Math.ceil(target / 60);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current.toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 16);
  });

});