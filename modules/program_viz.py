import os
from datetime import datetime, timedelta
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Range1d, Span, Legend, LegendItem, Div, Tabs, Panel
from bokeh.layouts import column, row, layout
from bokeh.palettes import Category10, Spectral6
import matplotlib.pyplot as plt
import numpy as np

def generate_program_visualizations(data, output_dir):
    """Generate visualizations for programs"""
    print("Generating program visualizations...")
    
    # Create program directory if it doesn't exist
    program_dir = os.path.join(output_dir, "programs")
    if not os.path.exists(program_dir):
        os.makedirs(program_dir)
    
    # Generate individual program pages
    for program in data['programs']:
        generate_program_page(program, data, program_dir)
    
    # Generate program summary page
    generate_program_summary(data, program_dir)
    
    # Generate program distribution charts
    generate_program_distribution_charts(data, program_dir)
    
    print(f"Program visualizations generated in '{program_dir}'")

def generate_program_page(program, data, program_dir):
    """Generate a detailed page for a single program"""
    program_id = program['id']
    
    # Create a figure for the program timeline
    p = figure(
        title=f"Program: {program['name']} ({program_id})",
        x_axis_type="datetime",
        width=1200,
        height=600,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Customize appearance
    p.title.text_font_size = '16pt'
    p.xaxis.axis_label = "Timeline"
    p.yaxis.axis_label = "Products"
    p.grid.grid_line_alpha = 0.3
    p.background_fill_color = "#f8f9fa"
    
    # Find all products associated with this program
    associated_products = []
    for product in data['products']:
        for prog in product.get('programs', []):
            if isinstance(prog, str) and prog == program_id:
                associated_products.append(product)
                break
            elif isinstance(prog, dict) and prog.get('programID') == program_id:
                associated_products.append(product)
                break
    
    # Sort products by name
    associated_products.sort(key=lambda x: x['name'])
    
    # Plot products on timeline
    y_pos = 0
    all_dates = []
    has_renderers = False
    
    for product in associated_products:
        y_pos -= 1
        
        # Find the need date for this program-product relationship
        need_date = None
        for prog in product.get('programs', []):
            if isinstance(prog, dict) and prog.get('programID') == program_id and 'needDate' in prog:
                need_date = datetime.strptime(prog['needDate'], "%Y-%m-%d")
                all_dates.append(need_date)
                break
        
        # If no need date found, skip this product
        if not need_date:
            continue
        
        # Add product as a point on the timeline
        p.scatter(
            x=need_date, 
            y=y_pos, 
            size=15, 
            color=Category10[10][0], 
            alpha=0.8,
            legend_label="Product Need Date"
        )
        has_renderers = True
        
        # Add product label
        source = ColumnDataSource(data=dict(
            x=[need_date],
            y=[y_pos],
            text=[f"{product['name']} ({product['id']})"]
        ))
        p.text(
            x='x', 
            y='y', 
            text='text',
            source=source,
            text_font_size="10pt",
            text_baseline="middle",
            text_align="left",
            x_offset=10
        )
        
        # Add all tasks from the product roadmap to the timeline
        if 'roadmap' in product and isinstance(product['roadmap'], dict) and 'tasks' in product['roadmap']:
            for task in product['roadmap']['tasks']:
                if 'start' in task and 'end' in task:
                    start_date = datetime.strptime(task['start'], "%Y-%m-%d")
                    end_date = datetime.strptime(task['end'], "%Y-%m-%d")
                    all_dates.extend([start_date, end_date])
                    
                    # Add task bar
                    p.hbar(
                        y=y_pos,
                        left=start_date,
                        right=end_date,
                        height=0.3,
                        color=Category10[10][1],
                        alpha=0.6
                    )
                    has_renderers = True
    
    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Product", "$y"),
        ("Date", "$x{%F}"),
    ]
    hover.formatters = {
        "$x": "datetime"
    }
    p.add_tools(hover)
    
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
    
    # Create program info section
    program_info = f"""
    <div style="margin-bottom: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
        <h2>Program Details: {program['name']}</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>ID:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Sector:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program.get('sector', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Division:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program.get('division', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Customer:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program.get('customerName', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Mission Class:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program.get('missionClass', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Associated Products:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{len(associated_products)}</td>
            </tr>
        </table>
    </div>
    """
    
    # Create product list section
    product_list = "<div style='margin-top: 20px;'><h3>Associated Products</h3>"
    if associated_products:
        product_list += "<ul>"
        for product in associated_products:
            product_list += f"<li><a href='../products/product_{product['id']}.html'>{product['name']} ({product['id']})</a> - TRL: {product.get('trl', 'N/A')}</li>"
        product_list += "</ul>"
    else:
        product_list += "<p>No associated products found for this program.</p>"
    product_list += "</div>"
    
    # Combine all elements
    info_div = Div(text=program_info + product_list, width=1200)
    
    # If there's no data to display, add a message
    if not has_renderers:
        no_data_message = Div(
            text="<div style='text-align: center; margin: 50px; color: #777;'><h3>No timeline data available for this program</h3><p>There are no products with need dates associated with this program.</p></div>",
            width=1200
        )
        layout = column(info_div, no_data_message)
    else:
        layout = column(info_div, p)
    
    # Output to file
    output_file(os.path.join(program_dir, f"program_{program_id}.html"))
    save(layout)

def generate_program_summary(data, program_dir):
    """Generate a summary page for all programs"""
    # Create a figure for program distribution by mission class
    mission_classes = {}
    for program in data['programs']:
        mission_class = program.get('missionClass', 'Unknown')
        if mission_class in mission_classes:
            mission_classes[mission_class] += 1
        else:
            mission_classes[mission_class] = 1
    
    # Create a figure for the mission class distribution
    p1 = figure(
        title="Programs by Mission Class",
        x_range=list(mission_classes.keys()),
        width=600,
        height=400,
        toolbar_location=None,
        tools=""
    )
    
    # Add bars
    p1.vbar(
        x=list(mission_classes.keys()),
        top=list(mission_classes.values()),
        width=0.5,
        color=Category10[10][0:len(mission_classes)],
        alpha=0.8
    )
    
    # Customize appearance
    p1.title.text_font_size = '14pt'
    p1.xaxis.axis_label = "Mission Class"
    p1.yaxis.axis_label = "Number of Programs"
    p1.xgrid.grid_line_color = None
    
    # Create a figure for program distribution by division
    divisions = {}
    for program in data['programs']:
        division = program.get('division', 'Unknown')
        if division in divisions:
            divisions[division] += 1
        else:
            divisions[division] = 1
    
    # Create a figure for the division distribution
    p2 = figure(
        title="Programs by Division",
        x_range=list(divisions.keys()),
        width=600,
        height=400,
        toolbar_location=None,
        tools=""
    )
    
    # Add bars
    p2.vbar(
        x=list(divisions.keys()),
        top=list(divisions.values()),
        width=0.5,
        color=Category10[10][0:len(divisions)],
        alpha=0.8
    )
    
    # Customize appearance
    p2.title.text_font_size = '14pt'
    p2.xaxis.axis_label = "Division"
    p2.yaxis.axis_label = "Number of Programs"
    p2.xgrid.grid_line_color = None
    
    # Create program list section
    program_list = """
    <div style="margin-top: 30px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">All Programs</h2>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <thead>
                    <tr style="background-color: #3498db; color: white;">
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Program Name</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">ID</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Division</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Sector</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Mission Class</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Customer</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add rows for each program
    for i, program in enumerate(sorted(data['programs'], key=lambda x: x['name'])):
        row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
        program_list += f"""
        <tr style="{row_style}">
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href='program_{program['id']}.html' style="color: #3498db;">{program['name']}</a></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program['id']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program.get('division', 'N/A')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program.get('sector', 'N/A')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program.get('missionClass', 'N/A')}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program.get('customerName', 'N/A')}</td>
        </tr>
        """
    
    program_list += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    # Create header
    header = """
    <div style="margin-bottom: 20px;">
        <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Program Summary</h1>
        <p>This page provides an overview of all programs and their distributions.</p>
        <p><a href="../index.html" style="color: #3498db; text-decoration: none;">Back to Dashboard</a></p>
    </div>
    """
    
    # Combine all elements
    header_div = Div(text=header, width=1200)
    program_list_div = Div(text=program_list, width=1200)
    
    # Create layout
    layout_obj = layout([
        [header_div],
        [p1, p2],
        [program_list_div]
    ])
    
    # Output to file
    output_file(os.path.join(program_dir, "program_summary.html"))
    save(layout_obj)

def generate_program_distribution_charts(data, program_dir):
    """Generate distribution charts for programs"""
    # Count products per program
    products_per_program = {}
    for program in data['programs']:
        products_per_program[program['id']] = 0
    
    for product in data['products']:
        for program_id in product.get('programs', []):
            if isinstance(program_id, str) and program_id in products_per_program:
                products_per_program[program_id] += 1
            elif isinstance(program_id, dict) and program_id.get('programID') in products_per_program:
                products_per_program[program_id.get('programID')] += 1
    
    # Create a figure for products per program
    program_names = []
    product_counts = []
    
    for program_id, count in products_per_program.items():
        program = next((p for p in data['programs'] if p['id'] == program_id), None)
        if program:
            program_names.append(f"{program['name']} ({program_id})")
            product_counts.append(count)
    
    # Sort by count
    sorted_indices = np.argsort(product_counts)[::-1]  # Descending order
    program_names = [program_names[i] for i in sorted_indices]
    product_counts = [product_counts[i] for i in sorted_indices]
    
    # Create a figure for products per program
    p = figure(
        title="Number of Products per Program",
        x_range=program_names,
        width=1200,
        height=500,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Add bars
    p.vbar(
        x=program_names,
        top=product_counts,
        width=0.7,
        color=Category10[10][0],
        alpha=0.8
    )
    
    # Customize appearance
    p.title.text_font_size = '14pt'
    p.xaxis.axis_label = "Program"
    p.yaxis.axis_label = "Number of Products"
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 45
    
    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Program", "@x"),
        ("Products", "@top"),
    ]
    p.add_tools(hover)
    
    # Output to file
    output_file(os.path.join(program_dir, "program_distribution.html"))
    save(p) 