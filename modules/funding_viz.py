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
    <div style="margin-bottom: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
        <h2>Funding Opportunity Details: {funding_name}</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>ID:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{funding_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Type:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{funding_type}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Source:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{funding_source}</td>
            </tr>
    """
    
    # Add dates if available
    if 'startDate' in funding:
        funding_info += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Start Date:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{funding['startDate']}</td>
        </tr>
        """
    elif 'closeDate' in funding:
        funding_info += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Close Date:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{funding['closeDate']}</td>
        </tr>
        """
    
    # Add amount if available
    if 'amount' in funding:
        funding_info += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Amount:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">${funding['amount']:,}</td>
        </tr>
        """
    elif 'fundingAmount' in funding:
        try:
            amount = int(funding['fundingAmount'])
            funding_info += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Amount:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">${amount:,}</td>
            </tr>
            """
        except (ValueError, TypeError):
            funding_info += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Amount:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{funding['fundingAmount']}</td>
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
        
        # Create funding list section
        funding_list = "<div style='margin-top: 20px;'><h2>All Funding Opportunities</h2><ul>"
        for funding in sorted(data['fundingOpportunities'], key=lambda x: x.get('name', x.get('announcementName', ''))):
            funding_name = funding.get('name', funding.get('announcementName', 'Unknown'))
            funding_id = funding['id']
            funding_list += f"<li><a href='funding_{funding_id}.html'>{funding_name} ({funding_id})</a>"
            
            # Add type and amount if available
            funding_details = []
            funding_type = funding.get('type', funding.get('pursuitType', None))
            if funding_type:
                funding_details.append(f"Type: {funding_type}")
            
            funding_amount = None
            if 'amount' in funding:
                funding_amount = funding['amount']
            elif 'fundingAmount' in funding:
                try:
                    funding_amount = int(funding['fundingAmount'])
                except (ValueError, TypeError):
                    funding_amount = funding['fundingAmount']
            
            if funding_amount is not None:
                if isinstance(funding_amount, (int, float)):
                    funding_details.append(f"Amount: ${funding_amount:,}")
                else:
                    funding_details.append(f"Amount: {funding_amount}")
            
            # Add pursuit count if available
            if 'pursuits' in funding and funding['pursuits']:
                pursuit_count = len(funding['pursuits'])
                funding_details.append(f"Pursuits: {pursuit_count}")
            
            if funding_details:
                funding_list += f" - {', '.join(funding_details)}"
            
            funding_list += "</li>"
        funding_list += "</ul></div>"
        
        # Create header
        header = """
        <div style="margin-bottom: 20px;">
            <h1>Funding Opportunities Summary</h1>
            <p>This page provides an overview of all funding opportunities and their distributions.</p>
            <p><a href="../index.html">Back to Dashboard</a> | <a href="pursuits_summary.html">View All Pursuits</a></p>
        </div>
        """
        
        # Combine all elements
        header_div = Div(text=header, width=1200)
        funding_list_div = Div(text=funding_list, width=1200)
        
        # Create layout
        layout_obj = layout([
            [header_div],
            [p1, p2],
            [funding_list_div]
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
    """Generate distribution charts for funding opportunities"""
    if 'fundingOpportunities' in data:
        # Create a figure for funding amount by type
        funding_by_type = {}
        
        for funding in data['fundingOpportunities']:
            funding_type = funding.get('type', funding.get('pursuitType', 'Unknown'))
            
            # Get amount from either 'amount' or 'fundingAmount' field
            amount = 0
            if 'amount' in funding:
                amount = funding['amount']
            elif 'fundingAmount' in funding:
                try:
                    amount = int(funding['fundingAmount'])
                except (ValueError, TypeError):
                    try:
                        # Try to extract numeric value if it's a string like "$100,000"
                        amount_str = funding['fundingAmount'].replace('$', '').replace(',', '')
                        amount = int(amount_str)
                    except (ValueError, TypeError, AttributeError):
                        amount = 0
            
            if funding_type not in funding_by_type:
                funding_by_type[funding_type] = 0
            
            funding_by_type[funding_type] += amount
        
        if funding_by_type:
            # Sort by amount
            sorted_types = sorted(funding_by_type.items(), key=lambda x: x[1], reverse=True)
            types = [t[0] for t in sorted_types]
            amounts = [t[1] for t in sorted_types]
            
            # Create a figure for funding amount by type
            p = figure(
                title="Total Funding Amount by Type",
                x_range=types,
                width=800,
                height=400,
                toolbar_location="above",
                tools="pan,wheel_zoom,box_zoom,reset,save",
            )
            
            # Add bars
            source = ColumnDataSource(data=dict(
                types=types,
                amounts=amounts,
                formatted_amounts=[f"${amount:,}" for amount in amounts],
                colors=[Category10[10][i % 10] for i in range(len(types))]
            ))
            
            p.vbar(
                x='types',
                top='amounts',
                width=0.7,
                source=source,
                line_color="white",
                fill_color='colors',
                alpha=0.8
            )
            
            # Customize appearance
            p.title.text_font_size = '14pt'
            p.xaxis.axis_label = "Funding Type"
            p.yaxis.axis_label = "Total Amount ($)"
            p.xgrid.grid_line_color = None
            p.xaxis.major_label_orientation = 45
            
            # Add hover tool
            hover = HoverTool()
            hover.tooltips = [
                ("Type", "@types"),
                ("Amount", "@formatted_amounts")
            ]
            p.add_tools(hover)
            
            # Output to file
            output_file(os.path.join(funding_dir, "funding_amount_by_type.html"))
            save(p)
        
        # Create a timeline of all funding opportunities
        funding_timeline = []
        
        for funding in data['fundingOpportunities']:
            start_date = None
            end_date = None
            
            # Try to get start date
            if 'startDate' in funding:
                try:
                    start_date = datetime.strptime(funding['startDate'], "%Y-%m-%d")
                except (ValueError, TypeError):
                    pass
            
            # Try to get end date from either endDate or closeDate
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
            
            # If we have at least one date, add to timeline
            if start_date or end_date:
                # If we only have one date, use it for both start and end
                if start_date and not end_date:
                    end_date = start_date + timedelta(days=90)  # Default to 3 months duration
                elif end_date and not start_date:
                    start_date = end_date - timedelta(days=90)  # Default to 3 months duration
                
                funding_name = funding.get('name', funding.get('announcementName', 'Unknown'))
                funding_type = funding.get('type', funding.get('pursuitType', 'Unknown'))
                funding_source = funding.get('source', funding.get('customer', 'Unknown'))
                
                # Get amount
                amount = 0
                if 'amount' in funding:
                    amount = funding['amount']
                elif 'fundingAmount' in funding:
                    try:
                        amount = int(funding['fundingAmount'])
                    except (ValueError, TypeError):
                        try:
                            # Try to extract numeric value if it's a string like "$100,000"
                            amount_str = funding['fundingAmount'].replace('$', '').replace(',', '')
                            amount = int(amount_str)
                        except (ValueError, TypeError, AttributeError):
                            amount = 0
                
                funding_timeline.append({
                    'id': funding['id'],
                    'name': funding_name,
                    'type': funding_type,
                    'source': funding_source,
                    'amount': amount,
                    'start_date': start_date,
                    'end_date': end_date
                })
        
        if funding_timeline:
            # Sort by start date
            funding_timeline.sort(key=lambda x: x['start_date'])
            
            # Create a figure for the funding timeline
            p = figure(
                title="Funding Opportunities Timeline",
                x_axis_type="datetime",
                width=1200,
                height=400,
                toolbar_location="above",
                tools="pan,wheel_zoom,box_zoom,reset,save",
            )
            
            # Customize appearance
            p.title.text_font_size = '14pt'
            p.xaxis.axis_label = "Timeline"
            p.yaxis.axis_label = ""
            p.grid.grid_line_alpha = 0.3
            p.background_fill_color = "#f8f9fa"
            
            # Process funding opportunities
            y_pos = 0
            all_dates = []
            
            # Create a color map for funding types
            funding_types = list(set(item['type'] for item in funding_timeline))
            color_map = {}
            for i, funding_type in enumerate(funding_types):
                color_map[funding_type] = Category10[10][i % 10]
            
            # Add funding bars
            for item in funding_timeline:
                y_pos -= 1
                all_dates.extend([item['start_date'], item['end_date']])
                
                # Create data source for the funding bar
                bar_source = ColumnDataSource(data=dict(
                    y=[y_pos],
                    left=[item['start_date']],
                    right=[item['end_date']],
                    name=[item['name']],
                    id=[item['id']],
                    type=[item['type']],
                    source=[item['source']],
                    amount=[f"${item['amount']:,}" if item['amount'] else 'N/A'],
                    start=[item['start_date']],
                    end=[item['end_date']]
                ))
                
                # Add funding bar
                color = color_map.get(item['type'], '#95a5a6')
                p.hbar(y='y', left='left', right='right', height=0.6, 
                       color=color, alpha=0.8, source=bar_source)
                
                # Create data source for the label
                label_source = ColumnDataSource(data=dict(
                    x=[item['start_date']],
                    y=[y_pos],
                    text=[item['name']]
                ))
                
                # Add label with offset to prevent overlap
                p.text(x='x', y='y', text='text', source=label_source,
                       text_font_size="9pt", text_baseline="middle", 
                       x_offset=5, text_align="left")
            
            # Add hover tool
            hover = HoverTool()
            hover.tooltips = [
                ("Name", "@name"),
                ("ID", "@id"),
                ("Type", "@type"),
                ("Source", "@source"),
                ("Amount", "@amount"),
                ("Start", "@start{%F}"),
                ("End", "@end{%F}")
            ]
            hover.formatters = {
                "@start": "datetime",
                "@end": "datetime"
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
            
            # Add legend
            legend_items = []
            for funding_type, color in color_map.items():
                legend_items.append((funding_type, [p.hbar(y=0, left=0, right=0, height=0, color=color)]))
            
            legend = Legend(items=legend_items, location="top_right")
            p.add_layout(legend)
            
            # Output to file
            output_file(os.path.join(funding_dir, "funding_timeline.html"))
            save(p) 