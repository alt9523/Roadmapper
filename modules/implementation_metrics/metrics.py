import os
import json
from datetime import datetime
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, HoverTool, Legend, LabelSet, DatetimeTickFormatter, NumeralTickFormatter
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import Category10, Category20, Spectral6
from bokeh.transform import cumsum, factor_cmap
from bokeh.embed import components
from bokeh.models.widgets import DataTable, TableColumn, HTMLTemplateFormatter, NumberFormatter, DateFormatter
from math import pi
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image
import io
import base64

def extract_implementation_data(data):
    """Extract implementation data from the roadmap data"""
    implementation_data = []
    
    for program in data.get('programs', []):
        program_id = program.get('id', '')
        program_name = program.get('name', '')
        
        for pmc in program.get('productMaterialCombinations', []):
            product_id = pmc.get('productID', '')
            material_id = pmc.get('materialID', '')
            part_name = pmc.get('partName', '')
            part_number = pmc.get('partNumber', '')
            lifetime_demand = int(pmc.get('lifetimeDemand', 0)) if pmc.get('lifetimeDemand', '').isdigit() else 0
            unit_cost_savings = float(pmc.get('unitCostSavings', 0)) if pmc.get('unitCostSavings', '').replace('.', '', 1).isdigit() else 0
            unit_schedule_savings = float(pmc.get('unitScheduleSavings', 0)) if pmc.get('unitScheduleSavings', '').replace('.', '', 1).isdigit() else 0
            need_date = pmc.get('needDate', '')
            adoption_status = pmc.get('adoptionStatus', '')
            
            # Calculate total savings
            total_cost_savings = lifetime_demand * unit_cost_savings
            total_schedule_savings = lifetime_demand * unit_schedule_savings
            
            # Get product and material names
            product_name = ''
            material_name = ''
            
            for product in data.get('products', []):
                if product.get('id', '') == product_id:
                    product_name = product.get('name', '')
                    break
            
            for material in data.get('materialSystems', []):
                if material.get('id', '') == material_id:
                    material_name = material.get('name', '')
                    break
            
            # Process status history
            status_history = pmc.get('statusHistory', [])
            baselined_date = None
            completed_date = None
            
            for status in status_history:
                if status.get('status', '') == 'Baselined':
                    try:
                        baselined_date = datetime.strptime(status.get('date', ''), '%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass
                elif status.get('status', '') == 'Complete':
                    try:
                        completed_date = datetime.strptime(status.get('date', ''), '%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass
            
            implementation_data.append({
                'program_id': program_id,
                'program_name': program_name,
                'product_id': product_id,
                'product_name': product_name,
                'material_id': material_id,
                'material_name': material_name,
                'part_name': part_name,
                'part_number': part_number,
                'lifetime_demand': lifetime_demand,
                'unit_cost_savings': unit_cost_savings,
                'unit_schedule_savings': unit_schedule_savings,
                'total_cost_savings': total_cost_savings,
                'total_schedule_savings': total_schedule_savings,
                'need_date': need_date,
                'adoption_status': adoption_status,
                'baselined_date': baselined_date,
                'completed_date': completed_date
            })
    
    return implementation_data

def generate_adoption_over_time_image(implementation_data, output_dir):
    """Generate adoption over time chart as an image and save to file"""
    print("Generating adoption over time visualization...")
    
    # Filter out entries without baselined dates
    filtered_data = [item for item in implementation_data if item['baselined_date'] is not None]
    
    if not filtered_data:
        print("No baselined date data available for adoption over time visualization.")
        return None
    
    # Sort by baselined date
    filtered_data.sort(key=lambda x: x['baselined_date'])
    
    # Create cumulative adoption data
    dates = [item['baselined_date'] for item in filtered_data]
    cumulative_count = list(range(1, len(filtered_data) + 1))
    
    # Create the matplotlib figure
    plt.figure(figsize=(10, 5))
    plt.plot(dates, cumulative_count, marker='o', linewidth=2, color="#3498db")
    
    # Style the plot
    plt.title("Adoption Over Time", fontsize=14, fontweight='bold', color="#2c3e50")
    plt.xlabel("Date", fontsize=12, color="#2c3e50")
    plt.ylabel("Cumulative Number of Parts", fontsize=12, color="#2c3e50")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    # Save the plot to file
    plot_path = os.path.join(output_dir, "adoption_over_time.png")
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    # Also save the HTML version for standalone viewing
    output_file(os.path.join(output_dir, "adoption_over_time.html"))
    
    # Create Bokeh version with hover
    p = figure(
        title="Adoption Over Time (Baselined Parts)",
        x_axis_label="Date",
        y_axis_label="Cumulative Number of Parts",
        x_axis_type="datetime",
        width=1200,
        height=500,
        background_fill_color="#f8f9fa",
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    
    source = ColumnDataSource(data={
        'x': dates,
        'y': cumulative_count,
        'part_name': [item['part_name'] for item in filtered_data],
        'program_name': [item['program_name'] for item in filtered_data]
    })
    
    p.line('x', 'y', source=source, line_width=2, color="#3498db")
    circles = p.scatter('x', 'y', source=source, size=8, color="#3498db", alpha=0.8)
    
    hover = HoverTool(
        tooltips=[
            ("Date", "@x{%F}"),
            ("Cumulative Parts", "@y"),
            ("Part", "@part_name"),
            ("Program", "@program_name")
        ],
        formatters={"@x": "datetime"},
        renderers=[circles]
    )
    p.add_tools(hover)
    
    save(p)
    
    return "adoption_over_time.png"

def generate_cost_savings_over_time_image(implementation_data, output_dir):
    """Generate cost savings over time chart as an image and save to file"""
    print("Generating cost savings over time visualization...")
    
    # Filter out entries without baselined dates
    filtered_data = [item for item in implementation_data if item['baselined_date'] is not None]
    
    if not filtered_data:
        print("No baselined date data available for cost savings over time visualization.")
        return None
    
    # Sort by baselined date
    filtered_data.sort(key=lambda x: x['baselined_date'])
    
    # Create cumulative cost savings data
    dates = []
    cumulative_savings = []
    running_total = 0
    
    for item in filtered_data:
        dates.append(item['baselined_date'])
        running_total += item['total_cost_savings']
        cumulative_savings.append(running_total)
    
    # Create the matplotlib figure
    plt.figure(figsize=(10, 5))
    plt.plot(dates, cumulative_savings, marker='o', linewidth=2, color="#27ae60")
    
    # Style the plot
    plt.title("Cumulative Cost Savings Over Time", fontsize=14, fontweight='bold', color="#2c3e50")
    plt.xlabel("Date", fontsize=12, color="#2c3e50")
    plt.ylabel("Cumulative Cost Savings ($)", fontsize=12, color="#2c3e50")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    # Save the plot to file
    plot_path = os.path.join(output_dir, "cost_savings_over_time.png")
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    # Also save the HTML version for standalone viewing
    output_file(os.path.join(output_dir, "cost_savings_over_time.html"))
    
    # Create Bokeh version with hover
    p = figure(
        title="Cumulative Cost Savings Over Time",
        x_axis_label="Date",
        y_axis_label="Cumulative Cost Savings ($)",
        x_axis_type="datetime",
        width=1200,
        height=500,
        background_fill_color="#f8f9fa",
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    
    source = ColumnDataSource(data={
        'x': dates,
        'y': cumulative_savings,
        'part_name': [item['part_name'] for item in filtered_data],
        'program_name': [item['program_name'] for item in filtered_data],
        'individual_savings': [item['total_cost_savings'] for item in filtered_data]
    })
    
    p.line('x', 'y', source=source, line_width=2, color="#27ae60")
    circles = p.scatter('x', 'y', source=source, size=8, color="#27ae60", alpha=0.8)
    
    hover = HoverTool(
        tooltips=[
            ("Date", "@x{%F}"),
            ("Cumulative Savings", "$@y{0,0.00}"),
            ("Part", "@part_name"),
            ("Program", "@program_name"),
            ("Individual Savings", "$@individual_savings{0,0.00}")
        ],
        formatters={"@x": "datetime"},
        renderers=[circles]
    )
    p.add_tools(hover)
    
    save(p)
    
    return "cost_savings_over_time.png"

def generate_schedule_savings_over_time_image(implementation_data, output_dir):
    """Generate schedule savings over time chart as an image and save to file"""
    print("Generating schedule savings over time visualization...")
    
    # Filter out entries without baselined dates
    filtered_data = [item for item in implementation_data if item['baselined_date'] is not None]
    
    if not filtered_data:
        print("No baselined date data available for schedule savings over time visualization.")
        return None
    
    # Sort by baselined date
    filtered_data.sort(key=lambda x: x['baselined_date'])
    
    # Create cumulative schedule savings data
    dates = []
    cumulative_savings = []
    running_total = 0
    
    for item in filtered_data:
        dates.append(item['baselined_date'])
        running_total += item['total_schedule_savings']
        cumulative_savings.append(running_total)
    
    # Create the matplotlib figure
    plt.figure(figsize=(10, 5))
    plt.plot(dates, cumulative_savings, marker='o', linewidth=2, color="#f39c12")
    
    # Style the plot
    plt.title("Cumulative Schedule Savings Over Time", fontsize=14, fontweight='bold', color="#2c3e50")
    plt.xlabel("Date", fontsize=12, color="#2c3e50")
    plt.ylabel("Cumulative Schedule Savings (Days)", fontsize=12, color="#2c3e50")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    # Save the plot to file
    plot_path = os.path.join(output_dir, "schedule_savings_over_time.png")
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    # Also save the HTML version for standalone viewing
    output_file(os.path.join(output_dir, "schedule_savings_over_time.html"))
    
    # Create Bokeh version with hover
    p = figure(
        title="Cumulative Schedule Savings Over Time",
        x_axis_label="Date",
        y_axis_label="Cumulative Schedule Savings (Days)",
        x_axis_type="datetime",
        width=1200,
        height=500,
        background_fill_color="#f8f9fa",
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    
    source = ColumnDataSource(data={
        'x': dates,
        'y': cumulative_savings,
        'part_name': [item['part_name'] for item in filtered_data],
        'program_name': [item['program_name'] for item in filtered_data],
        'individual_savings': [item['total_schedule_savings'] for item in filtered_data]
    })
    
    p.line('x', 'y', source=source, line_width=2, color="#f39c12")
    circles = p.scatter('x', 'y', source=source, size=8, color="#f39c12", alpha=0.8)
    
    hover = HoverTool(
        tooltips=[
            ("Date", "@x{%F}"),
            ("Cumulative Savings", "@y{0,0} days"),
            ("Part", "@part_name"),
            ("Program", "@program_name"),
            ("Individual Savings", "@individual_savings{0,0} days")
        ],
        formatters={"@x": "datetime"},
        renderers=[circles]
    )
    p.add_tools(hover)
    
    save(p)
    
    return "schedule_savings_over_time.png"

def generate_material_pie_chart_image(implementation_data, output_dir):
    """Generate material pie chart as an image and save to file"""
    print("Generating material system pie chart...")
    
    # Count parts by material system
    material_counts = Counter()
    for item in implementation_data:
        if item['material_name']:
            material_counts[item['material_name']] += 1
    
    if not material_counts:
        print("No material system data available for pie chart visualization.")
        return None
    
    # Get labels and sizes
    labels = list(material_counts.keys())
    sizes = list(material_counts.values())
    
    # Create color palette
    colors = plt.cm.tab10.colors[:len(labels)]
    
    # Create the matplotlib figure
    plt.figure(figsize=(8, 6))
    patches, texts, autotexts = plt.pie(
        sizes, 
        labels=labels, 
        colors=colors,
        autopct='%1.1f%%', 
        startangle=90,
        shadow=False,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1}
    )
    
    # Style the plot
    plt.title("Material System Distribution", fontsize=14, fontweight='bold', color="#2c3e50")
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
    
    # Improve label visibility
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    
    # Save the plot to file
    plot_path = os.path.join(output_dir, "material_system_pie.png")
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    # Also save an interactive version with Bokeh
    output_file(os.path.join(output_dir, "adoption_by_material.html"))
    
    # Create data for Bokeh
    data = pd.DataFrame({
        'material': list(material_counts.keys()),
        'count': list(material_counts.values())
    })
    data['angle'] = data['count'] / data['count'].sum() * 2 * pi
    data['percentage'] = data['count'] / data['count'].sum() * 100
    
    # Use a color palette
    if len(data) <= 10:
        bokeh_colors = Category10[max(3, len(data))]
    else:
        bokeh_colors = Category20[max(3, min(len(data), 20))]
    
    data['color'] = bokeh_colors[:len(data)]
    
    # Create the figure
    p = figure(
        title="Adoption by Material System",
        width=600,
        height=600,
        toolbar_location=None,
        tools="hover",
        tooltips=[("Material", "@material"), ("Count", "@count"), ("Percentage", "@percentage{0.0}%")],
        background_fill_color="#f8f9fa"
    )
    
    # Create pie chart
    p.wedge(
        x=0, y=0, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='material',
        source=data
    )
    
    # Style the plot
    p.title.text_font_size = "14pt"
    p.title.text_color = "#2c3e50"
    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    
    save(p)
    
    return "material_system_pie.png"

def generate_implementation_summary(implementation_data, output_dir):
    """Generate a summary page for implementation metrics"""
    print("Generating implementation summary page...")
    
    # Define successful adoption statuses
    successful_statuses = ['Baselined', 'Production', 'Complete']
    
    # Filter data to only include parts with successful adoption status
    successful_parts = [item for item in implementation_data if item['adoption_status'] in successful_statuses]
    
    # Calculate summary metrics (only counting successful adoptions)
    # Count total parts including lifetime demand (quantity)
    total_parts = sum(item['lifetime_demand'] for item in successful_parts)
    total_cost_savings = sum(item['total_cost_savings'] for item in successful_parts)
    total_schedule_savings = sum(item['total_schedule_savings'] for item in successful_parts)
    
    # Count total programs with successful adoptions
    program_ids = set(item['program_id'] for item in successful_parts)
    total_programs = len(program_ids)
    
    # Count parts by status
    status_counts = Counter()
    for item in implementation_data:
        status = item['adoption_status']
        if status and status != 'Closed':
            status_counts[status] += 1
    
    # Count parts by material system
    material_counts = Counter()
    for item in implementation_data:
        if item['material_name']:
            material_counts[item['material_name']] += 1
    
    # Generate chart images
    adoption_chart_path = generate_adoption_over_time_image(implementation_data, output_dir)
    cost_savings_chart_path = generate_cost_savings_over_time_image(implementation_data, output_dir)
    schedule_savings_chart_path = generate_schedule_savings_over_time_image(implementation_data, output_dir)
    material_chart_path = generate_material_pie_chart_image(implementation_data, output_dir)
    
    # Create HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Implementation Metrics</title>
        
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
                background: linear-gradient(to right, #3498db, #2c3e50);
                color: white;
                padding: 20px;
                text-align: center;
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
            .back-link {{
                display: inline-block;
                margin-top: 20px;
                padding: 8px 15px;
                background-color: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                transition: background-color 0.3s ease;
            }}
            .back-link:hover {{
                background-color: #2980b9;
            }}
            .nav-links {{
                margin-top: 15px;
            }}
            .nav-link {{
                color: white;
                text-decoration: none;
                padding: 8px 15px;
                background-color: rgba(255,255,255,0.2);
                border-radius: 4px;
                margin: 0 5px;
                transition: background-color 0.3s;
            }}
            .nav-link:hover {{
                background-color: rgba(255,255,255,0.3);
            }}
            .status-badge {{
                display: inline-block;
                padding: 5px 10px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                margin: 5px;
            }}
            .status-Baselined {{
                background-color: #3498db;
            }}
            .status-Complete {{
                background-color: #27ae60;
            }}
            .status-Production {{
                background-color: #9b59b6;
            }}
            .status-Prototyping {{
                background-color: #f39c12;
            }}
            .status-Developing {{
                background-color: #95a5a6;
            }}
            .status-Targeting {{
                background-color: #7f8c8d;
            }}
            .material-item {{
                display: inline-block;
                margin: 5px 10px;
                padding: 5px 10px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #ddd;
            }}
            .chart-container {{
                width: 100%;
                margin: 20px auto;
                text-align: center;
            }}
            .chart-img {{
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .status-cards-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-top: 20px;
            }}
            .status-section {{
                flex: 1;
                min-width: 180px;
                margin-bottom: 20px;
            }}
            .status-header {{
                padding: 10px 15px;
                color: white;
                border-radius: 4px;
                margin-bottom: 15px;
                text-align: center;
            }}
            .status-items {{
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}
            .part-card {{
                background-color: #f8f9fa;
                border-radius: 4px;
                padding: 10px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .program-name {{
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            .part-name {{
                color: #7f8c8d;
            }}
            .material-charts {{
                display: flex;
                flex-wrap: wrap;
                margin-top: 20px;
            }}
            .material-list {{
                flex: 1;
                min-width: 250px;
                padding-right: 20px;
            }}
            .material-pie {{
                flex: 1;
                min-width: 450px;
                text-align: center;
            }}
            .section-heading {{
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 20px;
                color: #2c3e50;
                font-size: 18px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h1>Implementation Metrics</h1>
                    <div>
                        <a href="../index.html" class="nav-link">Back to Dashboard</a>
                    </div>
                </div>
                <div class="nav-links">
                    <a href="adoption_over_time.html" class="nav-link">Adoption Over Time</a>
                    <a href="cost_savings_over_time.html" class="nav-link">Cost Savings</a>
                    <a href="schedule_savings_over_time.html" class="nav-link">Schedule Savings</a>
                    <a href="adoption_by_material.html" class="nav-link">Material Breakdown</a>
                    <a href="parts_by_status.html" class="nav-link">Parts by Status</a>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">Total Programs</div>
                    <div class="metric-value">{total_programs}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Total Parts</div>
                    <div class="metric-value">{total_parts}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Total Cost Savings</div>
                    <div class="metric-value">${total_cost_savings:,.2f}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Total Schedule Savings</div>
                    <div class="metric-value">{total_schedule_savings:,.0f} days</div>
                </div>
            </div>
            
            <div class="summary-card">
                <h2>Adoption and Savings Over Time</h2>
                <div class="chart-container">
                    <h3 class="section-heading">Parts Adoption Over Time</h3>
                    <img src="{adoption_chart_path}" alt="Adoption Over Time Chart" class="chart-img" />
                </div>
                <div class="chart-container">
                    <h3 class="section-heading">Cost Savings Over Time</h3>
                    <img src="{cost_savings_chart_path}" alt="Cost Savings Over Time Chart" class="chart-img" />
                </div>
                <div class="chart-container">
                    <h3 class="section-heading">Schedule Savings Over Time</h3>
                    <img src="{schedule_savings_chart_path}" alt="Schedule Savings Over Time Chart" class="chart-img" />
                </div>
            </div>
            
            <div class="summary-card">
                <h2>Adoption Status Breakdown</h2>
                <div class="status-cards-container">
    """
    
    # Define all possible statuses and their display order
    all_statuses = ['Targeting', 'Developing', 'Prototyping', 'Baselined', 'Production', 'Complete']
    
    # Add status cards for each status, including ones with no items
    for status in all_statuses:
        count = status_counts.get(status, 0)
        status_class = status.replace(' ', '.')
        html += f"""
                    <div class="status-section">
                        <div class="status-header status-{status_class}">{status}: {count}</div>
                        <div class="status-items">
        """
        
        # Add part cards for items with this status
        items_added = False
        for item in implementation_data:
            if item['adoption_status'] == status and item['adoption_status'] != 'Closed':
                items_added = True
                html += f"""
                            <div class="part-card">
                                <div class="program-name">{item['program_name']}</div>
                                <div class="part-name">{item['part_name']}</div>
                            </div>
                """
        
        # Add a message if no items
        if not items_added:
            html += """
                            <div class="part-card" style="text-align:center; font-style:italic; color:#999;">
                                No parts in this status
                            </div>
            """
        
        html += """
                        </div>
                    </div>
        """
    
    html += """
                </div>
            </div>
            
            <div class="summary-card">
                <h2>Material System Breakdown</h2>
                <div class="material-charts">
                    <div class="material-list">
                        <h3 class="section-heading">Parts by Material System</h3>
    """
    
    # Add material counts
    for material, count in material_counts.most_common():
        html += f"""
                        <div class="material-item"><strong>{material}</strong>: {count} parts</div>
        """
    
    html += f"""
                    </div>
                    <div class="material-pie">
                        <h3 class="section-heading">Distribution</h3>
                        <img src="{material_chart_path}" alt="Material System Distribution" class="chart-img" />
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write the HTML to a file
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(html)
    
    return "index.html"

def generate_implementation_metrics(data, output_dir):
    """Generate all implementation metrics visualizations"""
    print("Generating implementation metrics visualizations...")
    
    # Create output directory if it doesn't exist
    metrics_dir = os.path.join(output_dir, "implementation")
    if not os.path.exists(metrics_dir):
        os.makedirs(metrics_dir)
    
    # Extract implementation data
    implementation_data = extract_implementation_data(data)
    
    if not implementation_data:
        print("No implementation data found.")
        return None
    
    # Generate visualizations
    summary_path = generate_implementation_summary(implementation_data, metrics_dir)
    
    print(f"Implementation metrics visualizations generated in '{metrics_dir}'")
    
    return os.path.join("implementation", "index.html") 