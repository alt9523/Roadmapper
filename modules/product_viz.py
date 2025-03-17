import os
from datetime import datetime, timedelta
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Range1d, Span, Legend, LegendItem, Div, Tabs, Panel, CheckboxGroup, CustomJS, RadioButtonGroup
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import Category10, Spectral6, Turbo256
from bokeh.transform import factor_cmap
import matplotlib.pyplot as plt
import numpy as np
from bokeh.embed import components

# Define funding type colors
FUNDING_COLORS = {
    'Division IRAD': '#3498db',  # Blue
    'Sector IRAD': '#2ecc71',    # Green
    'CRAD': '#e74c3c',           # Red
    'Planned': '#f39c12',        # Orange
    'Customer': '#9b59b6',       # Purple
    'Internal': '#1abc9c',       # Teal
    'External': '#d35400',       # Dark Orange
    'None': '#95a5a6'            # Gray
}

# Global CSS style for all pages
GLOBAL_STYLE = """
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f8f9fa;
    }
    .container {
        width: 1200px;
        max-width: 100%;
        margin: 0 auto;
        padding: 25px;
        box-sizing: border-box;
    }
    .summary-card {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        padding: 25px;
        margin-bottom: 20px;
        width: 1200px;
        max-width: 100%;
        box-sizing: border-box;
    }
    .header {
        background: linear-gradient(to right, #3498db, #2c3e50);
        color: white;
        padding: 20px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        width: 1200px;
        max-width: 100%;
        box-sizing: border-box;
    }
    .header h1 {
        margin: 0;
        font-size: 28px;
        color: white;
    }
    .header p {
        color: white;
        margin: 10px 0;
    }
    .section-heading {
        color: #2c3e50;
        margin-top: 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        font-size: 22px;
    }
    .subsection-heading {
        color: #2c3e50;
        font-size: 18px;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .nav-link {
        color: white;
        text-decoration: none;
        padding: 8px 15px;
        background-color: rgba(255,255,255,0.2);
        border-radius: 4px;
        margin: 0 5px;
        display: inline-block;
        transition: background-color 0.3s;
    }
    .nav-link:hover {
        background-color: rgba(255,255,255,0.3);
    }
    .metric-item {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #3498db;
        margin: 10px 0;
    }
    .metric-label {
        color: #7f8c8d;
    }
    .chart-container {
        width: 100%;
        margin: 20px auto;
        text-align: center;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        margin: 5px;
    }
    .material-item {
        display: inline-block;
        margin: 5px 10px;
        padding: 5px 10px;
        background-color: #f8f9fa;
        border-radius: 4px;
        border: 1px solid #ddd;
    }
</style>
"""

def generate_product_visualizations(data, output_dir, status_colors):
    """Generate visualizations for products"""
    print("Generating product visualizations...")
    
    # Create product directory if it doesn't exist
    product_dir = os.path.join(output_dir, "products")
    if not os.path.exists(product_dir):
        os.makedirs(product_dir)
    
    # Import the new product detail module
    from modules.product_detail import generate_product_detail_page
    
    # Generate individual product pages using the new detailed layout
    for product in data['products']:
        generate_product_detail_page(product, data, product_dir, status_colors)
    
    # Generate product summary page
    generate_product_summary(data, product_dir)
    
    # Generate product distribution charts
    generate_product_distribution_charts(data, product_dir)
    
    print(f"Product visualizations generated in '{product_dir}'")

def generate_product_page(product, data, product_dir, status_colors):
    """Generate a detailed page for a single product"""
    product_id = product['id']
    
    # Create a figure for the product roadmap
    p = figure(
        x_axis_type="datetime",
        width=1200,
        height=600,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        background_fill_color="#f8f9fa",
        sizing_mode="stretch_width"
    )
    
    # Customize appearance according to style guide
    p.title.text_font_size = '22px'
    p.title.text_color = '#2c3e50'
    p.xaxis.axis_label = "Timeline"
    p.yaxis.axis_label = "Tasks"
    p.grid.grid_line_alpha = 0.3
    
    # Get all material systems for this product
    material_systems = []
    for material_id in product.get('materialSystems', []):
        if isinstance(material_id, str):
            material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
        elif isinstance(material_id, dict) and 'materialID' in material_id:
            material = next((m for m in data['materialSystems'] if m['id'] == material_id['materialID']), None)
        else:
            continue
            
        if material:
            material_systems.append(material)
    
    # Create material system toggle if there are multiple materials
    selected_material = None
    if len(material_systems) > 1:
        # We'll implement this in the HTML directly
        # Default to all materials
        selected_material = "all"
    
    # Process tasks by lane
    lanes = ['Design', 'Manufacturing', 'M&P', 'Quality', 'Other']
    y_pos = 0
    legend_items = []
    all_dates = []
    all_tasks = []
    
    # Collect program need dates first to organize them better
    program_need_dates = []
    for program in data['programs']:
        for combo in program.get('productMaterialCombinations', []):
            if combo.get('productID') == product_id and 'needDate' in combo:
                try:
                    need_date = datetime.strptime(combo['needDate'], "%Y-%m-%d")
                    all_dates.append(need_date)
                    
                    # Get part name and number
                    part_name = combo.get('partName', 'N/A')
                    part_number = combo.get('partNumber', 'N/A')
                    
                    program_need_dates.append({
                        'date': need_date,
                        'program_name': program['name'],
                        'program_id': program['id'],
                        'part_name': part_name,
                        'part_number': part_number
                    })
                except (ValueError, TypeError):
                    # Skip if date can't be parsed
                    pass
    
    # Sort program need dates by date
    program_need_dates.sort(key=lambda x: x['date'])
    
    # Add program need dates as vertical lines with better positioning
    y_offset = 0
    for need_date_info in program_need_dates:
        need_date = need_date_info['date']
        
        # Add program line
        program_line = Span(location=need_date, dimension='height', 
                           line_color='#e74c3c', line_width=2, line_dash='solid')
        p.add_layout(program_line)
        
        # Calculate y position for staggered labels to avoid overlap
        y_position = 0 + (y_offset * 0.7)  # Stagger the labels vertically
        
        # Add program label with improved formatting and positioning
        program_label = Label(
            x=need_date, 
            y=y_position, 
            text=f"{need_date_info['program_name']} ({need_date_info['program_id']})\nPart: {need_date_info['part_name']}\nPN: {need_date_info['part_number']}",
            text_color='#e74c3c',
            text_font_style='bold',
            text_font_size='9pt',
            border_line_color='#e74c3c',
            border_line_alpha=0.5,
            background_fill_color="white",
            background_fill_alpha=0.9,
            angle=90,
            angle_units='deg',
            x_offset=5,
            y_offset=0
        )
        p.add_layout(program_label)
        
        # Increment offset for next label
        y_offset += 1
        # Reset if we've gone too far
        if y_offset > 5:
            y_offset = 0
    
    for lane in lanes:
        # Add lane label using ColumnDataSource
        lane_source = ColumnDataSource(data=dict(
            x=[datetime.now()],
            y=[y_pos],
            text=[f"--- {lane} ---"]
        ))
        
        # Add lane label
        p.text(x='x', y='y', text='text', source=lane_source,
               text_font_style="bold", text_align="right", text_baseline="middle")
        
        # Add lane tasks from product roadmap
        lane_tasks = [t for t in product.get('roadmap', []) if t.get('lane', 'Other') == lane]
        
        # Add design tools and documentation to Design lane
        if lane == 'Design':
            # Add design tools
            if 'designTools' in product:
                for tool in product.get('designTools', []):
                    if isinstance(tool, dict):
                        tool_copy = tool.copy()
                        tool_copy['task'] = tool.get('name', 'Unknown Tool')
                        tool_copy['start'] = tool.get('start', '')
                        tool_copy['end'] = tool.get('end', '')
                        tool_copy['fundingType'] = tool.get('funding', 'None')
                        lane_tasks.append(tool_copy)
            
            # Add documentation
            if 'documentation' in product:
                for doc in product.get('documentation', []):
                    if isinstance(doc, dict):
                        doc_copy = doc.copy()
                        doc_copy['task'] = doc.get('name', 'Unknown Document')
                        doc_copy['start'] = doc.get('start', '')
                        doc_copy['end'] = doc.get('end', '')
                        doc_copy['fundingType'] = doc.get('funding', 'None')
                        lane_tasks.append(doc_copy)
        
        # Add special NDT and part acceptance to Quality lane
        if lane == 'Quality':
            # Add special NDT
            if 'specialNDT' in product:
                for ndt in product.get('specialNDT', []):
                    if isinstance(ndt, dict):
                        ndt_copy = ndt.copy()
                        ndt_copy['task'] = ndt.get('name', 'Unknown NDT')
                        ndt_copy['start'] = ndt.get('startDate', '')
                        ndt_copy['end'] = ndt.get('endDate', '')
                        ndt_copy['fundingType'] = ndt.get('funding', 'None')
                        lane_tasks.append(ndt_copy)
            
            # Add part acceptance
            if 'partAcceptance' in product:
                for acceptance in product.get('partAcceptance', []):
                    if isinstance(acceptance, dict):
                        acceptance_copy = acceptance.copy()
                        acceptance_copy['task'] = acceptance.get('name', 'Unknown Acceptance')
                        acceptance_copy['start'] = acceptance.get('startDate', '')
                        acceptance_copy['end'] = acceptance.get('endDate', '')
                        acceptance_copy['fundingType'] = acceptance.get('funding', 'None')
                        lane_tasks.append(acceptance_copy)
        
        # Add material system tasks
        for material in material_systems:
            # Skip if a specific material is selected and this is not it
            if selected_material and selected_material != 'all' and material['id'] != selected_material:
                continue
                
            if 'roadmap' in material:
                for task in material['roadmap']:
                    if task.get('lane', 'M&P') == lane:
                        task_copy = task.copy()
                        task_copy['material'] = material['name']
                        task_copy['materialID'] = material['id']
                        lane_tasks.append(task_copy)
        
        # Sort tasks by start date
        lane_tasks.sort(key=lambda x: datetime.strptime(x.get('start', x.get('startDate', '2025-01-01')), "%Y-%m-%d") if x.get('start') or x.get('startDate') else datetime.now())
        
        for task in lane_tasks:
            y_pos -= 1
            all_tasks.append(task)  # Store all tasks for reference
            
            # Handle different date field names
            start_key = 'start' if 'start' in task else 'startDate'
            end_key = 'end' if 'end' in task else 'endDate'
            
            if not task.get(start_key) or not task.get(end_key):
                continue
                
            start_date = datetime.strptime(task[start_key], "%Y-%m-%d")
            end_date = datetime.strptime(task[end_key], "%Y-%m-%d")
            all_dates.extend([start_date, end_date])
            
            # Get task funding type and color
            funding_type = task.get('fundingType', 'None')
            color = FUNDING_COLORS.get(funding_type, '#999999')
            
            # Get task status
            status = task.get('status', 'Planned')
            
            # Check if task is floating
            is_floating = task.get('float', False)
            float_indicator = " (Floating)" if is_floating else ""
            
            # Get additional details if available
            additional_details = task.get('additionalDetails', '')
            
            # Get material info if available
            material_info = f" [{task.get('material', '')}]" if 'material' in task else ""
            material_id = task.get('materialID', '')
            
            # Create data source for the task
            task_source = ColumnDataSource(data=dict(
                start=[start_date],
                end=[end_date],
                y=[y_pos],
                task=[task.get('task', '')],
                status=[status],
                funding=[funding_type],
                floating=[is_floating],
                details=[additional_details],
                material=[task.get('material', '')],
                material_id=[material_id]
            ))
            
            # Add task rectangle with a unique name for identification in the callback
            task_rect = p.hbar(y='y', left='start', right='end', height=0.8, source=task_source,
                   color=color, alpha=0.8, name=f"task_{y_pos}")
            
            # Add hover tool for task
            hover = HoverTool(renderers=[task_rect], tooltips=[
                ("Task", "@task"),
                ("Status", "@status"),
                ("Timeline", "@start{%F} to @end{%F}"),
                ("Funding", "@funding"),
                ("Floating", "@floating"),
                ("Material", "@material"),
                ("Details", "@details")
            ], formatters={"@start": "datetime", "@end": "datetime"})
            p.add_tools(hover)
            
            # Add task label - place inside the box if there's enough space
            task_label = task.get('task', '') + float_indicator + material_info
            task_duration = (end_date - start_date).days
            
            # Place text inside the box if duration is long enough (more than 60 days)
            if task_duration > 60:
                # Place text inside the box
                text_x = start_date + (end_date - start_date) / 2  # Center of the bar
                p.text(x=text_x, y=y_pos, text=[task_label],
                       text_font_size="9pt", text_align="center", text_baseline="middle",
                       text_color="white", text_font_style="bold")
            else:
                # Place text outside the box (to the right)
                p.text(x=end_date, y=y_pos, text=[task_label],
                       text_font_size="9pt", text_align="left", text_baseline="middle",
                       x_offset=5)  # Add a small offset
            
            # Add to legend if not already there
            if funding_type not in [item.label for item in legend_items]:
                legend_items.append(LegendItem(label=funding_type, renderers=[task_rect]))
    
    # Add legend for funding types
    if legend_items:
        legend = Legend(items=legend_items, location="top_right", title="Funding Types")
        p.add_layout(legend, 'right')
    
    # Set x-axis range based on all dates
    if all_dates:
        min_date = min(all_dates) - timedelta(days=30)
        max_date = max(all_dates) + timedelta(days=30)
        p.x_range = Range1d(min_date, max_date)
    
    # Set y-axis range
    p.y_range = Range1d(y_pos - 1, 1)
    
    # Add today line
    today_line = Span(location=datetime.now(), dimension='height', line_color='#3498db', line_dash='dashed', line_width=2)
    p.add_layout(today_line)
    
    # Add today label
    today_label = Label(
        x=datetime.now(),
        y=0.5,
        text="Today",
        text_color="#3498db",
        text_font_style="bold",
        text_align="center",
        background_fill_color="white",
        background_fill_alpha=0.7
    )
    p.add_layout(today_label)
    
    # Import the components function for embedding Bokeh plots
    from bokeh.embed import components
    
    # Generate script and div components for the Bokeh plot
    script, div = components(p)
    
    # Count materials and associated programs
    materials_count = len(material_systems)
    
    # Count associated programs
    associated_programs = set()
    program_names = []
    for program in data['programs']:
        for combo in program.get('productMaterialCombinations', []):
            if combo.get('productID') == product_id:
                associated_programs.add(program['id'])
                program_names.append(f"{program['name']} ({program['id']})")
    
    programs_count = len(associated_programs)
    
    # Count total tasks
    total_tasks = len(all_tasks)
    
    # Create HTML content for the page
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{product['name']} ({product_id})</title>
        
        <!-- Include Bokeh scripts -->
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.6.3.min.js"></script>
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.6.3.min.js"></script>
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.6.3.min.js"></script>
        
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
            }}
            .container {{
                width: 1200px;
                max-width: 100%;
                margin: 0 auto;
                padding: 25px;
                box-sizing: border-box;
            }}
            .header {{
                background: linear-gradient(135deg, #3498db, #2c3e50);
                color: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .summary-card {{
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                padding: 25px;
                margin-bottom: 20px;
            }}
            .summary-card h2 {{
                color: #2c3e50;
                margin-top: 0;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                font-size: 22px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}
            .metric-item {{
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                padding: 20px;
                text-align: center;
            }}
            .metric-value {{
                font-size: 28px;
                font-weight: bold;
                color: #3498db;
                margin: 10px 0;
            }}
            .metric-label {{
                color: #7f8c8d;
            }}
            .nav-links {{
                margin-top: 15px;
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 10px;
            }}
            .nav-link {{
                color: white;
                text-decoration: none;
                padding: 8px 15px;
                background-color: rgba(255,255,255,0.2);
                border-radius: 4px;
                margin: 0 5px;
                transition: background-color 0.3s;
                display: inline-block;
            }}
            .nav-link:hover {{
                background-color: rgba(255,255,255,0.3);
            }}
            .section-heading {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 20px;
                font-size: 18px;
            }}
            .subsection-heading {{
                color: #2c3e50;
                font-size: 18px;
                margin-top: 20px;
                margin-bottom: 10px;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
            }}
            ul {{
                padding-left: 20px;
                margin-top: 10px;
            }}
            li {{
                margin-bottom: 5px;
            }}
            .material-item {{
                display: inline-block;
                margin: 5px 10px;
                padding: 5px 10px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #ddd;
            }}
            .funding-legend {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin-top: 15px;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }}
            .color-box {{
                width: 16px;
                height: 16px;
                display: inline-block;
                margin-right: 8px;
                border-radius: 3px;
            }}
            .bk-root {{
                width: 100% !important;
            }}
            .bk-root .bk-plot-wrapper {{
                width: 100% !important;
            }}
            @media (max-width: 768px) {{
                .metrics-grid {{
                    grid-template-columns: 1fr 1fr;
                }}
            }}
            @media (max-width: 480px) {{
                .metrics-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header with navigation -->
            <div class="header">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h1>{product['name']} ({product_id})</h1>
                    <div>
                        <a href="product_summary.html" class="nav-link">Back to Product Summary</a>
                        <a href="../index.html" class="nav-link">Back to Dashboard</a>
                    </div>
                </div>
                <div class="nav-links">
                    <a href="#requirements" class="nav-link">Requirements</a>
                    <a href="#business-case" class="nav-link">Business Case</a>
                    <a href="#roadmap" class="nav-link">Roadmap</a>
                    <span class="nav-link">TRL: {product.get('trl', 'N/A')}</span>
                </div>
            </div>
            
            <!-- Key Metrics -->
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">TRL</div>
                    <div class="metric-value">{product.get('trl', 'N/A')}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Material Systems</div>
                    <div class="metric-value">{materials_count}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Associated Programs</div>
                    <div class="metric-value">{programs_count}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Tasks</div>
                    <div class="metric-value">{total_tasks}</div>
                </div>
            </div>
            
            <!-- Requirements -->
            <div id="requirements" class="summary-card">
                <h2>Requirements</h2>
    """
    
    # Add requirements if available
    requirements = product.get('requirements', {})
    if requirements:
        html_content += '<ul>'
        for req_type, req_text in requirements.items():
            html_content += f'<li><strong>{req_type}:</strong> {req_text}</li>'
        html_content += '</ul>'
    else:
        html_content += "<p>No requirements specified</p>"
    
    html_content += """
            </div>
            
            <!-- Business Case -->
            <div id="business-case" class="summary-card">
                <h2>Business Case</h2>
    """
    
    # Add business case if available
    business_case = product.get('businessCase', {})
    if business_case:
        # Business category items
        business_items = []
        for key in ["Save schedule", "Save hardware costs", "Relieve supply chain constraints", "Increase Pwin by hitting PTW"]:
            if key in business_case and business_case[key] is True:
                business_items.append(key)
        
        # Unconventional Design category items
        design_items = []
        for key in ["Reduce specialty training", "Save weight", "Increase performance", "Unify parts"]:
            if key in business_case and business_case[key] is True:
                design_items.append(key)
        
        # Agility throughout program category items
        agility_items = []
        for key in ["Quickly iterate design/EMs", "Agility in Design and AI&T", "Digital Spares"]:
            if key in business_case and business_case[key] is True:
                agility_items.append(key)
        
        if business_items:
            html_content += """
                <h3 class="subsection-heading">Business</h3>
                <ul>
            """
            for item in business_items:
                html_content += f"<li>{item}</li>"
            html_content += "</ul>"
        
        if design_items:
            html_content += """
                <h3 class="subsection-heading">Unconventional Design</h3>
                <ul>
            """
            for item in design_items:
                html_content += f"<li>{item}</li>"
            html_content += "</ul>"
        
        if agility_items:
            html_content += """
                <h3 class="subsection-heading">Agility throughout program</h3>
                <ul>
            """
            for item in agility_items:
                html_content += f"<li>{item}</li>"
            html_content += "</ul>"
        
        # If no items were found to be true
        if not business_items and not design_items and not agility_items:
            html_content += "<p>No business case drivers selected</p>"
    else:
        html_content += "<p>No business case information available</p>"
    
    html_content += """
            </div>
    """
    
    # Add material system filter if there are multiple materials
    if len(material_systems) > 1:
        html_content += """
            <div class="summary-card">
                <h2>Filter by Material System</h2>
                <div class="material-filter">
                    <select id="material-select">
                        <option value="all">All Materials</option>
        """
        
        for material in material_systems:
            html_content += f'<option value="{material["id"]}">{material["name"]} ({material["id"]})</option>'
        
        html_content += """
                    </select>
                    <button id="filter-button" class="nav-link" style="background-color: #3498db; margin-left: 10px;">Apply Filter</button>
                </div>
            </div>
        """
    
    # Add funding type legend
    html_content += """
            <div class="summary-card">
                <h2>Funding Type Legend</h2>
                <div class="funding-legend">
    """
    
    for funding_type, color in FUNDING_COLORS.items():
        html_content += f'<div class="legend-item"><span class="color-box" style="background-color: {color};"></span>{funding_type}</div>'
    
    html_content += """
                </div>
            </div>
            
            <!-- Roadmap -->
            <div id="roadmap" class="summary-card">
                <h2>Product Roadmap</h2>
    """
    
    # Embed the Bokeh plot
    html_content += div
    
    html_content += """
            </div>
        </div>
    """
    
    # Add JavaScript for material filtering if needed
    if len(material_systems) > 1:
        html_content += """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const materialSelect = document.getElementById('material-select');
                const filterButton = document.getElementById('filter-button');
                
                // Apply initial filtering if there's a stored selection
                const selectedMaterial = localStorage.getItem('selectedMaterial');
                if (selectedMaterial) {
                    materialSelect.value = selectedMaterial;
                }
                
                // Add filter button click handler
                filterButton.addEventListener('click', function() {
                    const materialId = materialSelect.value;
                    localStorage.setItem('selectedMaterial', materialId);
                    
                    // Refresh the page to apply the filter
                    window.location.reload();
                });
            });
        </script>
        """
    
    # Add Bokeh script at the end
    html_content += script
    
    html_content += """
    </body>
    </html>
    """
    
    # Write the HTML to the file
    with open(os.path.join(product_dir, f"product_{product_id}.html"), "w") as f:
        f.write(html_content)
    
    print(f"Generated product page for {product['name']} ({product_id})")

def generate_product_summary(data, product_dir):
    """Generate a summary page for all products with styling matching implementation metrics page"""
    print("Generating product summary page...")
    
    # Calculate key metrics
    total_products = len(data['products'])
    total_material_systems = len(data['materialSystems'])
    total_programs = len(data['programs'])
    
    # Count total tasks across all products
    total_tasks = 0
    for product in data['products']:
        total_tasks += len(product.get('roadmap', []))
        total_tasks += len(product.get('designTools', []))
        total_tasks += len(product.get('documentation', []))
        total_tasks += len(product.get('specialNDT', []))
        total_tasks += len(product.get('partAcceptance', []))
    
    # Create TRL distribution data
    trls = {}
    for product in data['products']:
        trl = product.get('trl', 'Unknown')
        trl_key = str(trl) if trl else 'Unknown'
        if trl_key in trls:
            trls[trl_key] += 1
        else:
            trls[trl_key] = 1
    
    # Sort TRLs for display
    numeric_trls = []
    non_numeric_trls = []
    
    for k in trls.keys():
        if k == 'Unknown' or not k:
            continue
        try:
            numeric_trls.append(int(k))
        except (ValueError, TypeError):
            non_numeric_trls.append(k)
    
    numeric_trls.sort()
    non_numeric_trls.sort()
    sorted_trls = [str(trl) for trl in numeric_trls] + non_numeric_trls
    if 'Unknown' in trls or '' in trls:
        sorted_trls.append('Unknown')
    
    # Create TRL chart data
    trl_values = [trls[trl] for trl in sorted_trls]
    
    # Create a figure for the TRL distribution with improved styling
    p_trl = figure(
        title="Products by Technology Readiness Level (TRL)",
        x_range=sorted_trls,
        width=600,
        height=400,
        toolbar_location=None,
        background_fill_color="#f8f9fa",
        sizing_mode="stretch_width"  # Make responsive
    )
    
    # Set bar colors - use a blue gradient
    trl_colors = ['#3498db'] * len(sorted_trls)
    
    source_trl = ColumnDataSource(data={
        'x': sorted_trls,
        'top': trl_values,
        'line_color': trl_colors,
        'fill_color': trl_colors,
        'hatch_color': trl_colors,
    })
    
    # Add bars with better styling
    p_trl.vbar(
        x='x', top='top', width=0.5,
        line_color='line_color', fill_color='fill_color', hatch_color='hatch_color',
        line_alpha=0.8, fill_alpha=0.8, hatch_alpha=0.8,
        source=source_trl
    )
    
    # Customize appearance
    p_trl.title.text_font_size = '14pt'
    p_trl.title.text_color = '#2c3e50'
    p_trl.xaxis.axis_label = "TRL"
    p_trl.yaxis.axis_label = "Number of Products"
    p_trl.xgrid.grid_line_color = None
    
    # Create program distribution data
    program_product_counts = {}
    for program in data['programs']:
        program_name = program['name']
        product_count = 0
        product_ids = set()
        
        for combo in program.get('productMaterialCombinations', []):
            product_id = combo.get('productID')
            if product_id and product_id not in product_ids:
                product_ids.add(product_id)
                product_count += 1
        
        program_product_counts[program_name] = product_count
    
    # Sort by count
    sorted_programs = sorted(program_product_counts.items(), key=lambda x: x[1], reverse=True)
    program_names = [p[0] for p in sorted_programs]
    program_values = [p[1] for p in sorted_programs]
    
    # Create a figure for the program distribution
    p_program = figure(
        title="Products by Program",
        x_range=program_names,
        width=600,
        height=400,
        toolbar_location=None,
        background_fill_color="#f8f9fa",
        sizing_mode="stretch_width"  # Make responsive
    )
    
    # Use a different color palette for program bars
    program_colors = []
    for i in range(len(program_names)):
        idx = i % len(Category10[10])
        program_colors.append(Category10[10][idx])
    
    source_program = ColumnDataSource(data={
        'x': program_names,
        'top': program_values,
        'line_color': program_colors,
        'fill_color': program_colors,
        'hatch_color': program_colors,
    })
    
    # Add bars with better styling
    p_program.vbar(
        x='x', top='top', width=0.5,
        line_color='line_color', fill_color='fill_color', hatch_color='hatch_color',
        line_alpha=0.8, fill_alpha=0.8, hatch_alpha=0.8,
        source=source_program
    )
    
    # Customize appearance
    p_program.title.text_font_size = '14pt'
    p_program.title.text_color = '#2c3e50'
    p_program.xaxis.axis_label = "Program"
    p_program.yaxis.axis_label = "Number of Products"
    p_program.xgrid.grid_line_color = None
    p_program.xaxis.major_label_orientation = 45
    
    # Create funding distribution data
    funding_counts = {}
    
    # Count funding types across all products
    for product in data['products']:
        # Count in roadmap tasks
        for task in product.get('roadmap', []):
            funding_type = task.get('fundingType', '')
            if not funding_type:
                funding_type = 'None'
            if funding_type in funding_counts:
                funding_counts[funding_type] += 1
            else:
                funding_counts[funding_type] = 1
        
        # Count in design tools
        for tool in product.get('designTools', []):
            if isinstance(tool, dict):
                funding_type = tool.get('funding', '')
                if not funding_type:
                    funding_type = 'None'
                if funding_type in funding_counts:
                    funding_counts[funding_type] += 1
                else:
                    funding_counts[funding_type] = 1
        
        # Count other elements (documentation, NDT, part acceptance)
        for item_list in [product.get('documentation', []), product.get('specialNDT', []), product.get('partAcceptance', [])]:
            for item in item_list:
                if isinstance(item, dict):
                    funding_type = item.get('funding', '')
                    if not funding_type:
                        funding_type = 'None'
                    if funding_type in funding_counts:
                        funding_counts[funding_type] += 1
                    else:
                        funding_counts[funding_type] = 1
    
    # Sort by count
    sorted_funding = sorted(funding_counts.items(), key=lambda x: x[1], reverse=True)
    funding_names = [f[0] for f in sorted_funding]
    funding_values = [f[1] for f in sorted_funding]
    
    # Create a figure for the funding distribution
    p_funding = figure(
        title="Tasks by Funding Type",
        x_range=funding_names,
        width=1200,
        height=400,
        toolbar_location=None,
        background_fill_color="#f8f9fa",
        sizing_mode="stretch_width"  # Make responsive
    )
    
    # Get funding colors
    funding_colors = [FUNDING_COLORS.get(name, '#999999') for name in funding_names]
    
    source_funding = ColumnDataSource(data={
        'x': funding_names,
        'top': funding_values,
        'line_color': funding_colors,
        'fill_color': funding_colors,
        'hatch_color': funding_colors,
    })
    
    # Add bars with better styling
    p_funding.vbar(
        x='x', top='top', width=0.5,
        line_color='line_color', fill_color='fill_color', hatch_color='hatch_color',
        line_alpha=0.8, fill_alpha=0.8, hatch_alpha=0.8,
        source=source_funding
    )
    
    # Customize appearance
    p_funding.title.text_font_size = '14pt'
    p_funding.title.text_color = '#2c3e50'
    p_funding.xaxis.axis_label = "Funding Type"
    p_funding.yaxis.axis_label = "Number of Tasks"
    p_funding.xgrid.grid_line_color = None
    p_funding.xaxis.major_label_orientation = 45
    
    # Import the components function for embedding Bokeh plots
    from bokeh.embed import components
    
    # Generate script and div components for each figure
    script_trl, div_trl = components(p_trl)
    script_program, div_program = components(p_program)
    script_funding, div_funding = components(p_funding)
    
    # Create HTML content with embedded scripts and divs
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Product Summary</title>
        
        <!-- Include Bokeh scripts -->
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.6.3.min.js"></script>
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.6.3.min.js"></script>
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.6.3.min.js"></script>
        
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
            }}
            .container {{
                width: 1200px;
                max-width: 100%;
                margin: 0 auto;
                padding: 25px;
                box-sizing: border-box;
            }}
            .header {{
                background: linear-gradient(135deg, #3498db, #2c3e50);
                color: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .summary-card {{
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                padding: 25px;
                margin-bottom: 20px;
            }}
            .summary-card h2 {{
                color: #2c3e50;
                margin-top: 0;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                font-size: 22px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}
            .metric-item {{
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                padding: 20px;
                text-align: center;
            }}
            .metric-value {{
                font-size: 28px;
                font-weight: bold;
                color: #3498db;
                margin: 10px 0;
            }}
            .metric-label {{
                color: #7f8c8d;
            }}
            .nav-links {{
                margin-top: 15px;
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 10px;
            }}
            .nav-link {{
                color: white;
                text-decoration: none;
                padding: 8px 15px;
                background-color: rgba(255,255,255,0.2);
                border-radius: 4px;
                margin: 0 5px;
                transition: background-color 0.3s;
                display: inline-block;
            }}
            .nav-link:hover {{
                background-color: rgba(255,255,255,0.3);
            }}
            .section-heading {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 20px;
                font-size: 18px;
            }}
            .subsection-heading {{
                color: #2c3e50;
                font-size: 18px;
                margin-top: 20px;
                margin-bottom: 10px;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
            }}
            ul {{
                padding-left: 20px;
                margin-top: 10px;
            }}
            li {{
                margin-bottom: 5px;
            }}
            .material-item {{
                display: inline-block;
                margin: 5px 10px;
                padding: 5px 10px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #ddd;
            }}
            .funding-legend {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin-top: 15px;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }}
            .color-box {{
                width: 16px;
                height: 16px;
                display: inline-block;
                margin-right: 8px;
                border-radius: 3px;
            }}
            .bk-root {{
                width: 100% !important;
            }}
            .bk-root .bk-plot-wrapper {{
                width: 100% !important;
            }}
            @media (max-width: 768px) {{
                .metrics-grid {{
                    grid-template-columns: 1fr 1fr;
                }}
            }}
            @media (max-width: 480px) {{
                .metrics-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header with navigation -->
            <div class="header">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h1>Product Summary</h1>
                    <div>
                        <a href="../index.html" class="nav-link">Back to Dashboard</a>
                    </div>
                </div>
                <div class="nav-links">
                    <a href="product_material_distribution.html" class="nav-link">View Distribution Charts</a>
                    <a href="../materials/material_summary.html" class="nav-link">Material Systems</a>
                    <a href="../programs/program_summary.html" class="nav-link">Programs</a>
                </div>
            </div>
            
            <!-- Key Metrics -->
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">Total Products</div>
                    <div class="metric-value">{total_products}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Total Material Systems</div>
                    <div class="metric-value">{total_material_systems}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Programs</div>
                    <div class="metric-value">{total_programs}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Total Tasks</div>
                    <div class="metric-value">{total_tasks}</div>
                </div>
            </div>
            
            <!-- Charts Section -->
            <div class="summary-card">
                <h2>Product Distribution</h2>
                <div class="charts-container">
                    <!-- First row of charts -->
                    <div class="chart-wrapper" style="width: 48%;">
                        <h3 class="section-heading">Products by TRL</h3>
    """
    
    # Embed TRL chart
    html_content += div_trl
    
    html_content += """
                    </div>
                    <!-- SWAPPED: Now showing Tasks by Funding Type in second position -->
                    <div class="chart-wrapper" style="width: 48%;">
                        <h3 class="section-heading">Tasks by Funding Type</h3>
    """
    
    # Embed Funding chart (swapped position with Program chart)
    html_content += div_funding
    
    html_content += """
                    </div>
                </div>
                
                <!-- SWAPPED: Now showing Products by Program in second row -->
                <div class="chart-wrapper">
                    <h3 class="section-heading">Products by Program</h3>
    """
    
    # Embed Program chart (swapped position with Funding chart)
    html_content += div_program
    
    html_content += """
                </div>
            </div>
            
            <!-- Product List -->
            <div class="summary-card">
                <h2>All Products</h2>
                <div style="overflow-x: auto;">
                    <table class="product-table">
                        <thead>
                            <tr>
                                <th>Product Name</th>
                                <th>ID</th>
                                <th>TRL</th>
                                <th>Associated Programs</th>
                                <th>Material Systems</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # Add product rows
    for product in sorted(data['products'], key=lambda x: x['name']):
        # Get associated programs
        associated_programs = []
        for program in data['programs']:
            for combo in program.get('productMaterialCombinations', []):
                if combo.get('productID') == product['id']:
                    associated_programs.append(f"{program['name']} ({program['id']})")
                    break  # Only count each program once per product
        
        # Get material systems
        material_systems = []
        for material_entry in product.get('materialSystems', []):
            if isinstance(material_entry, str):
                material_id = material_entry
            elif isinstance(material_entry, dict) and 'materialID' in material_entry:
                material_id = material_entry['materialID']
            else:
                continue
                
            material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
            if material:
                material_systems.append(f"{material['name']} ({material_id})")
        
        # Format lists for display
        programs_display = ", ".join(associated_programs) if associated_programs else "None"
        materials_display = ", ".join(material_systems) if material_systems else "None"
        trl_display = product.get('trl', '') if product.get('trl') else ''
        
        html_content += f"""
                            <tr>
                                <td><a href='product_{product['id']}.html'>{product['name']}</a></td>
                                <td>{product['id']}</td>
                                <td>{trl_display}</td>
                                <td>{programs_display}</td>
                                <td>{materials_display}</td>
                            </tr>
        """
    
    html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Add Bokeh scripts at the end -->
    """
    
    # Add the script tags for each plot
    html_content += script_trl
    html_content += script_program
    html_content += script_funding
    
    html_content += """
    </body>
    </html>
    """
    
    # Write the HTML to the file
    with open(os.path.join(product_dir, "product_summary.html"), "w") as f:
        f.write(html_content)
    
    print("Product summary page generated successfully.")

def generate_product_distribution_charts(data, product_dir):
    """Generate distribution charts for products"""
    # Count material systems per product
    materials_per_product = {}
    for product in data['products']:
        product_id = product['id']
        materials_per_product[product_id] = len(product.get('materialSystems', []))
    
    # Create a figure for materials per product
    product_names = []
    material_counts = []
    
    for product_id, count in materials_per_product.items():
        product = next((p for p in data['products'] if p['id'] == product_id), None)
        if product:
            product_names.append(f"{product['name']} ({product_id})")
            material_counts.append(count)
    
    # Sort by count
    sorted_indices = np.argsort(material_counts)[::-1]  # Descending order
    product_names = [product_names[i] for i in sorted_indices]
    material_counts = [material_counts[i] for i in sorted_indices]
    
    # Create a figure for materials per product
    p = figure(
        title="Number of Material Systems per Product",
        x_range=product_names,
        width=1200,
        height=500,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Add bars
    p.vbar(
        x=product_names,
        top=material_counts,
        width=0.7,
        color=Category10[10][1],
        alpha=0.8
    )
    
    # Customize appearance
    p.title.text_font_size = '14pt'
    p.title.text_color = '#2c3e50'
    p.xaxis.axis_label = "Product"
    p.yaxis.axis_label = "Number of Material Systems"
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 45
    p.background_fill_color = "#f8f9fa"
    
    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Product", "@x"),
        ("Material Systems", "@top"),
    ]
    p.add_tools(hover)
    
    # Create a figure for tasks per funding type
    funding_counts = {}
    
    # Count funding types across all products
    for product in data['products']:
        # Count in roadmap tasks
        for task in product.get('roadmap', []):
            funding_type = task.get('fundingType', 'None')
            if funding_type in funding_counts:
                funding_counts[funding_type] += 1
            else:
                funding_counts[funding_type] = 1
        
        # Count in design tools
        for tool in product.get('designTools', []):
            if isinstance(tool, dict):
                funding_type = tool.get('funding', 'None')
                if funding_type in funding_counts:
                    funding_counts[funding_type] += 1
                else:
                    funding_counts[funding_type] = 1
        
        # Count in documentation
        for doc in product.get('documentation', []):
            if isinstance(doc, dict):
                funding_type = doc.get('funding', 'None')
                if funding_type in funding_counts:
                    funding_counts[funding_type] += 1
                else:
                    funding_counts[funding_type] = 1
        
        # Count in special NDT
        for ndt in product.get('specialNDT', []):
            if isinstance(ndt, dict):
                funding_type = ndt.get('funding', 'None')
                if funding_type in funding_counts:
                    funding_counts[funding_type] += 1
                else:
                    funding_counts[funding_type] = 1
        
        # Count in part acceptance
        for acceptance in product.get('partAcceptance', []):
            if isinstance(acceptance, dict):
                funding_type = acceptance.get('funding', 'None')
                if funding_type in funding_counts:
                    funding_counts[funding_type] += 1
                else:
                    funding_counts[funding_type] = 1
    
    # Sort by count
    sorted_funding = sorted(funding_counts.items(), key=lambda x: x[1], reverse=True)
    funding_names = [f[0] for f in sorted_funding]
    funding_values = [f[1] for f in sorted_funding]
    
    # Create a figure for the funding distribution
    p2 = figure(
        title="Tasks by Funding Type",
        x_range=funding_names,
        width=1200,
        height=500,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Add bars with colors matching the funding type colors
    p2.vbar(
        x=funding_names,
        top=funding_values,
        width=0.7,
        color=[FUNDING_COLORS.get(name, '#999999') for name in funding_names],
        alpha=0.8
    )
    
    # Customize appearance
    p2.title.text_font_size = '14pt'
    p2.title.text_color = '#2c3e50'
    p2.xaxis.axis_label = "Funding Type"
    p2.yaxis.axis_label = "Number of Tasks"
    p2.xgrid.grid_line_color = None
    p2.xaxis.major_label_orientation = 45
    
    # Add hover tool
    hover2 = HoverTool()
    hover2.tooltips = [
        ("Funding Type", "@x"),
        ("Number of Tasks", "@top"),
    ]
    p2.add_tools(hover2)
    
    # Create header with updated styling to match implementation page
    header = """
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1>Product Distribution Charts</h1>
            <div>
                <a href="product_summary.html" class="nav-link">Back to Product Summary</a>
                <a href="../index.html" class="nav-link">Back to Dashboard</a>
            </div>
        </div>
        <div style="margin-top: 10px;">
            <a href="#material-systems" class="nav-link">Material Systems</a>
            <a href="#funding-types" class="nav-link">Funding Types</a>
        </div>
    </div>
    """
    
    # Create metrics section
    # Calculate metrics for the cards
    total_products = len(data['products'])
    total_materials = len(data['materialSystems'])
    total_tasks = sum(funding_counts.values())
    avg_materials_per_product = sum(material_counts) / len(material_counts) if material_counts else 0
    
    metrics_html = f"""
    <div class="summary-card">
        <h2 class="section-heading">Key Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-item">
                <div class="metric-label">Total Products</div>
                <div class="metric-value">{total_products}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Material Systems</div>
                <div class="metric-value">{total_materials}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Total Tasks</div>
                <div class="metric-value">{total_tasks}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Avg Materials/Product</div>
                <div class="metric-value">{avg_materials_per_product:.1f}</div>
            </div>
        </div>
    </div>
    """
    
    # Create funding legend explanation with updated styling
    funding_legend = """
    <div class="summary-card">
        <h2 class="section-heading">Funding Type Legend</h2>
        <div style="display: flex; flex-wrap: wrap; margin-top: 15px;">
    """
    
    for funding_type, color in FUNDING_COLORS.items():
        funding_legend += f'<div class="material-item"><span style="display: inline-block; width: 20px; height: 20px; background-color: {color}; margin-right: 10px; vertical-align: middle;"></span>{funding_type}</div>'
    
    funding_legend += """
        </div>
    </div>
    """
    
    # Create distribution charts section - matching implementation page style
    materials_chart = """
    <div id="material-systems" class="summary-card">
        <h2 class="section-heading">Material Systems per Product</h2>
        <p>This chart shows the number of material systems used for each product.</p>
        <div class="chart-container">
            <!-- The bokeh material systems chart will be placed here -->
        </div>
    </div>
    """
    
    funding_chart = """
    <div id="funding-types" class="summary-card">
        <h2 class="section-heading">Tasks by Funding Type</h2>
        <p>This chart shows the distribution of tasks across different funding types.</p>
        <div class="chart-container">
            <!-- The bokeh funding chart will be placed here -->
        </div>
    </div>
    """
    
    # Add media queries and additional styles
    additional_styles = """
    <style>
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        @media (max-width: 768px) {
            .metrics-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
        @media (max-width: 480px) {
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
        .chart-container {
            width: 100%;
            margin: 20px auto;
            text-align: center;
        }
    </style>
    """
    
    # Create divs with improved structure
    header_div = Div(text=GLOBAL_STYLE + additional_styles + header, width=1200)
    metrics_div = Div(text=metrics_html, width=1200)
    funding_legend_div = Div(text=funding_legend, width=1200)
    materials_chart_div = Div(text=materials_chart, width=1200)
    funding_chart_div = Div(text=funding_chart, width=1200)
    
    # Create layout with better structure
    layout_obj = column(
        header_div,
        metrics_div,
        funding_legend_div,
        materials_chart_div,
        p,
        funding_chart_div,
        p2
    )
    
    # Output to file
    output_file(os.path.join(product_dir, "product_material_distribution.html"))
    save(layout_obj) 