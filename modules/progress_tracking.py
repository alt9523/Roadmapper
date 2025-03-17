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
                    'status': task.get('status', 'Unknown'),
                    'float': task.get('float', False),
                    'additionalDetails': task.get('additionalDetails', '')
                }
                all_tasks.append(task_info)
    
    # Process product tasks
    for product in data.get('products', []):
        # Process roadmap tasks
        if 'roadmap' in product:
            for task in product.get('roadmap', []):
                task_info = {
                    'id': f"P{product['id']}_T{task.get('task', 'Unknown')}",
                    'name': task.get('task', 'Unknown'),
                    'entity_type': 'Product',
                    'entity_name': product.get('name', 'Unknown'),
                    'entity_id': product.get('id', 'Unknown'),
                    'start': task.get('start', ''),
                    'end': task.get('end', ''),
                    'status': task.get('status', 'Unknown'),
                    'float': task.get('float', False),
                    'additionalDetails': task.get('additionalDetails', '')
                }
                all_tasks.append(task_info)
        
        # Process design tools tasks
        if 'designTools' in product:
            for tool in product.get('designTools', []):
                if isinstance(tool, dict):
                    task_info = {
                        'id': f"P{product['id']}_DT_{tool.get('name', 'Unknown')}",
                        'name': tool.get('name', 'Unknown'),
                        'entity_type': 'Design Tool',
                        'entity_name': product.get('name', 'Unknown'),
                        'entity_id': product.get('id', 'Unknown'),
                        'start': tool.get('start', ''),
                        'end': tool.get('end', ''),
                        'status': tool.get('status', 'Unknown'),
                        'float': tool.get('float', False),
                        'additionalDetails': tool.get('additionalDetails', '')
                    }
                    all_tasks.append(task_info)
        
        # Process documentation tasks
        if 'documentation' in product:
            for doc in product.get('documentation', []):
                if isinstance(doc, dict):
                    task_info = {
                        'id': f"P{product['id']}_DOC_{doc.get('name', 'Unknown')}",
                        'name': doc.get('name', 'Unknown'),
                        'entity_type': 'Documentation',
                        'entity_name': product.get('name', 'Unknown'),
                        'entity_id': product.get('id', 'Unknown'),
                        'start': doc.get('start', ''),
                        'end': doc.get('end', ''),
                        'status': doc.get('status', 'Unknown'),
                        'float': doc.get('float', False),
                        'additionalDetails': doc.get('additionalDetails', '')
                    }
                    all_tasks.append(task_info)
        
        # Process special NDT tasks
        if 'specialNDT' in product:
            for ndt in product.get('specialNDT', []):
                if isinstance(ndt, dict):
                    task_info = {
                        'id': f"P{product['id']}_NDT_{ndt.get('name', 'Unknown')}",
                        'name': ndt.get('name', 'Unknown'),
                        'entity_type': 'Special NDT',
                        'entity_name': product.get('name', 'Unknown'),
                        'entity_id': product.get('id', 'Unknown'),
                        'start': ndt.get('startDate', ''),
                        'end': ndt.get('endDate', ''),
                        'status': ndt.get('status', 'Unknown'),
                        'float': ndt.get('float', False),
                        'additionalDetails': ndt.get('additionalDetails', '')
                    }
                    all_tasks.append(task_info)
        
        # Process part acceptance tasks
        if 'partAcceptance' in product:
            for acceptance in product.get('partAcceptance', []):
                if isinstance(acceptance, dict):
                    task_info = {
                        'id': f"P{product['id']}_PA_{acceptance.get('name', 'Unknown')}",
                        'name': acceptance.get('name', 'Unknown'),
                        'entity_type': 'Part Acceptance',
                        'entity_name': product.get('name', 'Unknown'),
                        'entity_id': product.get('id', 'Unknown'),
                        'start': acceptance.get('startDate', ''),
                        'end': acceptance.get('endDate', ''),
                        'status': acceptance.get('status', 'Unknown'),
                        'float': acceptance.get('float', False),
                        'additionalDetails': acceptance.get('additionalDetails', '')
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
                    'status': task.get('status', 'Unknown'),
                    'float': task.get('float', False),
                    'additionalDetails': task.get('additionalDetails', '')
                }
                all_tasks.append(task_info)
    
    # Filter out tasks without dates
    valid_tasks = [t for t in all_tasks if t['start'] and t['end']]
    
    if not valid_tasks:
        print("No valid tasks with dates found for burndown chart")
        return
    
    # Convert dates to datetime objects
    for task in valid_tasks:
        task['start_date'] = datetime.strptime(task['start'], "%Y-%m-%d")
        task['end_date'] = datetime.strptime(task['end'], "%Y-%m-%d")
    
    # Create a DataFrame for analysis
    df = pd.DataFrame(valid_tasks)
    
    # Calculate overall date range
    min_date = df['start_date'].min()
    max_date = df['end_date'].max()
    date_range = pd.date_range(start=min_date, end=max_date, freq='MS')  # Monthly
    
    # Count tasks by status and date
    status_counts = {}
    for status in df['status'].unique():
        status_counts[status] = []
        
    # For each month, count tasks that should be complete by that time
    for date in date_range:
        for status in status_counts.keys():
            count = len(df[(df['end_date'] <= date) & (df['status'] == status)])
            status_counts[status].append(count)
    
    # Create a stacked area chart
    p = figure(
        title="Task Completion Over Time",
        x_axis_type="datetime",
        width=1000,
        height=500,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Customize appearance
    p.title.text_font_size = '16pt'
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Number of Tasks"
    p.grid.grid_line_alpha = 0.3
    
    # Define colors for different statuses
    colors = {
        'Complete': '#43a047',
        'In Progress': '#ff9800',
        'Planned': '#4a89ff',
        'Not Started': '#9e9e9e',
        'On Hold': '#9c27b0',
        'Delayed': '#e53935'
    }
    
    # Sort statuses for stacking
    sorted_statuses = ['Complete', 'In Progress', 'Planned', 'Not Started', 'On Hold', 'Delayed']
    sorted_statuses = [s for s in sorted_statuses if s in status_counts]
    
    # Add other statuses that might not be in our predefined list
    for status in status_counts.keys():
        if status not in sorted_statuses:
            sorted_statuses.append(status)
    
    # Create a combined data source for all statuses
    source_data = {'x': list(date_range)}
    
    # Add each status as a column
    for status in sorted_statuses:
        if status in status_counts:
            source_data[status] = status_counts[status]
    
    source = ColumnDataSource(data=source_data)
    
    # Create stacked areas
    renderers = []
    bottom = None
    
    for status in sorted_statuses:
        if status not in status_counts:
            continue
            
        color = colors.get(status, '#999999')
        
        if bottom is None:
            # First area starts from zero
            renderer = p.varea(x='x', y1=0, y2=status, source=source, color=color, alpha=0.8, legend_label=status)
            bottom = status
        else:
            # Create a new column that is the sum of this status and all below it
            sum_column = f"{status}_sum"
            source.data[sum_column] = [a + b for a, b in zip(source.data[status], source.data[bottom])]
            
            # Stack this area on top of the previous sum
            renderer = p.varea(x='x', y1=bottom, y2=sum_column, source=source, color=color, alpha=0.8, legend_label=status)
            bottom = sum_column
        
        renderers.append(renderer)
    
    # Add hover tool
    hover = HoverTool(tooltips=[
        ("Date", "@x{%F}"),
        ("Tasks", "@$name")
    ], formatters={"@x": "datetime"})
    p.add_tools(hover)
    
    # Configure legend
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    
    # Add today marker
    today = datetime.now()
    today_line = Span(location=today, dimension='height', line_color='red', line_dash='dashed', line_width=2)
    p.add_layout(today_line)
    
    today_label = Label(x=today, y=0, text="Today", text_color='red', text_font_style='bold')
    p.add_layout(today_label)
    
    # Create a table with task details
    columns = [
        TableColumn(field="id", title="ID"),
        TableColumn(field="name", title="Task"),
        TableColumn(field="entity_type", title="Type"),
        TableColumn(field="entity_name", title="Entity"),
        TableColumn(field="start", title="Start Date"),
        TableColumn(field="end", title="End Date"),
        TableColumn(field="status", title="Status"),
        TableColumn(field="float", title="Floating"),
        TableColumn(field="additionalDetails", title="Details")
    ]
    
    source = ColumnDataSource(df)
    data_table = DataTable(source=source, columns=columns, width=1000, height=300)
    
    # Create layout
    layout_obj = column(p, data_table)
    
    # Save the visualization
    save(layout_obj)

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
    
    # Extract real data from the roadmap
    # Count tasks by category and status
    categories = {
        "Design Tasks": {"total": 0, "complete": 0},
        "Manufacturing Tasks": {"total": 0, "complete": 0},
        "Testing Tasks": {"total": 0, "complete": 0},
        "Qualification Tasks": {"total": 0, "complete": 0},
        "Documentation Tasks": {"total": 0, "complete": 0}
    }
    
    # Process all products
    for product in data.get('products', []):
        # Process roadmap tasks
        for task in product.get('roadmap', []):
            lane = task.get('lane', 'Other')
            status = task.get('status', '')
            
            if lane == 'Design':
                categories["Design Tasks"]["total"] += 1
                if status == 'Complete':
                    categories["Design Tasks"]["complete"] += 1
            elif lane == 'Manufacturing':
                categories["Manufacturing Tasks"]["total"] += 1
                if status == 'Complete':
                    categories["Manufacturing Tasks"]["complete"] += 1
            elif lane in ['Testing', 'Test']:
                categories["Testing Tasks"]["total"] += 1
                if status == 'Complete':
                    categories["Testing Tasks"]["complete"] += 1
            elif lane in ['Qualification', 'Quality']:
                categories["Qualification Tasks"]["total"] += 1
                if status == 'Complete':
                    categories["Qualification Tasks"]["complete"] += 1
        
        # Process design tools
        for tool in product.get('designTools', []):
            if isinstance(tool, dict):
                categories["Design Tasks"]["total"] += 1
                if tool.get('status') == 'Complete':
                    categories["Design Tasks"]["complete"] += 1
        
        # Process documentation
        for doc in product.get('documentation', []):
            if isinstance(doc, dict):
                categories["Documentation Tasks"]["total"] += 1
                if doc.get('status') == 'Complete':
                    categories["Documentation Tasks"]["complete"] += 1
        
        # Process special NDT (counts as testing)
        for ndt in product.get('specialNDT', []):
            if isinstance(ndt, dict):
                categories["Testing Tasks"]["total"] += 1
                if ndt.get('status') == 'Complete':
                    categories["Testing Tasks"]["complete"] += 1
        
        # Process part acceptance (counts as qualification)
        for acceptance in product.get('partAcceptance', []):
            if isinstance(acceptance, dict):
                categories["Qualification Tasks"]["total"] += 1
                if acceptance.get('status') == 'Complete':
                    categories["Qualification Tasks"]["complete"] += 1
    
    # Process material systems
    for material in data.get('materialSystems', []):
        for task in material.get('roadmap', []):
            # Assume material tasks are testing/qualification
            categories["Testing Tasks"]["total"] += 1
            if task.get('status') == 'Complete':
                categories["Testing Tasks"]["complete"] += 1
    
    # Calculate percentages
    category_names = list(categories.keys())
    planned = [100] * len(category_names)  # 100% is always the plan
    
    # Calculate actual percentages
    actual = []
    for category in category_names:
        if categories[category]["total"] > 0:
            completion_percentage = (categories[category]["complete"] / categories[category]["total"]) * 100
            actual.append(round(completion_percentage, 1))
        else:
            actual.append(0)
    
    # Create a comparison bar chart
    p = figure(
        title="Planned vs. Actual Progress",
        x_range=category_names,
        width=800,
        height=400,
        toolbar_location="right",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Create data sources
    source_planned = ColumnDataSource(data=dict(
        x=category_names,
        y=planned,
        desc=["Planned Progress"] * len(category_names)
    ))
    
    source_actual = ColumnDataSource(data=dict(
        x=category_names,
        y=actual,
        desc=["Actual Progress"] * len(category_names)
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
        'Category': category_names,
        'Planned': planned,
        'Actual': actual,
        'Difference': [a - p for a, p in zip(actual, planned)],
        'Total Tasks': [categories[cat]["total"] for cat in category_names],
        'Completed Tasks': [categories[cat]["complete"] for cat in category_names]
    }
    
    summary_source = ColumnDataSource(data=summary_data)
    
    summary_columns = [
        TableColumn(field="Category", title="Category"),
        TableColumn(field="Total Tasks", title="Total Tasks"),
        TableColumn(field="Completed Tasks", title="Completed"),
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
        <p>The data is based on the completion status of tasks in the roadmap.</p>
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