/**
 * Generates the HTML for a product roadmap visualization
 */

/**
 * Format a date string for display
 * @param {string} dateString - The date string to format
 * @returns {string} The formatted date
 */
function formatDate(dateString) {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleDateString();
}

/**
 * Format a date for input elements
 * @param {Date|string} date - The date to format
 * @returns {string} The date formatted as YYYY-MM-DD
 */
function formatDateForInput(date) {
  const d = new Date(date);
  let month = '' + (d.getMonth() + 1);
  let day = '' + d.getDate();
  const year = d.getFullYear();

  if (month.length < 2) month = '0' + month;
  if (day.length < 2) day = '0' + day;

  return [year, month, day].join('-');
}

/**
 * Get CSS color based on task status
 * @param {string} status - The task status
 * @param {string} fundingType - Optional funding type
 * @returns {string} CSS class names for the task
 */
function getTaskStatusClasses(status, fundingType) {
  const statusLower = (status || "").toLowerCase();
  let classes = "";
  
  if (statusLower === "complete") {
    classes = "complete";
  } else if (statusLower === "in progress") {
    classes = "in-progress";
    
    // Add funding type class if available
    if (fundingType) {
      const fundingTypeLower = fundingType.toLowerCase().replace(/\s+/g, '-');
      classes += ` funding-${fundingTypeLower}`;
    }
  } else {
    classes = "planned";
  }
  
  return classes;
}

/**
 * Generate the HTML for a product roadmap
 * @param {Object} product - The product object
 * @param {Array} allPrograms - All programs data
 * @param {Array} allMaterials - All material systems data
 * @param {string} startDate - Optional start date
 * @returns {string} The HTML for the roadmap
 */
function generateRoadmapHtml(product, allPrograms, allMaterials, startDate = null) {
  console.log("Generating roadmap HTML for product:", product.name);
  
  // Default to today's date if no start date provided
  if (!startDate) {
    startDate = new Date();
  } else if (typeof startDate === 'string') {
    startDate = new Date(startDate);
  }
  
  // Determine the starting quarter based on the date
  const startYear = startDate.getFullYear();
  const startMonth = startDate.getMonth();
  const startQuarter = Math.floor(startMonth / 3) + 1;
  
  // Generate quarters for 3 years (12 quarters)
  const quarters = [];
  let currentYear = startYear;
  let currentQuarter = startQuarter;
  
  for (let i = 0; i < 12; i++) {
    quarters.push(`${currentYear}-Q${currentQuarter}`);
    currentQuarter++;
    if (currentQuarter > 4) {
      currentQuarter = 1;
      currentYear++;
    }
  }
  
  // Get related programs and sort them by need date
  const relatedPrograms = [];
  if (product.programs && product.programs.length > 0) {
    product.programs.forEach(programId => {
      const program = allPrograms.find(p => p.id === programId);
      if (program) {
        relatedPrograms.push(program);
      }
    });
    
    // Sort programs by need date
    relatedPrograms.sort((a, b) => {
      const dateA = a.needDate ? new Date(a.needDate) : new Date('9999-12-31');
      const dateB = b.needDate ? new Date(b.needDate) : new Date('9999-12-31');
      return dateA - dateB;
    });
  }
  
  // Create the roadmap HTML
  let html = `
    <div class="roadmap-container">
      <div class="roadmap-timeline-controls">
        <label for="start-date">Start Date:</label>
        <input type="date" id="start-date" class="start-date-picker" value="${formatDateForInput(startDate)}">
      </div>
      <div class="roadmap-timeline">
        <div class="roadmap-header">
          <div class="roadmap-header-lane">Date</div>`;
  
  // Add quarter headers
  quarters.forEach(quarter => {
    const [year, q] = quarter.split('-');
    html += `<div class="roadmap-header-quarter">${year}<br>${q}</div>`;
  });
  
  html += `</div>`;
  
  // Add programs row
  html += `<div class="roadmap-row programs-row">
    <div class="roadmap-lane-title">Programs</div>
    <div class="roadmap-lane-content">`;
  
  // Group programs by quarter to prevent overlapping
  const programsByQuarter = {};
  
  relatedPrograms.forEach(program => {
    if (program.needDate) {
      const needDate = new Date(program.needDate);
      const needYear = needDate.getFullYear();
      const needMonth = needDate.getMonth();
      const needQuarter = Math.floor(needMonth / 3) + 1;
      const needQuarterStr = `${needYear}-Q${needQuarter}`;
      
      if (!programsByQuarter[needQuarterStr]) {
        programsByQuarter[needQuarterStr] = [];
      }
      programsByQuarter[needQuarterStr].push(program);
    }
  });
  
  // Add program markers based on need dates, stacked vertically if needed
  Object.keys(programsByQuarter).forEach(quarter => {
    const quarterIndex = quarters.indexOf(quarter);
    if (quarterIndex >= 0) {
      const position = quarterIndex * 100 + 50;
      const programs = programsByQuarter[quarter];
      
      programs.forEach((program, index) => {
        // Offset each program vertically to prevent overlap
        const verticalOffset = index * 30;
        html += `
          <div class="program-marker" style="left: ${position}px; top: ${verticalOffset}px;" title="${program.name} Need Date: ${formatDate(program.needDate)}">
            <div class="program-marker-point"></div>
            <div class="program-marker-label">${program.name}</div>
          </div>`;
      });
    }
  });
  
  html += `</div></div>`;
  
  // Add milestone row
  html += `<div class="roadmap-row milestone-row">
    <div class="roadmap-lane-title">Milestones</div>
    <div class="roadmap-lane-content">`;
  
  // Group milestones by quarter to prevent overlapping
  const milestonesByQuarter = {};
  
  if (product.milestones && product.milestones.length > 0) {
    product.milestones.forEach(milestone => {
      const date = new Date(milestone.date);
      const year = date.getFullYear();
      const month = date.getMonth();
      const quarter = Math.floor(month / 3) + 1;
      const milestoneQuarter = `${year}-Q${quarter}`;
      
      if (!milestonesByQuarter[milestoneQuarter]) {
        milestonesByQuarter[milestoneQuarter] = [];
      }
      milestonesByQuarter[milestoneQuarter].push(milestone);
    });
  }
  
  // Add milestone markers, stacked vertically if needed
  Object.keys(milestonesByQuarter).forEach(quarter => {
    const quarterIndex = quarters.indexOf(quarter);
    if (quarterIndex >= 0) {
      const position = quarterIndex * 100 + 50;
      const milestones = milestonesByQuarter[quarter];
      
      milestones.forEach((milestone, index) => {
        // Offset each milestone vertically to prevent overlap
        const verticalOffset = index * 30;
        html += `
          <div class="roadmap-milestone" style="left: ${position}px; top: ${verticalOffset}px;" title="${milestone.name}: ${milestone.description}">
            <div class="milestone-marker"></div>
            <div class="milestone-label">${milestone.name}</div>
          </div>`;
      });
    }
  });
  
  html += `</div></div>`;
  
  // Add swimlanes for each category
  const lanes = ["Design", "Manufacturing", "M&P", "Quality"];
  
  lanes.forEach(lane => {
    html += `
      <div class="roadmap-row">
        <div class="roadmap-lane-title">${lane}</div>
        <div class="roadmap-lane-content" data-lane="${lane}">`;
    
    // For M&P lane, include material system tasks
    if (lane === "M&P" && product.materialSystems && product.materialSystems.length > 0) {
      // Process material systems tasks
      const materialTasksPositions = {};
      
      // Get all material system tasks
      product.materialSystems.forEach(materialId => {
        const material = allMaterials.find(m => m.id === materialId);
        
        if (material && material.roadmap && material.roadmap.length > 0) {
          material.roadmap.forEach(task => {
            // Calculate position and width based on dates
            const startTaskDate = new Date(task.start);
            const endTaskDate = new Date(task.end);
            
            const startTaskYear = startTaskDate.getFullYear();
            const startTaskMonth = startTaskDate.getMonth();
            const startTaskQuarter = Math.floor(startTaskMonth / 3) + 1;
            const taskStartQuarter = `${startTaskYear}-Q${startTaskQuarter}`;
            
            const endTaskYear = endTaskDate.getFullYear();
            const endTaskMonth = endTaskDate.getMonth();
            const endTaskQuarter = Math.floor(endTaskMonth / 3) + 1;
            const taskEndQuarter = `${endTaskYear}-Q${endTaskQuarter}`;
            
            // Find positions in our quarters array
            const startIndex = quarters.indexOf(taskStartQuarter);
            const endIndex = quarters.indexOf(taskEndQuarter);
            
            // Only show if the end is visible
            if (endIndex >= 0) {
              let startPosition = 0;
              let width = 0;
              
              if (startIndex >= 0) {
                // Task starts within the visible range
                startPosition = startIndex * 100;
                width = (endIndex - startIndex + 1) * 100;
              } else {
                // Task starts before the visible range
                startPosition = 0; // Start at the beginning of the visible range
                width = (endIndex + 1) * 100; // Width from beginning to end date
              }
              
              // Create a position key to group overlapping tasks
              const posKey = `${startPosition}-${width}`;
              if (!materialTasksPositions[posKey]) {
                materialTasksPositions[posKey] = [];
              }
              
              materialTasksPositions[posKey].push({
                task,
                materialId,
                materialName: material.name
              });
            }
          });
        }
      });
      
      // Render material tasks
      Object.keys(materialTasksPositions).forEach(posKey => {
        const [startPosition, width] = posKey.split('-').map(Number);
        const tasks = materialTasksPositions[posKey];
        
        tasks.forEach((taskObj, index) => {
          const { task, materialName } = taskObj;
          const statusClasses = getTaskStatusClasses(task.status, task.fundingType);
          
          // Calculate vertical position
          const verticalOffset = index * 30;
          
          html += `
            <div class="roadmap-task ${statusClasses}" 
                 style="left: ${startPosition}px; width: ${width}px; top: ${verticalOffset}px;"
                 title="${task.task} (${materialName}): ${formatDate(task.start)} - ${formatDate(task.end)}${task.fundingType ? ' | Funding: ' + task.fundingType : ''}">
              <div class="task-label">${task.task} (${materialName})</div>
            </div>`;
        });
      });
    }
    
    // Add product tasks for the current lane
    if (product.roadmap && product.roadmap.length > 0) {
      const laneTasksPositions = {};
      
      product.roadmap.forEach(task => {
        if (task.lane === lane) {
          // Calculate position and width based on dates
          const startTaskDate = new Date(task.start);
          const endTaskDate = new Date(task.end);
          
          const startTaskYear = startTaskDate.getFullYear();
          const startTaskMonth = startTaskDate.getMonth();
          const startTaskQuarter = Math.floor(startTaskMonth / 3) + 1;
          const taskStartQuarter = `${startTaskYear}-Q${startTaskQuarter}`;
          
          const endTaskYear = endTaskDate.getFullYear();
          const endTaskMonth = endTaskDate.getMonth();
          const endTaskQuarter = Math.floor(endTaskMonth / 3) + 1;
          const taskEndQuarter = `${endTaskYear}-Q${endTaskQuarter}`;
          
          // Find positions in our quarters array
          const startIndex = quarters.indexOf(taskStartQuarter);
          const endIndex = quarters.indexOf(taskEndQuarter);
          
          // Only show if the end is visible
          if (endIndex >= 0) {
            let startPosition = 0;
            let width = 0;
            
            if (startIndex >= 0) {
              // Task starts within the visible range
              startPosition = startIndex * 100;
              width = (endIndex - startIndex + 1) * 100;
            } else {
              // Task starts before the visible range
              startPosition = 0; // Start at the beginning of the visible range
              width = (endIndex + 1) * 100; // Width from beginning to end date
            }
            
            // Create a position key to group overlapping tasks
            const posKey = `${startPosition}-${width}`;
            if (!laneTasksPositions[posKey]) {
              laneTasksPositions[posKey] = [];
            }
            
            laneTasksPositions[posKey].push(task);
          }
        }
      });
      
      // Render product tasks
      Object.keys(laneTasksPositions).forEach(posKey => {
        const [startPosition, width] = posKey.split('-').map(Number);
        const tasks = laneTasksPositions[posKey];
        
        tasks.forEach((task, index) => {
          const statusClasses = getTaskStatusClasses(task.status, task.fundingType);
          
          // Calculate vertical position
          const verticalOffset = index * 30;
          
          html += `
            <div class="roadmap-task ${statusClasses}" 
                 style="left: ${startPosition}px; width: ${width}px; top: ${verticalOffset}px;"
                 title="${task.task}: ${formatDate(task.start)} - ${formatDate(task.end)}${task.fundingType ? ' | Funding: ' + task.fundingType : ''}">
              <div class="task-label">${task.task}</div>
            </div>`;
        });
      });
    }
    
    html += `</div>
      </div>`;
  });
  
  html += `</div>`;
  
  // Add color key
  html += `
    <div class="roadmap-key">
      <h4>Roadmap Key</h4>
      <div class="key-items">
        <div class="key-item">
          <div class="key-color planned"></div>
          <div class="key-label">Planned</div>
        </div>
        <div class="key-item">
          <div class="key-color in-progress funding-sector-irad"></div>
          <div class="key-label">In Development (Sector IRAD)</div>
        </div>
        <div class="key-item">
          <div class="key-color in-progress funding-division-irad"></div>
          <div class="key-label">In Development (Division IRAD)</div>
        </div>
        <div class="key-item">
          <div class="key-color in-progress funding-crad"></div>
          <div class="key-label">In Development (CRAD)</div>
        </div>
        <div class="key-item">
          <div class="key-color complete"></div>
          <div class="key-label">Complete</div>
        </div>
      </div>
      <p class="roadmap-source-note">Roadmap tasks are sourced from the product's roadmap data and the selected material system.</p>
    </div>`;
  
  return html;
}

module.exports = { generateRoadmapHtml }; 