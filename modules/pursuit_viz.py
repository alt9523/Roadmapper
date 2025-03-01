import os
from datetime import datetime, timedelta
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Range1d, Span, Legend, LegendItem, Div, Tabs, Panel
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import Category10, Spectral6
from bokeh.transform import factor_cmap
import matplotlib.pyplot as plt
import numpy as np

def generate_pursuit_section(pursuit, data, funding_dir, funding_id):
    """Generate HTML section for a single pursuit within a funding opportunity"""
    pursuit_id = pursuit['pursuitID']
    pursuit_name = pursuit.get('pursuitName', 'Unnamed Pursuit')
    
    # Create pursuit info section
    pursuit_section = f"""
    <div style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 5px;">
        <h3>Pursuit: {pursuit_name} ({pursuit_id})</h3>
        <table style="width: 100%; border-collapse: collapse;">
    """
    
    # Add submission date if available
    if 'targetedSubmissionDate' in pursuit and pursuit['targetedSubmissionDate']:
        pursuit_section += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Targeted Submission Date:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pursuit['targetedSubmissionDate']}</td>
        </tr>
        """
    
    # Add Pcap and Pgo if available
    if 'Pcap' in pursuit and pursuit['Pcap']:
        pursuit_section += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Probability of Capture (Pcap):</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pursuit['Pcap']}</td>
        </tr>
        """
    
    if 'Pgo' in pursuit and pursuit['Pgo']:
        pursuit_section += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Probability of Go (Pgo):</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pursuit['Pgo']}</td>
        </tr>
        """
    
    # Add other relevance if available
    if 'otherRelevance' in pursuit and pursuit['otherRelevance']:
        pursuit_section += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Other Relevance:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pursuit['otherRelevance']}</td>
        </tr>
        """
    
    # Add details if available
    if 'details' in pursuit and pursuit['details']:
        pursuit_section += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Details:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pursuit['details']}</td>
        </tr>
        """
    
    # Close the table
    pursuit_section += """
        </table>
    """
    
    # Add related products and materials section
    related_products_section = generate_related_products_section(pursuit, data)
    if related_products_section:
        pursuit_section += related_products_section
    
    # Add potential value visualization if available
    potential_value_section = generate_potential_value_visualization(pursuit, funding_dir, funding_id, pursuit_id)
    if potential_value_section:
        pursuit_section += potential_value_section
    
    # Close the pursuit section div
    pursuit_section += """
    </div>
    """
    
    return pursuit_section

def generate_related_products_section(pursuit, data):
    """Generate HTML section for related products and materials"""
    # Check if there are related products
    if 'relatedProducts' not in pursuit or not pursuit['relatedProducts']:
        return ""
    
    related_products_section = """
    <div style="margin-top: 15px;">
        <h4>Related Products and Materials</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #e0e0e0;">
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Product</th>
                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Material System</th>
            </tr>
    """
    
    # Process related products based on format
    related_items = []
    
    # Handle string format like "P1 | MS1, P3 | MS2"
    if isinstance(pursuit['relatedProducts'], str):
        product_material_pairs = pursuit['relatedProducts'].split(',')
        for pair in product_material_pairs:
            pair = pair.strip()
            if '|' in pair:
                product_id, material_id = pair.split('|')
                related_items.append({
                    'product_id': product_id.strip(),
                    'material_id': material_id.strip()
                })
    
    # Handle array format with Product/Material objects
    elif isinstance(pursuit['relatedProducts'], list):
        for item in pursuit['relatedProducts']:
            if isinstance(item, dict):
                product_id = item.get('Product', '')
                material_id = item.get('Material', '')
                if product_id:
                    related_items.append({
                        'product_id': product_id,
                        'material_id': material_id
                    })
    
    # Add rows for each related product and material
    for item in related_items:
        product_id = item['product_id']
        material_id = item['material_id']
        
        # Find product and material names
        product_name = "Unknown"
        material_name = "Unknown"
        
        # Look up product name
        for product in data.get('products', []):
            if product['id'] == product_id:
                product_name = product['name']
                break
        
        # Look up material name
        for material in data.get('materialSystems', []):
            if material['id'] == material_id:
                material_name = material['name']
                break
        
        related_products_section += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">
                <a href="../products/product_{product_id}.html">{product_name} ({product_id})</a>
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">
                <a href="../materials/material_{material_id}.html">{material_name} ({material_id})</a>
            </td>
        </tr>
        """
    
    related_products_section += """
        </table>
    </div>
    """
    
    return related_products_section

def generate_potential_value_visualization(pursuit, funding_dir, funding_id, pursuit_id):
    """Generate visualization for potential value over fiscal years"""
    if 'potentialValue' not in pursuit or not pursuit['potentialValue']:
        return ""
    
    # Extract potential value data
    potential_value = pursuit['potentialValue']
    if not isinstance(potential_value, list) or not potential_value:
        return ""
    
    # Get the first (and typically only) potential value object
    value_data = potential_value[0]
    if not isinstance(value_data, dict):
        return ""
    
    # Extract fiscal years and values
    fiscal_years = []
    values = []
    
    for year, value in value_data.items():
        if year.startswith('FY'):
            fiscal_years.append(year)
            
            # Convert value to float
            if isinstance(value, (int, float)):
                values.append(float(value))
            elif isinstance(value, str):
                # Remove $ and commas
                clean_value = value.replace('$', '').replace(',', '')
                try:
                    values.append(float(clean_value))
                except ValueError:
                    values.append(0)
            else:
                values.append(0)
    
    # If no valid data, return empty string
    if not fiscal_years or not values:
        return ""
    
    # Sort by fiscal year
    sorted_data = sorted(zip(fiscal_years, values), key=lambda x: x[0])
    fiscal_years = [item[0] for item in sorted_data]
    values = [item[1] for item in sorted_data]
    
    # Create a bar chart for potential value
    plt.figure(figsize=(10, 6))
    bars = plt.bar(fiscal_years, values, color=Category10[10][0])
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'${height:,.0f}', ha='center', va='bottom')
    
    # Add labels and title
    plt.title(f'Potential Value by Fiscal Year for {pursuit_id}')
    plt.xlabel('Fiscal Year')
    plt.ylabel('Value ($)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save the figure
    chart_filename = f"pursuit_value_{funding_id}_{pursuit_id}.png"
    plt.savefig(os.path.join(funding_dir, chart_filename), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create HTML section for the visualization
    potential_value_section = f"""
    <div style="margin-top: 15px;">
        <h4>Potential Value by Fiscal Year</h4>
        <div style="text-align: center;">
            <img src="{chart_filename}" alt="Potential Value Chart" style="max-width: 100%; border: 1px solid #ddd;">
        </div>
    </div>
    """
    
    return potential_value_section

def generate_pursuits_summary(funding_opportunities, data, funding_dir):
    """Generate a summary page for all pursuits across all funding opportunities"""
    print("Generating pursuits summary page...")
    
    # Collect all pursuits
    all_pursuits = []
    for funding in funding_opportunities:
        funding_id = funding['id']
        funding_name = funding.get('name', funding.get('announcementName', 'Unknown'))
        
        for pursuit in funding.get('pursuits', []):
            all_pursuits.append({
                'pursuit_id': pursuit['pursuitID'],
                'pursuit_name': pursuit.get('pursuitName', 'Unnamed Pursuit'),
                'funding_id': funding_id,
                'funding_name': funding_name,
                'submission_date': pursuit.get('targetedSubmissionDate', 'N/A'),
                'pcap': pursuit.get('Pcap', 'N/A'),
                'pgo': pursuit.get('Pgo', 'N/A'),
                'pursuit': pursuit
            })
    
    # If no pursuits, create a simple message
    if not all_pursuits:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pursuits Summary</title>
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
                <h1>Pursuits Summary</h1>
                <p>No pursuits found in the data.</p>
                <p><a href="../index.html">Back to Dashboard</a> | <a href="funding_summary.html">Back to Funding Summary</a></p>
            </div>
        </body>
        </html>
        """
        
        with open(os.path.join(funding_dir, "pursuits_summary.html"), 'w') as f:
            f.write(html_content)
        
        return
    
    # Create HTML content for the summary page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pursuits Summary</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            h1 { color: #333; }
            h2, h3, h4 { color: #0066cc; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .container { max-width: 1200px; margin: 0 auto; }
            .card { 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                padding: 15px; 
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Pursuits Summary</h1>
            <p>This page provides an overview of all pursuits across all funding opportunities.</p>
            <p><a href="../index.html">Back to Dashboard</a> | <a href="funding_summary.html">Back to Funding Summary</a></p>
            
            <div class="card">
                <h2>All Pursuits</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #e0e0e0;">
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Pursuit ID</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Pursuit Name</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Funding Opportunity</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Submission Date</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Pcap</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Pgo</th>
                    </tr>
    """
    
    # Add rows for each pursuit
    for pursuit in all_pursuits:
        html_content += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pursuit['pursuit_id']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pursuit['pursuit_name']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">
                <a href="funding_{pursuit['funding_id']}.html">{pursuit['funding_name']} ({pursuit['funding_id']})</a>
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pursuit['submission_date']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pursuit['pcap']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{pursuit['pgo']}</td>
        </tr>
        """
    
    html_content += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write to file
    with open(os.path.join(funding_dir, "pursuits_summary.html"), 'w') as f:
        f.write(html_content)
    
    print(f"Pursuits summary page generated in '{funding_dir}/pursuits_summary.html'") 