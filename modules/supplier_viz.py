import os
from datetime import datetime, timedelta
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Range1d, Span, Legend, LegendItem, Div, Tabs, Panel
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import Category10, Spectral6
from bokeh.transform import factor_cmap
import matplotlib.pyplot as plt
import numpy as np

def generate_supplier_visualizations(data, output_dir):
    """Generate visualizations for suppliers"""
    print("Generating supplier visualizations...")
    
    # Create suppliers directory if it doesn't exist
    supplier_dir = os.path.join(output_dir, "suppliers")
    if not os.path.exists(supplier_dir):
        os.makedirs(supplier_dir)
    
    # Generate individual supplier pages for printing suppliers
    if 'printingSuppliers' in data:
        for supplier in data['printingSuppliers']:
            generate_printing_supplier_page(supplier, data, supplier_dir)
    
    # Generate individual supplier pages for post-processing suppliers
    if 'postProcessingSuppliers' in data:
        for supplier in data['postProcessingSuppliers']:
            generate_postprocessing_supplier_page(supplier, data, supplier_dir)
    
    # Generate supplier summary page
    generate_supplier_summary(data, supplier_dir)
    
    # Generate supplier distribution charts
    generate_supplier_distribution_charts(data, supplier_dir)
    
    print(f"Supplier visualizations generated in '{supplier_dir}'")

def generate_printing_supplier_page(supplier, data, supplier_dir):
    """Generate a detailed page for a single printing supplier"""
    supplier_id = supplier['id']
    
    # Create a figure for the supplier roadmap if available
    roadmap_section = ""
    if 'supplierRoadmap' in supplier and 'tasks' in supplier['supplierRoadmap']:
        p = figure(
            title=f"Roadmap for {supplier['name']} ({supplier_id})",
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
        all_dates = []
        
        # Add roadmap tasks
        for task in supplier['supplierRoadmap']['tasks']:
            y_pos -= 1
            
            if not task.get('start') or not task.get('end'):
                continue
                
            start_date = datetime.strptime(task['start'], "%Y-%m-%d")
            end_date = datetime.strptime(task['end'], "%Y-%m-%d")
            all_dates.extend([start_date, end_date])
            
            # Add funding type if available
            funding = f" ({task.get('fundingType', '')})" if 'fundingType' in task else ""
            category = f" [{task.get('category', '')}]" if 'category' in task else ""
            task_name = f"{task['task']}{funding}{category}"
            
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
            color_map = {
                'Complete': '#43a047',
                'In Progress': '#ff9800',
                'Planned': '#4a89ff'
            }
            color = color_map.get(task['status'], '#95a5a6')
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
        
        # Output to file
        output_file(os.path.join(supplier_dir, f"supplier_roadmap_{supplier_id}.html"))
        save(p)
        
        roadmap_section = f"""
        <div style="margin-top: 20px;">
            <h3>Supplier Roadmap</h3>
            <p><a href="supplier_roadmap_{supplier_id}.html" target="_blank">View detailed roadmap</a></p>
        </div>
        """
    
    # Create supplier info section
    supplier_info = f"""
    <div style="margin-bottom: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
        <h2>Printing Supplier Details: {supplier['name']}</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>ID:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{supplier_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Supplier Number:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{supplier.get('supplierNumber', 'N/A')}</td>
            </tr>
    """
    
    # Add NDA status if available
    if 'ndaStatus' in supplier:
        nda_status = supplier['ndaStatus'].get('status', 'N/A')
        nda_date = supplier['ndaStatus'].get('date', 'N/A')
        supplier_info += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>NDA Status:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{nda_status} (Date: {nda_date})</td>
        </tr>
        """
    
    # Close the table
    supplier_info += """
        </table>
    </div>
    """
    
    # Add material systems section
    material_systems_section = """
    <div style="margin-top: 20px; padding: 15px; background-color: #e8f4f8; border-radius: 5px;">
        <h3>Material Systems and Printers</h3>
    """
    
    if 'materialSystems' in supplier:
        for material_entry in supplier['materialSystems']:
            material_id = material_entry.get('materialID')
            material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
            
            if material:
                material_systems_section += f"""
                <div style="margin-bottom: 15px; padding: 10px; background-color: #f5f5f5; border-radius: 3px;">
                    <h4><a href="../materials/material_{material_id}.html">{material['name']} ({material_id})</a></h4>
                    <p><strong>Printers:</strong></p>
                    <ul>
                """
                
                for printer in material_entry.get('printer', []):
                    if isinstance(printer, dict):
                        printer_name = printer.get('name', 'Unknown')
                        qual_status = printer.get('qualStatus', 'Unknown')
                        material_systems_section += f"<li>{printer_name} - Status: {qual_status}</li>"
                    else:
                        material_systems_section += f"<li>{printer}</li>"
                
                material_systems_section += """
                    </ul>
                </div>
                """
    else:
        material_systems_section += "<p>No material systems information available.</p>"
    
    material_systems_section += """
    </div>
    """
    
    # Add additional capabilities section
    capabilities_section = """
    <div style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 5px;">
        <h3>Additional Capabilities</h3>
    """
    
    if 'additionalCapabilities' in supplier and supplier['additionalCapabilities']:
        capabilities_section += "<ul>"
        for capability in supplier['additionalCapabilities']:
            capabilities_section += f"<li>{capability}</li>"
        capabilities_section += "</ul>"
    else:
        capabilities_section += "<p>No additional capabilities information available.</p>"
    
    capabilities_section += """
    </div>
    """
    
    # Add related products section
    products_section = """
    <div style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
        <h3>Related Products</h3>
    """
    
    # Find products that use materials from this supplier
    related_products = set()
    if 'materialSystems' in supplier:
        for material_entry in supplier['materialSystems']:
            material_id = material_entry.get('materialID')
            
            for product in data['products']:
                for product_material in product.get('materialSystems', []):
                    if isinstance(product_material, str) and product_material == material_id:
                        related_products.add(product['id'])
                    elif isinstance(product_material, dict) and product_material.get('materialID') == material_id:
                        related_products.add(product['id'])
    
    if related_products:
        products_section += "<ul>"
        for product_id in related_products:
            product = next((p for p in data['products'] if p['id'] == product_id), None)
            if product:
                products_section += f"<li><a href='../products/product_{product_id}.html'>{product['name']} ({product_id})</a></li>"
        products_section += "</ul>"
    else:
        products_section += "<p>No related products found.</p>"
    
    products_section += """
    </div>
    """
    
    # Create header
    header = f"""
    <div style="margin-bottom: 20px;">
        <h1>Printing Supplier: {supplier['name']}</h1>
        <p><a href="../index.html">Back to Dashboard</a> | <a href="supplier_summary.html">Back to Supplier Summary</a></p>
    </div>
    """
    
    # Combine all elements
    full_content = header + supplier_info + material_systems_section + capabilities_section + products_section + roadmap_section
    
    # Create the HTML page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Supplier: {supplier['name']}</title>
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
    with open(os.path.join(supplier_dir, f"supplier_{supplier_id}.html"), 'w') as f:
        f.write(html_content)

def generate_postprocessing_supplier_page(supplier, data, supplier_dir):
    """Generate a detailed page for a single post-processing supplier"""
    supplier_id = supplier['id']
    
    # Create supplier info section
    supplier_info = f"""
    <div style="margin-bottom: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
        <h2>Post-Processing Supplier Details: {supplier['name']}</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>ID:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{supplier_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Supplier Number:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{supplier.get('supplierNumber', 'N/A')}</td>
            </tr>
    """
    
    # Add NDA status if available
    if 'ndaStatus' in supplier:
        nda_status = supplier['ndaStatus'].get('status', 'N/A')
        nda_date = supplier['ndaStatus'].get('date', 'N/A')
        supplier_info += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>NDA Status:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{nda_status} (Date: {nda_date})</td>
        </tr>
        """
    
    # Close the table
    supplier_info += """
        </table>
    </div>
    """
    
    # Add processes section
    processes_section = """
    <div style="margin-top: 20px; padding: 15px; background-color: #e8f4f8; border-radius: 5px;">
        <h3>Processes</h3>
    """
    
    if 'processs' in supplier and supplier['processs']:
        processes_section += "<ul>"
        for process in supplier['processs']:
            processes_section += f"<li>{process}</li>"
        processes_section += "</ul>"
    else:
        processes_section += "<p>No processes information available.</p>"
    
    processes_section += """
    </div>
    """
    
    # Add related products section
    products_section = """
    <div style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
        <h3>Related Products</h3>
    """
    
    # Find products that use this post-processing supplier
    related_products = set()
    for product in data['products']:
        if 'postProcessingSuppliers' in product:
            for pp in product['postProcessingSuppliers']:
                if 'supplier' in pp and supplier_id in pp['supplier']:
                    related_products.add(product['id'])
    
    if related_products:
        products_section += "<ul>"
        for product_id in related_products:
            product = next((p for p in data['products'] if p['id'] == product_id), None)
            if product:
                products_section += f"<li><a href='../products/product_{product_id}.html'>{product['name']} ({product_id})</a></li>"
        products_section += "</ul>"
    else:
        products_section += "<p>No related products found.</p>"
    
    products_section += """
    </div>
    """
    
    # Create header
    header = f"""
    <div style="margin-bottom: 20px;">
        <h1>Post-Processing Supplier: {supplier['name']}</h1>
        <p><a href="../index.html">Back to Dashboard</a> | <a href="supplier_summary.html">Back to Supplier Summary</a></p>
    </div>
    """
    
    # Combine all elements
    full_content = header + supplier_info + processes_section + products_section
    
    # Create the HTML page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Supplier: {supplier['name']}</title>
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
    with open(os.path.join(supplier_dir, f"supplier_{supplier_id}.html"), 'w') as f:
        f.write(html_content)

def generate_supplier_summary(data, supplier_dir):
    """Generate a summary page for all suppliers"""
    # Create a figure for supplier distribution by type
    supplier_types = {
        'Printing Suppliers': len(data.get('printingSuppliers', [])),
        'Post-Processing Suppliers': len(data.get('postProcessingSuppliers', []))
    }
    
    # Create a figure for the supplier type distribution
    p1 = figure(
        title="Suppliers by Type",
        x_range=list(supplier_types.keys()),
        width=600,
        height=400,
        toolbar_location=None,
        tools=""
    )
    
    # Add bars
    p1.vbar(
        x=list(supplier_types.keys()),
        top=list(supplier_types.values()),
        width=0.5,
        color=Category10[10][0:len(supplier_types)],
        alpha=0.8
    )
    
    # Customize appearance
    p1.title.text_font_size = '14pt'
    p1.xaxis.axis_label = "Supplier Type"
    p1.yaxis.axis_label = "Number of Suppliers"
    p1.xgrid.grid_line_color = None
    
    # Create a figure for material systems per printing supplier
    if 'printingSuppliers' in data:
        materials_per_supplier = {}
        for supplier in data['printingSuppliers']:
            supplier_id = supplier['id']
            materials_per_supplier[supplier_id] = len(supplier.get('materialSystems', []))
        
        # Create a figure for materials per supplier
        supplier_names = []
        material_counts = []
        
        for supplier_id, count in materials_per_supplier.items():
            supplier = next((s for s in data['printingSuppliers'] if s['id'] == supplier_id), None)
            if supplier:
                supplier_names.append(f"{supplier['name']} ({supplier_id})")
                material_counts.append(count)
        
        # Sort by count
        sorted_indices = np.argsort(material_counts)[::-1]  # Descending order
        supplier_names = [supplier_names[i] for i in sorted_indices]
        material_counts = [material_counts[i] for i in sorted_indices]
        
        # Create a figure for materials per supplier
        p2 = figure(
            title="Number of Material Systems per Printing Supplier",
            x_range=supplier_names,
            width=1200,
            height=400,
            toolbar_location=None,
            tools=""
        )
        
        # Add bars
        p2.vbar(
            x=supplier_names,
            top=material_counts,
            width=0.7,
            color=Category10[10][3],
            alpha=0.8
        )
        
        # Customize appearance
        p2.title.text_font_size = '14pt'
        p2.xaxis.axis_label = "Supplier"
        p2.yaxis.axis_label = "Number of Material Systems"
        p2.xgrid.grid_line_color = None
        p2.xaxis.major_label_orientation = 45
    else:
        # Create an empty figure if no printing suppliers
        p2 = figure(
            title="Number of Material Systems per Printing Supplier",
            width=1200,
            height=400,
            toolbar_location=None,
            tools=""
        )
        p2.title.text_font_size = '14pt'
    
    # Create printing supplier list section
    printing_supplier_list = """
    <div style="margin-top: 30px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Printing Suppliers</h2>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <thead>
                    <tr style="background-color: #3498db; color: white;">
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Supplier Name</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">ID</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Supplier Number</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">NDA Status</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Material Systems</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    if 'printingSuppliers' in data:
        for i, supplier in enumerate(sorted(data['printingSuppliers'], key=lambda x: x['name'])):
            row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
            
            # Get NDA status
            nda_status = "N/A"
            if 'ndaStatus' in supplier and 'status' in supplier['ndaStatus']:
                nda_status = supplier['ndaStatus']['status']
                if 'date' in supplier['ndaStatus'] and supplier['ndaStatus']['date']:
                    nda_status += f" ({supplier['ndaStatus']['date']})"
            
            # Count material systems
            material_count = len(supplier.get('materialSystems', []))
            
            printing_supplier_list += f"""
            <tr style="{row_style}">
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href='supplier_{supplier['id']}.html' style="color: #3498db;">{supplier['name']}</a></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{supplier['id']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{supplier.get('supplierNumber', 'N/A')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{nda_status}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material_count}</td>
            </tr>
            """
    else:
        printing_supplier_list += """
        <tr>
            <td colspan="5" style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">No printing suppliers found</td>
        </tr>
        """
    
    printing_supplier_list += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    # Create post-processing supplier list section
    postprocessing_supplier_list = """
    <div style="margin-top: 30px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Post-Processing Suppliers</h2>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <thead>
                    <tr style="background-color: #3498db; color: white;">
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Supplier Name</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">ID</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Supplier Number</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">NDA Status</th>
                        <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Processes</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    if 'postProcessingSuppliers' in data:
        for i, supplier in enumerate(sorted(data['postProcessingSuppliers'], key=lambda x: x['name'])):
            row_style = "background-color: #f2f9ff;" if i % 2 == 0 else "background-color: #ffffff;"
            
            # Get NDA status
            nda_status = "N/A"
            if 'ndaStatus' in supplier and 'status' in supplier['ndaStatus']:
                nda_status = supplier['ndaStatus']['status']
                if 'date' in supplier['ndaStatus'] and supplier['ndaStatus']['date']:
                    nda_status += f" ({supplier['ndaStatus']['date']})"
            
            # Get processes
            processes = ", ".join(supplier.get('processs', [])) if 'processs' in supplier else "N/A"
            
            postprocessing_supplier_list += f"""
            <tr style="{row_style}">
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href='supplier_{supplier['id']}.html' style="color: #3498db;">{supplier['name']}</a></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{supplier['id']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{supplier.get('supplierNumber', 'N/A')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{nda_status}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{processes}</td>
            </tr>
            """
    else:
        postprocessing_supplier_list += """
        <tr>
            <td colspan="5" style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">No post-processing suppliers found</td>
        </tr>
        """
    
    postprocessing_supplier_list += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    # Create header
    header = """
    <div style="margin-bottom: 20px;">
        <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Supplier Summary</h1>
        <p>This page provides an overview of all suppliers and their distributions.</p>
        <p><a href="../index.html" style="color: #3498db; text-decoration: none;">Back to Dashboard</a></p>
    </div>
    """
    
    # Combine all elements
    header_div = Div(text=header, width=1200)
    printing_supplier_list_div = Div(text=printing_supplier_list, width=1200)
    postprocessing_supplier_list_div = Div(text=postprocessing_supplier_list, width=1200)
    
    # Create layout
    layout_obj = layout([
        [header_div],
        [p1],
        [p2],
        [printing_supplier_list_div],
        [postprocessing_supplier_list_div]
    ])
    
    # Output to file
    output_file(os.path.join(supplier_dir, "supplier_summary.html"))
    save(layout_obj)

def generate_supplier_distribution_charts(data, supplier_dir):
    """Generate distribution charts for suppliers"""
    # Count products per supplier
    products_per_supplier = {}
    
    # Initialize counts for printing suppliers
    if 'printingSuppliers' in data:
        for supplier in data['printingSuppliers']:
            supplier_id = supplier['id']
            products_per_supplier[supplier_id] = 0
    
    # Initialize counts for post-processing suppliers
    if 'postProcessingSuppliers' in data:
        for supplier in data['postProcessingSuppliers']:
            supplier_id = supplier['id']
            products_per_supplier[supplier_id] = 0
    
    # Count products for printing suppliers through material systems
    for product in data['products']:
        for material_entry in product.get('materialSystems', []):
            material_id = None
            if isinstance(material_entry, str):
                material_id = material_entry
            elif isinstance(material_entry, dict) and 'materialID' in material_entry:
                material_id = material_entry['materialID']
            
            if material_id:
                # Find suppliers that provide this material
                if 'printingSuppliers' in data:
                    for supplier in data['printingSuppliers']:
                        if 'materialSystems' in supplier:
                            for supplier_material in supplier['materialSystems']:
                                if supplier_material.get('materialID') == material_id:
                                    products_per_supplier[supplier['id']] = products_per_supplier.get(supplier['id'], 0) + 1
    
    # Count products for post-processing suppliers directly
    for product in data['products']:
        if 'postProcessingSuppliers' in product:
            for pp in product['postProcessingSuppliers']:
                if 'supplier' in pp:
                    for supplier_id in pp['supplier']:
                        if supplier_id in products_per_supplier:
                            products_per_supplier[supplier_id] += 1
    
    # Create a figure for products per supplier
    supplier_names = []
    product_counts = []
    supplier_types = []
    
    for supplier_id, count in products_per_supplier.items():
        # Check if it's a printing supplier
        printing_supplier = next((s for s in data.get('printingSuppliers', []) if s['id'] == supplier_id), None)
        if printing_supplier:
            supplier_names.append(f"{printing_supplier['name']} ({supplier_id})")
            product_counts.append(count)
            supplier_types.append('Printing')
            continue
        
        # Check if it's a post-processing supplier
        postproc_supplier = next((s for s in data.get('postProcessingSuppliers', []) if s['id'] == supplier_id), None)
        if postproc_supplier:
            supplier_names.append(f"{postproc_supplier['name']} ({supplier_id})")
            product_counts.append(count)
            supplier_types.append('Post-Processing')
    
    # Sort by count
    sorted_indices = np.argsort(product_counts)[::-1]  # Descending order
    supplier_names = [supplier_names[i] for i in sorted_indices]
    product_counts = [product_counts[i] for i in sorted_indices]
    supplier_types = [supplier_types[i] for i in sorted_indices]
    
    # Create a figure for products per supplier
    source = ColumnDataSource(data=dict(
        suppliers=supplier_names,
        counts=product_counts,
        types=supplier_types
    ))
    
    p = figure(
        title="Number of Products per Supplier",
        x_range=supplier_names,
        width=1200,
        height=500,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Add bars with color based on supplier type
    color_map = {'Printing': Category10[10][3], 'Post-Processing': Category10[10][4]}
    p.vbar(
        x='suppliers',
        top='counts',
        width=0.7,
        source=source,
        line_color="white",
        fill_color=factor_cmap('types', palette=list(color_map.values()), factors=list(color_map.keys())),
        alpha=0.8
    )
    
    # Customize appearance
    p.title.text_font_size = '14pt'
    p.xaxis.axis_label = "Supplier"
    p.yaxis.axis_label = "Number of Products"
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 45
    
    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Supplier", "@suppliers"),
        ("Products", "@counts"),
        ("Type", "@types")
    ]
    p.add_tools(hover)
    
    # Add legend
    legend_items = []
    for supplier_type, color in color_map.items():
        legend_items.append((supplier_type, [p.vbar(x=0, top=0, width=0, color=color)]))
    
    legend = Legend(items=legend_items, location="top_right")
    p.add_layout(legend)
    
    # Output to file
    output_file(os.path.join(supplier_dir, "supplier_product_distribution.html"))
    save(p) 