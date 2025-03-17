import os
from datetime import datetime, timedelta
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Range1d, Span, Legend, LegendItem, Div, Tabs, Panel, CheckboxGroup, CustomJS, RadioButtonGroup
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import Category10, Spectral6, Turbo256
from bokeh.transform import factor_cmap
import numpy as np
from bokeh.embed import components

# Define funding type colors - copied from product_viz.py for consistency
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

def generate_product_detail_page(product, data, product_dir, status_colors):
    """Generate an updated detailed page for a single product with the new layout requirements"""
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
    
    # Process tasks by lane (similar logic to original function)
    lanes = ['Design', 'Manufacturing', 'M&P', 'Quality', 'Other']
    y_pos = 0
    legend_items = []
    all_dates = []
    all_tasks = []
    
    # Collect program need dates (similar logic to original function)
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
    
    # Add program need dates as vertical lines
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
    
    # Process tasks by lane (similar logic to original function)
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
    
    # Generate script and div components for the Bokeh plot
    script, div = components(p)
    
    # Count materials and associated programs
    materials_count = len(material_systems)
    
    # Get programs associated with this product and their material systems
    product_program_materials = []
    for program in data['programs']:
        program_materials = []
        for combo in program.get('productMaterialCombinations', []):
            if combo.get('productID') == product_id:
                material_id = combo.get('materialID')
                material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
                material_name = material['name'] if material else 'Unknown'
                
                # Check if this product-material-program combination already exists
                exists = False
                for existing in program_materials:
                    if existing['material_id'] == material_id:
                        exists = True
                        break
                
                if not exists:
                    program_materials.append({
                        'material_id': material_id,
                        'material_name': material_name,
                        'part_name': combo.get('partName', 'N/A'),
                        'part_number': combo.get('partNumber', 'N/A'),
                        'need_date': combo.get('needDate', 'N/A'),
                        'adoption_status': combo.get('adoptionStatus', 'N/A')
                    })
        
        if program_materials:
            product_program_materials.append({
                'program_id': program['id'],
                'program_name': program['name'],
                'materials': program_materials
            })
    
    programs_count = len(product_program_materials)
    
    # Count total tasks
    total_tasks = len(all_tasks)
    
    # Create HTML content for the page with the new layout
    with open(os.path.join(product_dir, f"product_{product_id}.html"), "w") as f:
        f.write(generate_product_html_content(product, product_id, materials_count, programs_count, 
                                             total_tasks, material_systems, product_program_materials,
                                             script, div))
    
    print(f"Generated updated product page for {product['name']} ({product_id})")

def generate_product_html_content(product, product_id, materials_count, programs_count, 
                                 total_tasks, material_systems, product_program_materials,
                                 script, div):
    """Generate the HTML content for the product detail page with the new layout:
    1. Requirements and business case side by side
    2. Programs listing with material systems
    3. Material system filter below programs
    4. Quad box layout for the 4 main swimlanes
    """
    
    # Start with the HTML head section
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
            .flex-container {{
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }}
            .flex-item {{
                flex: 1;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                padding: 25px;
            }}
            .quad-container {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                grid-template-rows: auto auto;
                gap: 20px;
                margin-bottom: 20px;
            }}
            .quad-item {{
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                padding: 20px;
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
            .status-badge {{
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
                margin-left: 5px;
                color: white;
            }}
            .status-planned {{
                background-color: #f39c12;
            }}
            .status-inprogress {{
                background-color: #3498db;
            }}
            .status-complete {{
                background-color: #2ecc71;
            }}
            .status-blocked {{
                background-color: #e74c3c;
            }}
            .status-deferred {{
                background-color: #95a5a6;
            }}
            .program-card {{
                margin-bottom: 15px;
                border-left: 4px solid #3498db;
                padding-left: 15px;
            }}
            .program-card h4 {{
                margin-top: 0;
                margin-bottom: 10px;
                color: #2c3e50;
            }}
            .material-badge {{
                display: inline-block;
                background-color: #eaf4fb;
                border: 1px solid #bde0f6;
                border-radius: 3px;
                padding: 3px 8px;
                margin-right: 5px;
                font-size: 13px;
                color: #3498db;
            }}
            .supplier-badge {{
                display: inline-block;
                background-color: #e8f5e9;
                border: 1px solid #c8e6c9;
                border-radius: 3px;
                padding: 3px 8px;
                margin-right: 5px;
                font-size: 13px;
                color: #2e7d32;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            table thead th {{
                background-color: #f8f9fa;
                padding: 8px;
                text-align: left;
                border-bottom: 2px solid #e9ecef;
            }}
            table tbody td {{
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }}
            .material-system-content {{
                display: none; /* Hide all material system content by default */
            }}
            .active-material {{
                display: block; /* Show only the active material system's content */
            }}
            @media (max-width: 768px) {{
                .flex-container {{
                    flex-direction: column;
                }}
                .quad-container {{
                    grid-template-columns: 1fr;
                }}
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
                    <a href="#info" class="nav-link">Info</a>
                    <a href="#programs" class="nav-link">Programs</a>
                    <a href="#lanes" class="nav-link">Swimlanes</a>
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
            
            <!-- Requirements and Business Case side by side -->
            <div id="info" class="flex-container">
                <!-- Requirements -->
                <div class="flex-item">
                    <h2 class="section-heading">Requirements</h2>
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
                <div class="flex-item">
                    <h2 class="section-heading">Business Case</h2>
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
            </div>
            
            <!-- Programs using this product -->
            <div id="programs" class="summary-card">
                <h2>Programs Using This Product</h2>
    """
    
    # Add programs and their material systems
    if product_program_materials:
        for program_info in product_program_materials:
            html_content += f"""
                <div class="program-card">
                    <h4>{program_info['program_name']} ({program_info['program_id']})</h4>
                    <table>
                        <thead>
                            <tr>
                                <th>Material System</th>
                                <th>Part Name</th>
                                <th>Part Number</th>
                                <th>Need Date</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for material in program_info['materials']:
                status_class = "status-planned"
                if material['adoption_status'].lower() == 'in progress':
                    status_class = "status-inprogress"
                elif material['adoption_status'].lower() == 'complete':
                    status_class = "status-complete"
                elif material['adoption_status'].lower() == 'blocked':
                    status_class = "status-blocked"
                elif material['adoption_status'].lower() == 'deferred':
                    status_class = "status-deferred"
                
                html_content += f"""
                            <tr>
                                <td><span class="material-badge">{material['material_name']} ({material['material_id']})</span></td>
                                <td>{material['part_name']}</td>
                                <td>{material['part_number']}</td>
                                <td>{material['need_date']}</td>
                                <td><span class="status-badge {status_class}">{material['adoption_status']}</span></td>
                            </tr>
                """
            
            html_content += """
                        </tbody>
                    </table>
                </div>
            """
    else:
        html_content += "<p>No programs are currently using this product.</p>"
    
    html_content += """
            </div>
            
            <!-- Material System Filter -->
    """
    
    # Add material system filter if there are materials
    if material_systems:
        html_content += """
            <div class="summary-card">
                <h2>Filter Roadmap by Material System</h2>
                <div class="material-filter" style="margin-top: 10px;">
                    <select id="material-select" style="padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
        """
        
        # Only show the applicable material systems, not "All Materials"
        for material in material_systems:
            html_content += f'<option value="{material["id"]}">{material["name"]} ({material["id"]})</option>'
        
        html_content += """
                    </select>
                    <button id="filter-button" class="nav-link" style="background-color: #3498db; margin-left: 10px;">Apply Filter</button>
                </div>
            </div>
        """
    
    # Quad box layout with swimlanes
    html_content += """
            <!-- Quad Box Layout for Swimlanes -->
            <div id="lanes" class="quad-container">
    """
    
    # Define the lanes to include in the quad box
    quad_lanes = ['Design', 'Manufacturing', 'M&P', 'Quality']
    
    # Create quad boxes for each lane
    for lane in quad_lanes:
        html_content += f"""
                <!-- {lane} Lane -->
                <div class="quad-item">
                    <h3 class="section-heading">{lane}</h3>
        """

        # For each material system, create a div with material-specific content
        for material in material_systems:
            material_id = material['id']
            html_content += f'<div class="material-system-content" id="material-{material_id}-{lane.lower()}">'
            
            # Add lane-specific content
            if lane == 'Design':
                # Add design tools
                html_content += """
                        <h4 class="subsection-heading">Design Tools</h4>
                        <ul>
                """
                
                if 'designTools' in product and product['designTools']:
                    for tool in product['designTools']:
                        if isinstance(tool, dict):
                            status = tool.get('status', 'Planned')
                            status_class = get_status_class(status)
                            html_content += f'<li>{tool.get("name", "Unknown")} <span class="status-badge {status_class}">{status}</span></li>'
                else:
                    html_content += "<li>No design tools specified</li>"
                
                html_content += """
                        </ul>
                        
                        <h4 class="subsection-heading">Documentation</h4>
                        <ul>
                """
                
                # Add documentation
                if 'documentation' in product and product['documentation']:
                    for doc in product['documentation']:
                        if isinstance(doc, dict):
                            status = doc.get('status', 'Planned')
                            status_class = get_status_class(status)
                            html_content += f'<li>{doc.get("name", "Unknown")} <span class="status-badge {status_class}">{status}</span></li>'
                else:
                    html_content += "<li>No documentation specified</li>"
                
                html_content += """
                        </ul>
                """
            
            elif lane == 'Manufacturing':
                # Add qualified machines and suppliers for this material system
                html_content += """
                        <h4 class="subsection-heading">Printing Suppliers</h4>
                        <ul>
                """
                
                if 'qualifiedMachines' in material:
                    for machine in material.get('qualifiedMachines', []):
                        if isinstance(machine, dict):
                            machine_name = machine.get('machine', 'Unknown Machine')
                            html_content += f'<li><strong>{machine_name}</strong>'
                            
                            # List suppliers for this machine
                            suppliers = machine.get('Supplier', [])
                            if suppliers:
                                html_content += ': '
                                for supplier_id in suppliers:
                                    html_content += f'<span class="supplier-badge">{supplier_id}</span> '
                            
                            html_content += '</li>'
                
                if not material.get('qualifiedMachines'):
                    html_content += "<li>No qualified machines specified</li>"
                
                html_content += """
                        </ul>
                        
                        <h4 class="subsection-heading">Post-Processing Suppliers</h4>
                        <ul>
                """
                
                # Add post-processing suppliers for this material system
                if 'postProcessing' in material:
                    for process in material.get('postProcessing', []):
                        if isinstance(process, dict):
                            process_name = process.get('name', 'Unknown Process')
                            html_content += f'<li><strong>{process_name}</strong>'
                            
                            # List suppliers for this process
                            suppliers = process.get('Supplier', [])
                            if suppliers:
                                html_content += ': '
                                for supplier_id in suppliers:
                                    html_content += f'<span class="supplier-badge">{supplier_id}</span> '
                            
                            html_content += '</li>'
                
                if not material.get('postProcessing'):
                    html_content += "<li>No post-processing suppliers specified for this material system</li>"
                
                html_content += """
                        </ul>
                        
                        <h4 class="subsection-heading">Product-Specific Post-Processing</h4>
                        <ul>
                """
                
                # Add product-specific post-processing suppliers
                product_post_processing = []
                for pp in product.get('postProcessingSuppliers', []):
                    if isinstance(pp, dict):
                        process_name = pp.get('process', 'Unknown Process')
                        suppliers = pp.get('supplier', [])
                        product_post_processing.append((process_name, suppliers))
                
                if product_post_processing:
                    for process, suppliers in product_post_processing:
                        html_content += f'<li><strong>{process}</strong>'
                        
                        if suppliers:
                            html_content += ': '
                            for supplier_id in suppliers:
                                html_content += f'<span class="supplier-badge">{supplier_id}</span> '
                        
                        html_content += '</li>'
                else:
                    html_content += "<li>No product-specific post-processing suppliers specified</li>"
                
                html_content += """
                        </ul>
                """
            
            elif lane == 'Quality':
                # Add standard NDE methods for this material system
                html_content += """
                        <h4 class="subsection-heading">Standard NDE Methods</h4>
                        <ul>
                """
                
                standard_ndt_methods = material.get('standardNDT', [])
                if standard_ndt_methods:
                    for ndt_method in standard_ndt_methods:
                        html_content += f'<li>{ndt_method}</li>'
                else:
                    html_content += "<li>No standard NDE methods specified for this material system</li>"
                
                html_content += """
                        </ul>
                        
                        <h4 class="subsection-heading">Special NDT</h4>
                        <ul>
                """
                
                # Add special NDT items
                if 'specialNDT' in product and product['specialNDT']:
                    for ndt in product['specialNDT']:
                        if isinstance(ndt, dict):
                            status = ndt.get('status', 'Planned')
                            status_class = get_status_class(status)
                            html_content += f'<li>{ndt.get("name", "Unknown")} <span class="status-badge {status_class}">{status}</span></li>'
                else:
                    html_content += "<li>No special NDT specified</li>"
                
                html_content += """
                        </ul>
                        
                        <h4 class="subsection-heading">Part Acceptance</h4>
                        <ul>
                """
                
                # Add part acceptance items
                if 'partAcceptance' in product and product['partAcceptance']:
                    for acceptance in product['partAcceptance']:
                        if isinstance(acceptance, dict):
                            status = acceptance.get('status', 'Planned')
                            status_class = get_status_class(status)
                            html_content += f'<li>{acceptance.get("name", "Unknown")} <span class="status-badge {status_class}">{status}</span></li>'
                else:
                    html_content += "<li>No part acceptance criteria specified</li>"
                
                html_content += """
                        </ul>
                """
            
            else:  # M&P lane or other
                # Show material-specific information for M&P lane
                if lane == 'M&P':
                    # Add material properties and other information
                    html_content += f"""
                        <h4 class="subsection-heading">Material Information</h4>
                        <ul>
                            <li><strong>Process:</strong> {material.get('process', 'N/A')}</li>
                            <li><strong>Material:</strong> {material.get('material', 'N/A')}</li>
                            <li><strong>MRL:</strong> {material.get('mrl', 'N/A')}</li>
                            <li><strong>Qualification:</strong> {material.get('qualification', 'N/A')}</li>
                            <li><strong>Qualification Class:</strong> {material.get('qualificationClass', 'N/A')}</li>
                            <li><strong>Statistical Basis:</strong> {material.get('statisticalBasis', 'N/A')}</li>
                        </ul>
                    """
                
                # Add roadmap tasks for this lane
                html_content += """
                        <h4 class="subsection-heading">Tasks</h4>
                """
                
                # Collect tasks from product roadmap for this lane
                lane_tasks = [t for t in product.get('roadmap', []) if t.get('lane', 'Other') == lane]
                
                # Also include material-specific tasks for this lane
                material_lane_tasks = []
                if 'roadmap' in material:
                    material_lane_tasks = [t for t in material['roadmap'] if t.get('lane', 'M&P') == lane]
                
                if lane_tasks or material_lane_tasks:
                    html_content += """
                        <ul>
                    """
                    
                    # Add product tasks
                    for task in lane_tasks:
                        status = task.get('status', 'Planned')
                        status_class = get_status_class(status)
                        html_content += f'<li>{task.get("task", "Unknown")} <span class="status-badge {status_class}">{status}</span></li>'
                    
                    # Add material tasks
                    for task in material_lane_tasks:
                        task_name = task.get('task', '')
                        status = task.get('status', 'Planned')
                        status_class = get_status_class(status)
                        html_content += f'<li>{task_name} [Material Task] <span class="status-badge {status_class}">{status}</span></li>'
                    
                    html_content += """
                        </ul>
                    """
                else:
                    html_content += "<p>No tasks specified for this lane</p>"
            
            # Close the material-specific div
            html_content += "</div>"
        
        # Close the quad-item div
        html_content += """
                </div>
        """
    
    # Add funding type legend
    html_content += """
            </div>
            
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
    
    # Add JavaScript for material filtering
    if material_systems:
        # Get the first material ID as default
        default_material_id = material_systems[0]['id'] if material_systems else ''
        
        html_content += f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const materialSelect = document.getElementById('material-select');
                const filterButton = document.getElementById('filter-button');
                
                // Function to show material-specific content
                function showMaterialContent(materialId) {{
                    // Hide all material content first
                    const allMaterialContent = document.querySelectorAll('.material-system-content');
                    allMaterialContent.forEach(content => {{
                        content.classList.remove('active-material');
                    }});
                    
                    // Show the selected material's content
                    const lanes = ['design', 'manufacturing', 'mandp', 'quality'];
                    lanes.forEach(lane => {{
                        const contentId = `material-${{materialId}}-${{lane}}`;
                        const contentElement = document.getElementById(contentId);
                        if (contentElement) {{
                            contentElement.classList.add('active-material');
                        }}
                    }});
                    
                    // Store the selection in localStorage
                    localStorage.setItem('selectedMaterial', materialId);
                }}
                
                // Apply initial filtering from stored selection or use first material
                const selectedMaterial = localStorage.getItem('selectedMaterial') || '{default_material_id}';
                if (selectedMaterial) {{
                    materialSelect.value = selectedMaterial;
                    showMaterialContent(selectedMaterial);
                }}
                
                // Add filter button click handler
                filterButton.addEventListener('click', function() {{
                    const materialId = materialSelect.value;
                    showMaterialContent(materialId);
                }});
                
                // Initial display
                showMaterialContent(materialSelect.value);
            }});
        </script>
        """
    
    # Add Bokeh script at the end
    html_content += script
    
    html_content += """
    </body>
    </html>
    """
    
    return html_content

def get_status_class(status):
    """Helper function to get the CSS class for a status badge"""
    status = status.lower()
    if status == 'in progress':
        return 'status-inprogress'
    elif status == 'complete':
        return 'status-complete'
    elif status == 'blocked':
        return 'status-blocked'
    elif status == 'deferred':
        return 'status-deferred'
    else:
        return 'status-planned'  # Default 