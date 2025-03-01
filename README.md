# Additive Manufacturing Roadmap Visualizer

This application generates interactive visualizations for additive manufacturing roadmap data stored in `roadmap.json`. It creates a comprehensive dashboard with detailed visualizations for programs, products, material systems, suppliers, funding opportunities, and their relationships.

## Features

- **Interactive Dashboard**: A central dashboard that provides access to all visualizations
- **Program Visualizations**: View program details, associated products, and program-specific roadmaps
- **Product Visualizations**: Explore product roadmaps, material systems, and associated programs
- **Material System Visualizations**: Analyze material systems, their properties, and qualification status
- **Supplier Visualizations**: View printing and post-processing suppliers and their capabilities
- **Funding Opportunity Visualizations**: Explore funding opportunities and their relationships to tasks
- **Relationship Visualizations**: Visualize relationships between different entities in the roadmap

## Requirements

- Python 3.6+
- Required Python packages:
  - bokeh
  - matplotlib
  - networkx
  - numpy

## Installation

1. Clone this repository or download the source code
2. Install the required packages:

```bash
pip install bokeh matplotlib networkx numpy
```

## Usage

1. Ensure your roadmap data is in a file named `roadmap.json` in the root directory
2. Run the main script:

```bash
python main.py
```

3. Open the generated `roadmap_visualizations/index.html` file in your web browser to view the dashboard

## File Structure

- `main.py`: Main entry point for the application
- `roadmap.json`: Input data file containing roadmap information
- `modules/`: Directory containing visualization modules
  - `program_viz.py`: Program visualization module
  - `product_viz.py`: Product visualization module
  - `material_viz.py`: Material system visualization module
  - `supplier_viz.py`: Supplier visualization module
  - `funding_viz.py`: Funding opportunity visualization module
  - `relationship_viz.py`: Relationship visualization module
  - `dashboard.py`: Dashboard generation module
- `roadmap_visualizations/`: Output directory for generated visualizations

## Output Structure

The application generates the following directory structure in the `roadmap_visualizations` directory:

- `index.html`: Main dashboard
- `programs/`: Program visualizations
- `products/`: Product visualizations
- `materials/`: Material system visualizations
- `suppliers/`: Supplier visualizations
- `funding/`: Funding opportunity visualizations
- `relationships/`: Relationship visualizations

## Customization

You can customize the visualizations by modifying the corresponding module files in the `modules/` directory. Each module contains functions for generating specific visualizations.

## Data Format

The application expects the `roadmap.json` file to contain the following main sections:

- `programs`: Array of program objects
- `products`: Array of product objects
- `materialSystems`: Array of material system objects
- `printingSuppliers`: Array of printing supplier objects
- `postProcessingSuppliers`: Array of post-processing supplier objects
- `fundingOpportunities`: Array of funding opportunity objects (optional)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 