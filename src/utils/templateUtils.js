/**
 * Utility functions for template generation
 */

/**
 * Safely converts data to a JSON string for client-side use
 * @param {Object} data - The data to stringify
 * @returns {string} - HTML-safe JSON string
 */
function safeJsonStringify(data) {
  try {
    return JSON.stringify(data)
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  } catch (error) {
    console.error('Error stringifying data:', error);
    return '{}';
  }
}

/**
 * Ensures data arrays exist even if they're empty
 * @param {Object} data - The roadmap data
 * @returns {Object} - Data with guaranteed arrays
 */
function sanitizeData(data) {
  return {
    programs: Array.isArray(data.programs) ? data.programs : [],
    products: Array.isArray(data.products) ? data.products : [],
    materialSystems: Array.isArray(data.materialSystems) ? data.materialSystems : [],
    suppliers: Array.isArray(data.suppliers) ? data.suppliers : [],
    cradOpportunities: Array.isArray(data.cradOpportunities) ? data.cradOpportunities : []
  };
}

module.exports = {
  safeJsonStringify,
  sanitizeData
}; 