import os
import json
import sys
from datetime import datetime

# Add the current directory to the path so Python can find the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import visualization modules
from modules.program_viz import generate_program_visualizations
from modules.product_viz import generate_product_visualizations
from modules.material_viz import generate_material_visualizations
from modules.supplier_viz import generate_supplier_visualizations
from modules.funding_viz import generate_funding_visualizations
from modules.relationship_viz import generate_relationship_visualizations
from modules.network_analysis import generate_advanced_network_analysis
from modules.progress_tracking import generate_progress_tracking
from modules.dashboard import generate_dashboard

# Define status colors for consistency
STATUS_COLORS = {
    'Complete': '#43a047',  # Green
    'In Progress': '#ff9800',  # Orange
    'Planned': '#4a89ff'  # Blue
}

def main():
    """Main function to generate all visualizations"""
    print("Generating roadmap visualizations...")
    
    # Load the roadmap data
    with open('roadmap.json', 'r') as f:
        data = json.load(f)
    
    # Map fundingOpps to fundingOpportunities for compatibility
    if 'fundingOpps' in data and 'fundingOpportunities' not in data:
        data['fundingOpportunities'] = data['fundingOpps']
    
    # Create output directory if it doesn't exist
    output_dir = "roadmap_visualizations"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate visualizations for each module
    generate_program_visualizations(data, output_dir)
    generate_product_visualizations(data, output_dir, STATUS_COLORS)
    generate_material_visualizations(data, output_dir, STATUS_COLORS)
    generate_supplier_visualizations(data, output_dir)
    generate_funding_visualizations(data, output_dir)
    generate_relationship_visualizations(data, output_dir)
    
    # Generate advanced network analysis
    network_analysis_path = generate_advanced_network_analysis(data, output_dir)
    
    # Generate progress tracking visualizations
    progress_path = generate_progress_tracking(data, output_dir)
    
    # Generate the main dashboard
    generate_dashboard(data, output_dir, network_analysis_path, progress_path)
    
    print(f"All visualizations generated in the '{output_dir}' directory.")
    print(f"Open '{output_dir}/index.html' in your browser to view the dashboard.")

if __name__ == "__main__":
    main() 