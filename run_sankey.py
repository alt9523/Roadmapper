import json
import os
from modules.relationship_viz_aligned import generate_sankey_diagram

# Load the data
with open('roadmap.json', 'r') as f:
    data = json.load(f)

# Create the output directory if it doesn't exist
output_dir = 'roadmap_visualizations/relationships'
os.makedirs(output_dir, exist_ok=True)

# Generate the Sankey diagram
generate_sankey_diagram(data, output_dir)

print("Sankey diagram generated successfully!")
print(f"Open {output_dir}/sankey_diagram.html in your browser to view it.") 