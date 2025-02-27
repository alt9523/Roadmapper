/**
 * CSS styles for the interactive roadmap
 * @returns {string} CSS styles as a string
 */
function getStyles() {
  return `
    /* Base styles */
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0;
      padding: 0;
      color: #333;
      background-color: #f5f5f5;
    }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    
    header {
      background-color: #2c3e50;
      color: white;
      padding: 15px 0;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    header h1 {
      margin: 0;
      padding: 0 20px;
      font-size: 24px;
    }
    
    /* Navigation */
    .nav-tabs {
      display: flex;
      background-color: #34495e;
      padding: 0 20px;
    }
    
    .nav-tab {
      padding: 12px 20px;
      color: #ecf0f1;
      cursor: pointer;
      transition: background-color 0.3s;
    }
    
    .nav-tab:hover, .nav-tab.active {
      background-color: #2c3e50;
    }
    
    /* Main content area */
    .main-content {
      background-color: white;
      border-radius: 5px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      margin-top: 20px;
      padding: 20px;
    }
    
    /* Tiles for programs, products, etc. */
    .tiles-container {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }
    
    .tile {
      background-color: #ecf0f1;
      border-radius: 5px;
      padding: 20px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.05);
      transition: transform 0.2s, box-shadow 0.2s;
      cursor: pointer;
    }
    
    .tile:hover {
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .tile-name {
      font-weight: bold;
      font-size: 18px;
      margin-bottom: 10px;
    }
    
    /* Roadmap specific styles */
    .roadmap-container {
      overflow-x: auto;
      margin-top: 20px;
    }
    
    .roadmap {
      min-width: 1000px;
      position: relative;
    }
    
    .roadmap-header {
      display: flex;
      border-bottom: 1px solid #ddd;
      position: sticky;
      top: 0;
      background-color: white;
      z-index: 10;
    }
    
    .roadmap-header-cell {
      flex: 1;
      padding: 10px;
      text-align: center;
      font-weight: bold;
      min-width: 100px;
    }
    
    .roadmap-row {
      display: flex;
      border-bottom: 1px solid #eee;
      position: relative;
      min-height: 60px;
    }
    
    .roadmap-lane-title {
      width: 200px;
      padding: 10px;
      background-color: #f9f9f9;
      font-weight: bold;
      display: flex;
      align-items: center;
      position: sticky;
      left: 0;
      z-index: 5;
    }
    
    .roadmap-lane-content {
      flex: 1;
      position: relative;
      min-height: 40px;
    }
    
    .roadmap-task {
      position: absolute;
      height: 30px;
      top: 5px;
      background-color: #3498db;
      border-radius: 3px;
      color: white;
      padding: 5px;
      box-sizing: border-box;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      cursor: pointer;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    
    .roadmap-task:hover {
      box-shadow: 0 2px 5px rgba(0,0,0,0.3);
      z-index: 2;
    }
    
    /* Detail views */
    .detail-view {
      display: none;
      background-color: white;
      border-radius: 5px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      margin-top: 20px;
      padding: 20px;
    }
    
    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 25px;
    }
    
    .detail-header h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: #333;
    }
    
    .back-button {
      background-color: #003087;
      color: white;
      border: none;
      border-radius: 6px;
      padding: 10px 20px;
      font-size: 15px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      float: right;
    }
    
    .back-button:hover {
      background-color: #00246b;
      transform: translateY(-2px);
      box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    
    /* Task details */
    .task-detail-section {
      background-color: #f9f9f9;
      border-radius: 5px;
      padding: 15px;
    }
    
    .task-detail-content {
      margin-top: 10px;
    }
    
    .detail-section {
      background-color: #f8f9fa;
      border-radius: 8px;
      padding: 25px;
      margin-bottom: 30px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      border: 1px solid #e9ecef;
      border-top: 3px solid #6a3093;
    }
    
    .detail-section h3 {
      margin-top: 0;
      margin-bottom: 20px;
      font-size: 22px;
      font-weight: 600;
      color: #333;
    }
    
    .product-metadata {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 15px;
      margin-bottom: 25px;
    }
    
    .product-metadata p {
      margin: 0;
      font-size: 15px;
      line-height: 1.5;
    }
    
    .product-metadata strong {
      font-weight: 600;
      color: #495057;
      margin-right: 8px;
    }
    
    /* Requirements Section */
    .requirements-section {
      margin-bottom: 25px;
    }
    
    .requirements-section h4 {
      margin-top: 0;
      margin-bottom: 15px;
      font-size: 18px;
      font-weight: 600;
      color: #6a3093;
      padding-bottom: 8px;
      border-bottom: 1px solid #e9ecef;
    }
    
    .requirements-list {
      list-style-type: none;
      padding: 0;
      margin: 0;
    }
    
    .requirements-list li {
      margin-bottom: 10px;
      font-size: 15px;
      line-height: 1.5;
      padding-left: 20px;
      position: relative;
    }
    
    .requirements-list li:before {
      content: "•";
      position: absolute;
      left: 0;
      color: #6a3093;
      font-size: 18px;
      line-height: 1;
    }
    
    .requirements-list strong {
      font-weight: 600;
      color: #495057;
      margin-right: 8px;
    }
    
    /* Business Case Section */
    .business-case-section {
      margin-bottom: 0;
    }
    
    .business-case-section h4 {
      margin-top: 0;
      margin-bottom: 15px;
      font-size: 18px;
      font-weight: 600;
      color: #6a3093;
      padding-bottom: 8px;
      border-bottom: 1px solid #e9ecef;
    }
    
    .business-case-list {
      list-style-type: none;
      padding: 0;
      margin: 0;
    }
    
    .business-case-list li {
      margin-bottom: 10px;
      font-size: 15px;
      line-height: 1.5;
      padding-left: 20px;
      position: relative;
    }
    
    .business-case-list li:before {
      content: "•";
      position: absolute;
      left: 0;
      color: #6a3093;
      font-size: 18px;
      line-height: 1;
    }
    
    .business-case-list strong {
      font-weight: 600;
      color: #495057;
      margin-right: 8px;
    }
    
    /* Related Programs Section */
    .related-section {
      margin-top: 30px;
      margin-bottom: 30px;
    }
    
    .related-section h3 {
      margin-top: 0;
      margin-bottom: 20px;
      font-size: 20px;
      font-weight: 600;
      color: #333;
    }
    
    /* Status indicators */
    .status-indicator {
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      margin-right: 5px;
    }
    
    .status-complete {
      background-color: #2ecc71;
    }
    
    .status-in-progress {
      background-color: #f39c12;
    }
    
    .status-planned {
      background-color: #3498db;
    }
    
    /* Related section styles */
    .related-section {
      margin-top: 30px;
    }
    
    .related-section h3 {
      margin-bottom: 15px;
      border-bottom: 1px solid #eee;
      padding-bottom: 10px;
    }
    
    .year-label {
      font-size: 10px;
      color: #7f8c8d;
    }
    
    /* Responsive design improvements */
    @media (max-width: 768px) {
      .tiles-container {
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      }
      
      .roadmap-lane-title {
        width: 150px;
      }
    }
    
    /* Print styles */
    @media print {
      body {
        background-color: white;
      }
      
      .nav-tabs, .back-button {
        display: none;
      }
      
      .container {
        max-width: 100%;
        margin: 0;
        padding: 0;
      }
      
      .roadmap-container {
        overflow: visible;
      }
    }
    
    /* Tooltip styles */
    .tooltip {
      position: relative;
      display: inline-block;
    }
    
    .tooltip .tooltip-text {
      visibility: hidden;
      width: 200px;
      background-color: #555;
      color: #fff;
      text-align: center;
      border-radius: 6px;
      padding: 5px;
      position: absolute;
      z-index: 1;
      bottom: 125%;
      left: 50%;
      margin-left: -100px;
      opacity: 0;
      transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltip-text {
      visibility: visible;
      opacity: 1;
    }
    
    /* Quad Box Styles */
    .specialized-quad-box {
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 20px;
      margin-top: 25px;
    }
    
    .quad-section {
      background-color: #f8f9fa;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      border: 1px solid #e9ecef;
      overflow: auto;
      max-height: 400px;
    }
    
    .quad-section h4 {
      margin-top: 0;
      margin-bottom: 15px;
      font-size: 18px;
      font-weight: 600;
      color: #333;
      padding-bottom: 10px;
      border-bottom: 1px solid #e9ecef;
    }
    
    /* Material Systems Section - Match MRL slider color */
    .material-section {
      border-top: 3px solid #007bff;
    }
    
    .material-header h5 {
      margin-top: 0;
      margin-bottom: 15px;
      font-size: 16px;
      color: #007bff;
    }
    
    .material-details p {
      margin: 8px 0;
      font-size: 14px;
      line-height: 1.5;
    }
    
    .material-details strong {
      font-weight: 600;
      color: #495057;
    }
    
    .view-details-button-container {
      margin-top: 20px;
      text-align: right;
    }
    
    .view-full-details {
      background-color: #007bff;
      color: white;
      border: none;
      border-radius: 6px;
      padding: 8px 16px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    
    .view-full-details:hover {
      background-color: #0056b3;
      transform: translateY(-2px);
      box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    
    /* Manufacturing Section - Unique color (magenta) */
    .manufacturing-section {
      border-top: 3px solid #e83e8c;
    }
    
    .manufacturing-section h5 {
      margin-top: 15px;
      margin-bottom: 10px;
      font-size: 15px;
      color: #e83e8c;
    }
    
    .manufacturing-section ul {
      list-style-type: none;
      padding: 0;
      margin: 0;
    }
    
    .manufacturing-section li {
      margin-bottom: 6px;
      font-size: 14px;
    }
    
    .supplier-link {
      color: #e83e8c;
      text-decoration: none;
      transition: color 0.2s ease;
    }
    
    .supplier-link:hover {
      color: #d6246f;
      text-decoration: underline;
    }
    
    /* Design Section */
    .design-section {
      border-top: 3px solid #2e8b57;
    }
    
    .design-section h5 {
      margin-top: 15px;
      margin-bottom: 10px;
      font-size: 15px;
      color: #2e8b57;
    }
    
    .design-section ul {
      list-style-type: none;
      padding: 0;
      margin: 0;
    }
    
    .design-section li {
      margin-bottom: 6px;
      font-size: 14px;
    }
    
    /* Quality Section */
    .quality-section {
      border-top: 3px solid #fd7e14;
    }
    
    .quality-section h5 {
      margin-top: 15px;
      margin-bottom: 10px;
      font-size: 15px;
      color: #fd7e14;
    }
    
    .quality-section ul {
      list-style-type: none;
      padding: 0;
      margin: 0;
    }
    
    .quality-section li {
      margin-bottom: 6px;
      font-size: 14px;
    }
    
    /* Post Processing Lists */
    .post-processing-list {
      list-style-type: none;
      padding: 0;
      margin: 5px 0 0 0;
    }
    
    .post-processing-list li {
      margin-bottom: 5px;
      font-size: 14px;
      padding-left: 15px;
      position: relative;
    }
    
    .post-processing-list li:before {
      content: "•";
      position: absolute;
      left: 0;
      color: #6c757d;
    }
    
    /* Consistent button styling */
    .view-details-button {
      background-color: #3498db;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 8px 16px;
      cursor: pointer;
      font-weight: normal;
      font-size: 14px;
      transition: background-color 0.2s;
    }
    
    .view-details-button:hover {
      background-color: #2980b9;
    }
    
    /* Consistent layout for the product details page */
    .readiness-bars-container {
      display: flex;
      justify-content: center;
      margin-bottom: 20px;
    }
    
    .readiness-bars {
      width: 70%;
      max-width: 800px;
    }
    
    /* Make supplier tiles match the reference image */
    .supplier-tile {
      background-color: #f0f8ff;
      border: 1px solid #d0e3f7;
      border-radius: 4px;
      padding: 8px 12px;
      margin-bottom: 5px;
      cursor: pointer;
      transition: all 0.2s ease;
      font-size: 14px;
    }
    
    .supplier-tile:hover {
      background-color: #d9edf7;
      border-color: #85c1e9;
    }
    
    /* Material Tiles Styles */
    .material-tiles {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 15px;
    }
    
    .material-tile {
      background-color: #f8f9fa;
      border: 1px solid #ddd;
      border-radius: 4px;
      padding: 6px 12px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    
    .material-tile:hover {
      background-color: #e9ecef;
      border-color: #adb5bd;
    }
    
    .material-tile.selected {
      background-color: #e3f2fd;
      border-color: #3498db;
      font-weight: bold;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .material-details {
      margin-bottom: 15px;
    }
    
    .material-details div {
      margin-bottom: 8px;
    }
    
    /* Add these styles for the enhanced product details page */
    .wide-quad-box {
      max-width: 1200px;
      width: 90%;
      margin: 0 auto;
    }
    
    .supplier-tiles {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 10px 0;
    }
    
    .supplier-tile {
      background-color: #f0f8ff; /* Light blue */
      border: 1px solid #b8d8f8;
      border-radius: 4px;
      padding: 8px 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      font-size: 14px;
      color: #2c3e50;
    }
    
    .supplier-tile:hover {
      background-color: #d9edf7;
      border-color: #85c1e9;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Update the button container style */
    .view-details-button-container {
      margin-top: 15px;
      text-align: center;
    }
    
    .view-details-button-container.left-aligned {
      text-align: left;
    }
    
    .view-details-button {
      background-color: #3498db;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 8px 16px;
      cursor: pointer;
      font-weight: bold;
      transition: background-color 0.2s;
    }
    
    .view-details-button:hover {
      background-color: #2980b9;
    }
    
    /* Make the specialized quad box responsive but prioritize desktop view */
    @media (min-width: 1200px) {
      .specialized-quad-box {
        gap: 25px; /* Larger gap on desktop */
      }
      
      .quad-section {
        padding: 20px; /* More padding on desktop */
      }
    }
    
    /* Program Details Styles */
    .program-details {
      padding: 20px;
      width: 100%;
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .program-details h1 {
      color: #000;
      font-size: 28px;
      margin-bottom: 20px;
      border-bottom: none;
    }
    
    .program-details-info {
      margin-bottom: 30px;
    }
    
    .program-details-info p {
      margin: 8px 0;
      font-size: 16px;
    }
    
    .products-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .product-card {
      border: 1px solid #ccc;
      border-radius: 4px;
      padding: 15px;
      width: 100%;
      max-width: 450px;
      background-color: #fff;
      cursor: pointer;
      transition: box-shadow 0.3s ease;
    }
    
    .product-card:hover {
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .product-card h3 {
      margin-top: 0;
      color: #003087;
      font-size: 18px;
      margin-bottom: 15px;
    }
    
    .product-status p {
      margin: 5px 0;
      font-size: 14px;
    }
    
    .back-button {
      background-color: #003087;
      color: white;
      border: none;
      padding: 8px 20px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
    }
    
    .back-button:hover {
      background-color: #00246b;
    }
    
    /* Business Case Styles */
    .business-case-section {
      margin-top: 15px;
    }
    
    .business-case-section h4 {
      margin-top: 0;
      margin-bottom: 10px;
      font-weight: 600;
      font-size: 16px;
    }
    
    .business-case-list {
      list-style-type: none;
      padding: 0;
      margin: 0;
    }
    
    .business-case-list li {
      margin-bottom: 8px;
    }
    
    .business-case-list li strong {
      font-weight: 600;
      margin-right: 5px;
    }
    
    /* Material Systems Styles in Quad Box */
    .material-systems-list {
      list-style-type: none;
      padding: 0;
      margin: 0;
    }
    
    .material-system-item {
      margin-bottom: 20px;
      border-bottom: 1px solid #eee;
      padding-bottom: 15px;
    }
    
    .material-system-item:last-child {
      border-bottom: none;
      margin-bottom: 0;
    }
    
    .material-header {
      margin-bottom: 8px;
    }
    
    .material-link {
      color: #003087;
      font-weight: 600;
      text-decoration: none;
      font-size: 16px;
    }
    
    .material-link:hover {
      text-decoration: underline;
    }
    
    .material-details p {
      margin: 5px 0;
      font-size: 14px;
    }
    
    .material-post-processing, .material-machines {
      margin-top: 8px;
    }
    
    .post-processing-list, .machines-list {
      margin: 5px 0 0 15px;
      padding: 0;
      font-size: 13px;
    }
    
    .post-processing-list li, .machines-list li {
      margin-bottom: 3px;
    }
    
    /* Material System Filter Styles */
    .material-system-filters {
      margin-bottom: 25px;
      padding: 20px;
      background-color: #f8f9fa;
      border-radius: 8px;
      border: 1px solid #e9ecef;
    }
    
    .filter-label {
      font-weight: 600;
      margin-bottom: 15px;
      color: #333;
      font-size: 18px;
    }
    
    .filter-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }
    
    .material-filter-btn {
      background-color: #f0f0f0;
      border: none;
      border-radius: 6px;
      padding: 12px 20px;
      cursor: pointer;
      font-size: 16px;
      font-weight: 500;
      transition: all 0.2s ease;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .material-filter-btn:hover {
      background-color: #e0e0e0;
      transform: translateY(-2px);
      box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    
    .material-filter-btn.active {
      background-color: #0056b3;
      color: white;
      box-shadow: 0 3px 6px rgba(0,0,0,0.2);
    }
    
    /* Material System Details Styles */
    .material-system-details {
      margin-bottom: 15px;
    }
    
    .material-system-details h5 {
      margin-top: 0;
      margin-bottom: 10px;
      color: #003087;
      font-size: 16px;
    }
    
    .manufacturing-for-material, .quality-for-material {
      margin-bottom: 15px;
    }
    
    .qualified-machines, .post-processing, .relevant-suppliers,
    .standard-ndt, .special-ndt, .part-acceptance,
    .product-machines, .product-suppliers {
      margin-bottom: 15px;
    }
    
    .qualified-machines h5, .post-processing h5, .relevant-suppliers h5,
    .standard-ndt h5, .special-ndt h5, .part-acceptance h5,
    .product-machines h5, .product-suppliers h5 {
      margin-top: 0;
      margin-bottom: 8px;
      font-size: 15px;
      color: #495057;
    }
    
    .machines-list, .post-processing-list, .suppliers-list, .ndt-list {
      list-style-type: none;
      padding: 0;
      margin: 0 0 0 5px;
    }
    
    .machines-list li, .post-processing-list li, .suppliers-list li, .ndt-list li {
      margin-bottom: 5px;
      font-size: 14px;
    }
    
    .view-details-button-container {
      margin-top: 15px;
    }
    
    .material-details-btn {
      background-color: #003087;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 6px 12px;
      font-size: 14px;
      cursor: pointer;
    }
    
    .material-details-btn:hover {
      background-color: #00246b;
    }
    
    /* Product Development Progress Styles */
    .product-development-progress {
      margin-bottom: 30px;
      padding: 20px 25px;
      background-color: #f8f9fa;
      border-radius: 8px;
      border: 1px solid #e9ecef;
      width: 80%;
      margin-left: auto;
      margin-right: auto;
    }
    
    .progress-section {
      margin-bottom: 10px;
      display: flex;
      align-items: center;
    }
    
    .progress-section:last-child {
      margin-bottom: 0;
    }
    
    .progress-section h4 {
      margin: 0;
      font-size: 18px;
      color: #333;
      font-weight: 600;
      width: 70px;
      flex-shrink: 0;
      text-align: right;
      padding-right: 15px;
    }
    
    .progress-container {
      width: 100%;
      position: relative;
    }
    
    .progress-bar-wrapper {
      height: 28px;
      background-color: #e9ecef;
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 5px;
      box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
      position: relative;
    }
    
    .progress-bar {
      height: 100%;
      border-radius: 8px;
      transition: width 0.5s ease;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding-right: 15px;
    }
    
    .trl-progress {
      background: linear-gradient(90deg, #5d4cb6, #7e6fd3);
    }
    
    .mrl-progress {
      background: linear-gradient(90deg, #007bff, #00b8d4);
    }
    
    .progress-current {
      color: white;
      font-weight: 600;
      font-size: 16px;
      text-shadow: 0 1px 2px rgba(0,0,0,0.3);
      white-space: nowrap;
    }
    
    .progress-labels {
      display: flex;
      justify-content: space-between;
      font-size: 14px;
      color: #6c757d;
    }
    
    .progress-min, .progress-max {
      color: #6c757d;
    }
  `;
}

module.exports = { getStyles }; 