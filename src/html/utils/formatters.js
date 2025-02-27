/**
 * Utility functions for formatting dates and other data
 * @returns {string} JavaScript code as a string
 */
function getFormatters() {
  return `
// Format date helpers
function formatDate(dateString) {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString();
}

function formatDateForInput(date) {
  const d = new Date(date);
  let month = '' + (d.getMonth() + 1);
  let day = '' + d.getDate();
  const year = d.getFullYear();

  if (month.length < 2) month = '0' + month;
  if (day.length < 2) day = '0' + day;

  return [year, month, day].join('-');
}

function getTaskStatusClasses(status, fundingType) {
  const statusLower = (status || "").toLowerCase();
  let classes = "";
  
  if (statusLower === "complete") {
    classes = "complete";
  } else if (statusLower === "in progress") {
    classes = "in-progress";
    
    // Add funding type class if available
    if (fundingType) {
      const fundingTypeLower = fundingType.toLowerCase().replace(/\\s+/g, '-');
      classes += \` funding-\${fundingTypeLower}\`;
    }
  } else {
    classes = "planned";
  }
  
  return classes;
}
`;
}

module.exports = { getFormatters }; 