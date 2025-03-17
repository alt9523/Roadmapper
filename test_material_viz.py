#!/usr/bin/env python
import json
from modules.material_viz import generate_material_visualizations

# Define status colors
status_colors = {
    'Complete': '#27ae60',    # green
    'In Progress': '#f39c12', # orange
    'Planned': '#3498db',     # blue
    'Baselined': '#9b59b6',   # purple
    'Prototyping': '#f1c40f', # yellow
    'Developing': '#95a5a6',  # light gray
    'Targeting': '#7f8c8d'    # dark gray
}

# Load data from roadmap.json
with open('roadmap.json', 'r') as f:
    data = json.load(f)

# Generate material visualizations
print("Generating material visualizations...")
generate_material_visualizations(data, 'output', status_colors)
print("Material visualizations generated in 'output/materials' directory.") 