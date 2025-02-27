// Date utility functions

/**
 * Format a date string to a readable format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

/**
 * Format a date for HTML input elements
 * @param {string} dateString - ISO date string
 * @returns {string} Date formatted as YYYY-MM-DD
 */
function formatDateForInput(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toISOString().split('T')[0];
}

/**
 * Get a color based on task status
 * @param {string} startDate - Start date string
 * @param {string} endDate - End date string
 * @returns {string} CSS color value
 */
function getStatusColor(startDate, endDate) {
  const now = new Date();
  const start = startDate ? new Date(startDate) : null;
  const end = endDate ? new Date(endDate) : null;
  
  if (!start || !end) return '#cccccc'; // Gray for undefined dates
  
  if (now < start) return '#4a89ff'; // Blue for future tasks
  if (now > end) return '#43a047'; // Green for completed tasks
  return '#ff9800'; // Orange for in-progress tasks
}

module.exports = {
  formatDate,
  formatDateForInput,
  getStatusColor
}; 