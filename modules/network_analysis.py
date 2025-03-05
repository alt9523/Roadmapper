"""
Advanced Network Analysis Module for Roadmap Visualizations

This module provides advanced network analysis features including:
1. Centrality metrics
2. Dependency chains visualization
3. Impact analysis for changes or delays
"""

import os
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, Range1d, Label, Div, Tabs, Panel
from bokeh.layouts import column, row, gridplot
from bokeh.palettes import Spectral5, Category10

def generate_advanced_network_analysis(data, output_dir):
    """Generate advanced network analysis visualizations"""
    print("Generating advanced network analysis visualizations...")
    
    # Create advanced network analysis directory
    network_dir = os.path.join(output_dir, "network_analysis")
    if not os.path.exists(network_dir):
        os.makedirs(network_dir)
    
    # Build the network graph
    G = build_network_graph(data)
    
    # Generate centrality metrics visualization
    generate_centrality_metrics(G, data, network_dir)
    
    # Generate dependency chains visualization
    generate_dependency_chains(G, data, network_dir)
    
    # Generate impact analysis visualization
    generate_impact_analysis(G, data, network_dir)
    
    # Generate summary page
    generate_network_analysis_summary(G, data, network_dir)
    
    print(f"Advanced network analysis visualizations generated in '{network_dir}'")
    
    # Return the path to the summary page for linking from the main dashboard
    return os.path.join("network_analysis", "index.html")

def build_network_graph(data):
    """Build a comprehensive network graph from the roadmap data"""
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add program nodes
    for program in data.get('programs', []):
        G.add_node(program['id'], 
                   label=program['name'], 
                   type='program',
                   layer=0,
                   details=program)
    
    # Add product nodes
    for product in data.get('products', []):
        G.add_node(product['id'], 
                   label=product['name'], 
                   type='product',
                   layer=1,
                   details=product)
        
        # Add edges from programs to products
        for program_entry in product.get('programs', []):
            if isinstance(program_entry, str):
                program_id = program_entry
            elif isinstance(program_entry, dict) and 'programID' in program_entry:
                program_id = program_entry['programID']
            else:
                continue
                
            G.add_edge(program_id, product['id'], 
                      weight=2, 
                      relationship_type='uses')
    
    # Add material system nodes
    for material in data.get('materialSystems', []):
        G.add_node(material['id'], 
                   label=material['name'], 
                   type='material',
                   layer=2,
                   details=material)
        
        # Add edges from products to materials
        for product in data.get('products', []):
            for material_entry in product.get('materialSystems', []):
                if isinstance(material_entry, str) and material_entry == material['id']:
                    G.add_edge(product['id'], material['id'], 
                              weight=2, 
                              relationship_type='uses_material')
                elif isinstance(material_entry, dict) and material_entry.get('materialID') == material['id']:
                    G.add_edge(product['id'], material['id'], 
                              weight=2, 
                              relationship_type='uses_material')
    
    # Add supplier nodes (printing suppliers)
    for supplier in data.get('printingSuppliers', []):
        G.add_node(supplier['id'], 
                   label=supplier['name'], 
                   type='supplier',
                   layer=3,
                   details=supplier)
        
        # Add edges from materials to suppliers
        if 'materialSystems' in supplier:
            for material_entry in supplier['materialSystems']:
                material_id = material_entry.get('materialID')
                if material_id:
                    G.add_edge(material_id, supplier['id'], 
                              weight=2, 
                              relationship_type='supplied_by')
    
    # Add supplier nodes (post-processing suppliers)
    for supplier in data.get('postProcessingSuppliers', []):
        G.add_node(supplier['id'], 
                   label=supplier['name'], 
                   type='post-supplier',
                   layer=3,
                   details=supplier)
        
        # Add edges from products to post-processing suppliers
        for product in data.get('products', []):
            if 'postProcessingSuppliers' in product:
                for pp in product['postProcessingSuppliers']:
                    if 'supplier' in pp and supplier['id'] in pp['supplier']:
                        G.add_edge(product['id'], supplier['id'], 
                                  weight=1, 
                                  style='dashed',
                                  relationship_type='post_processed_by')
    
    # Add funding opportunity nodes
    if 'fundingOpportunities' in data:
        for funding in data['fundingOpportunities']:
            funding_name = funding.get('name', funding.get('announcementName', 'Unknown'))
            G.add_node(funding['id'], 
                       label=funding_name, 
                       type='funding',
                       layer=4,
                       details=funding)
            
            # Add edges from funding to tasks with fundingID
            # Check program tasks
            for program in data.get('programs', []):
                if 'roadmap' in program and isinstance(program['roadmap'], list):
                    for task in program['roadmap']:
                        if task.get('fundingType') == funding['pursuitType']:
                            G.add_edge(funding['id'], program['id'], 
                                      weight=1, 
                                      style='dotted',
                                      relationship_type='funds')
                
                # Also check if roadmap has a tasks list (different structure)
                if 'roadmap' in program and isinstance(program['roadmap'], dict) and 'tasks' in program['roadmap']:
                    for task in program['roadmap']['tasks']:
                        if task.get('fundingType') == funding['pursuitType']:
                            G.add_edge(funding['id'], program['id'], 
                                      weight=1, 
                                      style='dotted',
                                      relationship_type='funds')
            
            # Check product tasks
            for product in data.get('products', []):
                if 'roadmap' in product and isinstance(product['roadmap'], list):
                    for task in product['roadmap']:
                        if task.get('fundingType') == funding['pursuitType']:
                            G.add_edge(funding['id'], product['id'], 
                                      weight=1, 
                                      style='dotted',
                                      relationship_type='funds')
    
    return G

def generate_centrality_metrics(G, data, network_dir):
    """Generate visualization of centrality metrics for the network"""
    print("Generating centrality metrics visualization...")
    
    # Calculate various centrality metrics
    degree_centrality = nx.degree_centrality(G)
    in_degree_centrality = nx.in_degree_centrality(G)
    out_degree_centrality = nx.out_degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    
    # Try to calculate eigenvector centrality, but handle disconnected graphs
    try:
        eigenvector_centrality = nx.eigenvector_centrality_numpy(G)
    except nx.NetworkXException:
        print("Network is disconnected. Calculating eigenvector centrality per component...")
        eigenvector_centrality = {}
        
        # Calculate for each weakly connected component
        for component in nx.weakly_connected_components(G):
            subgraph = G.subgraph(component)
            # If component has only one node, assign a value of 1
            if len(component) == 1:
                node = list(component)[0]
                eigenvector_centrality[node] = 1.0
            else:
                try:
                    # Try to calculate eigenvector centrality for the component
                    component_centrality = nx.eigenvector_centrality_numpy(subgraph)
                    eigenvector_centrality.update(component_centrality)
                except:
                    # If still fails, assign default values
                    for node in component:
                        eigenvector_centrality[node] = 0.01
        
        # Normalize values
        if eigenvector_centrality:
            max_val = max(eigenvector_centrality.values())
            if max_val > 0:
                for node in eigenvector_centrality:
                    eigenvector_centrality[node] /= max_val
    
    # Prepare data for visualization
    centrality_data = []
    for node in G.nodes():
        node_type = G.nodes[node]['type']
        node_label = G.nodes[node]['label']
        
        centrality_data.append({
            'id': node,
            'label': node_label,
            'type': node_type,
            'degree': degree_centrality[node],
            'in_degree': in_degree_centrality[node],
            'out_degree': out_degree_centrality[node],
            'betweenness': betweenness_centrality[node],
            'eigenvector': eigenvector_centrality.get(node, 0.0)
        })
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(centrality_data)
    
    # Sort by different centrality measures to find most important nodes
    critical_nodes_degree = df.sort_values('degree', ascending=False).head(10)
    critical_nodes_betweenness = df.sort_values('betweenness', ascending=False).head(10)
    critical_nodes_eigenvector = df.sort_values('eigenvector', ascending=False).head(10)
    
    # Create visualization
    # Set up the output file
    output_file(os.path.join(network_dir, "centrality_metrics.html"))
    
    # Create type color mapper
    node_type_colors = {
        'program': '#1f77b4',  # Blue
        'product': '#ff7f0e',  # Orange
        'material': '#2ca02c',  # Green
        'supplier': '#d62728',  # Red
        'post-supplier': '#9467bd',  # Purple
        'funding': '#8c564b'  # Brown
    }
    
    # Calculate colors based on node type
    df['color'] = df['type'].map(node_type_colors)
    
    # Create figures
    # Degree Centrality Plot
    degree_source = ColumnDataSource(df)
    
    p1 = figure(width=800, height=500, title="Degree Centrality",
               x_range=Range1d(start=-0.05, end=1.05), y_axis_label="Centrality Value")
    
    # Add hover tool for degree plot
    hover1 = HoverTool(tooltips=[
        ("ID", "@id"),
        ("Name", "@label"),
        ("Type", "@type"),
        ("Degree Centrality", "@degree{0.000}"),
        ("In-Degree Centrality", "@in_degree{0.000}"),
        ("Out-Degree Centrality", "@out_degree{0.000}")
    ])
    p1.add_tools(hover1)
    
    # Sort nodes by degree centrality for the plot
    sorted_indices = df['degree'].argsort()
    x_values = np.arange(len(df)) / (len(df) - 1) if len(df) > 1 else [0]
    
    # Create a new data source with sorted values
    sorted_data = {
        'x': x_values,
        'degree': df['degree'].values[sorted_indices],
        'in_degree': df['in_degree'].values[sorted_indices],
        'out_degree': df['out_degree'].values[sorted_indices],
        'id': df['id'].values[sorted_indices],
        'label': df['label'].values[sorted_indices],
        'type': df['type'].values[sorted_indices],
        'color': df['color'].values[sorted_indices]
    }
    sorted_source = ColumnDataSource(sorted_data)
    
    # Plot the centrality values
    p1.scatter('x', 'degree', source=sorted_source, size=10, color='color', alpha=0.8, legend_label="Degree", marker="circle")
    p1.line('x', 'degree', source=sorted_source, color='#1f77b4', line_width=2, alpha=0.7, legend_label="Degree")
    
    p1.scatter('x', 'in_degree', source=sorted_source, size=6, color='color', alpha=0.6, legend_label="In-Degree", marker="circle")
    p1.line('x', 'in_degree', source=sorted_source, color='#2ca02c', line_width=2, alpha=0.7, legend_label="In-Degree")
    
    p1.scatter('x', 'out_degree', source=sorted_source, size=6, color='color', alpha=0.6, legend_label="Out-Degree", marker="circle")
    p1.line('x', 'out_degree', source=sorted_source, color='#d62728', line_width=2, alpha=0.7, legend_label="Out-Degree")
    
    p1.xaxis.axis_label = "Nodes (Sorted by Degree Centrality)"
    p1.legend.location = "top_left"
    
    # Betweenness and Eigenvector Centrality Plot
    p2 = figure(width=800, height=500, title="Betweenness and Eigenvector Centrality",
               x_range=Range1d(start=-0.05, end=1.05), y_axis_label="Centrality Value")
    
    # Add hover tool for betweenness/eigenvector plot
    hover2 = HoverTool(tooltips=[
        ("ID", "@id"),
        ("Name", "@label"),
        ("Type", "@type"),
        ("Betweenness Centrality", "@betweenness{0.000}"),
        ("Eigenvector Centrality", "@eigenvector{0.000}")
    ])
    p2.add_tools(hover2)
    
    # Sort nodes by betweenness centrality for the plot
    sorted_indices_b = df['betweenness'].argsort()
    x_values_b = np.arange(len(df)) / (len(df) - 1) if len(df) > 1 else [0]
    
    # Create a new data source with sorted values
    sorted_data_b = {
        'x': x_values_b,
        'betweenness': df['betweenness'].values[sorted_indices_b],
        'eigenvector': df['eigenvector'].values[sorted_indices_b],
        'id': df['id'].values[sorted_indices_b],
        'label': df['label'].values[sorted_indices_b],
        'type': df['type'].values[sorted_indices_b],
        'color': df['color'].values[sorted_indices_b]
    }
    sorted_source_b = ColumnDataSource(sorted_data_b)
    
    # Plot the centrality values
    p2.scatter('x', 'betweenness', source=sorted_source_b, size=10, color='color', alpha=0.8, legend_label="Betweenness", marker="circle")
    p2.line('x', 'betweenness', source=sorted_source_b, color='#ff7f0e', line_width=2, alpha=0.7, legend_label="Betweenness")
    
    p2.scatter('x', 'eigenvector', source=sorted_source_b, size=6, color='color', alpha=0.6, legend_label="Eigenvector", marker="circle")
    p2.line('x', 'eigenvector', source=sorted_source_b, color='#9467bd', line_width=2, alpha=0.7, legend_label="Eigenvector")
    
    p2.xaxis.axis_label = "Nodes (Sorted by Betweenness Centrality)"
    p2.legend.location = "top_left"
    
    # Create tables of critical nodes
    critical_nodes_html = f"""
    <div style="margin-top: 20px;">
        <h2>Critical Nodes by Centrality Metrics</h2>
        
        <h3>Top 10 Nodes by Degree Centrality</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th>ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Degree Centrality</th>
            </tr>
            {''.join(f'<tr><td>{row["id"]}</td><td>{row["label"]}</td><td>{row["type"]}</td><td>{row["degree"]:.4f}</td></tr>' for _, row in critical_nodes_degree.iterrows())}
        </table>
        
        <h3>Top 10 Nodes by Betweenness Centrality</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th>ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Betweenness Centrality</th>
            </tr>
            {''.join(f'<tr><td>{row["id"]}</td><td>{row["label"]}</td><td>{row["type"]}</td><td>{row["betweenness"]:.4f}</td></tr>' for _, row in critical_nodes_betweenness.iterrows())}
        </table>
        
        <h3>Top 10 Nodes by Eigenvector Centrality</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th>ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Eigenvector Centrality</th>
            </tr>
            {''.join(f'<tr><td>{row["id"]}</td><td>{row["label"]}</td><td>{row["type"]}</td><td>{row["eigenvector"]:.4f}</td></tr>' for _, row in critical_nodes_eigenvector.iterrows())}
        </table>
    </div>
    """
    
    # Create Div element with the critical nodes HTML
    critical_nodes_div = Div(text=critical_nodes_html, width=800)
    
    # Add explanation text
    explanation_html = """
    <div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 5px solid #0275d8;">
        <h3>Understanding Centrality Metrics</h3>
        <p><strong>Degree Centrality:</strong> Measures how many direct connections each node has. Nodes with high degree centrality are hubs in the network.</p>
        <p><strong>In-Degree Centrality:</strong> Measures how many incoming connections each node has. Nodes with high in-degree are dependent on many other components.</p>
        <p><strong>Out-Degree Centrality:</strong> Measures how many outgoing connections each node has. Nodes with high out-degree support many other components.</p>
        <p><strong>Betweenness Centrality:</strong> Measures how often a node appears on the shortest paths between other nodes. Nodes with high betweenness are critical for information flow.</p>
        <p><strong>Eigenvector Centrality:</strong> Measures the influence of a node based on the connections it has to other high-value nodes. Nodes with high eigenvector centrality are connected to other important nodes.</p>
    </div>
    """
    
    # Create Div element with the explanation HTML
    explanation_div = Div(text=explanation_html, width=800)
    
    # Combine everything into a layout
    layout_elements = [
        explanation_div,
        gridplot([[p1], [p2]], width=800, height=500),
        critical_nodes_div
    ]
    
    layout_obj = column(layout_elements)
    
    # Save to an HTML file
    save(layout_obj)
    
    print(f"Centrality metrics visualization saved to '{network_dir}/centrality_metrics.html'")

def generate_dependency_chains(G, data, network_dir):
    """Generate visualization of dependency chains in the network"""
    print("Generating dependency chains visualization...")
    
    # Set up the output file
    output_file(os.path.join(network_dir, "dependency_chains.html"))
    
    # Find paths from programs to suppliers
    dependency_chains = []
    
    # Get all program nodes
    program_nodes = [node for node in G.nodes() if G.nodes[node]['type'] == 'program']
    
    # Get all supplier nodes (both printing and post-processing)
    supplier_nodes = [node for node in G.nodes() if G.nodes[node]['type'] in ['supplier', 'post-supplier']]
    
    # For each program, find paths to suppliers
    # Limit the number of combinations to avoid excessive computation
    max_combinations = 100  # Set a reasonable limit
    program_supplier_pairs = []
    
    for program in program_nodes:
        for supplier in supplier_nodes:
            program_supplier_pairs.append((program, supplier))
    
    # If there are too many combinations, sample them
    if len(program_supplier_pairs) > max_combinations:
        import random
        random.shuffle(program_supplier_pairs)
        program_supplier_pairs = program_supplier_pairs[:max_combinations]
        print(f"Too many program-supplier combinations. Limited to {max_combinations} random pairs.")
    
    # Find paths for the selected pairs
    for program, supplier in program_supplier_pairs:
        try:
            # Find all simple paths (no cycles) from program to supplier
            # Limit the path length to avoid excessive computation
            paths = list(nx.all_simple_paths(G, program, supplier, cutoff=4))
            
            # Limit the number of paths per pair to avoid excessive output
            if len(paths) > 5:
                # Keep the shortest paths if there are too many
                paths.sort(key=len)
                paths = paths[:5]
                
            for path in paths:
                # Construct chain details
                chain = {
                    'program': {'id': program, 'name': G.nodes[program]['label']},
                    'supplier': {'id': supplier, 'name': G.nodes[supplier]['label']},
                    'path': [{'id': node, 'name': G.nodes[node]['label'], 'type': G.nodes[node]['type']} for node in path],
                    'length': len(path)
                }
                dependency_chains.append(chain)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            # No path exists between these nodes
            continue
        except Exception as e:
            print(f"Error finding paths from {program} to {supplier}: {str(e)}")
            continue
    
    # Create visualization
    # Prepare data for visualization
    chain_html = f"""
    <div style="margin: 20px 0;">
        <h2>Dependency Chains Analysis</h2>
        <p>This analysis shows the chains of dependencies from Programs to Suppliers through Products and Materials.</p>
        
        <h3>Total Dependency Chains: {len(dependency_chains)}</h3>
        
        <div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 5px solid #0275d8;">
            <h4>Why Dependency Chains Matter</h4>
            <p>Dependency chains show how programs rely on products, materials, and suppliers. Longer chains may indicate:</p>
            <ul>
                <li>Higher complexity and risk</li>
                <li>More potential points of failure</li>
                <li>Need for stronger program management and coordination</li>
            </ul>
            <p>Programs with multiple dependencies on the same supplier may represent a single point of failure risk.</p>
        </div>
    """
    
    # Group chains by program
    grouped_chains = {}
    for chain in dependency_chains:
        program_id = chain['program']['id']
        if program_id not in grouped_chains:
            grouped_chains[program_id] = []
        grouped_chains[program_id].append(chain)
    
    # Add details for each program
    for program_id, chains in grouped_chains.items():
        program_name = chains[0]['program']['name']
        
        chain_html += f"""
        <h3>Program: {program_name} ({program_id})</h3>
        <p>Number of dependency chains: {len(chains)}</p>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
            <tr style="background-color: #f2f2f2;">
                <th>Supplier</th>
                <th>Dependency Path</th>
                <th>Chain Length</th>
            </tr>
        """
        
        # Sort chains by length
        sorted_chains = sorted(chains, key=lambda x: x['length'])
        
        for chain in sorted_chains:
            supplier_name = chain['supplier']['name']
            
            # Format the path as a string with arrows
            path_str = " → ".join([f"{node['name']} ({node['type']})" for node in chain['path']])
            
            chain_html += f"""
            <tr>
                <td>{supplier_name}</td>
                <td>{path_str}</td>
                <td>{chain['length']}</td>
            </tr>
            """
        
        chain_html += "</table>"
    
    chain_html += "</div>"
    
    # Create Div element with the chain HTML
    chain_div = Div(text=chain_html, width=1000)
    
    # Save to an HTML file
    save(chain_div)
    
    print(f"Dependency chains visualization saved to '{network_dir}/dependency_chains.html'")

def generate_impact_analysis(G, data, network_dir):
    """Generate visualization of impact analysis for changes or delays"""
    print("Generating impact analysis visualization...")
    
    # Set up the output file
    output_file(os.path.join(network_dir, "impact_analysis.html"))
    
    # Create impact analysis for each node type
    
    # Function to calculate downstream impact of a node
    def get_downstream_impact(node_id):
        # Get all nodes that can be reached from this node
        try:
            # Check if node exists in graph
            if node_id not in G:
                return {'programs': [], 'products': [], 'materials': [], 'suppliers': [], 'funding': [], 'total': 0}
                
            descendants = list(nx.descendants(G, node_id))
            
            # Group by type
            impact = {
                'programs': [n for n in descendants if G.nodes[n]['type'] == 'program'],
                'products': [n for n in descendants if G.nodes[n]['type'] == 'product'],
                'materials': [n for n in descendants if G.nodes[n]['type'] == 'material'],
                'suppliers': [n for n in descendants if G.nodes[n]['type'] in ['supplier', 'post-supplier']],
                'funding': [n for n in descendants if G.nodes[n]['type'] == 'funding'],
                'total': len(descendants)
            }
            return impact
            
        except (nx.NetworkXError, KeyError) as e:
            # Node not in graph or other NetworkX error
            print(f"Error calculating downstream impact for {node_id}: {str(e)}")
            return {'programs': [], 'products': [], 'materials': [], 'suppliers': [], 'funding': [], 'total': 0}
    
    # Function to calculate upstream dependencies of a node
    def get_upstream_dependencies(node_id):
        # Get all nodes that can reach this node
        try:
            # Check if node exists in graph
            if node_id not in G:
                return {'programs': [], 'products': [], 'materials': [], 'suppliers': [], 'funding': [], 'total': 0}
                
            ancestors = list(nx.ancestors(G, node_id))
            
            # Group by type
            dependencies = {
                'programs': [n for n in ancestors if G.nodes[n]['type'] == 'program'],
                'products': [n for n in ancestors if G.nodes[n]['type'] == 'product'],
                'materials': [n for n in ancestors if G.nodes[n]['type'] == 'material'],
                'suppliers': [n for n in ancestors if G.nodes[n]['type'] in ['supplier', 'post-supplier']],
                'funding': [n for n in ancestors if G.nodes[n]['type'] == 'funding'],
                'total': len(ancestors)
            }
            return dependencies
            
        except (nx.NetworkXError, KeyError) as e:
            # Node not in graph or other NetworkX error
            print(f"Error calculating upstream dependencies for {node_id}: {str(e)}")
            return {'programs': [], 'products': [], 'materials': [], 'suppliers': [], 'funding': [], 'total': 0}
    
    # Calculate impact and dependencies for all nodes
    impact_data = []
    
    for node in G.nodes():
        try:
            node_type = G.nodes[node]['type']
            node_label = G.nodes[node]['label']
            
            downstream_impact = get_downstream_impact(node)
            upstream_dependencies = get_upstream_dependencies(node)
            
            impact_data.append({
                'id': node,
                'label': node_label,
                'type': node_type,
                'downstream_impact': downstream_impact,
                'upstream_dependencies': upstream_dependencies,
                'impact_score': downstream_impact['total'],
                'dependency_score': upstream_dependencies['total']
            })
        except Exception as e:
            print(f"Error processing node {node}: {str(e)}")
            continue
    
    # Convert to DataFrame for easier manipulation
    if not impact_data:
        # Handle case where no valid impact data was calculated
        print("No valid impact data could be calculated. Creating basic report.")
        impact_html = """
        <div style="margin: 20px 0;">
            <h2>Impact Analysis</h2>
            <p>Unable to calculate impact analysis for this network. The network structure may not support this type of analysis.</p>
        </div>
        """
        impact_div = Div(text=impact_html, width=1000)
        save(impact_div)
        return
        
    impact_df = pd.DataFrame(impact_data)
    
    # Sort by impact score to find most critical nodes
    critical_nodes_impact = impact_df.sort_values('impact_score', ascending=False).head(15)
    
    # Create visualization
    # Create HTML table for high-impact nodes
    impact_html = f"""
    <div style="margin: 20px 0;">
        <h2>Impact Analysis</h2>
        <p>This analysis shows the potential impact of delays or changes to different components in the roadmap.</p>
        
        <div style="margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-left: 5px solid #0275d8;">
            <h3>How to Use This Analysis</h3>
            <p>Impact analysis helps identify critical components that, if delayed or changed, would have widespread effects across the roadmap:</p>
            <ul>
                <li><strong>High Impact Score:</strong> Components that affect many other components downstream</li>
                <li><strong>High Dependency Score:</strong> Components that depend on many other components upstream</li>
            </ul>
            <p>Use this information to prioritize risk mitigation and focus management attention on the most critical components.</p>
        </div>
        
        <h3>Top 15 High-Impact Components</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th>ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Impact Score</th>
                <th>Impacts Programs</th>
                <th>Impacts Products</th>
                <th>Impacts Materials</th>
                <th>Impacts Suppliers</th>
            </tr>
    """
    
    for _, row in critical_nodes_impact.iterrows():
        impact_html += f"""
            <tr>
                <td>{row['id']}</td>
                <td>{row['label']}</td>
                <td>{row['type']}</td>
                <td>{row['impact_score']}</td>
                <td>{len(row['downstream_impact']['programs'])}</td>
                <td>{len(row['downstream_impact']['products'])}</td>
                <td>{len(row['downstream_impact']['materials'])}</td>
                <td>{len(row['downstream_impact']['suppliers'])}</td>
            </tr>
        """
    
    impact_html += """
        </table>
        
        <h3>Component-Specific Impact Analysis</h3>
        <p>Select a component type below to see detailed impact analysis:</p>
    """
    
    # Create sections for each node type
    node_types = ['program', 'product', 'material', 'supplier', 'post-supplier', 'funding']
    node_type_labels = {
        'program': 'Programs',
        'product': 'Products',
        'material': 'Material Systems',
        'supplier': 'Printing Suppliers',
        'post-supplier': 'Post-Processing Suppliers',
        'funding': 'Funding Opportunities'
    }
    
    for node_type in node_types:
        type_nodes = impact_df[impact_df['type'] == node_type].sort_values('impact_score', ascending=False)
        
        if len(type_nodes) == 0:
            continue
            
        impact_html += f"""
        <h3>{node_type_labels.get(node_type, node_type.capitalize())} Impact Analysis</h3>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th>ID</th>
                <th>Name</th>
                <th>Impact Score</th>
                <th>Dependency Score</th>
                <th>Details</th>
            </tr>
        """
        
        for _, row in type_nodes.iterrows():
            # Format the impact details
            impact_details = ', '.join([
                f"{len(row['downstream_impact']['programs'])} Programs",
                f"{len(row['downstream_impact']['products'])} Products",
                f"{len(row['downstream_impact']['materials'])} Materials",
                f"{len(row['downstream_impact']['suppliers'])} Suppliers"
            ])
            
            # Format the dependency details
            dependency_details = ', '.join([
                f"{len(row['upstream_dependencies']['programs'])} Programs",
                f"{len(row['upstream_dependencies']['products'])} Products",
                f"{len(row['upstream_dependencies']['materials'])} Materials",
                f"{len(row['upstream_dependencies']['suppliers'])} Suppliers"
            ])
            
            impact_html += f"""
            <tr>
                <td>{row['id']}</td>
                <td>{row['label']}</td>
                <td>{row['impact_score']}</td>
                <td>{row['dependency_score']}</td>
                <td>
                    <strong>Impacts:</strong> {impact_details}<br>
                    <strong>Depends on:</strong> {dependency_details}
                </td>
            </tr>
            """
        
        impact_html += "</table>"
    
    impact_html += "</div>"
    
    # Create Div element with the impact HTML
    impact_div = Div(text=impact_html, width=1000)
    
    # Save to an HTML file
    save(impact_div)
    
    print(f"Impact analysis visualization saved to '{network_dir}/impact_analysis.html'")

def generate_network_analysis_summary(G, data, network_dir):
    """Generate a summary page for network analysis"""
    print("Generating network analysis summary page...")
    
    # Calculate network metrics safely
    try:
        network_density = nx.density(G)
    except:
        network_density = "N/A"
    
    try:
        # Only calculate average path length if graph is strongly connected
        if nx.is_strongly_connected(G):
            avg_path_length = nx.average_shortest_path_length(G)
        else:
            avg_path_length = "N/A (Graph is not strongly connected)"
    except:
        avg_path_length = "N/A"
    
    try:
        connected_components = nx.number_weakly_connected_components(G)
    except:
        connected_components = "N/A"
    
    # Create HTML content for the summary page
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Advanced Network Analysis</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            h1 {{ color: #333; }}
            h2, h3, h4 {{ color: #0066cc; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 20px; }}
            .card h3 {{ margin-top: 0; }}
            .card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }}
            .metric {{ font-weight: bold; color: #333; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Advanced Network Analysis</h1>
            <p><a href="../index.html">Back to Dashboard</a></p>
            
            <div class="card">
                <h2>Network Overview</h2>
                <p>The roadmap network consists of <span class="metric">{len(G.nodes())}</span> nodes and <span class="metric">{len(G.edges())}</span> edges.</p>
                <p>Node types: 
                    <span class="metric">{len([n for n in G.nodes() if G.nodes[n]['type'] == 'program'])}</span> Programs, 
                    <span class="metric">{len([n for n in G.nodes() if G.nodes[n]['type'] == 'product'])}</span> Products, 
                    <span class="metric">{len([n for n in G.nodes() if G.nodes[n]['type'] == 'material'])}</span> Material Systems, 
                    <span class="metric">{len([n for n in G.nodes() if G.nodes[n]['type'] in ['supplier', 'post-supplier']])}</span> Suppliers, 
                    <span class="metric">{len([n for n in G.nodes() if G.nodes[n]['type'] == 'funding'])}</span> Funding Opportunities
                </p>
            </div>
            
            <div class="card-grid">
                <div class="card">
                    <h3>Centrality Metrics</h3>
                    <p>Identify the most critical components in the network based on their connections and position.</p>
                    <p><a href="centrality_metrics.html">View Centrality Analysis</a></p>
                </div>
                
                <div class="card">
                    <h3>Dependency Chains</h3>
                    <p>Analyze the chains of dependencies from Programs to Suppliers through Products and Materials.</p>
                    <p><a href="dependency_chains.html">View Dependency Chains</a></p>
                </div>
                
                <div class="card">
                    <h3>Impact Analysis</h3>
                    <p>Evaluate the potential impact of delays or changes to different components in the roadmap.</p>
                    <p><a href="impact_analysis.html">View Impact Analysis</a></p>
                </div>
            </div>
            
            <div class="card">
                <h2>Key Insights</h2>
                <ul>
                    <li>The network density is <span class="metric">{network_density if isinstance(network_density, str) else f"{network_density:.4f}"}</span> (proportion of actual connections to possible connections)</li>
                    <li>Average path length: <span class="metric">{avg_path_length if isinstance(avg_path_length, str) else f"{avg_path_length:.2f}"}</span></li>
                    <li>Number of connected components: <span class="metric">{connected_components}</span></li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write the HTML content to a file
    with open(os.path.join(network_dir, "index.html"), 'w') as f:
        f.write(html_content)
    
    print(f"Network analysis summary page generated in '{network_dir}/index.html'") 