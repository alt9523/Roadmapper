import os
from datetime import datetime, timedelta
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Range1d, Span, Legend, LegendItem, Div, Tabs, Panel
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import Category10, Spectral6
from bokeh.transform import factor_cmap
import matplotlib.pyplot as plt
import numpy as np

def generate_material_visualizations(data, output_dir, status_colors):
    """Generate visualizations for material systems"""
    print("Generating material system visualizations...")
    
    # Create materials directory if it doesn't exist
    material_dir = os.path.join(output_dir, "materials")
    if not os.path.exists(material_dir):
        os.makedirs(material_dir)
    
    # Generate individual material pages
    for material in data['materialSystems']:
        generate_material_page(material, data, material_dir, status_colors)
    
    # Generate material summary page
    generate_material_summary(data, material_dir)
    
    # Generate material distribution charts
    generate_material_distribution_charts(data, material_dir)
    
    print(f"Material system visualizations generated in '{material_dir}'")

def generate_material_page(material, data, material_dir, status_colors):
    """Generate a detailed page for a single material system"""
    material_id = material['id']
    
    # Create a figure for the material roadmap
    p = figure(
        title=f"Roadmap for {material['name']} ({material_id})",
        x_axis_type="datetime",
        width=1200,
        height=400,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Customize appearance
    p.title.text_font_size = '16pt'
    p.xaxis.axis_label = "Timeline"
    p.yaxis.axis_label = "Tasks"
    p.grid.grid_line_alpha = 0.3
    p.background_fill_color = "#f8f9fa"
    
    # Process roadmap tasks
    y_pos = 0
    legend_items = []
    all_dates = []
    
    # Add roadmap tasks
    if 'roadmap' in material:
        for task in material['roadmap']:
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
            task_name = f"{task['task']}{funding}"
            
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
    if 'milestones' in material:
        for milestone in material['milestones']:
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
    
    # Create material info section
    material_info = f"""
    <div style="margin-bottom: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
        <h2>Material System Details: {material['name']}</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>ID:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Process:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material.get('process', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Material:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material.get('material', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>MRL:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material.get('mrl', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Qualification:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material.get('qualification', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Qualification Class:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material.get('qualificationClass', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Statistical Basis:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material.get('statisticalBasis', 'N/A')}</td>
            </tr>
        </table>
    </div>
    """
    
    # Add material properties if available
    properties_section = ""
    if 'properties' in material:
        properties_section = """
        <div style="margin-top: 20px; padding: 15px; background-color: #e8f4f8; border-radius: 5px;">
            <h3>Material Properties</h3>
            <table style="width: 100%; border-collapse: collapse;">
        """
        for prop_name, prop_value in material['properties'].items():
            properties_section += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>{prop_name}:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{prop_value}</td>
            </tr>
            """
        properties_section += """
            </table>
        </div>
        """
    
    # Add processing parameters if available
    processing_section = ""
    if 'processingParameters' in material:
        processing_section = """
        <div style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 5px;">
            <h3>Processing Parameters</h3>
            <table style="width: 100%; border-collapse: collapse;">
        """
        for param_name, param_value in material['processingParameters'].items():
            processing_section += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>{param_name}:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{param_value}</td>
            </tr>
            """
        processing_section += """
            </table>
        </div>
        """
    
    # Add post-processing information
    post_processing_section = ""
    if 'postProcessing' in material:
        post_processing_section = """
        <div style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
            <h3>Post-Processing</h3>
            <ul>
        """
        for pp in material['postProcessing']:
            suppliers = ""
            if 'Supplier' in pp and pp['Supplier']:
                supplier_links = []
                for s in pp['Supplier']:
                    supplier_links.append(f'<a href="../suppliers/supplier_{s}.html">{s}</a>')
                suppliers = f" - Suppliers: {', '.join(supplier_links)}"
            post_processing_section += f"<li><strong>{pp['name']}</strong>{suppliers}</li>"
        post_processing_section += """
            </ul>
        </div>
        """
    
    # Add qualified machines information
    machines_section = ""
    if 'qualifiedMachines' in material:
        machines_section = """
        <div style="margin-top: 20px; padding: 15px; background-color: #e8f4f8; border-radius: 5px;">
            <h3>Qualified Machines</h3>
            <ul>
        """
        for machine in material['qualifiedMachines']:
            suppliers = ""
            if 'Supplier' in machine and machine['Supplier']:
                supplier_links = []
                for s in machine['Supplier']:
                    supplier_links.append(f'<a href="../suppliers/supplier_{s}.html">{s}</a>')
                suppliers = f" - Suppliers: {', '.join(supplier_links)}"
            machines_section += f"<li><strong>{machine['machine']}</strong>{suppliers}</li>"
        machines_section += """
            </ul>
        </div>
        """
    
    # Add standard NDT information
    ndt_section = ""
    if 'standardNDT' in material and material['standardNDT']:
        ndt_section = """
        <div style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 5px;">
            <h3>Standard NDT Methods</h3>
            <ul>
        """
        for ndt in material['standardNDT']:
            ndt_section += f"<li>{ndt}</li>"
        ndt_section += """
            </ul>
        </div>
        """
    
    # Add related products section
    products_section = """
    <div style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
        <h3>Related Products</h3>
        <ul>
    """
    
    related_products = []
    for product in data['products']:
        for material_entry in product.get('materialSystems', []):
            if isinstance(material_entry, str) and material_entry == material_id:
                related_products.append(product)
            elif isinstance(material_entry, dict) and material_entry.get('materialID') == material_id:
                related_products.append(product)
    
    if related_products:
        for product in related_products:
            products_section += f"<li><a href='../products/product_{product['id']}.html'>{product['name']} ({product['id']})</a></li>"
    else:
        products_section += "<li>No related products found</li>"
    
    products_section += """
        </ul>
    </div>
    """
    
    # Combine all elements
    info_div = Div(text=material_info + properties_section + processing_section + 
                       post_processing_section + machines_section + ndt_section + products_section, 
                   width=1200)
    
    # Create layout
    layout_obj = column(info_div, p)
    
    # Output to file
    output_file(os.path.join(material_dir, f"material_{material_id}.html"))
    save(layout_obj)

def generate_material_summary(data, material_dir):
    """Generate a summary page for all material systems"""
    # Create a figure for material distribution by process
    processes = {}
    for material in data['materialSystems']:
        process = material.get('process', 'Unknown')
        if process in processes:
            processes[process] += 1
        else:
            processes[process] = 1
    
    # Create a figure for the process distribution
    p1 = figure(
        title="Material Systems by Process",
        x_range=list(processes.keys()),
        width=600,
        height=400,
        toolbar_location=None,
        tools=""
    )
    
    # Add bars
    p1.vbar(
        x=list(processes.keys()),
        top=list(processes.values()),
        width=0.5,
        color=Category10[10][0:len(processes)],
        alpha=0.8
    )
    
    # Customize appearance
    p1.title.text_font_size = '14pt'
    p1.xaxis.axis_label = "Process"
    p1.yaxis.axis_label = "Number of Material Systems"
    p1.xgrid.grid_line_color = None
    p1.xaxis.major_label_orientation = 45
    
    # Create a figure for material distribution by MRL
    mrls = {}
    for material in data['materialSystems']:
        mrl = material.get('mrl', 'Unknown')
        # Convert to string to ensure consistent key type
        mrl_key = str(mrl)
        if mrl_key in mrls:
            mrls[mrl_key] += 1
        else:
            mrls[mrl_key] = 1
    
    # Sort MRLs numerically
    numeric_mrls = []
    non_numeric_mrls = []
    
    for k in mrls.keys():
        if k == 'Unknown':
            continue
        try:
            numeric_mrls.append(int(k))
        except (ValueError, TypeError):
            non_numeric_mrls.append(k)
    
    # Sort numeric and non-numeric MRLs separately
    numeric_mrls.sort()
    non_numeric_mrls.sort()
    
    # Combine sorted MRLs
    sorted_mrls = [str(mrl) for mrl in numeric_mrls] + non_numeric_mrls
    
    # Add Unknown at the end if it exists
    if 'Unknown' in mrls:
        sorted_mrls.append('Unknown')
    
    # Create a figure for the MRL distribution
    p2 = figure(
        title="Material Systems by Manufacturing Readiness Level (MRL)",
        x_range=[str(mrl) for mrl in sorted_mrls],
        width=600,
        height=400,
        toolbar_location=None,
        tools=""
    )
    
    # Add bars
    p2.vbar(
        x=[str(mrl) for mrl in sorted_mrls],
        top=[mrls[mrl] for mrl in sorted_mrls],
        width=0.5,
        color=Category10[10][0:len(sorted_mrls)],
        alpha=0.8
    )
    
    # Customize appearance
    p2.title.text_font_size = '14pt'
    p2.xaxis.axis_label = "MRL"
    p2.yaxis.axis_label = "Number of Material Systems"
    p2.xgrid.grid_line_color = None
    
    # Create a figure for material distribution by qualification status
    qualifications = {}
    for material in data['materialSystems']:
        qual = material.get('qualification', 'Unknown')
        if qual in qualifications:
            qualifications[qual] += 1
        else:
            qualifications[qual] = 1
    
    # Create a figure for the qualification distribution
    p3 = figure(
        title="Material Systems by Qualification Status",
        x_range=list(qualifications.keys()),
        width=1200,
        height=400,
        toolbar_location=None,
        tools=""
    )
    
    # Add bars
    p3.vbar(
        x=list(qualifications.keys()),
        top=list(qualifications.values()),
        width=0.5,
        color=Category10[10][0:len(qualifications)],
        alpha=0.8
    )
    
    # Customize appearance
    p3.title.text_font_size = '14pt'
    p3.xaxis.axis_label = "Qualification Status"
    p3.yaxis.axis_label = "Number of Material Systems"
    p3.xgrid.grid_line_color = None
    
    # Create material list section
    material_list = """
    <div style="margin-top: 30px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">All Material Systems</h2>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <thead>
                    <tr style="background-color: #3498db; color: white;">
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Material Name</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">ID</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Process</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Material</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">MRL</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Qualification</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add rows for each material system
    for i, material in enumerate(sorted(data['materialSystems'], key=lambda x: x['name'])):
        row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
        material_list += f"""
        <tr style="{row_style}">
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href='material_{material['id']}.html' style="color: #3498db;">{material['name']}</a></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material['id']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material.get('process', 'N/A')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material.get('material', 'N/A')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material.get('mrl', 'N/A')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material.get('qualification', 'N/A')}</td>
        </tr>
        """
    
    material_list += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    # Create header
    header = """
    <div style="margin-bottom: 20px;">
        <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Material Systems Summary</h1>
        <p>This page provides an overview of all material systems and their distributions.</p>
        <p><a href="../index.html" style="color: #3498db; text-decoration: none;">Back to Dashboard</a></p>
    </div>
    """
    
    # Combine all elements
    header_div = Div(text=header, width=1200)
    material_list_div = Div(text=material_list, width=1200)
    
    # Create layout
    layout_obj = layout([
        [header_div],
        [p1, p2],
        [p3],
        [material_list_div]
    ])
    
    # Output to file
    output_file(os.path.join(material_dir, "material_summary.html"))
    save(layout_obj)

def generate_material_distribution_charts(data, material_dir):
    """Generate distribution charts for material systems"""
    # Count products per material system
    products_per_material = {}
    for material in data['materialSystems']:
        material_id = material['id']
        products_per_material[material_id] = 0
    
    for product in data['products']:
        for material_entry in product.get('materialSystems', []):
            if isinstance(material_entry, str) and material_entry in products_per_material:
                products_per_material[material_entry] += 1
            elif isinstance(material_entry, dict) and material_entry.get('materialID') in products_per_material:
                products_per_material[material_entry.get('materialID')] += 1
    
    # Create a figure for products per material
    material_names = []
    product_counts = []
    
    for material_id, count in products_per_material.items():
        material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
        if material:
            material_names.append(f"{material['name']} ({material_id})")
            product_counts.append(count)
    
    # Sort by count
    sorted_indices = np.argsort(product_counts)[::-1]  # Descending order
    material_names = [material_names[i] for i in sorted_indices]
    product_counts = [product_counts[i] for i in sorted_indices]
    
    # Create a figure for products per material
    p = figure(
        title="Number of Products per Material System",
        x_range=material_names,
        width=1200,
        height=500,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Add bars
    p.vbar(
        x=material_names,
        top=product_counts,
        width=0.7,
        color=Category10[10][2],
        alpha=0.8
    )
    
    # Customize appearance
    p.title.text_font_size = '14pt'
    p.xaxis.axis_label = "Material System"
    p.yaxis.axis_label = "Number of Products"
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 45
    
    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Material System", "@x"),
        ("Products", "@top"),
    ]
    p.add_tools(hover)
    
    # Output to file
    output_file(os.path.join(material_dir, "material_product_distribution.html"))
    save(p) 