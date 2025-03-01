import os
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, Range1d, Span, Legend, LegendItem, Div, Tabs, Panel
from bokeh.layouts import column, row, layout, gridplot
from bokeh.palettes import Category10, Spectral6
from bokeh.transform import factor_cmap
import numpy as np

def generate_relationship_visualizations(data, output_dir):
    """Generate visualizations for relationships between different entities"""
    print("Generating relationship visualizations...")
    
    # Create relationships directory if it doesn't exist
    relationship_dir = os.path.join(output_dir, "relationships")
    if not os.path.exists(relationship_dir):
        os.makedirs(relationship_dir)
    
    # Generate network graph
    generate_network_graph(data, relationship_dir)
    
    # Generate Sankey diagram
    generate_sankey_diagram(data, relationship_dir)
    
    # Generate relationship summary page
    generate_relationship_summary(data, relationship_dir)
    
    # Generate specific relationship visualizations
    generate_program_product_relationships(data, relationship_dir)
    generate_product_material_relationships(data, relationship_dir)
    generate_material_supplier_relationships(data, relationship_dir)
    generate_funding_task_relationships(data, relationship_dir)
    
    print(f"Relationship visualizations generated in '{relationship_dir}'")

def generate_network_graph(data, relationship_dir):
    """Generate a network graph showing relationships between all entities"""
    print("Generating network graph...")
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add program nodes
    for program in data.get('programs', []):
        G.add_node(program['id'], label=program['name'], type='program', layer=0)
    
    # Add product nodes
    for product in data.get('products', []):
        G.add_node(product['id'], label=product['name'], type='product', layer=1)
        
        # Add edges from programs to products
        for program_entry in product.get('programs', []):
            if isinstance(program_entry, str):
                program_id = program_entry
            elif isinstance(program_entry, dict) and 'programID' in program_entry:
                program_id = program_entry['programID']
            else:
                continue
                
            G.add_edge(program_id, product['id'], weight=2)
    
    # Add material system nodes
    for material in data.get('materialSystems', []):
        G.add_node(material['id'], label=material['name'], type='material', layer=2)
        
        # Add edges from products to materials
        for product in data.get('products', []):
            for material_entry in product.get('materialSystems', []):
                if isinstance(material_entry, str) and material_entry == material['id']:
                    G.add_edge(product['id'], material['id'], weight=2)
                elif isinstance(material_entry, dict) and material_entry.get('materialID') == material['id']:
                    G.add_edge(product['id'], material['id'], weight=2)
    
    # Add supplier nodes (printing suppliers)
    for supplier in data.get('printingSuppliers', []):
        G.add_node(supplier['id'], label=supplier['name'], type='supplier', layer=3)
        
        # Add edges from materials to suppliers
        if 'materialSystems' in supplier:
            for material_entry in supplier['materialSystems']:
                material_id = material_entry.get('materialID')
                if material_id:
                    G.add_edge(material_id, supplier['id'], weight=2)
    
    # Add supplier nodes (post-processing suppliers)
    for supplier in data.get('postProcessingSuppliers', []):
        G.add_node(supplier['id'], label=supplier['name'], type='post-supplier', layer=3)
        
        # Add edges from products to post-processing suppliers
        for product in data.get('products', []):
            if 'postProcessingSuppliers' in product:
                for pp in product['postProcessingSuppliers']:
                    if 'supplier' in pp and supplier['id'] in pp['supplier']:
                        G.add_edge(product['id'], supplier['id'], weight=1, style='dashed')
    
    # Add funding opportunity nodes
    if 'fundingOpportunities' in data:
        for funding in data['fundingOpportunities']:
            funding_name = funding.get('name', funding.get('announcementName', 'Unknown'))
            G.add_node(funding['id'], label=funding_name, type='funding', layer=4)
            
            # Add edges from funding to tasks with fundingID
            # Check program tasks
            for program in data.get('programs', []):
                if 'roadmap' in program and 'tasks' in program['roadmap']:
                    for task in program['roadmap']['tasks']:
                        if 'fundingID' in task and task['fundingID'] == funding['id']:
                            G.add_edge(funding['id'], program['id'], weight=1, style='dotted')
            
            # Check product tasks
            for product in data.get('products', []):
                if 'roadmap' in product and 'tasks' in product['roadmap']:
                    for task in product['roadmap']['tasks']:
                        if 'fundingID' in task and task['fundingID'] == funding['id']:
                            G.add_edge(funding['id'], product['id'], weight=1, style='dotted')
    
    # Create the figure with a white background
    plt.figure(figsize=(20, 12), facecolor='white')
    
    # Use multipartite layout to organize nodes by layer
    pos = nx.multipartite_layout(G, subset_key='layer', align='vertical')
    
    # Adjust vertical positions to avoid overlapping
    layer_counts = {}
    for node in G.nodes():
        layer = G.nodes[node]['layer']
        if layer not in layer_counts:
            layer_counts[layer] = 0
        layer_counts[layer] += 1
    
    # Spread nodes vertically within each layer
    for node in G.nodes():
        layer = G.nodes[node]['layer']
        if layer_counts[layer] > 1:
            # Find the index of this node among nodes in the same layer
            same_layer_nodes = [n for n in G.nodes() if G.nodes[n]['layer'] == layer]
            idx = same_layer_nodes.index(node)
            # Adjust vertical position
            pos[node][1] = (idx / (layer_counts[layer] - 1) - 0.5) * 0.9 if layer_counts[layer] > 1 else 0
    
    # Set node colors and sizes based on type
    node_colors = []
    node_sizes = []
    for node in G.nodes():
        node_type = G.nodes[node]['type']
        if node_type == 'program':
            node_colors.append('#1f77b4')  # Blue
            node_sizes.append(800)
        elif node_type == 'product':
            node_colors.append('#ff7f0e')  # Orange
            node_sizes.append(700)
        elif node_type == 'material':
            node_colors.append('#2ca02c')  # Green
            node_sizes.append(600)
        elif node_type == 'supplier':
            node_colors.append('#d62728')  # Red
            node_sizes.append(500)
        elif node_type == 'post-supplier':
            node_colors.append('#9467bd')  # Purple
            node_sizes.append(500)
        elif node_type == 'funding':
            node_colors.append('#8c564b')  # Brown
            node_sizes.append(600)
        else:
            node_colors.append('#7f7f7f')  # Gray
            node_sizes.append(400)
    
    # Draw edges with different styles based on edge attributes
    for edge in G.edges(data=True):
        start, end, attrs = edge
        style = attrs.get('style', 'solid')
        if style == 'dashed':
            nx.draw_networkx_edges(
                G, pos, 
                edgelist=[(start, end)],
                width=1.2, 
                alpha=0.7, 
                edge_color='gray', 
                arrows=True,
                arrowsize=15,
                style='dashed',
                connectionstyle='arc3,rad=0.1'  # Curved edges
            )
        elif style == 'dotted':
            nx.draw_networkx_edges(
                G, pos, 
                edgelist=[(start, end)],
                width=1.2, 
                alpha=0.7, 
                edge_color='gray', 
                arrows=True,
                arrowsize=15,
                style='dotted',
                connectionstyle='arc3,rad=0.1'  # Curved edges
            )
        else:
            nx.draw_networkx_edges(
                G, pos, 
                edgelist=[(start, end)],
                width=1.2, 
                alpha=0.7, 
                edge_color='gray', 
                arrows=True,
                arrowsize=15,
                connectionstyle='arc3,rad=0.1'  # Curved edges
            )
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, 
        node_size=node_sizes, 
        node_color=node_colors, 
        alpha=0.9,
        edgecolors='black',
        linewidths=1
    )
    
    # Add labels with white background for better readability
    labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    
    # Draw labels with a white background
    for node, (x, y) in pos.items():
        plt.text(
            x, y, 
            labels[node],
            fontsize=9,
            ha='center',
            va='center',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9)
        )
    
    # Add column headers
    plt.text(0.0, 1.05, "Programs", fontsize=16, ha='center', fontweight='bold')
    plt.text(0.25, 1.05, "Products", fontsize=16, ha='center', fontweight='bold')
    plt.text(0.5, 1.05, "Material Systems", fontsize=16, ha='center', fontweight='bold')
    plt.text(0.75, 1.05, "Suppliers", fontsize=16, ha='center', fontweight='bold')
    plt.text(1.0, 1.05, "Funding", fontsize=16, ha='center', fontweight='bold')
    
    # Add a legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#1f77b4', markersize=15, label='Programs'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff7f0e', markersize=15, label='Products'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ca02c', markersize=15, label='Material Systems'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#d62728', markersize=15, label='Printing Suppliers'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#9467bd', markersize=15, label='Post-Processing Suppliers'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#8c564b', markersize=15, label='Funding Opportunities')
    ]
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
    
    # Add title and remove axes
    plt.title('Roadmap Relationships Network', fontsize=20, pad=20)
    plt.axis('off')
    
    # Add a grid background to separate the columns
    plt.axvline(x=0.125, color='lightgray', linestyle='--', alpha=0.5)
    plt.axvline(x=0.375, color='lightgray', linestyle='--', alpha=0.5)
    plt.axvline(x=0.625, color='lightgray', linestyle='--', alpha=0.5)
    plt.axvline(x=0.875, color='lightgray', linestyle='--', alpha=0.5)
    
    # Save the figure with high resolution
    plt.tight_layout()
    plt.savefig(os.path.join(relationship_dir, "network_graph.png"), dpi=300, bbox_inches='tight')
    
    # Also save as SVG for better quality
    plt.savefig(os.path.join(relationship_dir, "network_graph.svg"), format='svg', bbox_inches='tight')
    
    plt.close()
    
    # Create an HTML page to display the network graph
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relationship Network Graph</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2, h3, h4 {{ color: #0066cc; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .image-container {{ text-align: center; margin: 20px 0; }}
            .image-container img {{ max-width: 100%; border: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Relationship Network Graph</h1>
            <p>This visualization shows the relationships between different entities in the roadmap data.</p>
            <p><a href="../index.html">Back to Dashboard</a> | <a href="relationship_summary.html">Back to Relationship Summary</a></p>
            
            <div class="image-container">
                <img src="network_graph.png" alt="Network Graph">
            </div>
            
            <h2>Legend</h2>
            <ul>
                <li><strong style="color: #1f77b4;">Programs</strong>: Space missions and projects</li>
                <li><strong style="color: #ff7f0e;">Products</strong>: Components and systems being developed</li>
                <li><strong style="color: #2ca02c;">Material Systems</strong>: Materials used in products</li>
                <li><strong style="color: #d62728;">Printing Suppliers</strong>: Suppliers providing 3D printing services</li>
                <li><strong style="color: #9467bd;">Post-Processing Suppliers</strong>: Suppliers providing post-processing services</li>
                <li><strong style="color: #8c564b;">Funding Opportunities</strong>: Sources of funding for tasks</li>
            </ul>
            
            <h2>Relationship Types</h2>
            <ul>
                <li><strong>Solid lines</strong>: Direct relationships (e.g., a product is used in a program)</li>
                <li><strong>Dashed lines</strong>: Post-processing relationships</li>
                <li><strong>Dotted lines</strong>: Funding relationships</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(relationship_dir, "network_graph.html"), 'w') as f:
        f.write(html_content)
    
    print(f"Network graph generated in '{relationship_dir}/network_graph.html'")

def generate_sankey_diagram(data, relationship_dir):
    """Generate a Sankey diagram showing flows between different entities"""
    print("Generating Sankey diagram...")
    
    # Create a figure
    plt.figure(figsize=(15, 10))
    
    # Initialize the Sankey diagram
    sankey = Sankey(ax=plt.gca(), scale=0.01, offset=0.2, head_angle=120, margin=0.4, shoulder=0)
    
    # Collect all the flows
    program_to_product = {}
    product_to_material = {}
    material_to_supplier = {}
    
    # Count program to product flows
    for product in data.get('products', []):
        for program_entry in product.get('programs', []):
            program_id = None
            if isinstance(program_entry, str):
                program_id = program_entry
            elif isinstance(program_entry, dict) and 'programID' in program_entry:
                program_id = program_entry['programID']
                
            if program_id:
                if program_id not in program_to_product:
                    program_to_product[program_id] = 0
                program_to_product[program_id] += 1
    
    # Count product to material flows
    for product in data.get('products', []):
        for material_entry in product.get('materialSystems', []):
            material_id = None
            if isinstance(material_entry, str):
                material_id = material_entry
            elif isinstance(material_entry, dict) and 'materialID' in material_entry:
                material_id = material_entry['materialID']
                
            if material_id:
                key = (product['id'], material_id)
                if key not in product_to_material:
                    product_to_material[key] = 0
                product_to_material[key] += 1
    
    # Count material to supplier flows
    for supplier in data.get('printingSuppliers', []):
        if 'materialSystems' in supplier:
            for material_entry in supplier['materialSystems']:
                material_id = material_entry.get('materialID')
                if material_id:
                    key = (material_id, supplier['id'])
                    if key not in material_to_supplier:
                        material_to_supplier[key] = 0
                    material_to_supplier[key] += 1
    
    # Add the first stage: Programs to Products
    program_flows = [-sum(program_to_product.values())]  # Total outflow
    
    # Add the diagram
    sankey.add(flows=program_flows, 
               labels=['Programs'],
               orientations=[0],
               pathlengths=[0.25],
               facecolor='#1f77b4')
    
    # Add the second stage: Products
    product_inflow = sum(program_to_product.values())
    product_outflow = sum(len(product.get('materialSystems', [])) for product in data.get('products', []))
    product_flows = [product_inflow, -product_outflow]
    
    sankey.add(flows=product_flows,
               labels=['Products'],
               orientations=[0, 0],
               pathlengths=[0.25, 0.25],
               facecolor='#ff7f0e',
               prior=0,
               connect=(0, 0))
    
    # Add the third stage: Materials
    material_inflow = product_outflow
    material_outflow = sum(1 for supplier in data.get('printingSuppliers', []) 
                          for material in supplier.get('materialSystems', []))
    material_flows = [material_inflow, -material_outflow]
    
    sankey.add(flows=material_flows,
               labels=['Materials'],
               orientations=[0, 0],
               pathlengths=[0.25, 0.25],
               facecolor='#2ca02c',
               prior=1,
               connect=(1, 0))
    
    # Add the fourth stage: Suppliers
    supplier_inflow = material_outflow
    supplier_flows = [supplier_inflow]
    
    sankey.add(flows=supplier_flows,
               labels=['Suppliers'],
               orientations=[0],
               pathlengths=[0.25],
               facecolor='#d62728',
               prior=2,
               connect=(1, 0))
    
    # Finish the diagram
    sankey.finish()
    plt.title('Roadmap Relationships Flow Diagram', fontsize=16)
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "sankey_diagram.png"), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(relationship_dir, "sankey_diagram.svg"), format='svg', bbox_inches='tight')
    plt.close()
    
    # Create an HTML page to display the Sankey diagram
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relationship Flow Diagram</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2, h3, h4 {{ color: #0066cc; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .image-container {{ text-align: center; margin: 20px 0; }}
            .image-container img {{ max-width: 100%; border: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Relationship Flow Diagram (Sankey)</h1>
            <p>This visualization shows the flow of relationships between different entities in the roadmap data.</p>
            <p><a href="../index.html">Back to Dashboard</a> | <a href="relationship_summary.html">Back to Relationship Summary</a></p>
            
            <div class="image-container">
                <img src="sankey_diagram.png" alt="Sankey Diagram">
            </div>
            
            <h2>Explanation</h2>
            <p>The Sankey diagram shows the flow of relationships from Programs to Products to Materials to Suppliers. The width of each flow represents the number of connections between entities.</p>
            
            <ul>
                <li><strong style="color: #1f77b4;">Programs</strong>: Space missions and projects</li>
                <li><strong style="color: #ff7f0e;">Products</strong>: Components and systems being developed</li>
                <li><strong style="color: #2ca02c;">Materials</strong>: Material systems used in products</li>
                <li><strong style="color: #d62728;">Suppliers</strong>: Suppliers providing materials and services</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(relationship_dir, "sankey_diagram.html"), 'w') as f:
        f.write(html_content)
    
    print(f"Sankey diagram generated in '{relationship_dir}/sankey_diagram.html'")

def generate_relationship_summary(data, relationship_dir):
    """Generate a summary page for all relationship visualizations"""
    print("Generating relationship summary page...")
    
    # Create HTML content for the summary page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relationship Visualizations Summary</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2, h3, h4 {{ color: #0066cc; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                padding: 15px; 
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }}
            .card h2 {{ margin-top: 0; }}
            .card-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
            }}
            .thumbnail {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 3px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Relationship Visualizations Summary</h1>
            <p>This page provides an overview of all relationship visualizations available in the roadmap data.</p>
            <p><a href="../index.html">Back to Dashboard</a></p>
            
            <div class="card">
                <h2>Overview Visualizations</h2>
                <div class="card-grid">
                    <div>
                        <h3>Network Graph</h3>
                        <p>A comprehensive view of all relationships between programs, products, materials, suppliers, and funding.</p>
                        <a href="network_graph.html">
                            <img src="network_graph.png" alt="Network Graph" class="thumbnail">
                        </a>
                        <p><a href="network_graph.html">View Network Graph</a></p>
                    </div>
                    
                    <div>
                        <h3>Sankey Diagram</h3>
                        <p>A flow diagram showing the relationships between different entities in the roadmap.</p>
                        <a href="sankey_diagram.html">
                            <img src="sankey_diagram.png" alt="Sankey Diagram" class="thumbnail">
                        </a>
                        <p><a href="sankey_diagram.html">View Sankey Diagram</a></p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Specific Relationship Visualizations</h2>
                <div class="card-grid">
                    <div>
                        <h3>Program-Product Relationships</h3>
                        <p>Visualizations showing the relationships between programs and products.</p>
                        <a href="program_product_relationships.html">
                            <img src="program_product_chart.png" alt="Program-Product Relationships" class="thumbnail">
                        </a>
                        <p><a href="program_product_relationships.html">View Program-Product Relationships</a></p>
                    </div>
                    
                    <div>
                        <h3>Product-Material Relationships</h3>
                        <p>Visualizations showing the relationships between products and material systems.</p>
                        <a href="product_material_relationships.html">
                            <img src="product_material_chart.png" alt="Product-Material Relationships" class="thumbnail">
                        </a>
                        <p><a href="product_material_relationships.html">View Product-Material Relationships</a></p>
                    </div>
                    
                    <div>
                        <h3>Material-Supplier Relationships</h3>
                        <p>Visualizations showing the relationships between material systems and suppliers.</p>
                        <a href="material_supplier_relationships.html">
                            <img src="material_supplier_chart.png" alt="Material-Supplier Relationships" class="thumbnail">
                        </a>
                        <p><a href="material_supplier_relationships.html">View Material-Supplier Relationships</a></p>
                    </div>
                    
                    <div>
                        <h3>Funding-Task Relationships</h3>
                        <p>Visualizations showing the relationships between funding opportunities and tasks.</p>
                        <a href="funding_task_relationships.html">
                            <img src="funding_task_chart.png" alt="Funding-Task Relationships" class="thumbnail">
                        </a>
                        <p><a href="funding_task_relationships.html">View Funding-Task Relationships</a></p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Relationship Statistics</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #e0e0e0;">
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Relationship Type</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Count</th>
                    </tr>
    """
    
    # Count relationships
    program_product_count = sum(len(product.get('programs', [])) for product in data.get('products', []))
    
    product_material_count = 0
    for product in data.get('products', []):
        product_material_count += len(product.get('materialSystems', []))
    
    material_supplier_count = 0
    for supplier in data.get('printingSuppliers', []):
        material_supplier_count += len(supplier.get('materialSystems', []))
    
    product_postsupplier_count = 0
    for product in data.get('products', []):
        for pp in product.get('postProcessingSuppliers', []):
            product_postsupplier_count += len(pp.get('supplier', []))
    
    funding_task_count = 0
    if 'fundingOpportunities' in data:
        # Check program tasks
        for program in data.get('programs', []):
            if 'roadmap' in program and 'tasks' in program['roadmap']:
                for task in program['roadmap']['tasks']:
                    if 'fundingID' in task:
                        funding_task_count += 1
        
        # Check product tasks
        for product in data.get('products', []):
            if 'roadmap' in product and 'tasks' in product['roadmap']:
                for task in product['roadmap']['tasks']:
                    if 'fundingID' in task:
                        funding_task_count += 1
    
    # Add relationship statistics to the HTML
    html_content += f"""
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">Program-Product Relationships</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{program_product_count}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">Product-Material Relationships</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{product_material_count}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">Material-Supplier Relationships</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{material_supplier_count}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">Product-PostProcessing Supplier Relationships</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{product_postsupplier_count}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">Funding-Task Relationships</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{funding_task_count}</td>
                    </tr>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write to file
    with open(os.path.join(relationship_dir, "relationship_summary.html"), 'w') as f:
        f.write(html_content)
    
    print(f"Relationship summary page generated in '{relationship_dir}/relationship_summary.html'")

def generate_program_product_relationships(data, relationship_dir):
    """Generate visualizations for program-product relationships"""
    print("Generating program-product relationship visualizations...")
    
    # Create a matrix of program-product relationships
    programs = data.get('programs', [])
    products = data.get('products', [])
    
    # Create a matrix to store the relationships
    matrix = []
    program_names = []
    product_names = []
    
    # Get program names
    for program in programs:
        program_names.append(f"{program['name']} ({program['id']})")
    
    # Get product names
    for product in products:
        product_names.append(f"{product['name']} ({product['id']})")
    
    # Create the matrix
    for program in programs:
        row = []
        for product in products:
            # Check if this program is associated with this product
            is_associated = False
            for program_entry in product.get('programs', []):
                if isinstance(program_entry, str) and program_entry == program['id']:
                    is_associated = True
                    break
                elif isinstance(program_entry, dict) and program_entry.get('programID') == program['id']:
                    is_associated = True
                    break
            
            row.append(1 if is_associated else 0)
        
        matrix.append(row)
    
    # Create a heatmap using matplotlib
    plt.figure(figsize=(12, 10))
    plt.imshow(matrix, cmap='Blues', aspect='auto')
    
    # Add labels
    plt.xticks(range(len(product_names)), product_names, rotation=90)
    plt.yticks(range(len(program_names)), program_names)
    
    plt.title('Program-Product Relationships')
    plt.xlabel('Products')
    plt.ylabel('Programs')
    
    # Add a colorbar
    cbar = plt.colorbar()
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(['No Relationship', 'Related'])
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "program_product_chart.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create a bar chart showing the number of products per program
    products_per_program = {}
    for program in programs:
        products_per_program[program['id']] = 0
    
    for product in products:
        for program_entry in product.get('programs', []):
            if isinstance(program_entry, str) and program_entry in products_per_program:
                products_per_program[program_entry] += 1
            elif isinstance(program_entry, dict) and program_entry.get('programID') in products_per_program:
                products_per_program[program_entry.get('programID')] += 1
    
    # Create a figure for products per program
    program_names = []
    product_counts = []
    
    for program_id, count in products_per_program.items():
        program = next((p for p in programs if p['id'] == program_id), None)
        if program:
            program_names.append(f"{program['name']} ({program_id})")
            product_counts.append(count)
    
    # Sort by count
    sorted_indices = np.argsort(product_counts)[::-1]  # Descending order
    program_names = [program_names[i] for i in sorted_indices]
    product_counts = [product_counts[i] for i in sorted_indices]
    
    # Create the bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(program_names, product_counts, color='#1f77b4')
    
    # Add labels
    plt.title('Number of Products per Program')
    plt.xlabel('Programs')
    plt.ylabel('Number of Products')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.0f}', ha='center', va='bottom')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "products_per_program.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create a bar chart showing the number of programs per product
    programs_per_product = {}
    for product in products:
        product_id = product['id']
        programs_per_product[product_id] = len(product.get('programs', []))
    
    # Create a figure for programs per product
    product_names = []
    program_counts = []
    
    for product_id, count in programs_per_product.items():
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            product_names.append(f"{product['name']} ({product_id})")
            program_counts.append(count)
    
    # Sort by count
    sorted_indices = np.argsort(program_counts)[::-1]  # Descending order
    product_names = [product_names[i] for i in sorted_indices]
    program_counts = [program_counts[i] for i in sorted_indices]
    
    # Create the bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(product_names, program_counts, color='#ff7f0e')
    
    # Add labels
    plt.title('Number of Programs per Product')
    plt.xlabel('Products')
    plt.ylabel('Number of Programs')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.0f}', ha='center', va='bottom')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "programs_per_product.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create an HTML page to display the visualizations
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Program-Product Relationships</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2, h3, h4 {{ color: #0066cc; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .image-container {{ text-align: center; margin: 20px 0; }}
            .image-container img {{ max-width: 100%; border: 1px solid #ddd; }}
            .card {{ 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                padding: 15px; 
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Program-Product Relationships</h1>
            <p>This page shows the relationships between programs and products in the roadmap data.</p>
            <p><a href="../index.html">Back to Dashboard</a> | <a href="relationship_summary.html">Back to Relationship Summary</a></p>
            
            <div class="card">
                <h2>Relationship Matrix</h2>
                <p>This heatmap shows which programs are associated with which products. Blue cells indicate a relationship exists.</p>
                <div class="image-container">
                    <img src="program_product_chart.png" alt="Program-Product Relationship Matrix">
                </div>
            </div>
            
            <div class="card">
                <h2>Products per Program</h2>
                <p>This chart shows the number of products associated with each program.</p>
                <div class="image-container">
                    <img src="products_per_program.png" alt="Products per Program">
                </div>
            </div>
            
            <div class="card">
                <h2>Programs per Product</h2>
                <p>This chart shows the number of programs associated with each product.</p>
                <div class="image-container">
                    <img src="programs_per_product.png" alt="Programs per Product">
                </div>
            </div>
            
            <div class="card">
                <h2>Detailed Relationships</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #e0e0e0;">
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Program</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Products</th>
                    </tr>
    """
    
    # Add program-product relationships to the table
    for program in programs:
        related_products = []
        
        for product in products:
            for program_entry in product.get('programs', []):
                if isinstance(program_entry, str) and program_entry == program['id']:
                    related_products.append(product)
                    break
                elif isinstance(program_entry, dict) and program_entry.get('programID') == program['id']:
                    related_products.append(product)
                    break
        
        html_content += f"""
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href="../programs/program_{program['id']}.html">{program['name']} ({program['id']})</a></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">
        """
        
        if related_products:
            html_content += "<ul>"
            for product in related_products:
                html_content += f"<li><a href='../products/product_{product['id']}.html'>{product['name']} ({product['id']})</a></li>"
            html_content += "</ul>"
        else:
            html_content += "No related products"
        
        html_content += """
                        </td>
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
    with open(os.path.join(relationship_dir, "program_product_relationships.html"), 'w') as f:
        f.write(html_content)
    
    print(f"Program-product relationship visualizations generated in '{relationship_dir}/program_product_relationships.html'")

def generate_product_material_relationships(data, relationship_dir):
    """Generate visualizations for product-material relationships"""
    print("Generating product-material relationship visualizations...")
    
    # Create a matrix of product-material relationships
    products = data.get('products', [])
    materials = data.get('materialSystems', [])
    
    # Create a matrix to store the relationships
    matrix = []
    product_names = []
    material_names = []
    
    # Get product names
    for product in products:
        product_names.append(f"{product['name']} ({product['id']})")
    
    # Get material names
    for material in materials:
        material_names.append(f"{material['name']} ({material['id']})")
    
    # Create the matrix
    for product in products:
        row = []
        for material in materials:
            # Check if this product is associated with this material
            is_associated = False
            for material_entry in product.get('materialSystems', []):
                if isinstance(material_entry, str) and material_entry == material['id']:
                    is_associated = True
                    break
                elif isinstance(material_entry, dict) and material_entry.get('materialID') == material['id']:
                    is_associated = True
                    break
            
            row.append(1 if is_associated else 0)
        
        matrix.append(row)
    
    # Create a heatmap using matplotlib
    plt.figure(figsize=(12, 10))
    plt.imshow(matrix, cmap='Greens', aspect='auto')
    
    # Add labels
    plt.xticks(range(len(material_names)), material_names, rotation=90)
    plt.yticks(range(len(product_names)), product_names)
    
    plt.title('Product-Material Relationships')
    plt.xlabel('Material Systems')
    plt.ylabel('Products')
    
    # Add a colorbar
    cbar = plt.colorbar()
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(['No Relationship', 'Related'])
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "product_material_chart.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create a bar chart showing the number of materials per product
    materials_per_product = {}
    for product in products:
        product_id = product['id']
        materials_per_product[product_id] = len(product.get('materialSystems', []))
    
    # Create a figure for materials per product
    product_names = []
    material_counts = []
    
    for product_id, count in materials_per_product.items():
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            product_names.append(f"{product['name']} ({product_id})")
            material_counts.append(count)
    
    # Sort by count
    sorted_indices = np.argsort(material_counts)[::-1]  # Descending order
    product_names = [product_names[i] for i in sorted_indices]
    material_counts = [material_counts[i] for i in sorted_indices]
    
    # Create the bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(product_names, material_counts, color='#2ca02c')
    
    # Add labels
    plt.title('Number of Material Systems per Product')
    plt.xlabel('Products')
    plt.ylabel('Number of Material Systems')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.0f}', ha='center', va='bottom')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "materials_per_product.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create a bar chart showing the number of products per material
    products_per_material = {}
    for material in materials:
        material_id = material['id']
        products_per_material[material_id] = 0
    
    for product in products:
        for material_entry in product.get('materialSystems', []):
            if isinstance(material_entry, str) and material_entry in products_per_material:
                products_per_material[material_entry] += 1
            elif isinstance(material_entry, dict) and material_entry.get('materialID') in products_per_material:
                products_per_material[material_entry.get('materialID')] += 1
    
    # Create a figure for products per material
    material_names = []
    product_counts = []
    
    for material_id, count in products_per_material.items():
        material = next((m for m in materials if m['id'] == material_id), None)
        if material:
            material_names.append(f"{material['name']} ({material_id})")
            product_counts.append(count)
    
    # Sort by count
    sorted_indices = np.argsort(product_counts)[::-1]  # Descending order
    material_names = [material_names[i] for i in sorted_indices]
    product_counts = [product_counts[i] for i in sorted_indices]
    
    # Create the bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(material_names, product_counts, color='#ff7f0e')
    
    # Add labels
    plt.title('Number of Products per Material System')
    plt.xlabel('Material Systems')
    plt.ylabel('Number of Products')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.0f}', ha='center', va='bottom')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "products_per_material.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create an HTML page to display the visualizations
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Product-Material Relationships</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2, h3, h4 {{ color: #0066cc; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .image-container {{ text-align: center; margin: 20px 0; }}
            .image-container img {{ max-width: 100%; border: 1px solid #ddd; }}
            .card {{ 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                padding: 15px; 
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Product-Material Relationships</h1>
            <p>This page shows the relationships between products and material systems in the roadmap data.</p>
            <p><a href="../index.html">Back to Dashboard</a> | <a href="relationship_summary.html">Back to Relationship Summary</a></p>
            
            <div class="card">
                <h2>Relationship Matrix</h2>
                <p>This heatmap shows which products are associated with which material systems. Green cells indicate a relationship exists.</p>
                <div class="image-container">
                    <img src="product_material_chart.png" alt="Product-Material Relationship Matrix">
                </div>
            </div>
            
            <div class="card">
                <h2>Materials per Product</h2>
                <p>This chart shows the number of material systems associated with each product.</p>
                <div class="image-container">
                    <img src="materials_per_product.png" alt="Materials per Product">
                </div>
            </div>
            
            <div class="card">
                <h2>Products per Material</h2>
                <p>This chart shows the number of products associated with each material system.</p>
                <div class="image-container">
                    <img src="products_per_material.png" alt="Products per Material">
                </div>
            </div>
            
            <div class="card">
                <h2>Detailed Relationships</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #e0e0e0;">
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Product</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Material Systems</th>
                    </tr>
    """
    
    # Add product-material relationships to the table
    for product in products:
        related_materials = []
        
        for material_entry in product.get('materialSystems', []):
            material_id = None
            if isinstance(material_entry, str):
                material_id = material_entry
            elif isinstance(material_entry, dict) and 'materialID' in material_entry:
                material_id = material_entry['materialID']
                
            if material_id:
                material = next((m for m in materials if m['id'] == material_id), None)
                if material:
                    related_materials.append((material, material_entry))
        
        html_content += f"""
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href="../materials/material_{material['id']}.html">{material['name']} ({material['id']})</a></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">
        """
        
        if related_materials:
            html_content += "<ul>"
            for material, material_entry in related_materials:
                # Add printer information if available
                printer_info = ""
                if isinstance(material_entry, dict) and 'printer' in material_entry:
                    printers = material_entry['printer']
                    if printers:
                        printer_info = f" - Printers: {', '.join(printers)}"
                
                html_content += f"<li><a href='../materials/material_{material['id']}.html'>{material['name']} ({material['id']})</a>{printer_info}</li>"
            html_content += "</ul>"
        else:
            html_content += "No related material systems"
        
        html_content += """
                        </td>
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
    with open(os.path.join(relationship_dir, "product_material_relationships.html"), 'w') as f:
        f.write(html_content)
    
    print(f"Product-material relationship visualizations generated in '{relationship_dir}/product_material_relationships.html'")

def generate_material_supplier_relationships(data, relationship_dir):
    """Generate visualizations for material-supplier relationships"""
    print("Generating material-supplier relationship visualizations...")
    
    # Create a matrix of material-supplier relationships
    materials = data.get('materialSystems', [])
    printing_suppliers = data.get('printingSuppliers', [])
    
    # Create a matrix to store the relationships
    matrix = []
    material_names = []
    supplier_names = []
    
    # Get material names
    for material in materials:
        material_names.append(f"{material['name']} ({material['id']})")
    
    # Get supplier names
    for supplier in printing_suppliers:
        supplier_names.append(f"{supplier['name']} ({supplier['id']})")
    
    # Create the matrix
    for material in materials:
        row = []
        for supplier in printing_suppliers:
            # Check if this material is associated with this supplier
            is_associated = False
            if 'materialSystems' in supplier:
                for material_entry in supplier['materialSystems']:
                    if material_entry.get('materialID') == material['id']:
                        is_associated = True
                        break
            
            row.append(1 if is_associated else 0)
        
        matrix.append(row)
    
    # Create a heatmap using matplotlib
    plt.figure(figsize=(12, 10))
    plt.imshow(matrix, cmap='Reds', aspect='auto')
    
    # Add labels
    plt.xticks(range(len(supplier_names)), supplier_names, rotation=90)
    plt.yticks(range(len(material_names)), material_names)
    
    plt.title('Material-Supplier Relationships')
    plt.xlabel('Printing Suppliers')
    plt.ylabel('Material Systems')
    
    # Add a colorbar
    cbar = plt.colorbar()
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(['No Relationship', 'Related'])
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "material_supplier_chart.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create a bar chart showing the number of suppliers per material
    suppliers_per_material = {}
    for material in materials:
        material_id = material['id']
        suppliers_per_material[material_id] = 0
        
        for supplier in printing_suppliers:
            if 'materialSystems' in supplier:
                for material_entry in supplier['materialSystems']:
                    if material_entry.get('materialID') == material_id:
                        suppliers_per_material[material_id] += 1
                        break
    
    # Create a figure for suppliers per material
    material_names = []
    supplier_counts = []
    
    for material_id, count in suppliers_per_material.items():
        material = next((m for m in materials if m['id'] == material_id), None)
        if material:
            material_names.append(f"{material['name']} ({material_id})")
            supplier_counts.append(count)
    
    # Sort by count
    sorted_indices = np.argsort(supplier_counts)[::-1]  # Descending order
    material_names = [material_names[i] for i in sorted_indices]
    supplier_counts = [supplier_counts[i] for i in sorted_indices]
    
    # Create the bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(material_names, supplier_counts, color='#d62728')
    
    # Add labels
    plt.title('Number of Suppliers per Material System')
    plt.xlabel('Material Systems')
    plt.ylabel('Number of Suppliers')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.0f}', ha='center', va='bottom')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "suppliers_per_material.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create a bar chart showing the number of materials per supplier
    materials_per_supplier = {}
    for supplier in printing_suppliers:
        supplier_id = supplier['id']
        materials_per_supplier[supplier_id] = len(supplier.get('materialSystems', []))
    
    # Create a figure for materials per supplier
    supplier_names = []
    material_counts = []
    
    for supplier_id, count in materials_per_supplier.items():
        supplier = next((s for s in printing_suppliers if s['id'] == supplier_id), None)
        if supplier:
            supplier_names.append(f"{supplier['name']} ({supplier_id})")
            material_counts.append(count)
    
    # Sort by count
    sorted_indices = np.argsort(material_counts)[::-1]  # Descending order
    supplier_names = [supplier_names[i] for i in sorted_indices]
    material_counts = [material_counts[i] for i in sorted_indices]
    
    # Create the bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(supplier_names, material_counts, color='#2ca02c')
    
    # Add labels
    plt.title('Number of Material Systems per Supplier')
    plt.xlabel('Suppliers')
    plt.ylabel('Number of Material Systems')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.0f}', ha='center', va='bottom')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "materials_per_supplier.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create an HTML page to display the visualizations
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Material-Supplier Relationships</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2, h3, h4 {{ color: #0066cc; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .image-container {{ text-align: center; margin: 20px 0; }}
            .image-container img {{ max-width: 100%; border: 1px solid #ddd; }}
            .card {{ 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                padding: 15px; 
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Material-Supplier Relationships</h1>
            <p>This page shows the relationships between material systems and printing suppliers in the roadmap data.</p>
            <p><a href="../index.html">Back to Dashboard</a> | <a href="relationship_summary.html">Back to Relationship Summary</a></p>
            
            <div class="card">
                <h2>Relationship Matrix</h2>
                <p>This heatmap shows which material systems are associated with which printing suppliers. Red cells indicate a relationship exists.</p>
                <div class="image-container">
                    <img src="material_supplier_chart.png" alt="Material-Supplier Relationship Matrix">
                </div>
            </div>
            
            <div class="card">
                <h2>Suppliers per Material</h2>
                <p>This chart shows the number of printing suppliers associated with each material system.</p>
                <div class="image-container">
                    <img src="suppliers_per_material.png" alt="Suppliers per Material">
                </div>
            </div>
            
            <div class="card">
                <h2>Materials per Supplier</h2>
                <p>This chart shows the number of material systems associated with each printing supplier.</p>
                <div class="image-container">
                    <img src="materials_per_supplier.png" alt="Materials per Supplier">
                </div>
            </div>
            
            <div class="card">
                <h2>Detailed Relationships</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #e0e0e0;">
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Material System</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Printing Suppliers</th>
                    </tr>
    """
    
    # Add material-supplier relationships to the table
    for material in materials:
        related_suppliers = []
        
        for supplier in printing_suppliers:
            if 'materialSystems' in supplier:
                for material_entry in supplier['materialSystems']:
                    if material_entry.get('materialID') == material['id']:
                        # Get printer information if available
                        printers = []
                        if 'printer' in material_entry:
                            for printer in material_entry['printer']:
                                if isinstance(printer, dict):
                                    printer_name = printer.get('name', 'Unknown')
                                    qual_status = printer.get('qualStatus', 'Unknown')
                                    printers.append(f"{printer_name} ({qual_status})")
                                else:
                                    printers.append(printer)
                        
                        related_suppliers.append((supplier, printers))
                        break
        
        html_content += f"""
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href="../materials/material_{material['id']}.html">{material['name']} ({material['id']})</a></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">
        """
        
        if related_suppliers:
            html_content += "<ul>"
            for supplier, printers in related_suppliers:
                printer_info = ""
                if printers:
                    printer_info = f" - Printers: {', '.join(printers)}"
                
                html_content += f"<li><a href='../suppliers/supplier_{supplier['id']}.html'>{supplier['name']} ({supplier['id']})</a>{printer_info}</li>"
            html_content += "</ul>"
        else:
            html_content += "No related suppliers"
        
        html_content += """
                        </td>
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
    with open(os.path.join(relationship_dir, "material_supplier_relationships.html"), 'w') as f:
        f.write(html_content)
    
    print(f"Material-supplier relationship visualizations generated in '{relationship_dir}/material_supplier_relationships.html'")

def generate_funding_task_relationships(data, relationship_dir):
    """Generate visualizations for funding-task relationships"""
    print("Generating funding-task relationship visualizations...")
    
    # Get funding opportunities
    funding_opportunities = data.get('fundingOpportunities', [])
    
    # Collect all tasks with funding IDs
    funded_tasks = []
    
    # Check program tasks
    for program in data.get('programs', []):
        if 'roadmap' in program and 'tasks' in program['roadmap']:
            for task in program['roadmap']['tasks']:
                if 'fundingID' in task:
                    funded_tasks.append({
                        'task': task['task'],
                        'program': program['name'],
                        'program_id': program['id'],
                        'start': task.get('start', 'N/A'),
                        'end': task.get('end', 'N/A'),
                        'status': task.get('status', 'N/A'),
                        'type': 'Program Task',
                        'fundingID': task['fundingID']
                    })
    
    # Check product tasks
    for product in data.get('products', []):
        if 'roadmap' in product and 'tasks' in product['roadmap']:
            for task in product['roadmap']['tasks']:
                if 'fundingID' in task:
                    funded_tasks.append({
                        'task': task['task'],
                        'product': product['name'],
                        'product_id': product['id'],
                        'start': task.get('start', 'N/A'),
                        'end': task.get('end', 'N/A'),
                        'status': task.get('status', 'N/A'),
                        'type': 'Product Task',
                        'fundingID': task['fundingID']
                    })
    
    # Check supplier tasks
    for supplier in data.get('printingSuppliers', []):
        if 'supplierRoadmap' in supplier and 'tasks' in supplier['supplierRoadmap']:
            for task in supplier['supplierRoadmap']['tasks']:
                if 'fundingID' in task:
                    funded_tasks.append({
                        'task': task['task'],
                        'supplier': supplier['name'],
                        'supplier_id': supplier['id'],
                        'start': task.get('start', 'N/A'),
                        'end': task.get('end', 'N/A'),
                        'status': task.get('status', 'N/A'),
                        'type': 'Supplier Task',
                        'fundingID': task['fundingID']
                    })
    
    # If no funded tasks or funding opportunities, create a simple message
    if not funded_tasks or not funding_opportunities:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Funding-Task Relationships</title>
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
                <h1>Funding-Task Relationships</h1>
                <p>No funding-task relationships found in the data.</p>
                <p><a href="../index.html">Back to Dashboard</a> | <a href="relationship_summary.html">Back to Relationship Summary</a></p>
            </div>
        </body>
        </html>
        """
        
        with open(os.path.join(relationship_dir, "funding_task_relationships.html"), 'w') as f:
            f.write(html_content)
        
        # Create a placeholder image
        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, "No funding-task relationships found", 
                 horizontalalignment='center', verticalalignment='center', fontsize=14)
        plt.axis('off')
        plt.savefig(os.path.join(relationship_dir, "funding_task_chart.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"No funding-task relationships found. Created placeholder in '{relationship_dir}/funding_task_relationships.html'")
        return
    
    # Count tasks per funding opportunity
    tasks_per_funding = {}
    for funding in funding_opportunities:
        tasks_per_funding[funding['id']] = 0
    
    for task in funded_tasks:
        funding_id = task['fundingID']
        if funding_id in tasks_per_funding:
            tasks_per_funding[funding_id] += 1
    
    # Create a bar chart showing the number of tasks per funding
    funding_names = []
    task_counts = []
    
    for funding_id, count in tasks_per_funding.items():
        funding = next((f for f in funding_opportunities if f['id'] == funding_id), None)
        if funding:
            funding_name = funding.get('name', funding.get('announcementName', 'Unknown'))
            funding_names.append(f"{funding_name} ({funding_id})")
            task_counts.append(count)
    
    # Sort by count
    sorted_indices = np.argsort(task_counts)[::-1]  # Descending order
    funding_names = [funding_names[i] for i in sorted_indices]
    task_counts = [task_counts[i] for i in sorted_indices]
    
    # Create the bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(funding_names, task_counts, color='#8c564b')
    
    # Add labels
    plt.title('Number of Tasks per Funding Opportunity')
    plt.xlabel('Funding Opportunities')
    plt.ylabel('Number of Tasks')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.0f}', ha='center', va='bottom')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "tasks_per_funding.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create a pie chart showing the distribution of task types
    task_types = {}
    for task in funded_tasks:
        task_type = task['type']
        if task_type not in task_types:
            task_types[task_type] = 0
        task_types[task_type] += 1
    
    # Create the pie chart
    plt.figure(figsize=(10, 8))
    plt.pie(task_types.values(), labels=task_types.keys(), autopct='%1.1f%%', 
            startangle=90, colors=plt.cm.Paired(range(len(task_types))))
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Distribution of Funded Task Types')
    
    # Save the figure
    plt.savefig(os.path.join(relationship_dir, "funded_task_types.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create an HTML page to display the visualizations
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Funding-Task Relationships</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2, h3, h4 {{ color: #0066cc; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .image-container {{ text-align: center; margin: 20px 0; }}
            .image-container img {{ max-width: 100%; border: 1px solid #ddd; }}
            .card {{ 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                padding: 15px; 
                margin-bottom: 20px;
                background-color: #f9f9f9;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Funding-Task Relationships</h1>
            <p>This page shows the relationships between funding opportunities and tasks in the roadmap data.</p>
            <p><a href="../index.html">Back to Dashboard</a> | <a href="relationship_summary.html">Back to Relationship Summary</a></p>
            
            <div class="card">
                <h2>Tasks per Funding Opportunity</h2>
                <p>This chart shows the number of tasks associated with each funding opportunity.</p>
                <div class="image-container">
                    <img src="tasks_per_funding.png" alt="Tasks per Funding Opportunity">
                </div>
            </div>
            
            <div class="card">
                <h2>Distribution of Funded Task Types</h2>
                <p>This chart shows the distribution of different types of tasks that receive funding.</p>
                <div class="image-container">
                    <img src="funded_task_types.png" alt="Distribution of Funded Task Types">
                </div>
            </div>
            
            <div class="card">
                <h2>Detailed Relationships</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #e0e0e0;">
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Funding Opportunity</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Tasks</th>
                    </tr>
    """
    
    # Add funding-task relationships to the table
    for funding in funding_opportunities:
        related_tasks = [task for task in funded_tasks if task['fundingID'] == funding['id']]
        funding_name = funding.get('name', funding.get('announcementName', 'Unknown'))
        
        html_content += f"""
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href="../funding/funding_{funding['id']}.html">{funding_name} ({funding['id']})</a></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">
        """
        
        if related_tasks:
            html_content += "<ul>"
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
                
                html_content += f"<li>{task['task']} ({task['type']}) - Related to: {related_link}</li>"
            html_content += "</ul>"
        else:
            html_content += "No related tasks"
        
        html_content += """
                        </td>
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
    with open(os.path.join(relationship_dir, "funding_task_relationships.html"), 'w') as f:
        f.write(html_content)
    
    print(f"Funding-task relationship visualizations generated in '{relationship_dir}/funding_task_relationships.html'") 