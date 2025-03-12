# Roadmap Visualization Updates

This document describes the changes made to the roadmap visualization code to handle the updated roadmap.json structure.

## Overview of Changes

The roadmap.json file structure has been updated with several new features:
1. Standardized header alignment across all tabs
2. Added "Float on roadmap" functionality
3. Added "Additional Details" text boxes
4. Updated funding dropdown options
5. Updated business case format to use checkboxes

The visualization code has been updated to handle these changes and display the new information in the generated HTML visualizations.

## Files Updated

### 1. main.py

- Added support for processing floating tasks with a new `process_floating_tasks` function
- Updated the STATUS_COLORS dictionary to include new status values:
  - 'Not Started': '#9e9e9e' (Gray)
  - 'On Hold': '#9c27b0' (Purple)
  - 'Delayed': '#e53935' (Red)
- Changed the input file to use `updated_roadmap.json` instead of `roadmap.json`

### 2. modules/product_viz.py

- Reorganized how tasks are displayed in swimlanes:
  - Design tools and documentation tasks are now shown in the Design swimlane
  - Special NDT and part acceptance tasks are now shown in the Quality swimlane
  - Material system tasks continue to be shown in their respective swimlanes
- Added a material system toggle for products with multiple material systems
- Changed task coloring to be based on funding source instead of status
- Added a new FUNDING_COLORS dictionary with colors for different funding types:
  - Division IRAD: Blue
  - Sector IRAD: Green
  - CRAD: Red
  - Planned: Orange
  - Customer: Purple
  - Internal: Teal
  - External: Dark Orange
  - None: Gray
- Standardized text placement:
  - For tasks with duration > 60 days: text is placed inside the box with white bold font
  - For shorter tasks: text is placed outside the box to the right
- Added material system name in brackets to task labels when applicable
- Added funding type distribution charts to the product summary page
- Added a funding legend to explain the color coding

### 3. modules/progress_tracking.py

- Updated task collection to include all sections:
  - designTools
  - documentation
  - specialNDT
  - partAcceptance
- Added support for the float and additionalDetails fields
- Updated the burndown chart to handle the new status values
- Added floating status and additional details to the task table

## How to Use

1. Generate the updated roadmap.json file using the `generate_updated_roadmap.py` script:
   ```
   python generate_updated_roadmap.py
   ```

2. Run the visualization code to generate the HTML visualizations:
   ```
   python main.py
   ```

3. Open the generated dashboard in your browser:
   ```
   roadmap_visualizations/index.html
   ```

## New Features in Visualizations

### Swimlane Organization

Tasks are now organized into swimlanes based on their type:
- Design swimlane: Contains design tasks, design tools, and documentation
- Manufacturing swimlane: Contains manufacturing tasks
- M&P swimlane: Contains materials and processes tasks
- Quality swimlane: Contains quality tasks, special NDT, and part acceptance
- Other swimlane: Contains miscellaneous tasks

### Material System Toggle

Products with multiple material systems now have a dropdown toggle that allows users to select which material system to display or to show all material systems.

### Funding-Based Coloring

Tasks are now colored based on their funding source rather than their status. A legend is provided to explain the color coding.

### Text Placement

Text placement is now standardized:
- For longer tasks (duration > 60 days), the text is placed inside the task bar with white bold font
- For shorter tasks, the text is placed outside the task bar to the right

### Float on Roadmap

Tasks marked as "floating" will maintain their relative position to other tasks even if they are delayed. The visualization shows these tasks with a "(Floating)" indicator and adjusts their dates based on the time elapsed since the float date.

### Additional Details

The additional details for each task are now displayed in tooltips when hovering over the task in the visualization.

### Business Case Format

The business case section now displays the checkbox-based format with three categories:
1. Business
   - Save schedule
   - Save hardware costs
   - Relieve supply chain constraints
   - Increase Pwin by hitting PTW
2. Unconventional Design
   - Reduce specialty training
   - Save weight
   - Increase performance
   - Unify parts
3. Agility throughout program
   - Quickly iterate design/EMs
   - Agility in Design and AI&T
   - Digital Spares

### Status Colors

The visualizations now use a consistent color scheme for task status:
- Complete: Green (#43a047)
- In Progress: Orange (#ff9800)
- Planned: Blue (#4a89ff)
- Not Started: Gray (#9e9e9e)
- On Hold: Purple (#9c27b0)
- Delayed: Red (#e53935) 