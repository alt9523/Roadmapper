import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab

class SimpleListTab(BaseTab):
    """Base class for tabs that manage a simple list of strings"""
    
    def __init__(self, form, tab_name, product_key, button_text="Add Item"):
        """
        Initialize a simple list tab
        
        Args:
            form: The parent form
            tab_name: The name of the tab
            product_key: The key in the product dictionary to store the list
            button_text: The text for the add button
        """
        # Initialize attributes before calling parent constructor
        self.product_key = product_key
        self.button_text = button_text
        self.entries = []
        super().__init__(form, tab_name)
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure the product key exists and is a list
        if self.product_key not in self.product or not isinstance(self.product[self.product_key], list):
            self.product[self.product_key] = []
        
        # Add button for new entry
        add_btn = ttk.Button(self.frame, text=self.button_text, 
                           command=lambda: self.add_entry())
        add_btn.grid(row=100, column=0, sticky=tk.W, padx=5, pady=10)
        
        # Add existing entries
        for item in self.product[self.product_key]:
            self.add_entry(item)
    
    def add_entry(self, value=""):
        """Add an entry to the form"""
        # Create a frame for this entry
        row_idx = len(self.entries)
        entry_frame = ttk.Frame(self.frame)
        entry_frame.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Entry field
        entry_var = tk.StringVar(value=value)
        entry_field = ttk.Entry(entry_frame, textvariable=entry_var, width=50)
        entry_field.grid(row=0, column=0, padx=5)
        
        # Remove button
        def remove_entry():
            entry_frame.destroy()
            self.entries.remove(entry_data)
        
        remove_btn = ttk.Button(entry_frame, text="Remove", command=remove_entry)
        remove_btn.grid(row=0, column=1, padx=5)
        
        # Store entry data
        entry_data = {
            "entry_var": entry_var,
            "frame": entry_frame
        }
        self.entries.append(entry_data)
        
        # Move the add button to the bottom
        self.frame.children['!button'].grid(row=row_idx + 1, column=0, sticky=tk.W, padx=5, pady=10)
    
    def collect_data(self):
        """Collect data from the tab"""
        # Get entries
        items = []
        for entry in self.entries:
            value = entry["entry_var"].get().strip()
            if value:
                items.append(value)
        self.product[self.product_key] = items 