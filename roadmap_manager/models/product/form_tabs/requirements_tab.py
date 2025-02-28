import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab

class RequirementsTab(BaseTab):
    """Tab for product requirements"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.requirement_fields = []
        super().__init__(form, "Requirements")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure requirements exists and is a dictionary
        if "requirements" not in self.product or not isinstance(self.product["requirements"], dict):
            self.product["requirements"] = {}
        
        # Add button for new requirement
        add_req_btn = ttk.Button(self.frame, text="Add Requirement", 
                                command=lambda: self.add_requirement_field())
        add_req_btn.grid(row=100, column=0, sticky=tk.W, padx=5, pady=10)
        
        # Add existing requirements
        requirements = self.product["requirements"]
        for req_name, req_value in requirements.items():
            self.add_requirement_field(req_name, req_value)
    
    def add_requirement_field(self, name="", value=""):
        """Add a requirement field to the form"""
        # Create a frame for this requirement
        row_idx = len(self.requirement_fields)
        req_frame = ttk.Frame(self.frame)
        req_frame.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Field name entry
        name_var = tk.StringVar(value=name)
        name_entry = ttk.Entry(req_frame, textvariable=name_var, width=20)
        name_entry.grid(row=0, column=0, padx=5)
        
        # Field value entry
        value_var = tk.StringVar(value=value)
        value_entry = ttk.Entry(req_frame, textvariable=value_var, width=50)
        value_entry.grid(row=0, column=1, padx=5)
        
        # Remove button
        def remove_field():
            req_frame.destroy()
            self.requirement_fields.remove(entry_data)
        
        remove_btn = ttk.Button(req_frame, text="Remove", command=remove_field)
        remove_btn.grid(row=0, column=2, padx=5)
        
        # Store entry data
        entry_data = {
            "name_var": name_var,
            "value_var": value_var,
            "frame": req_frame
        }
        self.requirement_fields.append(entry_data)
        
        # Move the add button to the bottom
        self.frame.children['!button'].grid(row=row_idx + 1, column=0, sticky=tk.W, padx=5, pady=10)
    
    def collect_data(self):
        """Collect data from the tab"""
        # Get requirements
        requirements = {}
        for entry in self.requirement_fields:
            name = entry["name_var"].get().strip()
            value = entry["value_var"].get().strip()
            if name:
                requirements[name] = value
        self.product["requirements"] = requirements 