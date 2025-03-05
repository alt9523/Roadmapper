import os
import json
import matplotlib.pyplot as plt

def generate_sankey_diagram(data, relationship_dir):
    """Generate a Sankey diagram showing flows between different entities with aligned columns"""
    print("Generating Sankey diagram...")
    
    # Create a figure with a larger size for better visibility
    plt.figure(figsize=(20, 12), facecolor='white')
    
    # Count flows between entities
    supplier_to_material_count = {}
    material_to_product_count = {}
    product_to_program_count = {}
    
    # Get all suppliers, materials, products, and programs
    suppliers = data.get('printingSuppliers', []) + data.get('postProcessingSuppliers', [])
    materials = data.get('materialSystems', [])
    products = data.get('products', [])
    programs = data.get('programs', [])
    
    # Create dictionaries to store entity names by ID
    supplier_names = {s['id']: s['name'] for s in suppliers}
    material_names = {m['id']: m['name'] for m in materials}
    product_names = {p['id']: p['name'] for p in products}
    program_names = {p['id']: p['name'] for p in programs}
    
    # Count supplier to material flows
    for supplier in data.get('printingSuppliers', []):
        if 'materialSystems' in supplier:
            for material_entry in supplier.get('materialSystems', []):
                material_id = material_entry.get('materialID')
                if material_id:
                    key = (supplier['id'], material_id)
                    supplier_to_material_count[key] = supplier_to_material_count.get(key, 0) + 1
    
    # Count material to product flows
    for product in products:
        for material_entry in product.get('materialSystems', []):
            material_id = None
            if isinstance(material_entry, str):
                material_id = material_entry
            elif isinstance(material_entry, dict) and 'materialID' in material_entry:
                material_id = material_entry['materialID']
                
            if material_id:
                key = (material_id, product['id'])
                material_to_product_count[key] = material_to_product_count.get(key, 0) + 1
    
    # Count product to program flows
    for product in products:
        for program_entry in product.get('programs', []):
            program_id = None
            if isinstance(program_entry, str):
                program_id = program_entry
            elif isinstance(program_entry, dict) and 'programID' in program_entry:
                program_id = program_entry['programID']
                
            if program_id:
                key = (product['id'], program_id)
                product_to_program_count[key] = product_to_program_count.get(key, 0) + 1
    
    # Create lists for Sankey diagram
    all_nodes = []
    all_links = []
    
    # Add supplier nodes with type information
    for supplier in suppliers:
        all_nodes.append({
            'name': supplier['name'],
            'color': '#8c564b',  # Brown
            'type': 'supplier'
        })
    
    # Add material nodes with type information
    for material in materials:
        all_nodes.append({
            'name': material['name'],
            'color': '#2ca02c',  # Green
            'type': 'material'
        })
    
    # Add product nodes with type information
    for product in products:
        all_nodes.append({
            'name': product['name'],
            'color': '#ff7f0e',  # Orange
            'type': 'product'
        })
    
    # Add program nodes with type information
    for program in programs:
        all_nodes.append({
            'name': program['name'],
            'color': '#1f77b4',  # Blue
            'type': 'program'
        })
    
    # Add supplier to material links
    for (supplier_id, material_id), value in supplier_to_material_count.items():
        if supplier_id in supplier_names and material_id in material_names:
            all_links.append({
                'source': supplier_names[supplier_id],
                'target': material_names[material_id],
                'value': value,
                'color': '#d6c1b0'  # Light brown
            })
    
    # Add material to product links
    for (material_id, product_id), value in material_to_product_count.items():
        if material_id in material_names and product_id in product_names:
            all_links.append({
                'source': material_names[material_id],
                'target': product_names[product_id],
                'value': value,
                'color': '#a3d6a3'  # Light green
            })
    
    # Add product to program links
    for (product_id, program_id), value in product_to_program_count.items():
        if product_id in product_names and program_id in program_names:
            all_links.append({
                'source': product_names[product_id],
                'target': program_names[program_id],
                'value': value,
                'color': '#ffcc99'  # Light orange
            })
    
    # Create HTML file with JavaScript for Sankey diagram
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relationship Flow Diagram (Sankey)</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <script src="https://unpkg.com/d3-sankey@0.12.3/dist/d3-sankey.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2, h3, h4 {{ color: #0066cc; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            #sankey-diagram {{ width: 100%; height: 600px; }}
            .node rect {{ opacity: 0.9; }}
            .node text {{ font-size: 12px; font-weight: bold; }}
            .link {{ opacity: 0.7; }}
            .link:hover {{ opacity: 0.9; }}
            .column-header {{ font-size: 16px; font-weight: bold; text-anchor: middle; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Relationship Flow Diagram (Sankey)</h1>
            <p>This visualization shows the flow of relationships from Suppliers to Materials to Products to Programs.</p>
            <p><a href="../index.html">Back to Dashboard</a> | <a href="relationship_summary.html">Back to Relationship Summary</a></p>
            
            <div id="sankey-diagram"></div>
            
            <script>
                // Data for the Sankey diagram
                const nodes = {json.dumps(all_nodes)};
                const links = {json.dumps(all_links)};
                
                // Set up the dimensions and margins
                const margin = {{top: 50, right: 50, bottom: 20, left: 50}};
                const width = 1100 - margin.left - margin.right;
                const height = 600 - margin.top - margin.bottom;
                
                // Create the SVG container
                const svg = d3.select("#sankey-diagram")
                    .append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
                
                // Define fixed column positions
                const columnPositions = {{
                    'supplier': 0,
                    'material': width / 3,
                    'product': 2 * width / 3,
                    'program': width - 20
                }};
                
                // Group nodes by type
                const nodesByType = {{
                    'supplier': [],
                    'material': [],
                    'product': [],
                    'program': []
                }};
                
                nodes.forEach(node => {{
                    if (node.type) {{
                        nodesByType[node.type].push(node);
                    }}
                }});
                
                // Calculate y positions for each node within its column
                Object.keys(nodesByType).forEach(type => {{
                    const typeNodes = nodesByType[type];
                    const totalNodes = typeNodes.length;
                    const spacing = height / (totalNodes + 1);
                    
                    typeNodes.forEach((node, i) => {{
                        node.x0 = columnPositions[type];
                        node.x1 = node.x0 + 20;  // Node width = 20
                        node.y0 = (i + 1) * spacing - 10;  // Center node at position
                        node.y1 = node.y0 + 20;  // Node height based on value
                    }});
                }});
                
                // Create a node map for quick lookup
                const nodeMap = {{}};
                nodes.forEach(node => {{
                    nodeMap[node.name] = node;
                }});
                
                // Process links to connect to the positioned nodes
                const processedLinks = links.map(link => {{
                    const sourceNode = nodeMap[link.source];
                    const targetNode = nodeMap[link.target];
                    
                    // Adjust the height of nodes based on number of connections
                    const linkHeight = Math.max(5, link.value * 3);
                    sourceNode.y1 = Math.max(sourceNode.y1, sourceNode.y0 + linkHeight);
                    targetNode.y1 = Math.max(targetNode.y1, targetNode.y0 + linkHeight);
                    
                    return {{
                        source: sourceNode,
                        target: targetNode,
                        value: link.value,
                        color: link.color
                    }};
                }});
                
                // Draw the links
                const link = svg.append("g")
                    .selectAll(".link")
                    .data(processedLinks)
                    .enter()
                    .append("path")
                    .attr("class", "link")
                    .attr("d", d => {{
                        // Calculate source and target points
                        const sourceX = d.source.x1;
                        const sourceY = (d.source.y0 + d.source.y1) / 2;
                        const targetX = d.target.x0;
                        const targetY = (d.target.y0 + d.target.y1) / 2;
                        
                        // Create a curved path
                        return `M${{sourceX}},${{sourceY}}
                                C${{sourceX + (targetX - sourceX) / 2}},${{sourceY}}
                                 ${{sourceX + (targetX - sourceX) / 2}},${{targetY}}
                                 ${{targetX}},${{targetY}}`;
                    }})
                    .attr("stroke", d => d.color)
                    .attr("stroke-width", d => Math.max(2, d.value * 2))
                    .attr("fill", "none")
                    .style("opacity", 0.7)
                    .on("mouseover", function() {{ d3.select(this).style("opacity", 0.9); }})
                    .on("mouseout", function() {{ d3.select(this).style("opacity", 0.7); }});
                
                // Add hover tooltips to links
                link.append("title")
                    .text(d => `${{d.source.name}} -> ${{d.target.name}}\\nValue: ${{d.value}}`);
                
                // Draw the nodes
                const node = svg.append("g")
                    .selectAll(".node")
                    .data(nodes)
                    .enter()
                    .append("g")
                    .attr("class", "node")
                    .attr("transform", d => `translate(${{d.x0}},${{d.y0}})`);
                
                // Add rectangles for the nodes
                node.append("rect")
                    .attr("height", d => d.y1 - d.y0)
                    .attr("width", d => d.x1 - d.x0)
                    .attr("fill", d => d.color)
                    .attr("stroke", "#000")
                    .attr("stroke-width", 1)
                    .style("opacity", 0.9);
                
                // Add labels to the nodes
                node.append("text")
                    .attr("x", d => d.type === 'program' ? -6 : d.x1 - d.x0 + 6)
                    .attr("y", d => (d.y1 - d.y0) / 2)
                    .attr("dy", "0.35em")
                    .attr("text-anchor", d => d.type === 'program' ? "end" : "start")
                    .text(d => d.name)
                    .style("font-size", "12px")
                    .style("font-weight", "bold")
                    .style("pointer-events", "none");
                
                // Add column headers
                const headers = [
                    {{ x: columnPositions.supplier + 10, y: -30, text: "Suppliers" }},
                    {{ x: columnPositions.material + 10, y: -30, text: "Materials" }},
                    {{ x: columnPositions.product + 10, y: -30, text: "Products" }},
                    {{ x: columnPositions.program + 10, y: -30, text: "Programs" }}
                ];
                
                svg.selectAll(".column-header")
                    .data(headers)
                    .enter()
                    .append("text")
                    .attr("class", "column-header")
                    .attr("x", d => d.x)
                    .attr("y", d => d.y)
                    .attr("text-anchor", "middle")
                    .text(d => d.text);
            </script>
            
            <h2>Explanation</h2>
            <p>The Sankey diagram shows the flow of relationships from Suppliers to Materials to Products to Programs. The width of each flow represents the number of connections between entities.</p>
            
            <ul>
                <li><strong style="color: #8c564b;">Suppliers</strong>: Suppliers providing materials and services</li>
                <li><strong style="color: #2ca02c;">Materials</strong>: Material systems used in products</li>
                <li><strong style="color: #ff7f0e;">Products</strong>: Components and systems being developed</li>
                <li><strong style="color: #1f77b4;">Programs</strong>: Space missions and projects</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    # Write the HTML file
    with open(os.path.join(relationship_dir, "sankey_diagram.html"), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Create a static image version using matplotlib for thumbnails
    plt.figure(figsize=(15, 8))
    plt.text(0.5, 0.5, "Interactive Sankey Diagram\n(Open HTML file to view)", 
             ha='center', va='center', fontsize=20)
    plt.axis('off')
    plt.savefig(os.path.join(relationship_dir, "sankey_diagram.png"), dpi=100, bbox_inches='tight')
    plt.close()
    
    print(f"Sankey diagram generated in '{relationship_dir}/sankey_diagram.html'") 