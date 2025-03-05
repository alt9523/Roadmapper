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
import json

# Import the aligned Sankey diagram generator
from modules.relationship_viz_aligned import generate_sankey_diagram

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
    
    # Convert positions to a format Bokeh can use
    # Bokeh's plotting is reversed compared to nx/matplotlib, so we need to adjust
    node_x = []
    node_y = []
    node_ids = []
    node_labels = []
    node_types = []
    node_sizes = []
    node_colors = []
    for node in G.nodes():
        node_ids.append(node)
        node_labels.append(G.nodes[node]['label'])
        node_types.append(G.nodes[node]['type'])
        node_x.append(pos[node][0] * 1000)  # Scale for better visualization
        node_y.append(pos[node][1] * 600)   # Scale for better visualization
        
        # Set node sizes and colors based on type
        node_type = G.nodes[node]['type']
        if node_type == 'program':
            node_colors.append('#1f77b4')  # Blue
            node_sizes.append(15)
        elif node_type == 'product':
            node_colors.append('#ff7f0e')  # Orange
            node_sizes.append(13)
        elif node_type == 'material':
            node_colors.append('#2ca02c')  # Green
            node_sizes.append(11)
        elif node_type == 'supplier':
            node_colors.append('#d62728')  # Red
            node_sizes.append(9)
        elif node_type == 'post-supplier':
            node_colors.append('#9467bd')  # Purple
            node_sizes.append(9)
        elif node_type == 'funding':
            node_colors.append('#8c564b')  # Brown
            node_sizes.append(11)
        else:
            node_colors.append('#7f7f7f')  # Gray
            node_sizes.append(8)
    
    # Create edge data
    edge_x0 = []
    edge_y0 = []
    edge_x1 = []
    edge_y1 = []
    edge_colors = []
    edge_widths = []
    edge_dashes = []
    edge_alphas = []
    
    for edge in G.edges(data=True):
        start, end, attrs = edge
        
        # Get positions of start and end nodes
        x0, y0 = pos[start][0] * 1000, pos[start][1] * 600
        x1, y1 = pos[end][0] * 1000, pos[end][1] * 600
        
        # Add a slight curve by offsetting the x,y values
        # For a quadratic curve, we need a control point
        control_x = (x0 + x1) / 2 + (y1 - y0) * 0.1  # Offset in x direction based on y diff
        control_y = (y0 + y1) / 2 + (x1 - x0) * 0.1  # Offset in y direction based on x diff
        
        # Store edge data
        edge_x0.append(x0)
        edge_y0.append(y0)
        edge_x1.append(x1)
        edge_y1.append(y1)
        
        # Set edge attributes based on style
        style = attrs.get('style', 'solid')
        if style == 'dashed':
            edge_colors.append('gray')
            edge_widths.append(1.2)
            edge_dashes.append([5, 3])
            edge_alphas.append(0.7)
        elif style == 'dotted':
            edge_colors.append('gray')
            edge_widths.append(1.2)
            edge_dashes.append([2, 2])
            edge_alphas.append(0.7)
        else:
            edge_colors.append('gray')
            edge_widths.append(1.5)
            edge_dashes.append([])
            edge_alphas.append(0.7)
    
    # Create a Bokeh figure
    # Set up the output file
    output_file(os.path.join(relationship_dir, "network_graph.html"))
    
    # Create a plot with a transparent background
    p = figure(
        title="Roadmap Relationships Network",
        width=1200, 
        height=800,
        x_range=(-50, 1050),
        y_range=(-350, 350),
        tools="pan,wheel_zoom,box_zoom,reset,save",
        toolbar_location="right",
    )
    
    # Set plot properties
    p.title.text_font_size = "20px"
    p.axis.visible = False
    p.grid.visible = False
    p.outline_line_color = None
    
    # Add hover tool for nodes
    node_hover = HoverTool(
        tooltips=[
            ("ID", "@id"),
            ("Name", "@label"),
            ("Type", "@type")
        ],
        renderers=[],  # Will be set later
    )
    p.add_tools(node_hover)
    
    # Create ColumnDataSource for nodes
    node_source = ColumnDataSource(data=dict(
        x=node_x,
        y=node_y,
        id=node_ids,
        label=node_labels,
        type=node_types,
        size=node_sizes,
        color=node_colors
    ))
    
    # Add nodes to the plot
    node_renderer = p.scatter(
        x="x", y="y", 
        source=node_source,
        size="size", 
        fill_color="color", 
        line_color="black",
        line_width=1,
        alpha=0.9,
        marker="circle"
    )
    
    # Add hover tool to node renderer
    node_hover.renderers = [node_renderer]
    
    # Add edges
    for i in range(len(edge_x0)):
        # Create a quadratic Bezier curve for each edge
        # Use line_dash and line_width from our calculated arrays
        p.line(
            [edge_x0[i], (edge_x0[i] + edge_x1[i]) / 2, edge_x1[i]],
            [edge_y0[i], (edge_y0[i] + edge_y1[i]) / 2, edge_y1[i]],
            line_color=edge_colors[i],
            line_width=edge_widths[i],
            line_dash=edge_dashes[i],
            line_alpha=edge_alphas[i]
        )
        
        # Add an arrow at the end of the edge
        # Create a small triangle at the end
        arrow_length = 10
        arrow_width = 5
        
        # Calculate direction vector
        dx = edge_x1[i] - edge_x0[i]
        dy = edge_y1[i] - edge_y0[i]
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            dx = dx / length
            dy = dy / length
        
        # Ensure we place the arrow near the end but not exactly at it (for curved edges)
        factor = 0.9
        tip_x = edge_x0[i] + dx * length * factor
        tip_y = edge_y0[i] + dy * length * factor
        
        # Calculate perpendicular vector for arrow width
        perp_dx = -dy
        perp_dy = dx
        
        # Triangle points
        x0, y0 = tip_x, tip_y
        x1, y1 = tip_x - arrow_length * dx + arrow_width * perp_dx, tip_y - arrow_length * dy + arrow_width * perp_dy
        x2, y2 = tip_x - arrow_length * dx - arrow_width * perp_dx, tip_y - arrow_length * dy - arrow_width * perp_dy
        
        # Add the arrow as a triangle
        p.scatter(
            x=[x0, x1, x2],
            y=[y0, y1, y2],
            marker="triangle",
            fill_color=edge_colors[i],
            line_color=None,
            fill_alpha=edge_alphas[i],
            size=8
        )
    
    # Add column headers for the different layers
    header_labels = ["Programs", "Products", "Material Systems", "Suppliers", "Funding"]
    header_xs = [0, 250, 500, 750, 1000]  # Adjust these based on the x-range
    
    for i, label in enumerate(header_labels):
        # Add header text
        header_text = Label(
            x=header_xs[i], y=320,
            text=label,
            text_font_size="16px",
            text_align="center",
            text_baseline="middle",
            text_font_style="bold"
        )
        p.add_layout(header_text)
        
        # Add vertical separator line
        if i > 0:
            separator = Span(
                location=(header_xs[i-1] + header_xs[i])/2,
                dimension='height',
                line_color='lightgray',
                line_dash='dashed',
                line_width=1
            )
            p.add_layout(separator)
    
    # Add a legend
    legend_items = []
    for node_type, color, label in [
        ('program', '#1f77b4', 'Programs'),
        ('product', '#ff7f0e', 'Products'),
        ('material', '#2ca02c', 'Material Systems'),
        ('supplier', '#d62728', 'Printing Suppliers'),
        ('post-supplier', '#9467bd', 'Post-Processing Suppliers'),
        ('funding', '#8c564b', 'Funding Opportunities')
    ]:
        # Create a renderer for this legend item (just a dummy scatter point outside the visible area)
        dummy_renderer = p.scatter(
            x=[-100], y=[-100],  # Outside visible area
            size=10,
            color=color,
            alpha=0.8,
            marker="circle"
        )
        # Add to legend items
        legend_items.append((label, [dummy_renderer]))
    
    # Create and add the legend
    legend = Legend(items=legend_items, location="center")
    legend.orientation = "horizontal"
    legend.spacing = 20
    p.add_layout(legend, 'below')
    
    # Export the network graph as a static image for the dashboard
    # We need to use a different approach since Bokeh doesn't directly support exporting as PNG
    # We'll generate an HTML with instructions to save the image
    
    # Save the interactive Bokeh visualization
    save(p)
    
    # Create a simple static version as PNG for the dashboard
    # Use nx.draw to create a static image
    plt.figure(figsize=(12, 8), facecolor='white')
    
    # Draw nodes with colors and sizes based on type
    for node_type, color in [
        ('program', '#1f77b4'),
        ('product', '#ff7f0e'),
        ('material', '#2ca02c'),
        ('supplier', '#d62728'),
        ('post-supplier', '#9467bd'),
        ('funding', '#8c564b')
    ]:
        nodelist = [node for node in G.nodes() if G.nodes[node]['type'] == node_type]
        if nodelist:
            size = 800 if node_type == 'program' else 700 if node_type == 'product' else 600
            nx.draw_networkx_nodes(
                G, pos, 
                nodelist=nodelist,
                node_size=size, 
                node_color=color, 
                alpha=0.9,
                edgecolors='black',
                linewidths=1
            )
    
    # Draw edges with different styles
    for style, line_style in [('dashed', 'dashed'), ('dotted', 'dotted'), (None, 'solid')]:
        edgelist = [(u, v) for u, v, d in G.edges(data=True) if d.get('style', None) == style]
        if edgelist:
            nx.draw_networkx_edges(
                G, pos, 
                edgelist=edgelist,
                width=1.2, 
                alpha=0.7, 
                edge_color='gray', 
                arrows=True,
                arrowsize=15,
                style=line_style,
                connectionstyle='arc3,rad=0.1'  # Curved edges
            )
    
    # Draw labels with a white background
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
    
    # Add title and remove axes
    plt.title('Roadmap Relationships Network', fontsize=20, pad=20)
    plt.axis('off')
    
    # Save the static image
    plt.savefig(os.path.join(relationship_dir, "network_graph.png"), dpi=300, bbox_inches='tight')
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
            .btn {{
                display: inline-block;
                padding: 8px 15px;
                background-color: #0066cc;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                transition: background-color 0.3s ease;
                margin: 10px;
            }}
            .btn:hover {{ background-color: #004c99; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Relationship Network Graph</h1>
            <p>This visualization shows the relationships between different entities in the roadmap data.</p>
            <p><a href="../index.html">Back to Dashboard</a> | <a href="relationship_summary.html">Back to Relationship Summary</a></p>
            
            <div class="image-container">
                <iframe src="network_graph.html" width="100%" height="800px" frameborder="0"></iframe>
            </div>
            
            <div style="text-align: center;">
                <a href="network_graph.html" class="btn" target="_blank">Open Interactive Graph in New Tab</a>
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
            
            <p>Use the interactive controls to explore the network:</p>
            <ul>
                <li><strong>Pan</strong>: Click and drag to move around</li>
                <li><strong>Zoom</strong>: Use mouse wheel or zoom tools</li>
                <li><strong>Hover</strong>: Hover over nodes to see details</li>
                <li><strong>Reset</strong>: Reset the view to default</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(relationship_dir, "network_graph_viewer.html"), 'w') as f:
        f.write(html_content)
    
    print(f"Network graph generated in '{relationship_dir}/network_graph.html'")

def generate_sankey_diagram(data, relationship_dir):
    """Generate a Sankey diagram showing flows between different entities with aligned columns"""
    # Import the aligned Sankey diagram generator
    from modules.relationship_viz_aligned import generate_sankey_diagram as generate_aligned_sankey
    
    # Call the aligned version
    generate_aligned_sankey(data, relationship_dir)

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
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h3, h4 {{ color: #2c3e50; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                padding: 15px; 
                margin-bottom: 20px;
                background-color: #f9f9f9;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
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
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 15px; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            thead tr {{ 
                background-color: #3498db; 
                color: white; 
            }}
            th, td {{ 
                padding: 12px; 
                text-align: left; 
                border: 1px solid #ddd; 
            }}
            tbody tr:nth-child(even) {{ 
                background-color: #f2f9ff; 
            }}
            tbody tr:nth-child(odd) {{ 
                background-color: #ffffff; 
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
