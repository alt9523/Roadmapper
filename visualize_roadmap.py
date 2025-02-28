import json
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Label, LabelSet, Range1d, Span, Legend, LegendItem
from bokeh.palettes import Category10, Spectral6
from bokeh.layouts import column
from bokeh.io import show
from datetime import datetime, timedelta
import os
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey

# Load the roadmap data
with open('roadmap.json', 'r') as f:
    data = json.load(f)

# Define colors for different statuses
STATUS_COLORS = {
    'Complete': '#43a047',  # Green
    'In Progress': '#ff9800',  # Orange
    'Planned': '#4a89ff'  # Blue
}

def generate_product_roadmap(product_id):
    # Find the product
    product = next((p for p in data['products'] if p['id'] == product_id), None)
    if not product:
        return None
    
    # Collect all tasks to determine height
    all_tasks = []
    for lane in ['Design', 'Manufacturing', 'M&P', 'Quality', 'Other']:
        lane_tasks = [t for t in product.get('roadmap', []) if t.get('lane', 'Other') == lane]
        all_tasks.extend(lane_tasks)
        
        # Also add material system tasks
        for material_id in product.get('materialSystems', []):
            material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
            if material and 'roadmap' in material:
                material_tasks = [t for t in material['roadmap'] if t.get('lane', 'M&P') == lane]
                all_tasks.extend(material_tasks)
    
    # Calculate appropriate height based on number of tasks
    height = max(400, len(all_tasks) * 50 + 100)
    
    # Create a figure with date x-axis
    p = figure(
        title=f"Roadmap for {product['name']} ({product['id']})",
        x_axis_type="datetime",
        width=1200,
        height=height,
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    
    # Customize appearance
    p.title.text_font_size = '16pt'
    p.xaxis.axis_label = "Timeline"
    p.yaxis.axis_label = "Tasks"
    p.grid.grid_line_alpha = 0.3
    p.background_fill_color = "#f8f9fa"
    
    # Process tasks by lane
    lanes = ['Design', 'Manufacturing', 'M&P', 'Quality', 'Other']
    y_pos = 0
    legend_items = []
    
    for lane in lanes:
        # Add lane label using ColumnDataSource
        lane_source = ColumnDataSource(data=dict(
            x=[datetime.now()],
            y=[y_pos],
            text=[f"--- {lane} ---"]
        ))
        
        # Add lane label
        p.text(x='x', y='y', text='text', source=lane_source,
               text_font_style="bold", text_align="right", text_baseline="middle")
        
        # Add lane tasks from product roadmap
        lane_tasks = [t for t in product.get('roadmap', []) if t.get('lane', 'Other') == lane]
        
        # Also add material system tasks
        for material_id in product.get('materialSystems', []):
            material = next((m for m in data['materialSystems'] if m['id'] == material_id), None)
            if material and 'roadmap' in material:
                for task in material['roadmap']:
                    if task.get('lane', 'M&P') == lane:
                        task['material'] = material['name']
                        lane_tasks.append(task)
        
        # Sort tasks by start date
        lane_tasks.sort(key=lambda x: datetime.strptime(x['start'], "%Y-%m-%d"))
        
        for task in lane_tasks:
            y_pos -= 1
            start_date = datetime.strptime(task['start'], "%Y-%m-%d")
            end_date = datetime.strptime(task['end'], "%Y-%m-%d")
            
            # Add funding type if available
            funding = f" ({task.get('fundingType', '')})" if 'fundingType' in task else ""
            material_info = f" [Material: {task.get('material', '')}]" if 'material' in task else ""
            task_name = f"{task['task']}{funding}{material_info}"
            
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
            color = STATUS_COLORS.get(task['status'], '#95a5a6')
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
                   x_offset=5, text_align="left")  # Add offset to prevent overlap
    
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
    
    # Add milestones as vertical lines
    for milestone in product.get('milestones', []):
        milestone_date = datetime.strptime(milestone['date'], "%Y-%m-%d")
        milestone_line = Span(location=milestone_date, dimension='height', 
                             line_color='red', line_dash='dashed', line_width=2)
        p.add_layout(milestone_line)
        
        # Add milestone label
        milestone_label = Label(x=milestone_date, y=0, 
                               text=milestone['name'],
                               text_color='red',
                               text_font_style='bold',
                               text_font_size='10pt',
                               angle=90,
                               angle_units='deg',
                               x_offset=10)
        p.add_layout(milestone_label)
    
    # Add program need dates as vertical lines
    for program_id in product.get('programs', []):
        program = next((p for p in data['programs'] if p['id'] == program_id), None)
        if program and 'needDate' in program:
            need_date = datetime.strptime(program['needDate'], "%Y-%m-%d")
            program_line = Span(location=need_date, dimension='height', 
                               line_color='purple', line_width=2)
            p.add_layout(program_line)
            
            # Add program label
            program_label = Label(x=need_date, y=0, 
                                 text=f"{program['name']} Need Date",
                                 text_color='purple',
                                 text_font_style='italic',
                                 text_font_size='10pt',
                                 angle=90,
                                 angle_units='deg',
                                 x_offset=5)
            p.add_layout(program_label)
    
    # Add legend for status colors
    for status, color in STATUS_COLORS.items():
        legend_items.append(LegendItem(label=status, renderers=[p.hbar(y=0, left=0, right=0, height=0, color=color)]))
    
    legend = Legend(items=legend_items, location="top_right")
    p.add_layout(legend)
    
    # Set y-range with padding
    p.y_range = Range1d(y_pos - 1, 1)
    
    # Find date range for x-axis
    all_dates = []
    for task in all_tasks:
        all_dates.append(datetime.strptime(task['start'], "%Y-%m-%d"))
        all_dates.append(datetime.strptime(task['end'], "%Y-%m-%d"))

    # Add program need dates
    for program_id in product.get('programs', []):
        program = next((prog for prog in data['programs'] if prog['id'] == program_id), None)
        if program and 'needDate' in program:
            all_dates.append(datetime.strptime(program['needDate'], "%Y-%m-%d"))

    # Add milestone dates
    for milestone in product.get('milestones', []):
        all_dates.append(datetime.strptime(milestone['date'], "%Y-%m-%d"))

    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
        # Add some padding (3 months before and after)
        min_date = min_date - timedelta(days=90)
        max_date = max_date + timedelta(days=90)
        p.x_range.start = min_date
        p.x_range.end = max_date
    
    # Output to file
    output_file(os.path.join("roadmap_visualizations", f"bokeh_product_{product_id}.html"))
    
    return p

def generate_index_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Interactive Roadmap Viewer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .product-list { margin-top: 20px; }
            .product-item { 
                padding: 10px; 
                margin-bottom: 20px; 
                background-color: #f5f5f5;
                border-radius: 5px;
            }
            .product-item h2 { 
                color: #0066cc; 
                margin-top: 0;
            }
            .product-details { margin: 10px 0; color: #666; }
            .product-link {
                display: inline-block;
                margin-top: 10px;
                padding: 8px 15px;
                background-color: #0066cc;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
            .product-link:hover {
                background-color: #004c99;
            }
        </style>
    </head>
    <body>
        <h1>Interactive Roadmap Viewer</h1>
        <div class="product-list">
    """
    
    for product in data['products']:
        product_id = product['id']
        html += f"""
        <div class="product-item">
            <h2>{product['name']} ({product_id})</h2>
            <div class="product-details">
                <strong>TRL:</strong> {product.get('trl', 'N/A')} | 
                <strong>Programs:</strong> {', '.join(product.get('programs', []))} |
                <strong>Material Systems:</strong> {', '.join(product.get('materialSystems', []))}
            </div>
            <a href="bokeh_product_{product_id}.html" class="product-link">View Roadmap</a>
        </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

# Create output directory if it doesn't exist
output_dir = "roadmap_visualizations"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Generate roadmaps for each product
for product in data['products']:
    p = generate_product_roadmap(product['id'])
    if p:
        save(p)

# Generate index page
index_html = generate_index_page()
with open(os.path.join(output_dir, "index.html"), "w") as f:
    f.write(index_html)

print(f"Bokeh roadmap visualizations generated in the '{output_dir}' directory.")
print(f"Open '{output_dir}/index.html' in your browser to view the roadmaps.")

def create_simple_sankey():
    # Create a figure
    plt.figure(figsize=(15, 10))
    
    # Initialize the Sankey diagram
    sankey = Sankey(ax=plt.gca(), scale=0.01, offset=0.2, head_angle=120, margin=0.4, shoulder=0)
    
    # Collect all the flows
    program_to_product = {}
    product_to_material = {}
    material_to_supplier = {}
    
    # Count program to product flows
    for product in data['products']:
        for program_id in product.get('programs', []):
            if program_id not in program_to_product:
                program_to_product[program_id] = 0
            program_to_product[program_id] += 1
    
    # Count product to material flows
    for product in data['products']:
        for material_id in product.get('materialSystems', []):
            key = (product['id'], material_id)
            if key not in product_to_material:
                product_to_material[key] = 0
            product_to_material[key] += 1
    
    # Count material to supplier flows
    for supplier in data['suppliers']:
        for material_id in supplier.get('materials', []):
            key = (material_id, supplier['id'])
            if key not in material_to_supplier:
                material_to_supplier[key] = 0
            material_to_supplier[key] += 1
    
    # Add the first stage: Programs to Products
    program_names = [p['name'] for p in data['programs']]
    program_flows = [-sum(program_to_product.values())]  # Total outflow
    
    # Add the diagram
    sankey.add(flows=program_flows, 
               labels=['Programs'],
               orientations=[0],
               pathlengths=[0.25],
               facecolor='#1f77b4')
    
    # Add the second stage: Products
    product_inflow = sum(program_to_product.values())
    product_outflow = sum(len(p.get('materialSystems', [])) for p in data['products'])
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
    material_outflow = sum(len(s.get('materials', [])) for s in data['suppliers'])
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
    plt.savefig(os.path.join(output_dir, "sankey_diagram.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create a more detailed network graph as an alternative
    create_network_graph()
    
    print(f"Sankey diagram generated in '{output_dir}/sankey_diagram.png'")
    print(f"Network graph generated in '{output_dir}/network_graph.png'")

def create_network_graph():
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add program nodes
    for program in data['programs']:
        G.add_node(program['id'], label=program['name'], type='program', layer=0)
    
    # Add product nodes
    for product in data['products']:
        G.add_node(product['id'], label=product['name'], type='product', layer=1)
        
        # Add edges from programs to products
        for program_id in product.get('programs', []):
            G.add_edge(program_id, product['id'], weight=2)
    
    # Add material system nodes
    for material in data['materialSystems']:
        G.add_node(material['id'], label=material['name'], type='material', layer=2)
        
        # Add edges from products to materials
        for product in data['products']:
            if material['id'] in product.get('materialSystems', []):
                G.add_edge(product['id'], material['id'], weight=2)
    
    # Add supplier nodes
    for supplier in data['suppliers']:
        G.add_node(supplier['id'], label=supplier['name'], type='supplier', layer=3)
        
        # Add edges from materials to suppliers
        for material_id in supplier.get('materials', []):
            G.add_edge(material_id, supplier['id'], weight=2)
    
    # Create the figure with a white background
    plt.figure(figsize=(20, 12), facecolor='white')
    
    # Use the 'layer' attribute directly instead of a lambda function
    pos = nx.multipartite_layout(G, subset_key='layer', align='vertical')
    
    # Adjust vertical positions to avoid overlapping
    layer_counts = [0, 0, 0, 0]
    for node in G.nodes():
        layer = G.nodes[node]['layer']
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
        else:  # supplier
            node_colors.append('#d62728')  # Red
            node_sizes.append(500)
    
    # Draw edges with curved arrows
    nx.draw_networkx_edges(
        G, pos, 
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
    plt.text(0.33, 1.05, "Products", fontsize=16, ha='center', fontweight='bold')
    plt.text(0.67, 1.05, "Material Systems", fontsize=16, ha='center', fontweight='bold')
    plt.text(1.0, 1.05, "Suppliers", fontsize=16, ha='center', fontweight='bold')
    
    # Add a legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#1f77b4', markersize=15, label='Programs'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff7f0e', markersize=15, label='Products'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ca02c', markersize=15, label='Material Systems'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#d62728', markersize=15, label='Suppliers')
    ]
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4)
    
    # Add title and remove axes
    plt.title('Roadmap Relationships Network', fontsize=20, pad=20)
    plt.axis('off')
    
    # Add a grid background to separate the columns
    plt.axvline(x=0.165, color='lightgray', linestyle='--', alpha=0.5)
    plt.axvline(x=0.5, color='lightgray', linestyle='--', alpha=0.5)
    plt.axvline(x=0.835, color='lightgray', linestyle='--', alpha=0.5)
    
    # Save the figure with high resolution
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "network_graph.png"), dpi=300, bbox_inches='tight')
    
    # Also save as SVG for better quality
    plt.savefig(os.path.join(output_dir, "network_graph.svg"), format='svg', bbox_inches='tight')
    
    plt.close()
    
    # Update the index.html to include the network graph
    update_index_with_network_graph()

def update_index_with_network_graph():
    """Update the index.html to include the network graph"""
    index_path = os.path.join(output_dir, "index.html")
    
    try:
        with open(index_path, 'r') as f:
            content = f.read()
        
        # Add network graph section before the closing body tag
        network_section = """
        <div style="margin-top: 30px; padding: 20px; background-color: #f5f5f5; border-radius: 5px;">
            <h2>Relationship Network</h2>
            <p>This diagram shows the relationships between Programs, Products, Material Systems, and Suppliers.</p>
            <img src="network_graph.png" style="max-width: 100%; margin-top: 15px; border: 1px solid #ddd;" alt="Relationship Network">
            <p style="margin-top: 10px;"><a href="sankey_diagram.png" style="color: #0066cc;">View Sankey Flow Diagram</a></p>
        </div>
        """
        
        updated_content = content.replace('</body>', f'{network_section}\n</body>')
        
        with open(index_path, 'w') as f:
            f.write(updated_content)
            
    except Exception as e:
        print(f"Error updating index.html: {e}")

# Run the script
create_simple_sankey()