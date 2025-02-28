import tkinter as tk
from tkinter import ttk
from ....date_entry import DateEntry
from .base_tab import BaseTab

class MilestonesTab(BaseTab):
    """Tab for milestones"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.milestone_entries = []
        super().__init__(form, "Milestones")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure milestones exists and is a list
        if "milestones" not in self.product or not isinstance(self.product["milestones"], list):
            self.product["milestones"] = []
        
        # Add button for new milestone
        add_ms_btn = ttk.Button(self.frame, text="Add Milestone", 
                              command=lambda: self.add_milestone())
        add_ms_btn.grid(row=100, column=0, sticky=tk.W, padx=5, pady=10)
        
        # Add existing milestones
        for milestone in self.product["milestones"]:
            self.add_milestone(milestone)
    
    def add_milestone(self, milestone_data=None):
        """Add a milestone to the form"""
        if milestone_data is None:
            milestone_data = {"name": "", "date": "", "description": ""}
        
        # Create a frame for this entry
        row_idx = len(self.milestone_entries)
        ms_frame = ttk.Frame(self.frame)
        ms_frame.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Milestone name
        ttk.Label(ms_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        name_var = tk.StringVar(value=milestone_data.get("name", ""))
        ttk.Entry(ms_frame, textvariable=name_var, width=20).grid(row=0, column=1, padx=5)
        
        # Date
        ttk.Label(ms_frame, text="Date:").grid(row=0, column=2, sticky=tk.W, padx=5)
        date_var = tk.StringVar(value=milestone_data.get("date", ""))
        DateEntry(ms_frame, textvariable=date_var, width=12).grid(row=0, column=3, padx=5)
        
        # Description
        ttk.Label(ms_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, padx=5)
        desc_var = tk.StringVar(value=milestone_data.get("description", ""))
        ttk.Entry(ms_frame, textvariable=desc_var, width=50).grid(row=1, column=1, columnspan=3, padx=5, pady=2)
        
        # Remove button
        def remove_milestone():
            ms_frame.destroy()
            self.milestone_entries.remove(entry_data)
        
        remove_btn = ttk.Button(ms_frame, text="Remove", command=remove_milestone)
        remove_btn.grid(row=0, column=4, rowspan=2, padx=5)
        
        # Store entry data
        entry_data = {
            "name_var": name_var,
            "date_var": date_var,
            "desc_var": desc_var,
            "frame": ms_frame
        }
        self.milestone_entries.append(entry_data)
        
        # Move the add button to the bottom
        self.frame.children['!button'].grid(row=row_idx + 1, column=0, sticky=tk.W, padx=5, pady=10)
    
    def collect_data(self):
        """Collect data from the tab"""
        # Get milestones
        milestones = []
        for entry in self.milestone_entries:
            name = entry["name_var"].get()
            if name:
                milestone_data = {
                    "name": name,
                    "date": entry["date_var"].get(),
                    "description": entry["desc_var"].get()
                }
                milestones.append(milestone_data)
        self.product["milestones"] = milestones 