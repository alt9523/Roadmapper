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
    
    # Generate program summary page
    generate_program_summary(data, program_dir)
    
    # Generate program distribution charts
    generate_program_distribution_charts(data, program_dir)
    
    # Generate individual program pages
    for program in data['programs']:
        generate_program_page(program, data, program_dir)
    
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
        sizing_mode="fixed",
    )
    
    # Customize appearance
    p.title.text_font_size = '16pt'
    p.xaxis.axis_label = "Timeline"
    p.yaxis.axis_label = "Products"
    p.grid.grid_line_alpha = 0.3
    p.background_fill_color = "#f8f9fa"
    
    # Create header with modern styling
    header = Div(
        text=f"""
        <div style="background: linear-gradient(to right, #3498db, #2c3e50); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">{program['name']} ({program_id})</h1>
            <div>
                    <a href="program_summary.html" style="color: white; text-decoration: none; margin-right: 15px; padding: 8px 15px; background-color: rgba(255,255,255,0.2); border-radius: 4px;">Program Summary</a>
                    <a href="../index.html" style="color: white; text-decoration: none; padding: 8px 15px; background-color: rgba(255,255,255,0.2); border-radius: 4px;">Main Dashboard</a>
                </div>
            </div>
            </div>
            """,
            width=1200
        )
        
        # Create layout with all elements
    layout_obj = column(
        header,
        p,
        sizing_mode="fixed",
        width=1200,
        align="center"
    )
    
    # Add wrapper style to center content
    style = Div(
        text="""
        <style>
            body {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 0;
                padding: 0;
                width: 100%;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }
            .bk-root {
                margin: 0 auto !important;
            }
        </style>
        """
    )
    
    # Final layout with style
    final_layout = column(style, layout_obj)
    
    # Output to file
    output_file(os.path.join(program_dir, f"program_{program_id}.html"))
    save(final_layout)
    
    print(f"Generated program page for {program_id}")

def generate_program_summary(data, program_dir):
    """Generate a summary page for all programs"""
    print("Generating program summary page...")
    
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
        width=500,
        height=350,
        toolbar_location=None,
        tools="hover",
        background_fill_color="#f8f9fa",
        tooltips=[("Mission Class", "@x"), ("Count", "@top")]
    )
    
    # Add bars
    p1.vbar(
        x=list(mission_classes.keys()),
        top=list(mission_classes.values()),
        width=0.5,
        color=Category10[10][0:len(mission_classes)],
        alpha=0.8
    )
    
    # Create layout with modern styling
    header = Div(
        text="""
        <div style="background: linear-gradient(to right, #3498db, #2c3e50); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">Program Summary</h1>
            <div>
                    <a href="../index.html" style="color: white; text-decoration: none; padding: 8px 15px; background-color: rgba(255,255,255,0.2); border-radius: 4px;">Main Dashboard</a>
                </div>
            </div>
        </div>
        """,
        width=1200
    )
    
    # Create layout
    layout_obj = column(
        header,
        p1,
        sizing_mode="fixed",
        width=1200,
        align="center"
    )
    
    # Add wrapper style to center content
    style = Div(
        text="""
        <style>
            body {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 0;
                padding: 0;
                width: 100%;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }
            .bk-root {
                margin: 0 auto !important;
            }
        </style>
        """
    )
    
    # Final layout with style
    final_layout = column(style, layout_obj)
    
    # Output to file
    output_file(os.path.join(program_dir, "program_summary.html"))
    save(final_layout)
    
    print("Generated program summary page")

def generate_program_distribution_charts(data, program_dir):
    """Generate distribution charts for programs"""
    print("Generating program distribution charts...")
    
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
        background_fill_color="#f8f9fa"
    )
    
    # Add bars
    p.vbar(
        x=program_names,
        top=product_counts,
        width=0.7,
        color="#3498db",
        alpha=0.8
    )
    
    # Customize appearance
    p.title.text_font_size = '16pt'
    p.xaxis.axis_label = "Program"
    p.yaxis.axis_label = "Number of Products"
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 45
    p.grid.grid_line_alpha = 0.3
    
    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Program", "@x"),
        ("Products", "@top"),
    ]
    p.add_tools(hover)
    
    # Create layout with modern styling
    header = Div(
        text="""
        <div style="background: linear-gradient(to right, #3498db, #2c3e50); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">Program Distribution</h1>
            <div>
                    <a href="program_summary.html" style="color: white; text-decoration: none; margin-right: 15px; padding: 8px 15px; background-color: rgba(255,255,255,0.2); border-radius: 4px;">Program Summary</a>
                    <a href="../index.html" style="color: white; text-decoration: none; padding: 8px 15px; background-color: rgba(255,255,255,0.2); border-radius: 4px;">Main Dashboard</a>
                </div>
            </div>
        </div>
        """,
        width=1200
    )
    
    description = Div(
        text="""
        <div style="background-color: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px;">
        <p>This chart shows the number of products associated with each program. Programs are sorted by the number of products in descending order.</p>
    </div>
        """,
        width=1200
    )
    
    # Create layout
    layout_obj = column(
        header,
        description,
        p,
        sizing_mode="fixed",
        width=1200,
        align="center"
    )
    
    # Add wrapper style to center content
    style = Div(
        text="""
        <style>
            body {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 0;
                padding: 0;
                width: 100%;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }
            .bk-root {
                margin: 0 auto !important;
            }
        </style>
        """
    )
    
    # Final layout with style
    final_layout = column(style, layout_obj)
    
    # Output to file
    output_file(os.path.join(program_dir, "program_distribution.html"))
    save(final_layout)
    
    print("Generated program distribution charts") 