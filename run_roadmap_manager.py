#!/usr/bin/env python
"""
Launcher script for the Roadmap Manager application
"""

import os
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from roadmap_manager.main import main

if __name__ == "__main__":
    main() 