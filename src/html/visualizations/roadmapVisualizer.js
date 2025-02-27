/**
 * Functions for creating roadmap visualizations
 * @returns {string} JavaScript code as a string
 */
function getRoadmapVisualizer() {
  console.log('Loading roadmap visualizer module');
  return `
// Create a roadmap visualization
function createRoadmapVisualization(item, container) {
  console.log('Creating roadmap visualization for:', item.name);
  
  // Check if the container exists
  if (!container) {
    console.error('Roadmap container not found');
    return;
  }
  
  // Clear the container
  container.innerHTML = '';
  
  // Get timeline data - could be from a program or product
  const timeline = item.timeline || [];
  
  // Create the roadmap visualization
  if (timeline && timeline.length > 0) {
    // Sort timeline items by date
    const sortedTimeline = [...timeline].sort((a, b) => {
      return new Date(a.date) - new Date(b.date);
    });
    
    // Find min and max dates for scaling
    const minDate = new Date(sortedTimeline[0].date);
    const maxDate = new Date(sortedTimeline[sortedTimeline.length - 1].date);
    
    // Add some padding to the date range (3 months)
    minDate.setMonth(minDate.getMonth() - 3);
    maxDate.setMonth(maxDate.getMonth() + 3);
    
    // Calculate the total time span in milliseconds
    const timeSpan = maxDate - minDate;
    
    // Create the roadmap HTML
    let roadmapHtml = \`
      <div class="roadmap-timeline">
        <div class="timeline-header">
          <div class="timeline-start-date">\${formatDate(minDate)}</div>
          <div class="timeline-end-date">\${formatDate(maxDate)}</div>
        </div>
        <div class="timeline-track">
    \`;
    
    // Add timeline items
    sortedTimeline.forEach(item => {
      const itemDate = new Date(item.date);
      // Calculate position as percentage of total time span
      const position = ((itemDate - minDate) / timeSpan) * 100;
      
      roadmapHtml += \`
        <div class="timeline-item \${item.type ? item.type.toLowerCase() : 'milestone'}" 
             style="left: \${position}%">
          <div class="timeline-item-marker"></div>
          <div class="timeline-item-label">\${item.name}</div>
          <div class="timeline-item-date">\${formatDate(itemDate)}</div>
          \${item.description ? \`<div class="timeline-item-description">\${item.description}</div>\` : ''}
        </div>
      \`;
    });
    
    roadmapHtml += \`
        </div>
      </div>
    \`;
    
    container.innerHTML = roadmapHtml;
  } else {
    container.innerHTML = '<p>No timeline data available.</p>';
  }
}
`;
}

module.exports = { getRoadmapVisualizer }; 