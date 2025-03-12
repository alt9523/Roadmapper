import os
from datetime import datetime, timedelta
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Range1d, Span, Legend, LegendItem, Div, Tabs, Panel, CheckboxGroup, CustomJS, RadioButtonGroup
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import Category10, Spectral6, Turbo256
from bokeh.transform import factor_cmap
import matplotlib.pyplot as plt
import numpy as np

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

def generate_product_visualizations(data, output_dir, status_colors):
    """Generate visualizations for products"""
    print("Generating product visualizations...")
    
    # Create product directory if it doesn't exist
    product_dir = os.path.join(output_dir, "products")
    if not os.path.exists(product_dir):
        os.makedirs(product_dir)
    
    # Generate individual product pages
    for product in data['products']:
        generate_product_page(product, data, product_dir, status_colors)
    
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
        title=f"Roadmap for {product['name']} ({product_id})",
        x_axis_type="datetime",
        width=1200,
        height=600,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Customize appearance
    p.title.text_font_size = '16pt'
    p.xaxis.axis_label = "Timeline"
    p.yaxis.axis_label = "Tasks"
    p.grid.grid_line_alpha = 0.3
    p.background_fill_color = "#f8f9fa"
    
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
    material_toggle_div = None
    selected_material = None
    if len(material_systems) > 1:
        material_names = [f"{m['name']} ({m['id']})" for m in material_systems]
        material_toggle_html = f"""
        <div style="margin-bottom: 15px;">
            <label for="material-select">Select Material System: </label>
            <select id="material-select" onchange="changeMaterial(this.value)">
                <option value="all">All Materials</option>
                {"".join([f'<option value="{m["id"]}">{m["name"]} ({m["id"]})</option>' for m in material_systems])}
            </select>
        </div>
        <script>
            function changeMaterial(materialId) {{
                // Store the selected material ID in localStorage
                localStorage.setItem('selectedMaterial', materialId);
                // Reload the page to apply the filter
                location.reload();
            }}
            
            // Check if there's a selected material in localStorage
            window.onload = function() {{
                const selectedMaterial = localStorage.getItem('selectedMaterial');
                if (selectedMaterial) {{
                    document.getElementById('material-select').value = selectedMaterial;
                }}
            }};
        </script>
        """
        material_toggle_div = Div(text=material_toggle_html, width=1200)
        
        # Check if a material is selected (this is a placeholder - in a real implementation,
        # we would use a server-side approach or a more sophisticated client-side approach)
        # For now, we'll just use the first material as the selected one if there are multiple
        selected_material = material_systems[0]['id']
    
    # Process tasks by lane
    lanes = ['Design', 'Manufacturing', 'M&P', 'Quality', 'Other']
    y_pos = 0
    legend_items = []
    all_dates = []
    
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
                material=[task.get('material', '')]
            ))
            
            # Add task rectangle
            task_rect = p.hbar(y='y', left='start', right='end', height=0.8, source=task_source,
                   color=color, alpha=0.8)
            
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
    today_line = Span(location=datetime.now(), dimension='height', line_color='red', line_dash='dashed', line_width=2)
    p.add_layout(today_line)
    
    # Create product info section
    product_info = f"""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h2>{product['name']} ({product_id})</h2>
        <p><strong>TRL:</strong> {product.get('trl', 'Not specified')}</p>
        <p><strong>Requirements:</strong></p>
        <ul>
    """
    
    # Add requirements if available
    requirements = product.get('requirements', {})
    if requirements:
        for req_type, req_text in requirements.items():
            product_info += f"<li><strong>{req_type}:</strong> {req_text}</li>"
    else:
        product_info += "<li>No requirements specified</li>"
    
    product_info += "</ul>"
    
    # Add business case if available
    business_case = product.get('businessCase', {})
    if business_case:
        product_info += "<p><strong>Business Case:</strong></p><ul>"
        
        # Check if business case is in checkbox format
        if "Save schedule" in business_case:
            # Business category
            product_info += "<li><strong>Business:</strong><ul>"
            for key in ["Save schedule", "Save hardware costs", "Relieve supply chain constraints", "Increase Pwin by hitting PTW"]:
                if key in business_case:
                    value = "Yes" if business_case[key] else "No"
                    product_info += f"<li>{key}: {value}</li>"
            product_info += "</ul></li>"
            
            # Unconventional Design category
            product_info += "<li><strong>Unconventional Design:</strong><ul>"
            for key in ["Reduce specialty training", "Save weight", "Increase performance", "Unify parts"]:
                if key in business_case:
                    value = "Yes" if business_case[key] else "No"
                    product_info += f"<li>{key}: {value}</li>"
            product_info += "</ul></li>"
            
            # Agility throughout program category
            product_info += "<li><strong>Agility throughout program:</strong><ul>"
            for key in ["Quickly iterate design/EMs", "Agility in Design and AI&T", "Digital Spares"]:
                if key in business_case:
                    value = "Yes" if business_case[key] else "No"
                    product_info += f"<li>{key}: {value}</li>"
            product_info += "</ul></li>"
        else:
            # Legacy format
            for key, value in business_case.items():
                if isinstance(value, dict) and 'description' in value:
                    product_info += f"<li><strong>{key}:</strong> {value['description']}</li>"
                else:
                    product_info += f"<li><strong>{key}:</strong> {value}</li>"
        
        product_info += "</ul>"
    
    product_info += "</div>"
    
    # Create product info div
    product_info_div = Div(text=product_info, width=1200)
    
    # Create funding legend explanation
    funding_legend = """
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px;">
        <h3>Funding Type Legend</h3>
        <p>Tasks are colored based on their funding source:</p>
        <ul style="list-style-type: none; padding-left: 0;">
    """
    
    for funding_type, color in FUNDING_COLORS.items():
        funding_legend += f'<li style="margin-bottom: 5px;"><span style="display: inline-block; width: 20px; height: 20px; background-color: {color}; margin-right: 10px;"></span>{funding_type}</li>'
    
    funding_legend += """
        </ul>
    </div>
    """
    
    funding_legend_div = Div(text=funding_legend, width=1200)
    
    # Create layout with product info, material toggle (if applicable), roadmap, and funding legend
    if material_toggle_div:
        layout_obj = column(product_info_div, material_toggle_div, p, funding_legend_div)
    else:
        layout_obj = column(product_info_div, p, funding_legend_div)
    
    # Save the visualization
    output_file(os.path.join(product_dir, f"product_{product_id}.html"))
    save(layout_obj)

def generate_product_summary(data, product_dir):
    """Generate a summary page for all products"""
    # Create a figure for product distribution by TRL
    trls = {}
    for product in data['products']:
        trl = product.get('trl', 'Unknown')
        # Convert to string to ensure consistent key type
        trl_key = str(trl)
        if trl_key in trls:
            trls[trl_key] += 1
        else:
            trls[trl_key] = 1
    
    # Sort TRLs numerically
    numeric_trls = []
    non_numeric_trls = []
    
    for k in trls.keys():
        if k == 'Unknown':
            continue
        try:
            numeric_trls.append(int(k))
        except (ValueError, TypeError):
            non_numeric_trls.append(k)
    
    # Sort numeric and non-numeric TRLs separately
    numeric_trls.sort()
    non_numeric_trls.sort()
    
    # Combine sorted TRLs
    sorted_trls = [str(trl) for trl in numeric_trls] + non_numeric_trls
    
    # Add Unknown at the end if it exists
    if 'Unknown' in trls:
        sorted_trls.append('Unknown')
    
    # Create a figure for the TRL distribution
    p1 = figure(
        title="Products by Technology Readiness Level (TRL)",
        x_range=[str(trl) for trl in sorted_trls],
        width=600,
        height=400,
        toolbar_location=None,
        tools=""
    )
    
    # Add bars
    p1.vbar(
        x=[str(trl) for trl in sorted_trls],
        top=[trls[trl] for trl in sorted_trls],
        width=0.5,
        color=Category10[10][0:len(sorted_trls)],
        alpha=0.8
    )
    
    # Customize appearance
    p1.title.text_font_size = '14pt'
    p1.xaxis.axis_label = "TRL"
    p1.yaxis.axis_label = "Number of Products"
    p1.xgrid.grid_line_color = None
    
    # Create a figure for product distribution by program
    program_counts = {}
    for product in data['products']:
        for program_entry in product.get('programs', []):
            if isinstance(program_entry, str):
                program_id = program_entry
            elif isinstance(program_entry, dict) and 'programID' in program_entry:
                program_id = program_entry['programID']
            else:
                continue
                
            program = next((p for p in data['programs'] if p['id'] == program_id), None)
            if program:
                program_name = program['name']
                if program_name in program_counts:
                    program_counts[program_name] += 1
                else:
                    program_counts[program_name] = 1
    
    # Sort by count
    sorted_programs = sorted(program_counts.items(), key=lambda x: x[1], reverse=True)
    program_names = [p[0] for p in sorted_programs]
    program_values = [p[1] for p in sorted_programs]
    
    # Create a figure for the program distribution
    p2 = figure(
        title="Products by Program",
        x_range=program_names,
        width=600,
        height=400,
        toolbar_location=None,
        tools=""
    )
    
    # Add bars
    p2.vbar(
        x=program_names,
        top=program_values,
        width=0.5,
        color=Category10[10][0:len(program_names)],
        alpha=0.8
    )
    
    # Customize appearance
    p2.title.text_font_size = '14pt'
    p2.xaxis.axis_label = "Program"
    p2.yaxis.axis_label = "Number of Products"
    p2.xgrid.grid_line_color = None
    p2.xaxis.major_label_orientation = 45
    
    # Create a figure for funding distribution
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
    p3 = figure(
        title="Tasks by Funding Type",
        x_range=funding_names,
        width=600,
        height=400,
        toolbar_location=None,
        tools=""
    )
    
    # Add bars with colors matching the funding type colors
    p3.vbar(
        x=funding_names,
        top=funding_values,
        width=0.5,
        color=[FUNDING_COLORS.get(name, '#999999') for name in funding_names],
        alpha=0.8
    )
    
    # Customize appearance
    p3.title.text_font_size = '14pt'
    p3.xaxis.axis_label = "Funding Type"
    p3.yaxis.axis_label = "Number of Tasks"
    p3.xgrid.grid_line_color = None
    p3.xaxis.major_label_orientation = 45
    
    # Create product list section
    product_list = """
    <div style="margin-top: 30px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">All Products</h2>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <thead>
                    <tr style="background-color: #3498db; color: white;">
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Product Name</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">ID</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">TRL</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Associated Programs</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Material Systems</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add rows for each product
    for i, product in enumerate(sorted(data['products'], key=lambda x: x['name'])):
        row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
        
        # Get associated programs
        associated_programs = []
        for program_entry in product.get('programs', []):
            if isinstance(program_entry, str):
                program_id = program_entry
            elif isinstance(program_entry, dict) and 'programID' in program_entry:
                program_id = program_entry['programID']
            else:
                continue
                
            program = next((p for p in data['programs'] if p['id'] == program_id), None)
            if program:
                associated_programs.append(f"{program['name']} ({program_id})")
        
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
        
        product_list += f"""
        <tr style="{row_style}">
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href='product_{product['id']}.html' style="color: #3498db;">{product['name']}</a></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{product['id']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{product.get('trl', 'N/A')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{programs_display}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{materials_display}</td>
        </tr>
        """
    
    product_list += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    # Create funding legend explanation
    funding_legend = """
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; margin-bottom: 20px;">
        <h3>Funding Type Legend</h3>
        <p>Tasks are colored based on their funding source:</p>
        <ul style="list-style-type: none; padding-left: 0; display: flex; flex-wrap: wrap;">
    """
    
    for funding_type, color in FUNDING_COLORS.items():
        funding_legend += f'<li style="margin-bottom: 5px; margin-right: 20px;"><span style="display: inline-block; width: 20px; height: 20px; background-color: {color}; margin-right: 10px;"></span>{funding_type}</li>'
    
    funding_legend += """
        </ul>
    </div>
    """
    
    # Create header
    header = """
    <div style="margin-bottom: 20px;">
        <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Product Summary</h1>
        <p>This page provides an overview of all products and their distributions.</p>
        <p><a href="../index.html" style="color: #3498db; text-decoration: none;">Back to Dashboard</a></p>
    </div>
    """
    
    # Combine all elements
    header_div = Div(text=header, width=1200)
    funding_legend_div = Div(text=funding_legend, width=1200)
    product_list_div = Div(text=product_list, width=1200)
    
    # Create layout
    layout_obj = layout([
        [header_div],
        [funding_legend_div],
        [p1, p2],
        [p3],
        [product_list_div]
    ])
    
    # Output to file
    output_file(os.path.join(product_dir, "product_summary.html"))
    save(layout_obj)

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
    p.xaxis.axis_label = "Product"
    p.yaxis.axis_label = "Number of Material Systems"
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 45
    
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
    
    # Create funding legend explanation
    funding_legend = """
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; margin-bottom: 20px;">
        <h3>Funding Type Legend</h3>
        <p>Tasks are colored based on their funding source:</p>
        <ul style="list-style-type: none; padding-left: 0; display: flex; flex-wrap: wrap;">
    """
    
    for funding_type, color in FUNDING_COLORS.items():
        funding_legend += f'<li style="margin-bottom: 5px; margin-right: 20px;"><span style="display: inline-block; width: 20px; height: 20px; background-color: {color}; margin-right: 10px;"></span>{funding_type}</li>'
    
    funding_legend += """
        </ul>
    </div>
    """
    
    funding_legend_div = Div(text=funding_legend, width=1200)
    
    # Create header
    header = """
    <div style="margin-bottom: 20px;">
        <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Product Distribution Charts</h1>
        <p>This page provides distribution charts for products and their associated data.</p>
        <p><a href="product_summary.html" style="color: #3498db; text-decoration: none;">Back to Product Summary</a> | 
        <a href="../index.html" style="color: #3498db; text-decoration: none;">Back to Dashboard</a></p>
    </div>
    """
    
    header_div = Div(text=header, width=1200)
    
    # Create layout with both charts
    layout_obj = column(header_div, funding_legend_div, p, p2)
    
    # Output to file
    output_file(os.path.join(product_dir, "product_material_distribution.html"))
    save(layout_obj) 