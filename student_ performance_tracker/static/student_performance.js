document.addEventListener("DOMContentLoaded", function() {
  if(!window.DASH) return;
  const subjects = window.DASH.subjects.map(s => s.subject);
  const obtained = window.DASH.subjects.map(s => s.obtained);
  const maxes = window.DASH.subjects.map(s => s.max);
  const assessments = window.DASH.assessments.map(a => a.title);
  const assessmentMarks = window.DASH.assessments.map(a => a.marksObtained);
  const palette = ['#06b6d4','#7c3aed','#f97316','#10b981','#ef4444'];
  const barCtx = document.getElementById('barChart').getContext('2d');
  new Chart(barCtx, {
    type: 'bar',
    data: {
      labels: subjects,
      datasets: [
        { label: 'Obtained', data: obtained, backgroundColor: subjects.map((_,i)=>palette[i%palette.length]), borderRadius:12 },
        { label: 'Max', data: maxes, backgroundColor: 'rgba(203,213,225,0.65)', borderRadius:12 }
      ]
    },
    options: {
      responsive:true,
      plugins: { legend: { position: 'top', labels: { usePointStyle:true } }, tooltip: { mode: 'index', intersect: false } },
      interaction: { mode: 'nearest', axis: 'x', intersect: false },
      scales: { x: { grid: { display:false } }, y: { beginAtZero:true, ticks: { stepSize: 20 } } },
      animation: { duration: 900, easing: 'easeOutQuart' }
    }
  });
  const donutCtx = document.getElementById('donutChart').getContext('2d');
  const percentBySub = window.DASH.subjects.map(s => Math.round(s.obtained / s.max * 100));
  new Chart(donutCtx, {
    type: 'doughnut',
    data: { labels: subjects, datasets: [{ data: percentBySub, backgroundColor: palette, hoverOffset:14 }] },
    options: {
      responsive:true,
      plugins: {
        tooltip: { callbacks: { label: function(ctx){ return ctx.label + ': ' + ctx.formattedValue + '%'; } } },
        legend: { position: 'bottom', labels: { boxWidth:12, padding:8 } }
      },
      animation: { duration: 900, easing: 'easeOutCubic' }
    }
  });
  const lineCtx = document.getElementById('lineChart').getContext('2d');
  const grd = lineCtx.createLinearGradient(0,0,0,220);
  grd.addColorStop(0, 'rgba(124,58,237,0.18)');
  grd.addColorStop(1, 'rgba(14,165,233,0.06)');
  new Chart(lineCtx, {
    type: 'line',
    data: {
      labels: assessments,
      datasets: [{
        label: 'Marks Obtained',
        data: assessmentMarks,
        fill: true,
        tension: 0.36,
        backgroundColor: grd,
        borderColor: '#7c3aed',
        pointBackgroundColor: '#fff',
        pointBorderColor: '#7c3aed',
        pointRadius: 5,
        segment: { borderWidth: 3 }
      }]
    },
    options: {
      responsive:true,
      plugins: { legend: { display:false }, tooltip: { mode: 'index', intersect: false } },
      scales: { x: { grid: { display:false } }, y: { beginAtZero:true } },
      animation: { duration: 1000, easing: 'easeOutExpo' }
    }
  });
});
