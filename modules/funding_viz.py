import os
from datetime import datetime, timedelta
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Range1d, Span, Legend, LegendItem, Div, Tabs, Panel
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import Category10, Spectral6
from bokeh.transform import factor_cmap
import matplotlib.pyplot as plt
import numpy as np
from .pursuit_viz import generate_pursuit_section, generate_pursuits_summary

def generate_funding_visualizations(data, output_dir):
    """Generate visualizations for funding opportunities"""
    print("Generating funding opportunity visualizations...")
    
    # Create funding directory if it doesn't exist
    funding_dir = os.path.join(output_dir, "funding")
    if not os.path.exists(funding_dir):
        os.makedirs(funding_dir)
    
    # Generate individual funding opportunity pages
    if 'fundingOpportunities' in data:
        for funding in data['fundingOpportunities']:
            generate_funding_page(funding, data, funding_dir)
    
    # Generate funding summary page
    generate_funding_summary(data, funding_dir)
    
    # Generate funding distribution charts
    generate_funding_distribution_charts(data, funding_dir)
    
    # Generate pursuits summary page
    if 'fundingOpportunities' in data:
        generate_pursuits_summary(data['fundingOpportunities'], data, funding_dir)
    
    print(f"Funding opportunity visualizations generated in '{funding_dir}'")

def generate_funding_page(funding, data, funding_dir):
    """Generate a detailed page for a single funding opportunity"""
    funding_id = funding['id']
    
    # Map field names from the actual data structure to the expected structure
    funding_name = funding.get('name', funding.get('announcementName', 'Unknown'))
    funding_type = funding.get('type', funding.get('pursuitType', 'N/A'))
    funding_source = funding.get('source', funding.get('customer', 'N/A'))
    funding_amount = funding.get('amount', funding.get('fundingAmount', 'N/A'))
    
    # Create funding info section
    funding_info = f"""
    <div style="margin-bottom: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Funding Opportunity Details: {funding_name}</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; width: 30%;"><strong>ID:</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">{funding_id}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Type:</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">{funding_type}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Source:</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">{funding_source}</td>
            </tr>
    """
    
    # Add dates if available
    if 'startDate' in funding:
        funding_info += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Start Date:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">{funding['startDate']}</td>
        </tr>
        """
    elif 'closeDate' in funding:
        funding_info += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Close Date:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">{funding['closeDate']}</td>
        </tr>
        """
    
    # Add amount if available
    if 'amount' in funding:
        funding_info += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Amount:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">${funding['amount']:,}</td>
        </tr>
        """
    elif 'fundingAmount' in funding:
        try:
            amount = int(funding['fundingAmount'])
            funding_info += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Amount:</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">${amount:,}</td>
            </tr>
            """
        except (ValueError, TypeError):
            funding_info += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Amount:</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">{funding['fundingAmount']}</td>
            </tr>
            """
    
    # Add cost share if available
    if 'costSharePercentage' in funding:
        funding_info += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Cost Share:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">{funding['costSharePercentage']}</td>
        </tr>
        """
    
    # Add solicitation number if available
    if 'solicitationNumber' in funding:
        funding_info += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Solicitation Number:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">{funding['solicitationNumber']}</td>
        </tr>
        """
    
    # Add status if available
    if 'status' in funding:
        status_value = funding['status']
        status_color = "#4a89ff"  # Default blue
        if status_value == "Awarded":
            status_color = "#43a047"  # Green
        elif status_value == "Closed":
            status_color = "#e53935"  # Red
        elif status_value == "Pursuing":
            status_color = "#ff9800"  # Orange
        elif status_value == "Reshaping":
            status_color = "#9c27b0"  # Purple
            
        funding_info += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Status:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">
                <span style="display: inline-block; padding: 4px 8px; background-color: {status_color}; color: white; border-radius: 4px;">{status_value}</span>
            </td>
        </tr>
        """
    
    # Add period of performance if available
    if 'periodOfPerformance' in funding and funding['periodOfPerformance']:
        funding_info += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>Period of Performance:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">{funding['periodOfPerformance']}</td>
        </tr>
        """
    
    # Close the table
    funding_info += """
        </table>
    </div>
    """
    
    # Add description section if available
    description_section = ""
    if 'description' in funding and funding['description']:
        description_section = f"""
        <div style="margin-top: 20px; padding: 15px; background-color: #e8f4f8; border-radius: 5px;">
            <h3>Description</h3>
            <p>{funding['description']}</p>
        </div>
        """
    
    # Add timeline visualization if dates are available
    timeline_section = ""
    start_date = None
    end_date = None
    
    # Try to get start and end dates from various fields
    if 'startDate' in funding:
        try:
            start_date = datetime.strptime(funding['startDate'], "%Y-%m-%d")
        except (ValueError, TypeError):
            pass
    
    if 'endDate' in funding:
        try:
            end_date = datetime.strptime(funding['endDate'], "%Y-%m-%d")
        except (ValueError, TypeError):
            pass
    elif 'closeDate' in funding:
        try:
            end_date = datetime.strptime(funding['closeDate'], "%Y-%m-%d")
        except (ValueError, TypeError):
            pass
    
    # If we have at least one date, create a timeline
    if start_date or end_date:
        # If we only have one date, use it for both start and end
        if start_date and not end_date:
            end_date = start_date + timedelta(days=90)  # Default to 3 months duration
        elif end_date and not start_date:
            start_date = end_date - timedelta(days=90)  # Default to 3 months duration
        
        # Create a figure for the funding timeline
        p = figure(
            title=f"Timeline for {funding_name}",
            x_axis_type="datetime",
            width=1000,
            height=200,
            toolbar_location="above",
            tools="pan,wheel_zoom,box_zoom,reset,save",
        )
        
        # Customize appearance
        p.title.text_font_size = '14pt'
        p.xaxis.axis_label = "Timeline"
        p.yaxis.axis_label = ""
        p.grid.grid_line_alpha = 0.3
        p.background_fill_color = "#f8f9fa"
        
        # Add funding period bar
        source = ColumnDataSource(data=dict(
            y=[0],
            left=[start_date],
            right=[end_date],
            name=[funding_name],
            start=[start_date],
            end=[end_date],
            type=[funding_type],
            amount=[f"${funding_amount}" if funding_amount != 'N/A' else 'N/A']
        ))
        
        p.hbar(y='y', left='left', right='right', height=0.4, 
               color=Category10[10][0], alpha=0.8, source=source)
        
        # Add hover tool
        hover = HoverTool()
        hover.tooltips = [
            ("Name", "@name"),
            ("Type", "@type"),
            ("Start", "@start{%F}"),
            ("End", "@end{%F}"),
            ("Amount", "@amount")
        ]
        hover.formatters = {
            "@start": "datetime",
            "@end": "datetime"
        }
        p.add_tools(hover)
        
        # Set y-range
        p.y_range = Range1d(-0.5, 0.5)
        
        # Set x-range with padding (3 months before and after)
        min_date = start_date - timedelta(days=90)
        max_date = end_date + timedelta(days=90)
        p.x_range.start = min_date
        p.x_range.end = max_date
        
        # Output to file
        output_file(os.path.join(funding_dir, f"funding_timeline_{funding_id}.html"))
        save(p)
        
        timeline_section = f"""
        <div style="margin-top: 20px;">
            <h3>Funding Timeline</h3>
            <p><a href="funding_timeline_{funding_id}.html" target="_blank">View detailed timeline</a></p>
            <iframe src="funding_timeline_{funding_id}.html" width="100%" height="250px" frameborder="0"></iframe>
        </div>
        """
    
    # Find related tasks that use this funding
    related_tasks = []
    
    # Check program tasks
    for program in data.get('programs', []):
        if 'roadmap' in program and 'tasks' in program['roadmap']:
            for task in program['roadmap']['tasks']:
                if 'fundingID' in task and task['fundingID'] == funding_id:
                    related_tasks.append({
                        'task': task['task'],
                        'program': program['name'],
                        'program_id': program['id'],
                        'start': task.get('start', 'N/A'),
                        'end': task.get('end', 'N/A'),
                        'status': task.get('status', 'N/A'),
                        'type': 'Program Task'
                    })
    
    # Check product tasks
    for product in data.get('products', []):
        if 'roadmap' in product and 'tasks' in product['roadmap']:
            for task in product['roadmap']['tasks']:
                if 'fundingID' in task and task['fundingID'] == funding_id:
                    related_tasks.append({
                        'task': task['task'],
                        'product': product['name'],
                        'product_id': product['id'],
                        'start': task.get('start', 'N/A'),
                        'end': task.get('end', 'N/A'),
                        'status': task.get('status', 'N/A'),
                        'type': 'Product Task'
                    })
    
    # Check supplier tasks
    for supplier in data.get('printingSuppliers', []):
        if 'supplierRoadmap' in supplier and 'tasks' in supplier['supplierRoadmap']:
            for task in supplier['supplierRoadmap']['tasks']:
                if 'fundingID' in task and task['fundingID'] == funding_id:
                    related_tasks.append({
                        'task': task['task'],
                        'supplier': supplier['name'],
                        'supplier_id': supplier['id'],
                        'start': task.get('start', 'N/A'),
                        'end': task.get('end', 'N/A'),
                        'status': task.get('status', 'N/A'),
                        'type': 'Supplier Task'
                    })
    
    # Add related tasks section
    tasks_section = """
    <div style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 5px;">
        <h3>Related Tasks</h3>
    """
    
    if related_tasks:
        tasks_section += """
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #e0e0e0;">
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Task</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Type</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Related To</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Start Date</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">End Date</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Status</th>
            </tr>
        """
        
        for task in related_tasks:
            # Determine the related entity link
            if 'program' in task:
                related_link = f"<a href='../programs/program_{task['program_id']}.html'>{task['program']}</a>"
            elif 'product' in task:
                related_link = f"<a href='../products/product_{task['product_id']}.html'>{task['product']}</a>"
            elif 'supplier' in task:
                related_link = f"<a href='../suppliers/supplier_{task['supplier_id']}.html'>{task['supplier']}</a>"
            else:
                related_link = "N/A"
            
            # Determine status color
            status_colors = {
                'Complete': '#43a047',
                'In Progress': '#ff9800',
                'Planned': '#4a89ff'
            }
            status_color = status_colors.get(task['status'], '#95a5a6')
            
            tasks_section += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{task['task']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{task['type']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{related_link}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{task['start']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{task['end']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; background-color: {status_color}; color: white;">{task['status']}</td>
            </tr>
            """
        
        tasks_section += "</table>"
        
        # Create a visualization of tasks by status
        status_counts = {}
        for task in related_tasks:
            status = task['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            # Create a figure for task status distribution
            p = figure(
                title="Tasks by Status",
                x_range=list(status_counts.keys()),
                width=400,
                height=300,
                toolbar_location=None,
                tools=""
            )
            
            # Add bars
            status_colors = {
                'Complete': '#43a047',
                'In Progress': '#ff9800',
                'Planned': '#4a89ff'
            }
            
            colors = [status_colors.get(status, '#95a5a6') for status in status_counts.keys()]
            
            p.vbar(
                x=list(status_counts.keys()),
                top=list(status_counts.values()),
                width=0.5,
                color=colors,
                alpha=0.8
            )
            
            # Customize appearance
            p.title.text_font_size = '12pt'
            p.xaxis.axis_label = "Status"
            p.yaxis.axis_label = "Number of Tasks"
            p.xgrid.grid_line_color = None
            
            # Output to file
            output_file(os.path.join(funding_dir, f"funding_tasks_status_{funding_id}.html"))
            save(p)
            
            tasks_section += f"""
            <div style="margin-top: 20px;">
                <h4>Tasks by Status</h4>
                <iframe src="funding_tasks_status_{funding_id}.html" width="100%" height="350px" frameborder="0"></iframe>
            </div>
            """
    else:
        tasks_section += "<p>No related tasks found for this funding opportunity.</p>"
    
    tasks_section += """
    </div>
    """
    
    # Add pursuits section if available
    pursuits_section = ""
    if 'pursuits' in funding and funding['pursuits']:
        pursuits_section = f"""
        <div style="margin-top: 20px;">
            <h2>Pursuits for this Funding Opportunity</h2>
            <p>This section shows the pursuits associated with this funding opportunity.</p>
        """
        
        for pursuit in funding['pursuits']:
            pursuits_section += generate_pursuit_section(pursuit, data, funding_dir, funding_id)
        
        pursuits_section += """
        </div>
        """
    
    # Create header
    header = f"""
    <div style="margin-bottom: 20px;">
        <h1>Funding Opportunity: {funding_name}</h1>
        <p><a href="../index.html">Back to Dashboard</a> | <a href="funding_summary.html">Back to Funding Summary</a> | <a href="pursuits_summary.html">View All Pursuits</a></p>
    </div>
    """
    
    # Combine all elements
    full_content = header + funding_info + description_section + timeline_section + pursuits_section + tasks_section
    
    # Create the HTML page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Funding: {funding_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2, h3, h4 {{ color: #0066cc; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            {full_content}
        </div>
    </body>
    </html>
    """
    
    # Write to file
    with open(os.path.join(funding_dir, f"funding_{funding_id}.html"), 'w') as f:
        f.write(html_content)

def generate_funding_summary(data, funding_dir):
    """Generate a summary page for all funding opportunities"""
    from datetime import datetime
    
    # Create a figure for funding distribution by type
    if 'fundingOpportunities' in data:
        funding_types = {}
        for funding in data['fundingOpportunities']:
            funding_type = funding.get('type', funding.get('pursuitType', 'Unknown'))
            funding_types[funding_type] = funding_types.get(funding_type, 0) + 1
        
        # Create a figure for funding type distribution
        p1 = figure(
            title="Funding Opportunities by Type",
            x_range=list(funding_types.keys()),
            width=600,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        # Add bars
        source1 = ColumnDataSource(data=dict(
            types=list(funding_types.keys()),
            counts=list(funding_types.values()),
            colors=[Category10[10][i % 10] for i in range(len(funding_types))]
        ))
        
        p1.vbar(
            x='types',
            top='counts',
            width=0.5,
            source=source1,
            fill_color='colors',
            alpha=0.8
        )
        
        # Customize appearance
        p1.title.text_font_size = '14pt'
        p1.xaxis.axis_label = "Funding Type"
        p1.yaxis.axis_label = "Number of Opportunities"
        p1.xgrid.grid_line_color = None
        p1.xaxis.major_label_orientation = 45
        
        # Create a figure for funding distribution by status
        funding_statuses = {}
        for funding in data['fundingOpportunities']:
            funding_status = funding.get('status', 'Unknown')
            funding_statuses[funding_status] = funding_statuses.get(funding_status, 0) + 1
        
        # Create a figure for funding status distribution
        p3 = figure(
            title="Funding Opportunities by Status",
            x_range=list(funding_statuses.keys()),
            width=600,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        # Define status colors
        status_colors = {
            "Considering": "#4a89ff",  # Blue
            "Pursuing": "#ff9800",     # Orange
            "Closed": "#e53935",       # Red
            "Awarded": "#43a047",      # Green
            "Reshaping": "#9c27b0",    # Purple
            "Unknown": "#9e9e9e"       # Gray
        }
        
        # Add bars
        source3 = ColumnDataSource(data=dict(
            statuses=list(funding_statuses.keys()),
            counts=list(funding_statuses.values()),
            colors=[status_colors.get(status, "#9e9e9e") for status in funding_statuses.keys()]
        ))
        
        p3.vbar(
            x='statuses',
            top='counts',
            width=0.5,
            source=source3,
            fill_color='colors',
            alpha=0.8
        )
        
        # Customize appearance
        p3.title.text_font_size = '14pt'
        p3.xaxis.axis_label = "Status"
        p3.yaxis.axis_label = "Number of Opportunities"
        p3.xgrid.grid_line_color = None
        p3.xaxis.major_label_orientation = 45
        
        # Create a figure for funding distribution by source
        funding_sources = {}
        for funding in data['fundingOpportunities']:
            funding_source = funding.get('source', funding.get('customer', 'Unknown'))
            funding_sources[funding_source] = funding_sources.get(funding_source, 0) + 1
        
        # Create a figure for funding source distribution
        p2 = figure(
            title="Funding Opportunities by Source",
            x_range=list(funding_sources.keys()),
            width=600,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        # Add bars
        source2 = ColumnDataSource(data=dict(
            sources=list(funding_sources.keys()),
            counts=list(funding_sources.values()),
            colors=[Category10[10][(i+2) % 10] for i in range(len(funding_sources))]
        ))
        
        p2.vbar(
            x='sources',
            top='counts',
            width=0.5,
            source=source2,
            fill_color='colors',
            alpha=0.8
        )
        
        # Customize appearance
        p2.title.text_font_size = '14pt'
        p2.xaxis.axis_label = "Funding Source"
        p2.yaxis.axis_label = "Number of Opportunities"
        p2.xgrid.grid_line_color = None
        p2.xaxis.major_label_orientation = 45
        
        # Get current date for filtering upcoming opportunities
        current_date = datetime.now()
        
        # Separate upcoming and past opportunities
        upcoming_opportunities = []
        all_opportunities = []
        
        for funding in data['fundingOpportunities']:
            funding_name = funding.get('name', funding.get('announcementName', 'Unknown'))
            funding_id = funding['id']
            funding_type = funding.get('type', funding.get('pursuitType', 'Unknown'))
            
            # Get close date if available
            close_date_str = funding.get('closeDate', '')
            close_date = None
            is_upcoming = True
            
            if close_date_str:
                try:
                    close_date = datetime.strptime(close_date_str, "%Y-%m-%d")
                    is_upcoming = close_date > current_date
                except (ValueError, TypeError):
                    pass
            
            # Get funding amount
            funding_amount = None
            if 'amount' in funding:
                funding_amount = funding['amount']
            elif 'fundingAmount' in funding:
                try:
                    if funding['fundingAmount'] and funding['fundingAmount'].strip():
                        amount_str = funding['fundingAmount'].replace('$', '').replace(',', '')
                        funding_amount = int(amount_str)
                except (ValueError, TypeError, AttributeError):
                    funding_amount = funding['fundingAmount']
            
            # Format amount for display
            amount_display = 'N/A'
            if funding_amount is not None:
                if isinstance(funding_amount, (int, float)):
                    amount_display = f"${funding_amount:,}"
                else:
                    amount_display = funding_amount
            
            # Get cost share if available
            cost_share = funding.get('costSharePercentage', 'N/A')
            
            # Get status if available
            status = funding.get('status', 'N/A')
            
            # Get period of performance if available
            period_of_performance = funding.get('periodOfPerformance', 'N/A')
            
            # Get pursuit count
            pursuit_count = len(funding.get('pursuits', [])) if 'pursuits' in funding else 0
            
            # Create opportunity data
            opportunity_data = {
                'id': funding_id,
                'name': funding_name,
                'type': funding_type,
                'status': status,
                'close_date': close_date_str,
                'period_of_performance': period_of_performance,
                'amount': amount_display,
                'cost_share': cost_share,
                'pursuit_count': pursuit_count,
                'is_upcoming': is_upcoming
            }
            
            all_opportunities.append(opportunity_data)
            if is_upcoming:
                upcoming_opportunities.append(opportunity_data)
        
        # Sort opportunities by close date (if available)
        upcoming_opportunities.sort(key=lambda x: x['close_date'] if x['close_date'] else '9999-12-31')
        all_opportunities.sort(key=lambda x: x['close_date'] if x['close_date'] else '9999-12-31')
        
        # Create upcoming opportunities section
        upcoming_section = """
        <div style="margin-top: 30px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Upcoming Funding Opportunities</h2>
        """
        
        if upcoming_opportunities:
            upcoming_section += """
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <thead>
                        <tr style="background-color: #3498db; color: white;">
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Name</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Type</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Status</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Close Date</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Period of Performance</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Amount</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Cost Share</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Pursuits</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for i, opp in enumerate(upcoming_opportunities):
                row_class = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
                upcoming_section += f"""
                <tr style="{row_class}">
                    <td style="padding: 10px; border: 1px solid #ddd;"><a href="funding_{opp['id']}.html" style="color: #3498db; font-weight: bold;">{opp['name']}</a></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{opp['type']}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{opp['status']}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{opp['close_date']}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{opp['period_of_performance']}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{opp['amount']}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{opp['cost_share']}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{opp['pursuit_count']}</td>
                </tr>
                """
            
            upcoming_section += """
                    </tbody>
                </table>
            </div>
            """
        else:
            upcoming_section += """
            <p style="padding: 15px; background-color: #f8f9fa; border-left: 4px solid #3498db; margin: 20px 0;">
                No upcoming funding opportunities found.
            </p>
            """
        
        upcoming_section += "</div>"
        
        # Create all opportunities section
        all_opps_section = """
        <div style="margin-top: 40px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">All Funding Opportunities</h2>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <thead>
                        <tr style="background-color: #3498db; color: white;">
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Name</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Type</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Status</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Close Date</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Period of Performance</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Amount</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Cost Share</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Pursuits</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for i, opp in enumerate(all_opportunities):
            row_class = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
            status_style = "color: #27ae60; font-weight: bold;" if opp['is_upcoming'] else "color: #7f8c8d;"
            status_text = "Upcoming" if opp['is_upcoming'] else "Past"
            
            all_opps_section += f"""
            <tr style="{row_class}">
                <td style="padding: 10px; border: 1px solid #ddd;"><a href="funding_{opp['id']}.html" style="color: #3498db; font-weight: bold;">{opp['name']}</a></td>
                <td style="padding: 10px; border: 1px solid #ddd;">{opp['type']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{opp['status']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{opp['close_date']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{opp['period_of_performance']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{opp['amount']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{opp['cost_share']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{opp['pursuit_count']}</td>
                <td style="padding: 10px; border: 1px solid #ddd; {status_style}">{status_text}</td>
            </tr>
            """
        
        all_opps_section += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        # Create header
        header = """
        <div style="margin-bottom: 30px;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 15px;">Funding Opportunities Summary</h1>
            <p style="font-size: 16px; color: #555;">This page provides an overview of all funding opportunities and their distributions.</p>
            <p><a href="../index.html" style="color: #3498db; text-decoration: none; font-weight: bold;">Back to Dashboard</a> | <a href="pursuits_summary.html" style="color: #3498db; text-decoration: none; font-weight: bold;">View All Pursuits</a></p>
        </div>
        """
        
        # Combine all elements
        header_div = Div(text=header, width=1200)
        upcoming_div = Div(text=upcoming_section, width=1200)
        all_opps_div = Div(text=all_opps_section, width=1200)
        
        # Create layout
        layout_obj = layout([
            [header_div],
            [p1, p2, p3],
            [upcoming_div],
            [all_opps_div]
        ])
        
        # Output to file
        output_file(os.path.join(funding_dir, "funding_summary.html"))
        save(layout_obj)
    else:
        # Create a simple page if no funding opportunities
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Funding Opportunities Summary</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                h1 { color: #333; }
                a { color: #0066cc; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .container { max-width: 1200px; margin: 0 auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Funding Opportunities Summary</h1>
                <p>No funding opportunities found in the data.</p>
                <p><a href="../index.html">Back to Dashboard</a></p>
            </div>
        </body>
        </html>
        """
        
        # Write to file
        with open(os.path.join(funding_dir, "funding_summary.html"), 'w') as f:
            f.write(html_content)

def generate_funding_distribution_charts(data, funding_dir):
    """Generate charts showing the distribution of funding opportunities"""
    print("Generating funding distribution charts...")
    
    if 'fundingOpportunities' not in data or not data['fundingOpportunities']:
        return
    
    # Create a figure for funding distribution by type
    funding_types = {}
    for funding in data['fundingOpportunities']:
        funding_type = funding.get('type', funding.get('pursuitType', 'Unknown'))
        funding_types[funding_type] = funding_types.get(funding_type, 0) + 1
    
    # Create a figure for funding distribution by status
    funding_statuses = {}
    for funding in data['fundingOpportunities']:
        funding_status = funding.get('status', 'Unknown')
        funding_statuses[funding_status] = funding_statuses.get(funding_status, 0) + 1
    
    # Create a figure for funding distribution by source
    funding_sources = {}
    for funding in data['fundingOpportunities']:
        funding_source = funding.get('source', funding.get('customer', 'Unknown'))
        funding_sources[funding_source] = funding_sources.get(funding_source, 0) + 1
    
    # Create figures
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    
    # Plot funding types
    axs[0].bar(funding_types.keys(), funding_types.values(), color='skyblue')
    axs[0].set_title('Funding Opportunities by Type')
    axs[0].set_xlabel('Type')
    axs[0].set_ylabel('Count')
    axs[0].tick_params(axis='x', rotation=45)
    
    # Plot funding statuses
    status_colors = {
        "Considering": "#4a89ff",  # Blue
        "Pursuing": "#ff9800",     # Orange
        "Closed": "#e53935",       # Red
        "Awarded": "#43a047",      # Green
        "Reshaping": "#9c27b0",    # Purple
        "Unknown": "#9e9e9e"       # Gray
    }
    
    status_colors_list = [status_colors.get(status, "#9e9e9e") for status in funding_statuses.keys()]
    axs[1].bar(funding_statuses.keys(), funding_statuses.values(), color=status_colors_list)
    axs[1].set_title('Funding Opportunities by Status')
    axs[1].set_xlabel('Status')
    axs[1].set_ylabel('Count')
    axs[1].tick_params(axis='x', rotation=45)
    
    # Plot funding sources
    axs[2].bar(funding_sources.keys(), funding_sources.values(), color='lightgreen')
    axs[2].set_title('Funding Opportunities by Source')
    axs[2].set_xlabel('Source')
    axs[2].set_ylabel('Count')
    axs[2].tick_params(axis='x', rotation=45)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    chart_path = os.path.join(funding_dir, 'funding_distribution.png')
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    # Create HTML page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Funding Distribution</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Funding Distribution</h1>
            <p>This page shows the distribution of funding opportunities.</p>
            <p><a href="../index.html">Back to Dashboard</a></p>
            <div style="text-align: center; margin-top: 20px;">
                <img src="funding_distribution.png" alt="Funding Distribution Charts" style="max-width: 100%; border: 1px solid #ddd;">
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write to file
    with open(os.path.join(funding_dir, "funding_distribution.html"), 'w') as f:
        f.write(html_content) 