// DOM manipulation helpers

/**
 * Creates an empty task detail section container
 * @returns {HTMLElement} The task detail section element
 */
function createEmptyDetailSection() {
  const detail = document.createElement('div');
  detail.id = 'taskDetailSection';
  detail.className = 'detail-view';
  
  // Try to append to container if it exists
  const container = document.querySelector('.container');
  if (container) {
    container.appendChild(detail);
  }
  
  return detail;
}

/**
 * Create a task detail section with task information
 * @param {Object} task - Task data object
 * @returns {HTMLElement} The populated task detail section
 */
function populateTaskDetails(task) {
  if (!task) {
    return createEmptyDetailSection();
  }
  
  const section = document.createElement('div');
  section.className = 'task-detail-section';
  
  // Import formatDate if available
  let formatDate;
  try {
    formatDate = require('./dateUtils').formatDate;
  } catch (e) {
    // Fallback if dateUtils is not available
    formatDate = (date) => date || 'N/A';
  }
  
  section.innerHTML = `
    <h3>${task.name}</h3>
    <div class="task-detail-content">
      <p><strong>Description:</strong> ${task.description || 'No description available'}</p>
      <p><strong>Start Date:</strong> ${formatDate(task.startDate)}</p>
      <p><strong>End Date:</strong> ${formatDate(task.endDate)}</p>
      <p><strong>Status:</strong> ${task.status || 'Not started'}</p>
    </div>
  `;
  
  return section;
}

/**
 * Adjusts row heights in the roadmap based on content
 * @param {HTMLElement|string} container - The roadmap container element or its ID
 */
function adjustRowHeights(container) {
  // If container is a string (ID), get the element
  if (typeof container === 'string') {
    container = document.getElementById(container);
    if (!container) return;
  }
  
  // Check if we're dealing with roadmap rows or regular rows
  const isRoadmap = container.querySelectorAll('.roadmap-row').length > 0;
  
  if (isRoadmap) {
    // Roadmap-specific row height adjustment
    const rows = container.querySelectorAll('.roadmap-row');
    
    rows.forEach(row => {
      const content = row.querySelector('.roadmap-lane-content');
      if (!content) return;
      
      const items = content.querySelectorAll('.roadmap-task, .roadmap-milestone, .program-marker');
      
      if (items.length > 0) {
        // Create a map to track vertical positions
        const verticalPositions = [];
        
        // First pass: collect all vertical positions and heights
        items.forEach(item => {
          const top = parseInt(item.style.top || '0', 10);
          const height = item.offsetHeight || 25; // Default height if not set
          
          verticalPositions.push({
            top: top,
            bottom: top + height + 5 // Add 5px padding
          });
        });
        
        // Find the maximum bottom position
        let maxBottom = 0;
        verticalPositions.forEach(pos => {
          if (pos.bottom > maxBottom) {
            maxBottom = pos.bottom;
          }
        });
        
        // Add padding and set the minimum height
        const newHeight = Math.max(60, maxBottom + 20); // Ensure at least 60px height with padding
        row.style.minHeight = newHeight + 'px';
        
        // Also set the lane title height to match
        const laneTitle = row.querySelector('.roadmap-lane-title');
        if (laneTitle) {
          laneTitle.style.height = (newHeight - 20) + 'px'; // Account for padding
        }
      }
    });
    
    // Second pass to adjust the roadmap-lane-content height
    rows.forEach(row => {
      const content = row.querySelector('.roadmap-lane-content');
      if (content) {
        content.style.height = row.style.minHeight;
      }
    });
  } else {
    // Regular row height adjustment
    const rows = container.querySelectorAll('.row');
    rows.forEach(row => {
      const cells = row.querySelectorAll('.cell');
      let maxHeight = 0;
      
      // Find the maximum height
      cells.forEach(cell => {
        cell.style.height = 'auto';
        maxHeight = Math.max(maxHeight, cell.offsetHeight);
      });
      
      // Apply the maximum height to all cells in the row
      cells.forEach(cell => {
        cell.style.height = `${maxHeight}px`;
      });
    });
  }
}

// Export the functions with clear, unique names
module.exports = {
  createEmptyDetailSection,
  populateTaskDetails,
  adjustRowHeights
}; 