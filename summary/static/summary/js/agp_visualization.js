document.addEventListener('DOMContentLoaded', () => {
    const chartContainer = document.getElementById('agpChart');
    const plotlyDataEl = document.getElementById('plotly-data');

    if (plotlyDataEl && chartContainer) {
        try {
            const graphData = JSON.parse(plotlyDataEl.textContent);
            function resizePlot() {
                const width = chartContainer.offsetWidth;
                const height = Math.max(200, Math.round(width / 1.7)); // 2:1 aspect ratio
                Plotly.newPlot(chartContainer, graphData.data, { ...graphData.layout, width, height }, { ...graphData.config, responsive: true });
            }
            resizePlot();
            window.addEventListener('resize', resizePlot);
        } catch (error) {
            chartContainer.innerHTML = `
                <div class="error-text">
                    <strong>Error rendering graph:</strong><br>${error.message}
                </div>`;
            console.error('Error rendering Plotly graph:', error);
        }
    }

    // Handle dropdowns
    window.changePeriodDays = () => {
        const period = document.getElementById('periodSelect').value;
        window.location.href = `?period_days=${period}`;
    };

    window.changeDate = () => {
        const period = document.getElementById('periodSelect').value;
        const date = document.getElementById('dateSelect')?.value;
        window.location.href = `?period_days=${period}&date=${date}`;
    };

    // Pattern highlighting
    const patternRanges = {
        night: [22, 7],
        morning: [7, 11],
        afternoon: [15, 18],
        noon: [11, 15],
        lunch: [11, 15],
        evening: [18, 22],
        dinner: [18, 22],
        breakfast: [7, 10],
        dawn: [3, 7],
        fasting: [5, 7],
        overnight: [22, 7]
    };

    document.querySelectorAll('.pattern-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.pattern-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            const pattern = item.dataset.pattern.toLowerCase();
            const rangeKey = Object.keys(patternRanges).find(key => pattern.includes(key));
            const range = rangeKey ? patternRanges[rangeKey] : null;
            if (range) highlightRange(range[0], range[1]);
            else resetHighlight();
        });
    });
    
    const pointsPerHour = 12;

    // Fetch CSS variable values
    const getCSSVariable = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

    const targetLowerColor = getCSSVariable('--agp-target-lower-line');
    const targetUpperColor = getCSSVariable('--agp-target-upper-line');

    const targetShapes = [
        {
            type: 'line', xref: 'paper', yref: 'y',
            x0: 0, x1: 1, y0: 70, y1: 70,
            line: { color: targetLowerColor, width: 2 }, // target_lower_line
            layer: 'below'
        },
        {
            type: 'line', xref: 'paper', yref: 'y',
            x0: 0, x1: 1, y0: 180, y1: 180,
            line: { color: targetUpperColor, width: 2 }, // target_upper_line
            layer: 'below'
        }
    ];
    const highlightRange = (startHour, endHour) => {
        const startIdx = startHour * pointsPerHour;
        const endIdx = endHour * pointsPerHour;

        const highlightShapes = startHour > endHour
            ? [
                { type: 'rect', x0: endIdx, x1: startIdx }
              ].map(s => ({
                ...s, xref: 'x', yref: 'paper', y0: 0, y1: 1,
                fillcolor: 'rgba(13, 17, 23, 0.8)', line: { width: 0 }, layer: 'above'
              }))
            : [
                { type: 'rect', x0: 0, x1: startIdx },
                { type: 'rect', x0: endIdx, x1: 24 * pointsPerHour }
              ].map(s => ({
                ...s, xref: 'x', yref: 'paper', y0: 0, y1: 1,
                fillcolor: 'rgba(13, 17, 23, 0.8)', line: { width: 0 }, layer: 'above'
              }));

        Plotly.relayout('agpChart', { shapes: [...targetShapes, ...highlightShapes] });
    };

    const resetHighlight = () => Plotly.relayout('agpChart', { shapes: targetShapes });
});
