# Roadmap Manager - Modular Structure

This directory contains the modular implementation of the Roadmap Manager application.

## Directory Structure

- `__init__.py` - Package initialization file
- `main.py` - Main application entry point
- `date_entry.py` - Custom DateEntry widget
- `utils.py` - Utility functions
- `models/` - Directory for data models
  - `__init__.py` - Package initialization file
  - `base.py` - Base model class
  - `program.py` - Program-related functionality
  - `product.py` - Product-related functionality (to be implemented)
  - `material.py` - Material system-related functionality (to be implemented)
  - `supplier.py` - Supplier-related functionality (to be implemented)
  - `funding.py` - Funding opportunity-related functionality (to be implemented)

## How to Run

The application can be run using the `run_roadmap_manager.py` script in the parent directory, or by using the `Roadmap_Manager.bat` file on Windows.

## Development

To add a new tab or functionality:

1. Create a new model file in the `models/` directory
2. Implement the necessary classes and methods
3. Import the model in `main.py`
4. Initialize the model in the `RoadmapManager` class
5. Add the tab creation to the `create_tabs` method

## Dependencies

- Python 3.6+
- Tkinter (included with most Python installations) 