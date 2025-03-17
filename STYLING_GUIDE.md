# Roadmap Visualizations Styling Guide

This document outlines the styling standards for the roadmap visualizations to ensure consistency across all pages.

## 1. Layout and Container Sizing

### 1.1 Container Width and Centering
- All containers should have a consistent width of 1200px
- Use `max-width: 100%` to ensure responsiveness
- Center containers with `margin: 0 auto`
- Use `box-sizing: border-box` to include padding in width calculations
- Example:
  ```css
  .container {
    width: 1200px;
    max-width: 100%;
    margin: 0 auto;
    padding: 25px;
    box-sizing: border-box;
  }
  ```

### 1.2 Body and Background Styling
- Body should use font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
- Background color for page: `#f8f9fa`
- Margin and padding reset to 0
- Example:
  ```css
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f8f9fa;
  }
  ```

### 1.3 Card Container Styling
- Background color: white (`#ffffff`)
- Padding: 25px
- Border radius: 8px
- Box shadow: `0 2px 10px rgba(0,0,0,0.05)`
- Margin between containers: 20px
- Example:
  ```css
  .summary-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    padding: 25px;
    margin-bottom: 20px;
  }
  ```

## 2. Header Styling

### 2.1 Page Headers
- Background: Linear gradient from `#3498db` to `#2c3e50`
- Text color: white
- Padding: 20px
- Border radius: 8px
- Box shadow: `0 4px 6px rgba(0,0,0,0.1)`
- Font size: 28px
- Centered text alignment
- Example:
  ```css
  .header {
    background: linear-gradient(to right, #3498db, #2c3e50);
    color: white;
    padding: 20px;
    text-align: center;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }
  .header h1 {
    margin: 0;
    font-size: 28px;
  }
  ```

### 2.2 Section Headers
- Color: `#2c3e50`
- Border bottom: 2px solid `#3498db`
- Padding bottom: 10px
- Font size: 22px
- Example:
  ```css
  .summary-card h2 {
    color: #2c3e50;
    margin-top: 0;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
    font-size: 22px;
  }
  ```

### 2.3 Subsection Headers
- Color: `#2c3e50`
- Border bottom: 2px solid `#3498db`
- Padding bottom: 10px
- Font size: 18px
- Example:
  ```css
  .section-heading {
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
    margin-bottom: 20px;
    color: #2c3e50;
    font-size: 18px;
  }
  ```

## 3. Navigation Links

### 3.1 Navigation Button Styling
- Text color: white
- Background: `rgba(255,255,255,0.2)`
- Padding: 8px 15px
- Border radius: 4px
- No text decoration
- Hover effect: changes background color
- Example:
  ```css
  .nav-link {
    color: white;
    text-decoration: none;
    padding: 8px 15px;
    background-color: rgba(255,255,255,0.2);
    border-radius: 4px;
    margin: 0 5px;
    transition: background-color 0.3s;
  }
  .nav-link:hover {
    background-color: rgba(255,255,255,0.3);
  }
  ```

## 4. Metric Cards and Grids

### 4.1 Metric Grid Layout
- Display grid with auto-fill columns
- Minimum column width of 250px
- Gap between items: 20px
- Example:
  ```css
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
  }
  ```

### 4.2 Metric Items
- Background color: white
- Border radius: 8px
- Box shadow: `0 2px 10px rgba(0,0,0,0.05)`
- Padding: 20px
- Text alignment: center
- Example:
  ```css
  .metric-item {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    padding: 20px;
    text-align: center;
  }
  ```

### 4.3 Metric Values and Labels
- Metric values: Large font (28px), bold, blue color (#3498db)
- Metric labels: Gray color (#7f8c8d)
- Example:
  ```css
  .metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #3498db;
    margin: 10px 0;
  }
  .metric-label {
    color: #7f8c8d;
  }
  ```

## 5. Chart Styling

### 5.1 Chart Containers
- Width: 100%
- Center alignment with `text-align: center`
- Margin: 20px auto
- Example:
  ```css
  .chart-container {
    width: 100%;
    margin: 20px auto;
    text-align: center;
  }
  ```

### 5.2 Chart Images
- Max width: 100%
- Auto height
- Border radius: 8px
- Box shadow: `0 2px 8px rgba(0,0,0,0.1)`
- Example:
  ```css
  .chart-img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  ```

### 5.3 Bokeh Chart Settings
- Background color: `#f8f9fa`
- Width and height depending on chart type:
  - Adoption/savings charts: 1200x500
  - Distribution charts: 600x600
- Title formatting: 14pt font size, #2c3e50 color
- Example:
  ```python
  p = figure(
      width=1200,
      height=500,
      background_fill_color="#f8f9fa"
  )
  p.title.text_font_size = "14pt"
  p.title.text_color = "#2c3e50"
  ```

## 6. Status Indicators and Badges

### 6.1 Status Badges
- Display: inline-block
- Padding: 5px 10px
- Border radius: 4px
- Color: white
- Font weight: bold
- Margin: 5px
- Example:
  ```css
  .status-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 4px;
    color: white;
    font-weight: bold;
    margin: 5px;
  }
  ```

### 6.2 Status Colors
- Baselined: `#3498db` (blue)
- Complete: `#27ae60` (green)
- Production: `#9b59b6` (purple)
- Prototyping: `#f39c12` (orange)
- Developing: `#95a5a6` (light gray)
- Targeting: `#7f8c8d` (dark gray)
- Example:
  ```css
  .status-Baselined {
    background-color: #3498db;
  }
  .status-Complete {
    background-color: #27ae60;
  }
  /* etc. */
  ```

## 7. Card and List Layouts

### 7.1 Status Section Layout
- Flexible containers with `display: flex`
- Flex wrap: wrap
- Gap between items: 20px
- Example:
  ```css
  .status-cards-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 20px;
  }
  ```

### 7.2 Item Cards
- Background color: #f8f9fa
- Border radius: 4px
- Padding: 10px
- Box shadow: `0 1px 3px rgba(0,0,0,0.1)`
- Example:
  ```css
  .part-card {
    background-color: #f8f9fa;
    border-radius: 4px;
    padding: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
  ```

## 8. Material System Lists 

### 8.1 Material Item Styling
- Display: inline-block
- Margins: 5px 10px
- Padding: 5px 10px
- Background color: #f8f9fa
- Border radius: 4px
- Border: 1px solid #ddd
- Example:
  ```css
  .material-item {
    display: inline-block;
    margin: 5px 10px;
    padding: 5px 10px;
    background-color: #f8f9fa;
    border-radius: 4px;
    border: 1px solid #ddd;
  }
  ```

### 8.2 Charts Section Layout
- Display: flex
- Flex wrap: wrap
- Example:
  ```css
  .material-charts {
    display: flex;
    flex-wrap: wrap;
    margin-top: 20px;
  }
  ```

## 9. Implementation Notes

When implementing these styling standards:

1. Center-justify page content with container margins set to `0 auto`
2. Maintain consistent styling across all pages
3. Ensure all containers have the same width (1200px) and are centered
4. Use a consistent page background color (#f8f9fa)
5. Apply the same font family consistently across all pages
6. Ensure all cards and containers have the same border radius (8px)
7. Use consistent box shadows to create depth
8. Center-align headings and important content sections
9. Use grid and flex layouts for responsive designs
10. Apply consistent color schemes for status indicators and metrics

By following these guidelines, we ensure a cohesive and professional appearance across all roadmap visualizations. 