import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab

class SpecialNDTTab(BaseTab):
    """Tab for special NDT information"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.ndt_entries = []
        super().__init__(form, "Special NDT")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure specialNDT exists and is a list
        if "specialNDT" not in self.product or not isinstance(self.product["specialNDT"], list):
            self.product["specialNDT"] = []
            print("Initialized empty specialNDT list")
        else:
            print(f"Found existing specialNDT: {self.product['specialNDT']}")
        
        # Create a frame for the special NDT list
        self.ndt_frame = ttk.Frame(self.frame)
        self.ndt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a frame for existing NDT entries
        self.existing_ndt_frame = ttk.Frame(self.ndt_frame)
        self.existing_ndt_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add existing special NDT entries
        for ndt in self.product["specialNDT"]:
            if isinstance(ndt, str):
                print(f"Adding existing NDT: {ndt}")
                self.add_ndt_entry(ndt)
            else:
                print(f"Skipping non-string NDT: {ndt}")
        
        # Add button for new special NDT at the bottom
        add_btn = ttk.Button(self.ndt_frame, text="Add Special NDT", 
                           command=lambda: self.add_ndt_entry())
        add_btn.pack(anchor=tk.W, pady=5)
    
    def add_ndt_entry(self, ndt_value=""):
        """Add a special NDT entry to the form"""
        print(f"Adding NDT entry: {ndt_value}")
        
        # Create a frame for this entry
        row_idx = len(self.ndt_entries)
        ndt_frame = ttk.Frame(self.existing_ndt_frame)
        ndt_frame.pack(fill=tk.X, pady=2)
        
        # NDT value
        value_var = tk.StringVar(value=ndt_value)
        value_entry = ttk.Entry(ndt_frame, textvariable=value_var, width=50)
        value_entry.grid(row=0, column=0, padx=5)
        
        # Remove button
        def remove_entry():
            ndt_frame.destroy()
            self.ndt_entries.remove(entry_data)
        
        remove_btn = ttk.Button(ndt_frame, text="Remove", command=remove_entry)
        remove_btn.grid(row=0, column=1, padx=5)
        
        # Store entry data
        entry_data = {
            "value_var": value_var,
            "frame": ndt_frame
        }
        self.ndt_entries.append(entry_data)
        return entry_data  # Return for testing/debugging
    
    def collect_data(self):
        """Collect data from the tab"""
        print("Collecting special NDT data...")
        
        special_ndt = []
        for i, entry in enumerate(self.ndt_entries):
            print(f"Processing NDT entry {i}")
            value = entry["value_var"].get().strip()
            print(f"  NDT Value: '{value}'")
            
            if value:  # Only add if value is not empty
                special_ndt.append(value)
                print(f"  Added NDT to specialNDT list")
            else:
                print(f"  Skipping empty NDT entry")
                
        print(f"Setting product['specialNDT'] to {special_ndt}")
        self.product["specialNDT"] = special_ndt
        print(f"After update: product['specialNDT'] = {self.product.get('specialNDT', [])}") 