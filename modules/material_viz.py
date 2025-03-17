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
    material_dir = os.path.join('roadmap_visualizations', "materials")
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
    
    # Customize appearance based on styling guide
    p.title.text_font_size = '16pt'
    p.title.text_color = "#2c3e50"
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
    
    # Create page header
    header = f"""
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1>Material System: {material['name']} ({material_id})</h1>
            <div>
                <a href="../index.html" class="nav-link">Back to Dashboard</a>
                <a href="material_summary.html" class="nav-link">All Materials</a>
                <a href="material_product_distribution.html" class="nav-link">Material Usage</a>
            </div>
        </div>
    </div>
    """
    
    # Create material info section (styled according to guide)
    material_info = f"""
    <div class="summary-card">
        <h2>Material System Details</h2>
        <div class="metrics-grid">
            <div class="metric-item">
                <div class="metric-label">ID</div>
                <div class="metric-value">{material_id}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Process</div>
                <div class="metric-value">{material.get('process', 'N/A')}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Material</div>
                <div class="metric-value">{material.get('material', 'N/A')}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">MRL</div>
                <div class="metric-value">{material.get('mrl', 'N/A')}</div>
            </div>
        </div>
    </div>
    """
    
    # Add qualifications section (new information)
    qualifications_section = ""
    if 'qualifications' in material and material['qualifications']:
        qualifications_section = f"""
        <div class="summary-card">
            <h2>Qualification Status</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; margin-bottom: 20px;">
        """
        
        for qual in material['qualifications']:
            # Create badge color based on qualification status
            qual_status = qual.get('qualification', 'Unknown')
            
            # Map qualification status to color
            status_color_map = {
                "Qualified": "#27ae60",  # green
                "In Progress": "#f39c12",  # orange
                "Planned": "#3498db",  # blue
                "Pending": "#95a5a6"   # light gray
            }
            
            qual_color = status_color_map.get(qual_status, "#7f8c8d")  # default dark gray
            
            qualifications_section += f"""
            <div class="part-card" style="background-color: #f8f9fa; border-radius: 4px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <p><strong>Class:</strong> {qual.get('qualificationClass', 'N/A')}</p>
                <p><strong>Status:</strong> <span class="status-badge" style="display: inline-block; padding: 5px 10px; border-radius: 4px; color: white; font-weight: bold; margin: 5px; background-color: {qual_color};">{qual_status}</span></p>
                <p><strong>Statistical Basis:</strong> {qual.get('statisticalBasis', 'N/A')}</p>
            </div>
            """
            
        qualifications_section += """
            </div>
    </div>
    """
    
    # Add material properties if available
    properties_section = ""
    if 'properties' in material:
        properties_section = """
        <div class="summary-card">
            <h2>Material Properties</h2>
            <table>
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
        """
        for i, (prop_name, prop_value) in enumerate(material['properties'].items()):
            row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
            properties_section += f"""
                <tr style="{row_style}">
                    <td><strong>{prop_name}</strong></td>
                    <td>{prop_value}</td>
                </tr>
            """
        properties_section += """
                </tbody>
            </table>
        </div>
        """
    
    # Add processing parameters if available
    processing_section = ""
    if 'processingParameters' in material:
        processing_section = """
        <div class="summary-card">
            <h2>Processing Parameters</h2>
            <table>
                <thead>
                    <tr>
                        <th>Parameter</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
        """
        for i, (param_name, param_value) in enumerate(material['processingParameters'].items()):
            row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
            processing_section += f"""
                <tr style="{row_style}">
                    <td><strong>{param_name}</strong></td>
                    <td>{param_value}</td>
                </tr>
            """
        processing_section += """
                </tbody>
            </table>
        </div>
        """
    
    # Add standard NDT information (new information)
    ndt_section = ""
    if 'standardNDT' in material and material['standardNDT']:
        ndt_section = """
        <div class="summary-card">
            <h2>Standard NDT Methods</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px;">
        """
        for ndt in material['standardNDT']:
            ndt_section += f"""
            <div class="material-item" style="display: inline-block; margin: 5px 10px; padding: 10px 15px; background-color: #f8f9fa; border-radius: 4px; border: 1px solid #ddd;">
                {ndt}
            </div>
            """
        ndt_section += """
            </div>
        </div>
        """
    
    # Add post-processing information
    post_processing_section = ""
    if 'postProcessing' in material:
        post_processing_section = """
        <div class="summary-card">
            <h2>Post-Processing</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 20px;">
        """
        for pp in material['postProcessing']:
            supplier_html = ""
            if 'Supplier' in pp and pp['Supplier']:
                supplier_html = "<div style='margin-top: 10px;'><strong>Suppliers:</strong> "
                supplier_links = []
                for s in pp['Supplier']:
                    if isinstance(s, dict) and 'id' in s:
                        supplier_id = s['id']
                        qual_status = s.get('qualStatus', 'Unknown')
                        supplier_links.append(f'<a href="../suppliers/supplier_{supplier_id}.html">{supplier_id}</a> ({qual_status})')
                    else:
                        supplier_links.append(f'<a href="../suppliers/supplier_{s}.html">{s}</a>')
                supplier_html += ", ".join(supplier_links) + "</div>"
                
            post_processing_section += f"""
            <div class="part-card" style="background-color: #f8f9fa; border-radius: 4px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-width: 200px;">
                <h3 style="margin-top: 0; font-size: 16px;">{pp['name']}</h3>
                {supplier_html}
            </div>
            """
        post_processing_section += """
            </div>
        </div>
        """
    
    # Add qualified machines information
    machines_section = ""
    if 'qualifiedMachines' in material:
        machines_section = """
        <div class="summary-card">
            <h2>Qualified Machines</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 20px;">
        """
        for machine in material['qualifiedMachines']:
            supplier_html = ""
            if 'Supplier' in machine and machine['Supplier']:
                supplier_html = "<div style='margin-top: 10px;'><strong>Suppliers:</strong> "
                supplier_links = []
                for s in machine['Supplier']:
                    if isinstance(s, dict) and 'id' in s:
                        supplier_id = s['id']
                        qual_status = s.get('qualStatus', 'Unknown')
                        supplier_links.append(f'<a href="../suppliers/supplier_{supplier_id}.html">{supplier_id}</a> ({qual_status})')
                    else:
                        supplier_links.append(f'<a href="../suppliers/supplier_{s}.html">{s}</a>')
                supplier_html += ", ".join(supplier_links) + "</div>"
                
            machines_section += f"""
            <div class="part-card" style="background-color: #f8f9fa; border-radius: 4px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-width: 200px;">
                <h3 style="margin-top: 0; font-size: 16px;">{machine['machine']}</h3>
                {supplier_html}
            </div>
            """
        machines_section += """
            </div>
        </div>
        """
    
    # Add related funding opportunities section (new information)
    funding_section = ""
    if 'relatedFundingOpps' in material and material['relatedFundingOpps']:
        funding_section = """
        <div class="summary-card">
            <h2>Related Funding Opportunities</h2>
            <table>
                <thead>
                    <tr>
                        <th>Opportunity ID</th>
                        <th>Pursuit ID</th>
                    </tr>
                </thead>
                <tbody>
        """
        for i, funding in enumerate(material['relatedFundingOpps']):
            row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
            
            # Check if funding is a string or dictionary
            if isinstance(funding, dict):
                opp_id = funding.get('opportunityID', 'N/A')
                pursuit_id = funding.get('pursuitID', 'N/A')
            else:
                # Handle case where funding is just a string
                opp_id = funding
                pursuit_id = 'N/A'
            
            funding_section += f"""
                <tr style="{row_style}">
                    <td>
                        <a href="../funding/opportunity_{opp_id}.html" style="color: #3498db;">{opp_id}</a>
                    </td>
                    <td>
                        <a href="../pursuits/pursuit_{pursuit_id}.html" style="color: #3498db;">{pursuit_id}</a>
                    </td>
                </tr>
            """
        funding_section += """
                </tbody>
            </table>
        </div>
        """
    
    # Add related products section
    products_section = """
    <div class="summary-card">
        <h2>Related Products</h2>
    """
    
    related_products = []
    for product in data['products']:
        for material_entry in product.get('materialSystems', []):
            if isinstance(material_entry, str) and material_entry == material_id:
                related_products.append(product)
            elif isinstance(material_entry, dict) and material_entry.get('materialID') == material_id:
                related_products.append(product)
    
    if related_products:
        products_section += """
        <table>
            <thead>
                <tr>
                    <th>Product ID</th>
                    <th>Product Name</th>
                </tr>
            </thead>
            <tbody>
        """
        for i, product in enumerate(related_products):
            row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
            products_section += f"""
                <tr style="{row_style}">
                    <td>{product['id']}</td>
                    <td>
                        <a href="../products/product_{product['id']}.html" style="color: #3498db;">{product['name']}</a>
                    </td>
                </tr>
            """
        products_section += """
            </tbody>
        </table>
        """
    else:
        products_section += """
        <div style="padding: 20px; text-align: center; color: #7f8c8d;">
            No related products found
        </div>
        """
    
    products_section += """
    </div>
    """
    
    # Create page CSS
    css_styles = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 1200px;
            max-width: 90%;
            margin: 0 auto;
            padding: 25px;
            box-sizing: border-box;
        }
        .header {
            background: linear-gradient(135deg, #3498db, #2c3e50);
            color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 8px 15px;
            background-color: rgba(255,255,255,0.2);
            border-radius: 4px;
            margin: 0 5px;
            transition: background-color 0.3s;
            display: inline-block;
        }
        .nav-link:hover {
            background-color: rgba(255,255,255,0.3);
        }
        .summary-card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            padding: 25px;
            margin-bottom: 20px;
            text-align: center;
        }
        .summary-card h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            font-size: 22px;
            text-align: center;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .metric-item {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            padding: 20px;
            text-align: center;
        }
        .metric-label {
            color: #7f8c8d;
            font-size: 14px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #3498db;
            margin: 10px 0;
        }
        .chart-container {
            width: 100%;
            margin: 20px auto;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        td {
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
        @media (max-width: 768px) {
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media (max-width: 480px) {
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """
    
    # Combine all elements
    page_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Material System: {material['name']} | Roadmap Visualization</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <!-- Include Bokeh scripts -->
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.6.3.min.js"></script>
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.6.3.min.js"></script>
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.6.3.min.js"></script>
        
        {css_styles}
    </head>
    <body>
        <div class="container">
            {header}
            {material_info}
            {qualifications_section}
            
            <div class="summary-card">
                <h2>Material Roadmap</h2>
                <div class="chart-container" id="roadmap-chart"></div>
            </div>
            
            {properties_section}
            {processing_section}
            {ndt_section}
            {post_processing_section}
            {machines_section}
            {funding_section}
            {products_section}
        </div>
    </body>
    </html>
    """
    
    # Create a div element with the HTML content
    template_div = Div(text=page_html, width=1200)
    
    # Create layout for the roadmap chart
    roadmap_div = Div(text="", width=1200, height=0)
    
    # Output to file
    output_file(os.path.join(material_dir, f"material_{material_id}.html"))
    save(layout([template_div, roadmap_div, p]))

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
    
    # Customize appearance based on styling guide
    p1.title.text_font_size = '14pt'
    p1.title.text_color = "#2c3e50"
    p1.xaxis.axis_label = "Process"
    p1.yaxis.axis_label = "Number of Material Systems"
    p1.xgrid.grid_line_color = None
    p1.xaxis.major_label_orientation = 45
    p1.background_fill_color = "#f8f9fa"
    
    # Add bars
    p1.vbar(
        x=list(processes.keys()),
        top=list(processes.values()),
        width=0.5,
        color=Category10[10][0:len(processes)],
        alpha=0.8
    )
    
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
    
    # Customize appearance based on styling guide
    p2.title.text_font_size = '14pt'
    p2.title.text_color = "#2c3e50"
    p2.xaxis.axis_label = "MRL"
    p2.yaxis.axis_label = "Number of Material Systems"
    p2.xgrid.grid_line_color = None
    p2.background_fill_color = "#f8f9fa"
    
    # Add bars
    p2.vbar(
        x=[str(mrl) for mrl in sorted_mrls],
        top=[mrls[mrl] for mrl in sorted_mrls],
        width=0.5,
        color=Category10[10][0:len(sorted_mrls)],
        alpha=0.8
    )
    
    # Count qualification statuses
    qualification_statuses = {}
    for material in data['materialSystems']:
        # Get qualification statuses from the qualifications array (new format)
        if 'qualifications' in material and material['qualifications']:
            for qual in material['qualifications']:
                status = qual.get('qualification', 'Unknown')
                if status in qualification_statuses:
                    qualification_statuses[status] += 1
                else:
                    qualification_statuses[status] = 1
        # Also include the legacy qualification field if available
        elif 'qualification' in material:
            status = material['qualification']
            if status in qualification_statuses:
                qualification_statuses[status] += 1
        else:
                qualification_statuses[status] = 1
    
    # Create a figure for qualification status distribution
    p3 = figure(
        title="Material Systems by Qualification Status",
        x_range=list(qualification_statuses.keys()),
        width=1200,
        height=400,
        toolbar_location=None,
        tools=""
    )
    
    # Customize appearance based on styling guide
    p3.title.text_font_size = '14pt'
    p3.title.text_color = "#2c3e50"
    p3.xaxis.axis_label = "Qualification Status"
    p3.yaxis.axis_label = "Number of Material Systems"
    p3.xgrid.grid_line_color = None
    p3.background_fill_color = "#f8f9fa"
    
    # Add bars with appropriate colors based on status
    status_colors = {
        "Qualified": "#27ae60",  # green
        "In Progress": "#f39c12",  # orange
        "Planned": "#3498db",    # blue
        "Pending": "#95a5a6",    # light gray
        "Unknown": "#7f8c8d"     # dark gray
    }
    
    colors = [status_colors.get(status, "#7f8c8d") for status in qualification_statuses.keys()]
    
    p3.vbar(
        x=list(qualification_statuses.keys()),
        top=list(qualification_statuses.values()),
        width=0.5,
        color=colors,
        alpha=0.8
    )
    
    # Create page header
    header = """
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1>Material Systems Summary</h1>
            <div>
                <a href="../index.html" class="nav-link">Back to Dashboard</a>
                <a href="material_product_distribution.html" class="nav-link">Material Usage</a>
            </div>
        </div>
    </div>
    """
    
    # Create statistics cards section
    total_materials = len(data['materialSystems'])
    qualified_count = sum(1 for m in data['materialSystems'] 
                        if any(q.get('qualification') == 'Qualified' 
                              for q in m.get('qualifications', []))
                        or m.get('qualification') == 'Qualified')
    
    in_progress_count = sum(1 for m in data['materialSystems'] 
                          if any(q.get('qualification') == 'In Progress' 
                                for q in m.get('qualifications', []))
                          or m.get('qualification') == 'In Progress')
    
    stats_section = f"""
    <div class="summary-card">
        <h2>Material Statistics</h2>
        <div class="metrics-grid">
            <div class="metric-item">
                <div class="metric-label">Total Material Systems</div>
                <div class="metric-value">{total_materials}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Qualified Materials</div>
                <div class="metric-value" style="color: #27ae60;">{qualified_count}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">In Progress</div>
                <div class="metric-value" style="color: #f39c12;">{in_progress_count}</div>
            </div>
        </div>
    </div>
    """
    
    # Create distribution charts section
    charts_section = """
    <div class="summary-card">
        <h2>Material Distributions</h2>
        <div class="chart-container" id="process-chart"></div>
        <div class="chart-container" id="mrl-chart"></div>
        <div class="chart-container" id="qualification-chart"></div>
    </div>
    """
    
    # Create material list section with qualifications
    material_list = """
    <div class="summary-card">
        <h2>All Material Systems</h2>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>Material Name</th>
                        <th>ID</th>
                        <th>Process</th>
                        <th>Material</th>
                        <th>MRL</th>
                        <th>Qualification Status</th>
                        <th>Statistical Basis</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add rows for each material system
    for i, material in enumerate(sorted(data['materialSystems'], key=lambda x: x['name'])):
        row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
        
        # Handle qualifications display (new format)
        qual_status_display = ""
        qual_stat_basis = ""
        
        if 'qualifications' in material and material['qualifications']:
            # Get qualifications from array (new format)
            qual_badges = []
            for qual in material['qualifications']:
                status = qual.get('qualification', 'Unknown')
                qual_class = qual.get('qualificationClass', 'N/A')
                status_color = status_colors.get(status, "#7f8c8d")
                
                qual_badges.append(
                    f'<span class="status-badge" style="display: inline-block; padding: 5px 10px; '
                    f'border-radius: 4px; color: white; font-weight: bold; margin: 5px; '
                    f'background-color: {status_color};">{status} ({qual_class})</span>'
                )
                
                # Get the statistical basis for display in the table
                if qual.get('statisticalBasis'):
                    qual_stat_basis += f"{qual.get('statisticalBasis')} ({qual_class}), "
                
            qual_status_display = "".join(qual_badges)
            qual_stat_basis = qual_stat_basis[:-2] if qual_stat_basis else "N/A"
        else:
            # Legacy format handling
            status = material.get('qualification', 'Unknown')
            status_color = status_colors.get(status, "#7f8c8d")
            qual_status_display = (
                f'<span class="status-badge" style="display: inline-block; padding: 5px 10px; '
                f'border-radius: 4px; color: white; font-weight: bold; margin: 5px; '
                f'background-color: {status_color};">{status}</span>'
            )
            qual_stat_basis = material.get('statisticalBasis', 'N/A')
            
        material_list += f"""
        <tr style="{row_style}">
            <td><a href='material_{material['id']}.html' style="color: #3498db;">{material['name']}</a></td>
            <td>{material['id']}</td>
            <td>{material.get('process', 'N/A')}</td>
            <td>{material.get('material', 'N/A')}</td>
            <td>{material.get('mrl', 'N/A')}</td>
            <td>{qual_status_display}</td>
            <td>{qual_stat_basis}</td>
        </tr>
        """
    
    material_list += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    # Create page CSS
    css_styles = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 1200px;
            max-width: 90%;
            margin: 0 auto;
            padding: 25px;
            box-sizing: border-box;
        }
        .header {
            background: linear-gradient(135deg, #3498db, #2c3e50);
            color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 8px 15px;
            background-color: rgba(255,255,255,0.2);
            border-radius: 4px;
            margin: 0 5px;
            transition: background-color 0.3s;
            display: inline-block;
        }
        .nav-link:hover {
            background-color: rgba(255,255,255,0.3);
        }
        .summary-card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            padding: 25px;
            margin-bottom: 20px;
            text-align: center;
        }
        .summary-card h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            font-size: 22px;
            text-align: center;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .metric-item {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            padding: 20px;
            text-align: center;
        }
        .metric-label {
            color: #7f8c8d;
            font-size: 14px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #3498db;
            margin: 10px 0;
        }
        .chart-container {
            width: 100%;
            margin: 20px auto;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        td {
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
        @media (max-width: 768px) {
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media (max-width: 480px) {
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """
    
    # Combine all elements into HTML page
    page_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Material Systems Summary | Roadmap Visualization</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <!-- Include Bokeh scripts -->
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.6.3.min.js"></script>
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.6.3.min.js"></script>
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.6.3.min.js"></script>
        
        {css_styles}
    </head>
    <body>
        <div class="container">
            {header}
            {stats_section}
            {charts_section}
            {material_list}
        </div>
    </body>
    </html>
    """
    
    # Create a div element with the HTML content
    template_div = Div(text=page_html, width=1200)
    
    # Create div elements for charts
    process_div = Div(text="", width=1200, height=0)
    mrl_div = Div(text="", width=1200, height=0)
    qual_div = Div(text="", width=1200, height=0)
    
    # Output to file
    output_file(os.path.join(material_dir, "material_summary.html"))
    save(layout([template_div, process_div, p1, mrl_div, p2, qual_div, p3]))

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
    
    # Customize appearance based on styling guide
    p.title.text_font_size = '16pt'
    p.title.text_color = "#2c3e50"
    p.xaxis.axis_label = "Material System"
    p.yaxis.axis_label = "Number of Products"
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 45
    p.background_fill_color = "#f8f9fa"
    
    # Add bars
    p.vbar(
        x=material_names,
        top=product_counts,
        width=0.7,
        color="#3498db",  # Use blue color from style guide
        alpha=0.8
    )
    
    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Material System", "@x"),
        ("Products", "@top"),
    ]
    p.add_tools(hover)
    
    # Create page header
    header = """
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1>Material Usage Distribution</h1>
            <div>
                <a href="../index.html" class="nav-link">Back to Dashboard</a>
                <a href="material_summary.html" class="nav-link">All Materials</a>
            </div>
        </div>
    </div>
    """
    
    # Create description
    description = """
    <div class="summary-card">
        <h2>Material Usage Analysis</h2>
        <p>This chart shows the number of products that use each material system. Materials used in more products may require higher priority for qualification and development.</p>
    </div>
    """
    
    # Create data table with statistics
    top_materials = sorted([(name, count) for name, count in zip(material_names, product_counts)], key=lambda x: x[1], reverse=True)[:5]
    
    usage_table = """
    <div class="summary-card">
        <h2>Top 5 Used Materials</h2>
        <table>
            <thead>
                <tr>
                    <th>Material System</th>
                    <th>Number of Products</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for i, (name, count) in enumerate(top_materials):
        row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
        usage_table += f"""
        <tr style="{row_style}">
            <td>{name}</td>
            <td>{count}</td>
        </tr>
        """
    
    usage_table += """
            </tbody>
        </table>
    </div>
    """
    
    # Create page CSS
    css_styles = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 1200px;
            max-width: 90%;
            margin: 0 auto;
            padding: 25px;
            box-sizing: border-box;
        }
        .header {
            background: linear-gradient(135deg, #3498db, #2c3e50);
            color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .nav-link {
            color: white;
            text-decoration: none;
            padding: 8px 15px;
            background-color: rgba(255,255,255,0.2);
            border-radius: 4px;
            margin: 0 5px;
            transition: background-color 0.3s;
            display: inline-block;
        }
        .nav-link:hover {
            background-color: rgba(255,255,255,0.3);
        }
        .summary-card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            padding: 25px;
            margin-bottom: 20px;
            text-align: center;
        }
        .summary-card h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            font-size: 22px;
            text-align: center;
        }
        .chart-container {
            width: 100%;
            margin: 20px auto;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        td {
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
    </style>
    """
    
    # Combine all elements into HTML page
    page_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Material Usage Distribution | Roadmap Visualization</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <!-- Include Bokeh scripts -->
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.6.3.min.js"></script>
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.6.3.min.js"></script>
        <script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.6.3.min.js"></script>
        
        {css_styles}
    </head>
    <body>
        <div class="container">
            {header}
            {description}
            <div class="summary-card">
                <h2>Material Usage Distribution</h2>
                <div class="chart-container" id="usage-chart"></div>
            </div>
            {usage_table}
        </div>
    </body>
    </html>
    """
    
    # Create a div element with the HTML content
    template_div = Div(text=page_html, width=1200)
    
    # Create div for chart
    chart_div = Div(text="", width=1200, height=0)
    
    # Output to file
    output_file(os.path.join(material_dir, "material_product_distribution.html"))
    save(layout([template_div, chart_div, p])) 