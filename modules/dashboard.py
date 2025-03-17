import os
from datetime import datetime
from bokeh.models import Div
from bokeh.layouts import layout
from bokeh.plotting import output_file, save

def generate_dashboard(data, output_dir, network_analysis_path=None, progress_path=None, implementation_path=None):
    """Generate the main dashboard/index page"""
    print("Generating main dashboard...")
    
    # Get counts for different entities
    program_count = len(data.get('programs', []))
    product_count = len(data.get('products', []))
    material_count = len(data.get('materialSystems', []))
    printing_supplier_count = len(data.get('printingSuppliers', []))
    postproc_supplier_count = len(data.get('postProcessingSuppliers', []))
    funding_count = len(data.get('fundingOpportunities', [])) if 'fundingOpportunities' in data else 0
    
    # Count pursuits
    pursuit_count = 0
    if 'fundingOpportunities' in data:
        for funding in data['fundingOpportunities']:
            pursuit_count += len(funding.get('pursuits', []))
    
    # Count implementation metrics
    implementation_count = 0
    for program in data.get('programs', []):
        implementation_count += len(program.get('productMaterialCombinations', []))
    
    # Create the dashboard HTML
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Additive Manufacturing Roadmap Dashboard</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 0; 
                background-color: #f8f9fa; 
            }}
            .container {{ 
                width: 1200px; 
                max-width: 100%; 
                margin: 0 auto; 
                padding: 20px; 
                box-sizing: border-box;
            }}
            .header {{ 
                background: linear-gradient(to right, #3498db, #2c3e50);
                color: white; 
                padding: 20px; 
                text-align: center;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header h1 {{ 
                margin: 0; 
                font-size: 28px;
            }}
            .header p {{ 
                margin: 10px 0 0 0; 
            }}
            .nav-links {{
                margin-top: 15px;
            }}
            .nav-link {{
                color: white;
                text-decoration: none;
                padding: 8px 15px;
                background-color: rgba(255,255,255,0.2);
                border-radius: 4px;
                margin: 0 5px;
                transition: background-color 0.3s;
            }}
            .nav-link:hover {{
                background-color: rgba(255,255,255,0.3);
            }}
            .card-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}
            .card {{ 
                background-color: white; 
                border-radius: 8px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                padding: 25px;
                transition: transform 0.3s ease;
            }}
            .card:hover {{ 
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .card h2 {{ 
                color: #2c3e50; 
                margin-top: 0;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                font-size: 22px;
            }}
            .card-content {{ 
                margin-bottom: 15px; 
            }}
            .card-footer {{ 
                display: flex;
                justify-content: space-between;
            }}
            .btn {{
                display: inline-block;
                padding: 8px 15px;
                background-color: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                transition: background-color 0.3s ease;
            }}
            .btn:hover {{ 
                background-color: #2980b9; 
            }}
            .stats {{ 
                display: flex; 
                flex-wrap: wrap;
                justify-content: space-between;
                margin-bottom: 20px;
                background-color: white;
                border-radius: 8px;
                padding: 25px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            .stat-item {{ 
                text-align: center; 
                padding: 10px; 
                flex: 1;
                min-width: 120px;
            }}
            .stat-value {{ 
                font-size: 28px; 
                font-weight: bold; 
                color: #3498db;
                margin: 5px 0;
            }}
            .stat-label {{ 
                color: #7f8c8d; 
            }}
            .footer {{ 
                text-align: center; 
                margin-top: 30px; 
                padding-top: 20px; 
                border-top: 1px solid #ddd;
                color: #7f8c8d;
            }}
            .overview-image {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
            }}
            .feature-card {{
                background-color: #f8f9fa;
                border-left: 4px solid #3498db;
            }}
            .overview-card {{
                width: 1200px;
                max-width: 100%;
                box-sizing: border-box;
                margin-bottom: 20px;
            }}
            @media (max-width: 768px) {{
                .card-grid {{
                    grid-template-columns: 1fr;
                }}
                .stat-item {{
                    min-width: 100px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Additive Manufacturing Roadmap Dashboard</h1>
                <p>Interactive visualizations for roadmap data</p>
                <div class="nav-links">
                    <a href="programs/program_summary.html" class="nav-link">Programs</a>
                    <a href="products/product_summary.html" class="nav-link">Products</a>
                    <a href="materials/material_summary.html" class="nav-link">Materials</a>
                    <a href="suppliers/supplier_summary.html" class="nav-link">Suppliers</a>
                    <a href="funding/funding_summary.html" class="nav-link">Funding</a>
                    <a href="implementation/index.html" class="nav-link">Implementation</a>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">{program_count}</div>
                    <div class="stat-label">Programs</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{product_count}</div>
                    <div class="stat-label">Products</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{material_count}</div>
                    <div class="stat-label">Material Systems</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{printing_supplier_count}</div>
                    <div class="stat-label">Printing Suppliers</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{postproc_supplier_count}</div>
                    <div class="stat-label">Post-Processing Suppliers</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{funding_count}</div>
                    <div class="stat-label">Funding Opportunities</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{pursuit_count}</div>
                    <div class="stat-label">Pursuits</div>
                </div>
            </div>
            
            <div class="card-grid">
                <div class="card">
                    <h2>Programs</h2>
                    <div class="card-content">
                        <p>View program details, associated products, and program-specific roadmaps.</p>
                    </div>
                    <div class="card-footer">
                        <a href="programs/program_summary.html" class="btn">View Programs</a>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Products</h2>
                    <div class="card-content">
                        <p>Explore product roadmaps, material systems, and associated programs.</p>
                    </div>
                    <div class="card-footer">
                        <a href="products/product_summary.html" class="btn">View Products</a>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Material Systems</h2>
                    <div class="card-content">
                        <p>Analyze material systems, their properties, and qualification status.</p>
                    </div>
                    <div class="card-footer">
                        <a href="materials/material_summary.html" class="btn">View Materials</a>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Suppliers</h2>
                    <div class="card-content">
                        <p>View printing and post-processing suppliers and their capabilities.</p>
                    </div>
                    <div class="card-footer">
                        <a href="suppliers/supplier_summary.html" class="btn">View Suppliers</a>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Funding Opportunities</h2>
                    <div class="card-content">
                        <p>Explore funding opportunities and their relationships to tasks.</p>
                    </div>
                    <div class="card-footer">
                        <a href="funding/funding_summary.html" class="btn">View Funding</a>
                        <a href="funding/pursuits_summary.html" class="btn">View Pursuits</a>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Relationships</h2>
                    <div class="card-content">
                        <p>Visualize relationships between different entities in the roadmap.</p>
                    </div>
                    <div class="card-footer">
                        <a href="relationships/relationship_summary.html" class="btn">View Relationships</a>
                    </div>
                </div>

                <div class="card">
                    <h2>Progress Tracking</h2>
                    <div class="card-content">
                        <p>Track progress with burndown charts for task completion, milestone achievement tracking, and comparison of planned vs. actual progress.</p>
                    </div>
                    <div class="card-footer">
                        <a href="progress/progress_dashboard.html" class="btn">View Progress</a>
                    </div>
                </div>

                <div class="card">
                    <h2>Implementation Metrics</h2>
                    <div class="card-content">
                        <p>Analyze adoption metrics, cost and schedule savings, and implementation status across programs and material systems.</p>
                    </div>
                    <div class="card-footer">
                        <a href="{implementation_path if implementation_path else 'implementation/index.html'}" class="btn">View Metrics</a>
                    </div>
                </div>

                <div class="card">
                    <h2>Advanced Network Analysis</h2>
                    <div class="card-content">
                        <p>Advanced network graph analysis with centrality metrics, dependency chains, and impact analysis.</p>
                    </div>
                    <div class="card-footer">
                        <a href="{network_analysis_path if network_analysis_path else 'relationships/relationship_summary.html'}" class="btn">View Analysis</a>
                    </div>
                </div>
            </div>
            
            <div class="card overview-card">
                <h2>Roadmap Overview</h2>
                <div class="card-content">
                    <p>This network graph shows the relationships between all entities in the roadmap data.</p>
                    <a href="relationships/network_graph.html">
                        <img src="relationships/network_graph.png" alt="Network Graph" class="overview-image">
                    </a>
                </div>
                <div class="card-footer">
                    <a href="relationships/network_graph.html" class="btn">View Full Graph</a>
                    {f'<a href="{network_analysis_path}" class="btn">View Advanced Analysis</a>' if network_analysis_path else ''}
                </div>
            </div>
            
            <div class="footer">
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write the dashboard HTML to the index.html file
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(dashboard_html)
    
    print(f"Main dashboard generated in '{output_dir}/index.html'") 