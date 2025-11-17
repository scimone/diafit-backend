document.addEventListener('DOMContentLoaded', () => {
    const chartContainer = document.getElementById('agpChart');
    const plotlyDataEl = document.getElementById('plotly-data');

    if (plotlyDataEl && chartContainer) {
        try {
            const graphData = JSON.parse(plotlyDataEl.textContent);
            Plotly.newPlot(chartContainer, graphData.data, graphData.layout, { responsive: true });
        } catch (error) {
            chartContainer.innerHTML = `
                <div class="error-text">
                    <strong>Error rendering graph:</strong><br>${error.message}
                </div>`;
            console.error('Error rendering Plotly graph:', error);
        }
    } else if (chartContainer && !plotlyDataEl) {
        chartContainer.innerHTML = '<div style="padding: 40px; text-align: center; color: #666;">No AGP graph data available for this period.</div>';
    }
});
