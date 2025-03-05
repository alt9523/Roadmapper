import os
from datetime import datetime, timedelta
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Range1d, Span, Legend, LegendItem, Div, Tabs, Panel
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import Category10, Spectral6
from bokeh.transform import factor_cmap
import matplotlib.pyplot as plt
import numpy as np

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
        
        # Also add material system tasks
        for material_id in product.get('materialSystems', []):
            if isinstance(material_id, str):
                material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
            elif isinstance(material_id, dict) and 'materialID' in material_id:
                material = next((m for m in data['materialSystems'] if m['id'] == material_id['materialID']), None)
            else:
                continue
                
            if material and 'roadmap' in material:
                for task in material['roadmap']:
                    if task.get('lane', 'M&P') == lane:
                        task_copy = task.copy()
                        task_copy['material'] = material['name']
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
            
            # Add funding type if available
            funding = f" ({task.get('fundingType', '')})" if 'fundingType' in task else ""
            material_info = f" [Material: {task.get('material', '')}]" if 'material' in task else ""
            task_name = f"{task['task']}{funding}{material_info}"
            
            # Create data source for the task bar
            bar_source = ColumnDataSource(data=dict(
                y=[y_pos],
                left=[start_date],
                right=[end_date],
                task=[task_name],
                start=[start_date],
                end=[end_date],
                status=[task['status']]
            ))
            
            # Add task bar
            color = status_colors.get(task['status'], '#95a5a6')
            p.hbar(y='y', left='left', right='right', height=0.6, 
                   color=color, alpha=0.8, source=bar_source)
            
            # Create data source for the task label
            label_source = ColumnDataSource(data=dict(
                x=[start_date],
                y=[y_pos],
                text=[task_name]
            ))
            
            # Add task label with offset to prevent overlap
            p.text(x='x', y='y', text='text', source=label_source,
                   text_font_size="9pt", text_baseline="middle", 
                   x_offset=5, text_align="left")
    
    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Task", "@task"),
        ("Start", "@start{%F}"),
        ("End", "@end{%F}"),
        ("Status", "@status")
    ]
    hover.formatters = {
        "@start": "datetime",
        "@end": "datetime"
    }
    p.add_tools(hover)
    
    # Add milestones as vertical lines
    for milestone in product.get('milestones', []):
        if not milestone.get('date'):
            continue
            
        milestone_date = datetime.strptime(milestone['date'], "%Y-%m-%d")
        all_dates.append(milestone_date)
        
        milestone_line = Span(location=milestone_date, dimension='height', 
                             line_color='red', line_dash='dashed', line_width=2)
        p.add_layout(milestone_line)
        
        # Add milestone label
        milestone_label = Label(x=milestone_date, y=0, 
                               text=milestone['name'],
                               text_color='red',
                               text_font_style='bold',
                               text_font_size='10pt',
                               angle=90,
                               angle_units='deg',
                               x_offset=10)
        p.add_layout(milestone_label)
    
    # Add program need dates as vertical lines
    for program_entry in product.get('programs', []):
        if isinstance(program_entry, str):
            program_id = program_entry
            program = next((p for p in data['programs'] if p['id'] == program_id), None)
            need_date = None
        elif isinstance(program_entry, dict):
            program_id = program_entry.get('programID')
            program = next((p for p in data['programs'] if p['id'] == program_id), None)
            need_date = datetime.strptime(program_entry['needDate'], "%Y-%m-%d") if 'needDate' in program_entry else None
        else:
            continue
            
        if program and need_date:
            all_dates.append(need_date)
            
            program_line = Span(location=need_date, dimension='height', 
                               line_color='purple', line_width=2)
            p.add_layout(program_line)
            
            # Add program label
            program_label = Label(x=need_date, y=0, 
                                 text=f"{program['name']} Need Date",
                                 text_color='purple',
                                 text_font_style='italic',
                                 text_font_size='10pt',
                                 angle=90,
                                 angle_units='deg',
                                 x_offset=5)
            p.add_layout(program_label)
    
    # Add legend for status colors
    for status, color in status_colors.items():
        legend_items.append(LegendItem(label=status, renderers=[p.hbar(y=0, left=0, right=0, height=0, color=color)]))
    
    legend = Legend(items=legend_items, location="top_right")
    p.add_layout(legend)
    
    # Set y-range with padding
    p.y_range = Range1d(y_pos - 1, 1)
    
    # Set x-range based on all dates
    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
        # Add some padding (3 months before and after)
        min_date = min_date - timedelta(days=90)
        max_date = max_date + timedelta(days=90)
        p.x_range.start = min_date
        p.x_range.end = max_date
    
    # Create product info section
    product_info = f"""
    <div style="margin-bottom: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Product Details: {product['name']}</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; width: 30%;"><strong>ID:</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">{product_id}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>TRL:</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">{product.get('trl', 'N/A')}</td>
            </tr>
    """
    
    # Add requirements if available
    if 'requirements' in product:
        product_info += "<tr><td style='padding: 12px; border-bottom: 1px solid #ddd;'><strong>Requirements:</strong></td><td style='padding: 12px; border-bottom: 1px solid #ddd;'><ul>"
        for req_type, req_text in product['requirements'].items():
            product_info += f"<li><strong>{req_type}:</strong> {req_text}</li>"
        product_info += "</ul></td></tr>"
    
    # Add associated programs with detailed information
    if 'programs' in product and product['programs']:
        program_info = "<tr><td style='padding: 12px; border-bottom: 1px solid #ddd;'><strong>Associated Programs:</strong></td><td style='padding: 12px; border-bottom: 1px solid #ddd;'>"
        
        # Create a table for program relationships
        program_info += """
        <table style="width: 100%; border-collapse: collapse; margin-top: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background-color: #3498db; color: white;">
                    <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Program</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Part</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Material</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Need Date</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Adoption Status</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Lifetime Demand</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Unit Cost Savings</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for i, program_entry in enumerate(product['programs']):
            row_class = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
            
            if isinstance(program_entry, str):
                program_id = program_entry
                program = next((p for p in data['programs'] if p['id'] == program_id), None)
                if program:
                    program_info += f"""
                    <tr style="{row_class}">
                        <td style="padding: 8px; border: 1px solid #ddd;"><a href='../programs/program_{program_id}.html' style="color: #3498db;">{program['name']} ({program_id})</a></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">N/A</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">N/A</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">N/A</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">N/A</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">N/A</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">N/A</td>
                    </tr>
                    """
            elif isinstance(program_entry, dict) and 'programID' in program_entry:
                program_id = program_entry['programID']
                program = next((p for p in data['programs'] if p['id'] == program_id), None)
                if program:
                    # Get additional details
                    part = program_entry.get('part', 'N/A')
                    material_id = program_entry.get('materialID', 'N/A')
                    need_date = program_entry.get('needDate', 'N/A')
                    adoption_status = program_entry.get('adoptionStatus', 'N/A')
                    lifetime_demand = program_entry.get('lifetimeDemand', 'N/A')
                    unit_cost_savings = program_entry.get('expectedUnitCostSavings', 'N/A')
                    
                    # Get material name if available
                    material_display = material_id
                    if material_id != 'N/A':
                        material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
                        if material:
                            material_display = f"<a href='../materials/material_{material_id}.html' style='color: #3498db;'>{material['name']} ({material_id})</a>"
                    
                    # Format adoption status with color
                    status_style = ""
                    if adoption_status.lower() == 'production':
                        status_style = "color: #27ae60; font-weight: bold;"  # Green
                    elif adoption_status.lower() == 'prototyping':
                        status_style = "color: #f39c12; font-weight: bold;"  # Orange
                    elif adoption_status.lower() == 'developing':
                        status_style = "color: #3498db; font-weight: bold;"  # Blue
                    elif adoption_status.lower() == 'targeting':
                        status_style = "color: #9b59b6; font-weight: bold;"  # Purple
                    elif adoption_status.lower() == 'closed':
                        status_style = "color: #e74c3c; font-weight: bold;"  # Red
                    
                    # Format unit cost savings
                    if unit_cost_savings and unit_cost_savings != 'N/A':
                        try:
                            unit_cost_savings = f"${int(unit_cost_savings):,}"
                        except (ValueError, TypeError):
                            pass
                    
                    program_info += f"""
                    <tr style="{row_class}">
                        <td style="padding: 8px; border: 1px solid #ddd;"><a href='../programs/program_{program_id}.html' style="color: #3498db;">{program['name']} ({program_id})</a></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{part}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{material_display}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{need_date}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; {status_style}">{adoption_status}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{lifetime_demand}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{unit_cost_savings}</td>
                    </tr>
                    """
        
        program_info += """
            </tbody>
        </table>
        """
        
        program_info += "</td></tr>"
        product_info += program_info
    
    # Add material systems
    product_info += "<tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>Material Systems:</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'><ul>"
    for material_entry in product.get('materialSystems', []):
        if isinstance(material_entry, str):
            material_id = material_entry
            material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
            if material:
                product_info += f"<li><a href='../materials/material_{material_id}.html'>{material['name']} ({material_id})</a></li>"
        elif isinstance(material_entry, dict) and 'materialID' in material_entry:
            material_id = material_entry['materialID']
            material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
            if material:
                printers = f" - Printers: {', '.join(material_entry.get('printer', []))}" if 'printer' in material_entry else ""
                product_info += f"<li><a href='../materials/material_{material_id}.html'>{material['name']} ({material_id})</a>{printers}</li>"
    product_info += "</ul></td></tr>"
    
    # Add post-processing suppliers
    if 'postProcessingSuppliers' in product:
        product_info += "<tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>Post-Processing:</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'><ul>"
        for pp in product['postProcessingSuppliers']:
            suppliers = ', '.join([f"<a href='../suppliers/supplier_{s}.html'>{s}</a>" for s in pp.get('supplier', [])])
            product_info += f"<li><strong>{pp['process']}:</strong> {suppliers}</li>"
        product_info += "</ul></td></tr>"
    
    # Close the table and div
    product_info += """
        </table>
    </div>
    """
    
    # Create business case section if available
    business_case = ""
    if 'businessCase' in product:
        business_case = f"""
        <div style="margin-top: 20px; padding: 15px; background-color: #e8f4f8; border-radius: 5px;">
            <h3>Business Case</h3>
            <ul>
                <li><strong>Cost Savings:</strong> {product['businessCase'].get('costSavings', 'N/A')}</li>
                <li><strong>Schedule Savings:</strong> {product['businessCase'].get('scheduleSavings', 'N/A')}</li>
                <li><strong>Performance Gains:</strong> {product['businessCase'].get('performanceGains', 'N/A')}</li>
            </ul>
        </div>
        """
    
    # Combine all elements
    info_div = Div(text=product_info + business_case, width=1200)
    
    # Create layout
    layout_obj = column(info_div, p)
    
    # Output to file
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
    product_list_div = Div(text=product_list, width=1200)
    
    # Create layout
    layout_obj = layout([
        [header_div],
        [p1, p2],
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
    
    # Output to file
    output_file(os.path.join(product_dir, "product_material_distribution.html"))
    save(p) 