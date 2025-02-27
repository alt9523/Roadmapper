/**
 * Styles for the technical roadmap visualization
 */

function getRoadmapStyles() {
  return `
    /* Roadmap Container Styles */
    .roadmap-container {
      margin-top: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
      overflow: hidden;
      background-color: #fff;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Timeline Controls */
    .roadmap-timeline-controls {
      padding: 10px;
      background-color: #f5f5f5;
      border-bottom: 1px solid #ddd;
      display: flex;
      align-items: center;
    }
    
    .start-date-picker {
      margin-left: 10px;
      padding: 5px;
      border-radius: 4px;
      border: 1px solid #ccc;
    }
    
    /* Timeline Styles */
    .roadmap-timeline {
      position: relative;
      overflow-x: auto;
    }
    
    /* Header Styles */
    .roadmap-header {
      display: flex;
      border-bottom: 1px solid #ddd;
      background-color: #f9f9f9;
    }
    
    .roadmap-header-lane {
      flex: 0 0 150px;
      padding: 10px;
      font-weight: bold;
      border-right: 1px solid #ddd;
    }
    
    .roadmap-header-quarter {
      flex: 0 0 100px;
      padding: 10px;
      text-align: center;
      font-weight: bold;
      border-right: 1px solid #eee;
    }
    
    /* Row Styles */
    .roadmap-row {
      display: flex;
      border-bottom: 1px solid #ddd;
      min-height: 60px;
    }
    
    .roadmap-lane-title {
      flex: 0 0 150px;
      padding: 10px;
      font-weight: bold;
      background-color: #f5f5f5;
      border-right: 1px solid #ddd;
      display: flex;
      align-items: center;
    }
    
    .roadmap-lane-content {
      flex: 1;
      position: relative;
      min-width: 1200px;
    }
    
    /* Task Styles */
    .roadmap-task {
      position: absolute;
      height: 25px;
      border-radius: 4px;
      padding: 4px;
      overflow: hidden;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      border: 1px solid rgba(255,255,255,0.2);
      cursor: pointer;
      transition: transform 0.1s, box-shadow 0.1s;
    }
    
    .roadmap-task:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.3);
      z-index: 10;
    }
    
    .roadmap-task.complete {
      background-color: #4CAF50;
      border-color: #81C784;
    }
    
    .roadmap-task.in-progress {
      background-color: #42A5F5;
      border-color: #90CAF9;
    }
    
    .roadmap-task.in-progress.funding-sector-irad {
      background-color: #AB47BC;
      border-color: #CE93D8;
    }
    
    .roadmap-task.in-progress.funding-division-irad {
      background-color: #FFA726;
      border-color: #FFCC80;
    }
    
    .roadmap-task.in-progress.funding-crad {
      background-color: #EC407A;
      border-color: #F48FB1;
    }
    
    .roadmap-task.planned {
      background-color: #BDBDBD;
      border-color: #E0E0E0;
      color: #212121;
    }
    
    .task-label {
      font-size: 12px;
      font-weight: bold;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
      color: white;
    }
    
    .roadmap-task.planned .task-label {
      color: #212121;
      text-shadow: none;
    }
    
    /* Program and Milestone Styles */
    .milestone-row {
      background-color: #f0f8ff;
      border-bottom: 2px solid #00269A;
    }
    
    .programs-row {
      background-color: #f0f0ff;
      border-bottom: 2px solid #00269A;
    }
    
    .roadmap-milestone {
      position: absolute;
      top: 5px;
      transform: translateX(-50%);
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 20px;
    }
    
    .milestone-marker {
      width: 20px;
      height: 20px;
      background-color: #4a89ff;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .milestone-label {
      margin-top: 5px;
      font-size: 12px;
      font-weight: bold;
      white-space: nowrap;
      transform: rotate(-45deg);
      transform-origin: top left;
    }
    
    .program-marker {
      position: absolute;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    
    .program-marker-point {
      width: 16px;
      height: 16px;
      background-color: #ff5722;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .program-marker-label {
      margin-top: 5px;
      font-size: 12px;
      font-weight: bold;
      white-space: nowrap;
    }
    
    /* Roadmap Key Styles */
    .roadmap-key {
      margin-top: 20px;
      padding: 15px;
      background-color: #f9f9f9;
      border-radius: 8px;
      border: 1px solid #ddd;
    }
    
    .roadmap-key h4 {
      margin-top: 0;
      margin-bottom: 10px;
    }
    
    .key-items {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
    }
    
    .key-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .key-color {
      width: 20px;
      height: 20px;
      border-radius: 4px;
    }
    
    .key-color.planned {
      background-color: #BDBDBD;
      border: 1px solid #E0E0E0;
    }
    
    .key-color.in-progress {
      background-color: #42A5F5;
      border: 1px solid #90CAF9;
    }
    
    .key-color.in-progress.funding-sector-irad {
      background-color: #AB47BC;
      border: 1px solid #CE93D8;
    }
    
    .key-color.in-progress.funding-division-irad {
      background-color: #FFA726;
      border: 1px solid #FFCC80;
    }
    
    .key-color.in-progress.funding-crad {
      background-color: #EC407A;
      border: 1px solid #F48FB1;
    }
    
    .key-color.complete {
      background-color: #4CAF50;
      border: 1px solid #81C784;
    }
    
    .key-label {
      font-size: 14px;
      color: #333;
    }
    
    .roadmap-source-note {
      margin-top: 10px;
      font-size: 12px;
      font-style: italic;
      color: #666;
    }
  `;
}

module.exports = { getRoadmapStyles }; 