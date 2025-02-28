#!/usr/bin/env python
"""
Launcher script for the Roadmap Manager application
"""

import os
import sys

# Get the absolute path of the directory containing this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the base directory to the path so Python can find the modules
sys.path.insert(0, BASE_DIR)

# Set the working directory to the base directory to ensure consistent file paths
os.chdir(BASE_DIR)

from roadmap_manager.main import main

if __name__ == "__main__":
    main() 