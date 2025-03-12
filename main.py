import os
import json
import sys
from datetime import datetime, timedelta

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
    'Planned': '#4a89ff',  # Blue
    'Not Started': '#9e9e9e',  # Gray
    'On Hold': '#9c27b0',  # Purple
    'Delayed': '#e53935'   # Red
}

def main():
    """Main function to generate all visualizations"""
    print("Generating roadmap visualizations...")
    
    # Load the roadmap data
    with open('updated_roadmap.json', 'r') as f:
        data = json.load(f)
    
    # Map fundingOpps to fundingOpportunities for compatibility
    if 'fundingOpps' in data and 'fundingOpportunities' not in data:
        data['fundingOpportunities'] = data['fundingOpps']
    
    # Create output directory if it doesn't exist
    output_dir = "roadmap_visualizations"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process floating tasks if needed
    process_floating_tasks(data)
    
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

def process_floating_tasks(data):
    """Process floating tasks to adjust dates based on time elapsed since float date"""
    print("Processing floating tasks...")
    
    today = datetime.now()
    
    # Process products
    for product in data.get('products', []):
        # Process all sections that might contain floating tasks
        sections = [
            {'key': 'designTools', 'date_keys': ('start', 'end')},
            {'key': 'documentation', 'date_keys': ('start', 'end')},
            {'key': 'specialNDT', 'date_keys': ('startDate', 'endDate')},
            {'key': 'partAcceptance', 'date_keys': ('startDate', 'endDate')},
            {'key': 'roadmap', 'date_keys': ('start', 'end')}
        ]
        
        for section in sections:
            if section['key'] in product:
                items = product[section['key']]
                start_key, end_key = section['date_keys']
                
                for item in items:
                    if isinstance(item, dict) and item.get('float', False) and item.get('floatDate'):
                        try:
                            # Calculate days elapsed since float date
                            float_dt = datetime.strptime(item['floatDate'], "%Y-%m-%d")
                            days_elapsed = (today - float_dt).days
                            
                            if days_elapsed > 0 and item.get(start_key):
                                # Adjust start date
                                start_dt = datetime.strptime(item[start_key], "%Y-%m-%d")
                                start_dt = start_dt + timedelta(days=days_elapsed)
                                item[start_key] = start_dt.strftime("%Y-%m-%d")
                                
                                # Adjust end date if it exists
                                if item.get(end_key):
                                    end_dt = datetime.strptime(item[end_key], "%Y-%m-%d")
                                    end_dt = end_dt + timedelta(days=days_elapsed)
                                    item[end_key] = end_dt.strftime("%Y-%m-%d")
                        except Exception as e:
                            print(f"Error adjusting floating dates: {str(e)}")
        
        # Update lastSaveDate to today
        product['lastSaveDate'] = today.strftime("%Y-%m-%d")

if __name__ == "__main__":
    main() 