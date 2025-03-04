import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab

class PartAcceptanceTab(BaseTab):
    """Tab for part acceptance information"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.acceptance_entries = []
        super().__init__(form, "Part Acceptance")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure partAcceptance exists and is a list
        if "partAcceptance" not in self.product or not isinstance(self.product["partAcceptance"], list):
            self.product["partAcceptance"] = []
            print("Initialized empty partAcceptance list")
        else:
            print(f"Found existing partAcceptance: {self.product['partAcceptance']}")
        
        # Create a frame for the part acceptance list
        self.acceptance_frame = ttk.Frame(self.frame)
        self.acceptance_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a frame for existing acceptance entries
        self.existing_acceptance_frame = ttk.Frame(self.acceptance_frame)
        self.existing_acceptance_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add existing part acceptance entries
        for acceptance in self.product["partAcceptance"]:
            if isinstance(acceptance, str):
                print(f"Adding existing acceptance: {acceptance}")
                self.add_acceptance_entry(acceptance)
            else:
                print(f"Skipping non-string acceptance: {acceptance}")
        
        # Add button for new part acceptance at the bottom
        add_btn = ttk.Button(self.acceptance_frame, text="Add Part Acceptance", 
                           command=lambda: self.add_acceptance_entry())
        add_btn.pack(anchor=tk.W, pady=5)
    
    def add_acceptance_entry(self, acceptance_value=""):
        """Add a part acceptance entry to the form"""
        print(f"Adding acceptance entry: {acceptance_value}")
        
        # Create a frame for this entry
        row_idx = len(self.acceptance_entries)
        acceptance_frame = ttk.Frame(self.existing_acceptance_frame)
        acceptance_frame.pack(fill=tk.X, pady=2)
        
        # Acceptance value
        value_var = tk.StringVar(value=acceptance_value)
        value_entry = ttk.Entry(acceptance_frame, textvariable=value_var, width=50)
        value_entry.grid(row=0, column=0, padx=5)
        
        # Remove button
        def remove_entry():
            acceptance_frame.destroy()
            self.acceptance_entries.remove(entry_data)
        
        remove_btn = ttk.Button(acceptance_frame, text="Remove", command=remove_entry)
        remove_btn.grid(row=0, column=1, padx=5)
        
        # Store entry data
        entry_data = {
            "value_var": value_var,
            "frame": acceptance_frame
        }
        self.acceptance_entries.append(entry_data)
        return entry_data  # Return for testing/debugging
    
    def collect_data(self):
        """Collect data from the tab"""
        print("Collecting part acceptance data...")
        
        part_acceptance = []
        for i, entry in enumerate(self.acceptance_entries):
            print(f"Processing acceptance entry {i}")
            value = entry["value_var"].get().strip()
            print(f"  Acceptance Value: '{value}'")
            
            if value:  # Only add if value is not empty
                part_acceptance.append(value)
                print(f"  Added acceptance to partAcceptance list")
            else:
                print(f"  Skipping empty acceptance entry")
                
        print(f"Setting product['partAcceptance'] to {part_acceptance}")
        self.product["partAcceptance"] = part_acceptance
        print(f"After update: product['partAcceptance'] = {self.product.get('partAcceptance', [])}")
        
        # Return True to indicate validation passed
        return True 