import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab

class BusinessCaseTab(BaseTab):
    """Tab for business case drivers information"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.business_case_checkboxes = {}
        super().__init__(form, "Business Case Drivers")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure businessCase exists and is a dictionary
        if "businessCase" not in self.product or not isinstance(self.product["businessCase"], dict):
            self.product["businessCase"] = {}
        
        # Create a frame for the business case drivers
        self.business_case_frame = ttk.Frame(self.frame)
        self.business_case_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Define the categories and their items
        categories = {
            "Business": [
                "Save schedule",
                "Save hardware costs",
                "Relieve supply chain constraints",
                "Increase Pwin by hitting PTW",
                "Reduce specialty training"
            ],
            "Unconventional Design": [
                "Save weight",
                "Increase performance",
                "Unify parts"
            ],
            "Agility throughout program": [
                "Quickly iterate design/EMs",
                "Agility in Design and AI&T",
                "Digital Spares"
            ]
        }
        
        # Create the checkboxes for each category and item
        row = 0
        for category, items in categories.items():
            # Add category label
            category_label = ttk.Label(self.business_case_frame, text=category, font=("TkDefaultFont", 10, "bold"))
            category_label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=(10, 5))
            row += 1
            
            # Add items with checkboxes
            for item in items:
                var = tk.BooleanVar(value=self.product.get("businessCase", {}).get(item, False))
                checkbox = ttk.Checkbutton(self.business_case_frame, text=item, variable=var)
                checkbox.grid(row=row, column=0, sticky=tk.W, padx=25, pady=2)
                self.business_case_checkboxes[item] = var
                row += 1
    
    def collect_data(self):
        """Collect data from the tab"""
        # Get the selected business case drivers
        business_case = {}
        
        # Store the checkbox values
        for item, var in self.business_case_checkboxes.items():
            business_case[item] = var.get()
        
        # Update the product
        self.product["businessCase"] = business_case
        
        # Return True to indicate validation passed
        return True