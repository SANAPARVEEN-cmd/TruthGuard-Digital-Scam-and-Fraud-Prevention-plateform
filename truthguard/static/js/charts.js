/**
 * TruthGuard Dashboard Charts
 * Uses real data from window.dashboardData (passed by Django view)
 * Canvas IDs match dashboard/index.html exactly
 */

document.addEventListener('DOMContentLoaded', function () {

  // ── Chart.js global defaults ───────────────────────────────────────────────
  Chart.defaults.color          = '#94a3b8';
  Chart.defaults.borderColor    = 'rgba(255,255,255,0.07)';
  Chart.defaults.font.family    = "'Inter','Segoe UI',sans-serif";

  const data = window.dashboardData || {};

  // ── Helper: parse Django JSON data ────────────────────────────────────────
  function parseDistribution(raw, keyField, valueField) {
    if (!raw || !raw.length) return { labels: [], values: [] };
    return {
      labels: raw.map(d => d[keyField]),
      values: raw.map(d => d[valueField]),
    };
  }

  // ── Tooltip shared style ──────────────────────────────────────────────────
  const tooltipStyle = {
    backgroundColor: 'rgba(15,23,42,0.95)',
    borderColor:     'rgba(6,182,212,0.4)',
    borderWidth:     1,
    titleColor:      '#e2e8f0',
    bodyColor:       '#94a3b8',
    padding:         12,
  };

  // ══════════════════════════════════════════════════════════════════════════
  // 1. Threat Level Distribution — Doughnut  →  canvas id="threatChart"
  // ══════════════════════════════════════════════════════════════════════════
  const threatCtx = document.getElementById('threatChart');
  if (threatCtx) {
    const dist   = parseDistribution(data.threatDistribution, 'threat_level', 'count');

    // Label map for display
    const labelMap = { safe:'Safe', low:'Low', medium:'Medium', high:'High', critical:'Critical' };
    const colorMap = {
      safe:     'rgba(34,197,94,0.85)',
      low:      'rgba(134,239,172,0.85)',
      medium:   'rgba(234,179,8,0.85)',
      high:     'rgba(249,115,22,0.85)',
      critical: 'rgba(220,38,38,0.85)',
    };
    const borderMap = {
      safe:'#22c55e', low:'#86efac', medium:'#eab308', high:'#f97316', critical:'#dc2626'
    };

    // Use real data if available, else fallback demo data
    const labels = dist.labels.length
      ? dist.labels.map(l => labelMap[l] || l)
      : ['Critical','High','Medium','Low'];
    const values = dist.values.length
      ? dist.values
      : [127, 342, 891, 2871];
    const bgColors     = dist.labels.length ? dist.labels.map(l => colorMap[l]   || 'rgba(148,163,184,0.7)') : Object.values(colorMap).reverse();
    const borderColors = dist.labels.length ? dist.labels.map(l => borderMap[l]  || '#94a3b8')               : Object.values(borderMap).reverse();

    new Chart(threatCtx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: bgColors,
          borderColor:     borderColors,
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
            labels: { padding:20, usePointStyle:true, pointStyle:'rectRounded', font:{size:12}, color:'#94a3b8' }
          },
          tooltip: {
            ...tooltipStyle,
            callbacks: {
              label: ctx => {
                const total = ctx.dataset.data.reduce((a,b) => a+b, 0);
                const pct   = ((ctx.parsed / total) * 100).toFixed(1);
                return `  ${ctx.label}: ${ctx.parsed.toLocaleString()} (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 2. Entity Types — Horizontal Bar  →  canvas id="entityTypeChart"
  // ══════════════════════════════════════════════════════════════════════════
  const entityCtx = document.getElementById('entityTypeChart');
  if (entityCtx) {
    const dist = parseDistribution(data.entityTypeDistribution, 'entity_type', 'count');

    const typeLabel = { phone:'Phone Numbers', email:'Email Addresses', website:'Websites' };
    const labels = dist.labels.length
      ? dist.labels.map(l => typeLabel[l] || l)
      : ['Phone Numbers','Email Addresses','URLs','Domains','IP Addresses'];
    const values = dist.values.length
      ? dist.values
      : [4231, 3124, 2876, 1543, 769];

    const bgColors = [
      'rgba(6,182,212,0.75)',
      'rgba(99,102,241,0.75)',
      'rgba(236,72,153,0.75)',
      'rgba(249,115,22,0.75)',
      'rgba(34,197,94,0.75)',
    ];
    const borderColors = ['#06b6d4','#6366f1','#ec4899','#f97316','#22c55e'];

    new Chart(entityCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Count',
          data: values,
          backgroundColor: bgColors.slice(0, labels.length),
          borderColor:     borderColors.slice(0, labels.length),
          borderWidth: 1.5,
          borderRadius: 6,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
          tooltip: {
            ...tooltipStyle,
            callbacks: { label: ctx => `  ${ctx.parsed.x.toLocaleString()} entities` }
          }
        },
        scales: {
          x: { grid:{color:'rgba(255,255,255,0.06)'}, ticks:{color:'#64748b'}, border:{color:'rgba(255,255,255,0.07)'} },
          y: { grid:{display:false}, ticks:{color:'#94a3b8', font:{size:12}}, border:{color:'rgba(255,255,255,0.07)'} }
        }
      }
    });
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 3. Reports Timeline (7 Days) — Line  →  canvas id="timelineChart"
  // ══════════════════════════════════════════════════════════════════════════
  const timelineCtx = document.getElementById('timelineChart');
  if (timelineCtx) {
    // Use real timeline data if available
    let timelineLabels, timelineValues;
    if (data.reportsTimeline && data.reportsTimeline.length) {
      timelineLabels = data.reportsTimeline.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('en-US', { weekday:'short', month:'short', day:'numeric' });
      });
      timelineValues = data.reportsTimeline.map(d => d.count);
    } else {
      timelineLabels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
      timelineValues = [12, 19, 8, 25, 17, 10, 22];
    }

    new Chart(timelineCtx, {
      type: 'line',
      data: {
        labels: timelineLabels,
        datasets: [{
          label: 'Reports',
          data: timelineValues,
          borderColor:           '#06b6d4',
          backgroundColor:       'rgba(6,182,212,0.10)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor:  '#06b6d4',
          pointRadius: 4,
          pointHoverRadius: 7,
          borderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode:'index', intersect:false },
        plugins: {
          legend: {
            position:'top', align:'end',
            labels: { usePointStyle:true, pointStyle:'circle', padding:18, color:'#94a3b8', font:{size:12} }
          },
          tooltip: tooltipStyle,
        },
        scales: {
          x: { grid:{color:'rgba(255,255,255,0.05)'}, ticks:{color:'#64748b'}, border:{color:'rgba(255,255,255,0.07)'} },
          y: { grid:{color:'rgba(255,255,255,0.05)'}, ticks:{color:'#64748b'}, border:{color:'rgba(255,255,255,0.07)'}, beginAtZero:true }
        }
      }
    });
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 4. Alert Severity — Doughnut  →  canvas id="alertChart"
  // ══════════════════════════════════════════════════════════════════════════
  const alertCtx = document.getElementById('alertChart');
  if (alertCtx) {
    const dist = parseDistribution(data.alertSeverity, 'severity', 'count');

    const sevLabel  = { low:'Low', medium:'Medium', high:'High', critical:'Critical' };
    const sevColor  = { low:'rgba(34,197,94,0.85)', medium:'rgba(234,179,8,0.85)', high:'rgba(249,115,22,0.85)', critical:'rgba(220,38,38,0.85)' };
    const sevBorder = { low:'#22c55e', medium:'#eab308', high:'#f97316', critical:'#dc2626' };

    const labels = dist.labels.length
      ? dist.labels.map(l => sevLabel[l] || l)
      : ['Critical','High','Medium','Low'];
    const values = dist.values.length
      ? dist.values
      : [8, 23, 41, 15];
    const bgColors     = dist.labels.length ? dist.labels.map(l => sevColor[l]  || 'rgba(148,163,184,0.7)') : Object.values(sevColor).reverse();
    const borderColors = dist.labels.length ? dist.labels.map(l => sevBorder[l] || '#94a3b8')               : Object.values(sevBorder).reverse();

    new Chart(alertCtx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: bgColors,
          borderColor:     borderColors,
          borderWidth: 2,
          hoverOffset: 10,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position:'bottom',
            labels: { padding:16, usePointStyle:true, font:{size:12}, color:'#94a3b8' }
          },
          tooltip: {
            ...tooltipStyle,
            callbacks: {
              label: ctx => {
                const total = ctx.dataset.data.reduce((a,b) => a+b, 0);
                const pct   = ((ctx.parsed / total) * 100).toFixed(1);
                return `  ${ctx.label}: ${ctx.parsed} (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 5. KPI counter animation
  // ══════════════════════════════════════════════════════════════════════════
  document.querySelectorAll('.kpi-value[data-value], .counter[data-target]').forEach(el => {
    const target = parseInt(el.dataset.value || el.dataset.target || '0', 10);
    if (!target) return;
    let current  = 0;
    const step   = Math.ceil(target / 60);
    const timer  = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current.toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 16);
  });

  // ══════════════════════════════════════════════════════════════════════════
  // 6. Add height to canvas containers so charts are visible
  // ══════════════════════════════════════════════════════════════════════════
  ['threatChart','entityTypeChart','timelineChart','alertChart'].forEach(id => {
    const canvas = document.getElementById(id);
    if (canvas) {
      const parent = canvas.parentElement;
      if (parent && !parent.style.height) {
        parent.style.height = id === 'timelineChart' ? '280px' : '260px';
        parent.style.position = 'relative';
      }
    }
  });

});