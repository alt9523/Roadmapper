"""
Progress Tracking Module for Roadmap Visualizations

This module provides progress tracking visualizations including:
1. Burndown charts for task completion
2. Milestone achievement tracking
3. Comparison of planned vs. actual progress
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Div, Tabs, Panel, DataTable, TableColumn, DateFormatter, Span
from bokeh.transform import dodge
from bokeh.layouts import column, row, gridplot
from bokeh.palettes import Category10, Spectral6

def generate_progress_tracking(data, output_dir):
    """Generate progress tracking visualizations"""
    print("Generating progress tracking visualizations...")
    
    # Create progress tracking directory
    progress_dir = os.path.join(output_dir, "progress")
    if not os.path.exists(progress_dir):
        os.makedirs(progress_dir)
    
    # Generate burndown charts
    generate_burndown_charts(data, progress_dir)
    
    # Generate milestone tracking
    generate_milestone_tracking(data, progress_dir)
    
    # Generate planned vs actual comparison
    generate_planned_vs_actual(data, progress_dir)
    
    # Generate progress dashboard summary
    generate_progress_dashboard(data, progress_dir)
    
    print(f"Progress tracking visualizations generated in '{progress_dir}'")
    
    # Return path to progress dashboard for linking from main dashboard
    return os.path.join("progress", "progress_dashboard.html")

def generate_burndown_charts(data, progress_dir):
    """Generate burndown charts showing task completion over time"""
    print("Generating burndown charts...")
    
    # Set up the output file
    output_file(os.path.join(progress_dir, "burndown_charts.html"))
    
    # Collect all tasks from programs and products
    all_tasks = []
    
    # Process program tasks
    for program in data.get('programs', []):
        if 'roadmap' in program and 'tasks' in program['roadmap']:
            for task in program['roadmap']['tasks']:
                task_info = {
                    'id': f"P{program['id']}_T{task.get('task', 'Unknown')}",
                    'name': task.get('task', 'Unknown'),
                    'entity_type': 'Program',
                    'entity_name': program.get('name', 'Unknown'),
                    'entity_id': program.get('id', 'Unknown'),
                    'start': task.get('start', ''),
                    'end': task.get('end', ''),
                    'status': task.get('status', 'Unknown')
                }
                all_tasks.append(task_info)
    
    # Process product tasks
    for product in data.get('products', []):
        if 'roadmap' in product and 'tasks' in product['roadmap']:
            for task in product['roadmap']['tasks']:
                task_info = {
                    'id': f"P{product['id']}_T{task.get('task', 'Unknown')}",
                    'name': task.get('task', 'Unknown'),
                    'entity_type': 'Product',
                    'entity_name': product.get('name', 'Unknown'),
                    'entity_id': product.get('id', 'Unknown'),
                    'start': task.get('start', ''),
                    'end': task.get('end', ''),
                    'status': task.get('status', 'Unknown')
                }
                all_tasks.append(task_info)
    
    # Process material system tasks
    for material in data.get('materialSystems', []):
        if 'roadmap' in material:
            for task in material.get('roadmap', []):
                task_info = {
                    'id': f"M{material['id']}_T{task.get('task', 'Unknown')}",
                    'name': task.get('task', 'Unknown'),
                    'entity_type': 'Material',
                    'entity_name': material.get('name', 'Unknown'),
                    'entity_id': material.get('id', 'Unknown'),
                    'start': task.get('startDate', ''),
                    'end': task.get('endDate', ''),
                    'status': task.get('status', 'Unknown')
                }
                all_tasks.append(task_info)
    
    # Create a task status summary
    status_counts = {
        'Complete': 0,
        'In Progress': 0,
        'Planned': 0
    }
    
    for task in all_tasks:
        status = task['status']
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = 1
    
    # Create a simulated burndown chart (since we don't have historical data)
    today = datetime.now()
    dates = [today - timedelta(days=x) for x in range(90, -1, -7)]  # Last 90 days
    
    # Generate simulated data
    total_tasks = sum(status_counts.values())
    completed_tasks = []
    remaining_tasks = []
    
    # Simulate a burndown trend
    for i, date in enumerate(dates):
        progress_ratio = i / len(dates)
        completed = int(progress_ratio * status_counts['Complete'])
        completed_tasks.append(completed)
        remaining_tasks.append(total_tasks - completed)
    
    # Create ideal trend line
    ideal_remaining = []
    for i, date in enumerate(dates):
        progress_ratio = i / len(dates)
        ideal = int(total_tasks * (1 - progress_ratio))
        ideal_remaining.append(ideal)
    
    # Convert dates to strings for Bokeh
    date_strings = [date.strftime('%Y-%m-%d') for date in dates]
    
    # Create Bokeh figure
    p = figure(
        title="Task Burndown Chart",
        x_range=date_strings,
        width=800,
        height=400,
        toolbar_location="right",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Add hover tool
    hover = HoverTool(
        tooltips=[
            ("Date", "@x"),
            ("Tasks", "@y"),
        ]
    )
    p.add_tools(hover)
    
    # Plot the data
    source_actual = ColumnDataSource(data=dict(
        x=date_strings,
        y=remaining_tasks,
        completed=completed_tasks
    ))
    
    source_ideal = ColumnDataSource(data=dict(
        x=date_strings,
        y=ideal_remaining
    ))
    
    # Plot actual burndown
    p.line('x', 'y', source=source_actual, line_width=3, line_color='#0066cc', legend_label="Actual Remaining")
    p.scatter('x', 'y', source=source_actual, size=8, color='#0066cc')
    
    # Plot ideal burndown
    p.line('x', 'y', source=source_ideal, line_width=2, line_color='#ff7f0e', line_dash='dashed', legend_label="Ideal Burndown")
    
    # Style the plot
    p.title.text_font_size = "16px"
    p.xaxis.major_label_orientation = 1.2
    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    p.yaxis.axis_label = "Remaining Tasks"
    
    # Create a task status summary panel
    status_data = {
        'Status': list(status_counts.keys()),
        'Count': list(status_counts.values())
    }
    
    status_source = ColumnDataSource(data=status_data)
    
    status_columns = [
        TableColumn(field="Status", title="Status"),
        TableColumn(field="Count", title="Count")
    ]
    
    status_table = DataTable(
        source=status_source,
        columns=status_columns,
        width=300,
        height=150
    )
    
    status_div = Div(
        text="<h3>Task Status Summary</h3>",
        width=300,
        height=30
    )
    
    status_panel = column(status_div, status_table)
    
    # Create a task completion visualization - simple donut chart using Div with HTML/CSS
    total_count = sum(status_counts.values())
    complete_count = status_counts.get('Complete', 0)
    complete_percentage = round((complete_count / total_count) * 100) if total_count > 0 else 0
    
    completion_div = Div(
        text=f"""
        <h3>Overall Completion</h3>
        <div style="position: relative; width: 150px; height: 150px; margin: 0 auto;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 50%; 
                      background: conic-gradient(#43a047 0% {complete_percentage}%, #e0e0e0 {complete_percentage}% 100%);">
            </div>
            <div style="position: absolute; top: 20%; left: 20%; width: 60%; height: 60%; 
                      border-radius: 50%; background: white; display: flex; align-items: center; 
                      justify-content: center; font-size: 24px; font-weight: bold;">
                {complete_percentage}%
            </div>
        </div>
        <div style="text-align: center; margin-top: 10px;">
            {complete_count} of {total_count} tasks complete
        </div>
        """,
        width=300,
        height=250
    )
    
    # Layout everything
    layout = row(
        p,
        column(completion_div, status_panel)
    )
    
    # Save the burndown chart
    save(layout)

def generate_milestone_tracking(data, progress_dir):
    """Generate milestone achievement tracking"""
    print("Generating milestone achievement tracking...")
    
    # Set up the output file
    output_file(os.path.join(progress_dir, "milestone_tracking.html"))
    
    # Collect all milestones from programs and products
    all_milestones = []
    
    # Process program milestones
    for program in data.get('programs', []):
        if 'milestones' in program:
            for milestone in program['milestones']:
                milestone_info = {
                    'id': f"P{program['id']}_M{milestone.get('name', 'Unknown')}",
                    'name': milestone.get('name', 'Unknown'),
                    'entity_type': 'Program',
                    'entity_name': program.get('name', 'Unknown'),
                    'entity_id': program.get('id', 'Unknown'),
                    'date': milestone.get('date', ''),
                    'description': milestone.get('description', ''),
                    'status': 'Complete' if milestone.get('date', '') and datetime.strptime(milestone.get('date', '2099-12-31'), '%Y-%m-%d') < datetime.now() else 'Planned'
                }
                all_milestones.append(milestone_info)
    
    # Process product milestones
    for product in data.get('products', []):
        if 'milestones' in product:
            for milestone in product['milestones']:
                milestone_info = {
                    'id': f"P{product['id']}_M{milestone.get('name', 'Unknown')}",
                    'name': milestone.get('name', 'Unknown'),
                    'entity_type': 'Product',
                    'entity_name': product.get('name', 'Unknown'),
                    'entity_id': product.get('id', 'Unknown'),
                    'date': milestone.get('date', ''),
                    'description': milestone.get('description', ''),
                    'status': 'Complete' if milestone.get('date', '') and datetime.strptime(milestone.get('date', '2099-12-31'), '%Y-%m-%d') < datetime.now() else 'Planned'
                }
                all_milestones.append(milestone_info)
    
    # Process material system milestones
    for material in data.get('materialSystems', []):
        if 'milestones' in material:
            for milestone in material['milestones']:
                milestone_info = {
                    'id': f"M{material['id']}_M{milestone.get('name', 'Unknown')}",
                    'name': milestone.get('name', 'Unknown'),
                    'entity_type': 'Material',
                    'entity_name': material.get('name', 'Unknown'),
                    'entity_id': material.get('id', 'Unknown'),
                    'date': milestone.get('date', ''),
                    'description': milestone.get('description', ''),
                    'status': 'Complete' if milestone.get('date', '') and datetime.strptime(milestone.get('date', '2099-12-31'), '%Y-%m-%d') < datetime.now() else 'Planned'
                }
                all_milestones.append(milestone_info)
    
    # Create a milestone table
    if all_milestones:
        # Sort milestones by date
        all_milestones = sorted(all_milestones, key=lambda x: x['date'] if x['date'] else '2099-12-31')
        
        # Create milestone data for table
        milestone_data = {
            'Entity': [m['entity_name'] for m in all_milestones],
            'Milestone': [m['name'] for m in all_milestones],
            'Date': [m['date'] for m in all_milestones],
            'Description': [m['description'] for m in all_milestones],
            'Status': [m['status'] for m in all_milestones],
            'Type': [m['entity_type'] for m in all_milestones],
        }
        
        milestone_source = ColumnDataSource(data=milestone_data)
        
        milestone_columns = [
            TableColumn(field="Entity", title="Entity"),
            TableColumn(field="Type", title="Type"),
            TableColumn(field="Milestone", title="Milestone"),
            TableColumn(field="Date", title="Date"),
            TableColumn(field="Status", title="Status"),
            TableColumn(field="Description", title="Description")
        ]
        
        milestone_table = DataTable(
            source=milestone_source,
            columns=milestone_columns,
            width=800,
            height=400
        )
        
        milestone_div = Div(
            text="<h2>Milestone Tracking</h2><p>Track progress of key milestones across programs, products, and materials.</p>",
            width=800,
            height=70
        )
        
        # Create a timeline visualization
        # Prepare data for timeline
        today = datetime.now()
        earliest_date = today - timedelta(days=180)  # 6 months ago
        latest_date = today + timedelta(days=365)  # 1 year ahead
        
        timeline_milestones = []
        for m in all_milestones:
            if m['date']:
                try:
                    date = datetime.strptime(m['date'], '%Y-%m-%d')
                    if earliest_date <= date <= latest_date:
                        timeline_milestones.append(m)
                except ValueError:
                    # Skip milestones with invalid dates
                    pass
        
        if timeline_milestones:
            # Sort by date
            timeline_milestones = sorted(timeline_milestones, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
            
            # Create timeline visualization
            p = figure(
                title="Milestone Timeline",
                x_range=(earliest_date.strftime('%Y-%m-%d'), latest_date.strftime('%Y-%m-%d')),
                width=800,
                height=300,
                y_range=(-0.5, len(timeline_milestones) - 0.5),
                toolbar_location="right",
                tools="pan,wheel_zoom,box_zoom,reset,save",
            )
            
            # Add today line
            today_line = Span(
                location=today.strftime('%Y-%m-%d'),
                dimension='height',
                line_color='red',
                line_dash='dashed',
                line_width=2
            )
            p.add_layout(today_line)
            
            # Add today label
            today_label = Label(
                x=today.strftime('%Y-%m-%d'),
                y=len(timeline_milestones) - 0.5,
                text="Today",
                text_font_size="10pt",
                text_color="red",
                x_offset=5,
                y_offset=10
            )
            p.add_layout(today_label)
            
            # Plot milestones
            source = ColumnDataSource(data=dict(
                x=[datetime.strptime(m['date'], '%Y-%m-%d').strftime('%Y-%m-%d') for m in timeline_milestones],
                y=list(range(len(timeline_milestones))),
                name=[m['name'] for m in timeline_milestones],
                entity=[m['entity_name'] for m in timeline_milestones],
                status=[m['status'] for m in timeline_milestones],
                color=['#43a047' if m['status'] == 'Complete' else '#ff9800' for m in timeline_milestones]
            ))
            
            # Add hover tool
            hover = HoverTool(
                tooltips=[
                    ("Milestone", "@name"),
                    ("Entity", "@entity"),
                    ("Date", "@x"),
                    ("Status", "@status")
                ]
            )
            p.add_tools(hover)
            
            # Add milestones as diamonds
            p.scatter('x', 'y', source=source, size=15, fill_color='color', line_color='black', marker='diamond')
            
            # Add milestone names
            for i, milestone in enumerate(timeline_milestones):
                milestone_name = Label(
                    x=datetime.strptime(milestone['date'], '%Y-%m-%d').strftime('%Y-%m-%d'),
                    y=i,
                    text=f"{milestone['name']} ({milestone['entity_name']})",
                    text_font_size="9pt",
                    x_offset=10,
                    y_offset=0
                )
                p.add_layout(milestone_name)
            
            # Style the plot
            p.title.text_font_size = "16px"
            p.xaxis.major_label_orientation = 1.2
            p.yaxis.visible = False
            p.ygrid.grid_line_color = None
            p.xgrid.grid_line_color = "lightgray"
            p.xgrid.grid_line_alpha = 0.5
            
            # Layout everything
            layout = column(milestone_div, p, milestone_table)
        else:
            layout = column(milestone_div, milestone_table)
    else:
        # If no milestones, create a placeholder
        placeholder_div = Div(
            text="<h2>Milestone Tracking</h2><p>No milestones found in the roadmap data.</p>",
            width=800,
            height=400
        )
        layout = column(placeholder_div)
    
    # Save the milestone tracking
    save(layout)

def generate_planned_vs_actual(data, progress_dir):
    """Generate planned vs actual progress visualization"""
    print("Generating planned vs. actual progress visualization...")
    
    # Set up the output file
    output_file(os.path.join(progress_dir, "planned_vs_actual.html"))
    
    # Create a simulated comparison of planned vs. actual progress
    # Since we don't have actual progress data, we'll create a simulation
    
    # Categories for comparison
    categories = [
        "Design Tasks",
        "Manufacturing Tasks",
        "Testing Tasks", 
        "Qualification Tasks",
        "Documentation Tasks"
    ]
    
    # Simulated planned percentages
    planned = [100, 100, 100, 100, 100]
    
    # Simulated actual percentages (create some variation)
    actual = [95, 80, 70, 60, 90]
    
    # Create a comparison bar chart
    p = figure(
        title="Planned vs. Actual Progress",
        x_range=categories,
        width=800,
        height=400,
        toolbar_location="right",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Create data sources
    source_planned = ColumnDataSource(data=dict(
        x=categories,
        y=planned,
        desc=["Planned Progress"] * len(categories)
    ))
    
    source_actual = ColumnDataSource(data=dict(
        x=categories,
        y=actual,
        desc=["Actual Progress"] * len(categories)
    ))
    
    # Add hover tool
    hover = HoverTool(
        tooltips=[
            ("Category", "@x"),
            ("Progress", "@y%"),
            ("Type", "@desc")
        ]
    )
    p.add_tools(hover)
    
    # Plot bars
    bar_width = 0.3
    
    # Planned bars
    p.vbar(
        x=dodge('x', -bar_width/2, range=p.x_range), 
        top='y', 
        width=bar_width, 
        source=source_planned,
        color='#0066cc',
        legend_label="Planned"
    )
    
    # Actual bars
    p.vbar(
        x=dodge('x', bar_width/2, range=p.x_range), 
        top='y', 
        width=bar_width, 
        source=source_actual,
        color='#ff9800',
        legend_label="Actual"
    )
    
    # Style the plot
    p.title.text_font_size = "16px"
    p.xaxis.major_label_orientation = 0.7
    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    p.y_range.start = 0
    p.y_range.end = 110
    p.yaxis.axis_label = "Completion Percentage"
    
    # Create a summary table
    summary_data = {
        'Category': categories,
        'Planned': planned,
        'Actual': actual,
        'Difference': [a - p for a, p in zip(actual, planned)],
    }
    
    summary_source = ColumnDataSource(data=summary_data)
    
    summary_columns = [
        TableColumn(field="Category", title="Category"),
        TableColumn(field="Planned", title="Planned %"),
        TableColumn(field="Actual", title="Actual %"),
        TableColumn(field="Difference", title="Difference %")
    ]
    
    summary_table = DataTable(
        source=summary_source,
        columns=summary_columns,
        width=800,
        height=200
    )
    
    # Add explanation
    explanation_div = Div(
        text="""
        <h2>Planned vs. Actual Progress</h2>
        <p>This visualization compares planned progress against actual progress across different categories of tasks.</p>
        <p><em>Note: This is simulated data for demonstration purposes. In a real implementation, this would be based on actual progress tracking data.</em></p>
        """,
        width=800,
        height=100
    )
    
    # Layout everything
    layout = column(explanation_div, p, summary_table)
    
    # Save the visualization
    save(layout)

def generate_progress_dashboard(data, progress_dir):
    """Generate the progress tracking dashboard"""
    print("Generating progress tracking dashboard...")
    
    # Set up the output file
    output_file(os.path.join(progress_dir, "progress_dashboard.html"))
    
    # Create dashboard HTML with matching style to main dashboard
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Progress Tracking Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                background-color: #0066cc; 
                color: white; 
                padding: 20px; 
                text-align: center;
                border-radius: 5px 5px 0 0;
                margin-bottom: 20px;
            }}
            .header h1 {{ margin: 0; }}
            .header p {{ margin: 10px 0 0 0; }}
            .nav-links {{
                display: flex;
                background-color: white;
                padding: 10px 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                justify-content: flex-start;
                flex-wrap: wrap;
            }}
            .nav-links a {{
                color: #0066cc;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }}
            .nav-links a:hover {{
                text-decoration: underline;
            }}
            .card-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}
            .card {{ 
                background-color: white; 
                border-radius: 5px; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                transition: transform 0.3s ease;
            }}
            .card:hover {{ 
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .card h2 {{ 
                color: #0066cc; 
                margin-top: 0;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 10px;
            }}
            .card-content {{ margin-bottom: 15px; }}
            .card-footer {{ 
                display: flex;
                justify-content: flex-start;
            }}
            .btn {{
                display: inline-block;
                padding: 8px 15px;
                background-color: #0066cc;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                transition: background-color 0.3s ease;
            }}
            .btn:hover {{ background-color: #004c99; }}
            .footer {{ 
                text-align: center; 
                margin-top: 30px; 
                padding-top: 20px; 
                border-top: 1px solid #ddd;
                color: #666;
            }}
            .summary-card {{
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }}
            .summary-card h2 {{
                color: #0066cc;
                margin-top: 0;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 10px;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            .note {{
                font-style: italic;
                color: #666;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Progress Tracking Dashboard</h1>
                <p>Track task completion, milestone achievements, and compare planned vs. actual progress</p>
            </div>
            
            <div class="nav-links">
                <a href="../index.html">Back to Main Dashboard</a> |
                <a href="burndown_charts.html">Burndown Charts</a> |
                <a href="milestone_tracking.html">Milestone Tracking</a> |
                <a href="planned_vs_actual.html">Planned vs. Actual</a>
            </div>
            
            <div class="card-grid">
                <div class="card">
                    <h2>Burndown Charts</h2>
                    <div class="card-content">
                        <p>Track task completion over time with burndown charts showing the remaining work and completion trends.</p>
                    </div>
                    <div class="card-footer">
                        <a href="burndown_charts.html" class="btn">View Charts</a>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Milestone Tracking</h2>
                    <div class="card-content">
                        <p>Monitor the achievement of key milestones across programs, products, and material systems.</p>
                    </div>
                    <div class="card-footer">
                        <a href="milestone_tracking.html" class="btn">View Milestones</a>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Planned vs. Actual</h2>
                    <div class="card-content">
                        <p>Compare planned progress against actual progress to identify areas that need attention.</p>
                    </div>
                    <div class="card-footer">
                        <a href="planned_vs_actual.html" class="btn">View Comparison</a>
                    </div>
                </div>
            </div>
            
            <div class="summary-card">
                <h2>Progress Summary</h2>
                <p>This dashboard provides tools to track progress of tasks and milestones across the entire roadmap.</p>
                <p>Use these visualizations to:</p>
                <ul>
                    <li>Monitor task completion rates and trends over time</li>
                    <li>Track upcoming and completed milestones</li>
                    <li>Identify discrepancies between planned and actual progress</li>
                    <li>Make data-driven decisions to keep projects on track</li>
                </ul>
                <p class="note">Note: The visualizations currently use simulated data for demonstration purposes. In a production environment, these would be populated with actual progress data.</p>
            </div>
            
            <div class="footer">
                <p>Generated on {datetime.now().strftime('%Y-%m-%d')} | Additive Manufacturing Roadmap</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write the HTML to file
    with open(os.path.join(progress_dir, "progress_dashboard.html"), 'w') as f:
        f.write(dashboard_html) 