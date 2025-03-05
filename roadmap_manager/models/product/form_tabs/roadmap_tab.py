import tkinter as tk
from tkinter import ttk
from ....date_entry import DateEntry
from .base_tab import BaseTab

class RoadmapTab(BaseTab):
    """Tab for roadmap tasks"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.roadmap_entries = []
        super().__init__(form, "Roadmap")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure roadmap exists and is a list
        if "roadmap" not in self.product or not isinstance(self.product["roadmap"], list):
            self.product["roadmap"] = []
        
        # Add button for new roadmap task
        add_task_btn = ttk.Button(self.frame, text="Add Roadmap Task", 
                                command=lambda: self.add_roadmap_task())
        add_task_btn.grid(row=100, column=0, sticky=tk.W, padx=5, pady=10)
        
        # Add existing roadmap tasks
        for task in self.product["roadmap"]:
            self.add_roadmap_task(task)
    
    def add_roadmap_task(self, task_data=None):
        """Add a roadmap task to the form"""
        if task_data is None:
            task_data = {"task": "", "start": "", "end": "", "status": "", "lane": "", "fundingType": ""}
        
        # Create a frame for this entry
        row_idx = len(self.roadmap_entries)
        task_frame = ttk.Frame(self.frame)
        task_frame.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Task name
        ttk.Label(task_frame, text="Task:").grid(row=0, column=0, sticky=tk.W, padx=5)
        task_var = tk.StringVar(value=task_data.get("task", ""))
        ttk.Entry(task_frame, textvariable=task_var, width=30).grid(row=0, column=1, padx=5)
        
        # Start date
        ttk.Label(task_frame, text="Start:").grid(row=0, column=2, sticky=tk.W, padx=5)
        start_var = tk.StringVar(value=task_data.get("start", ""))
        start_date_entry = DateEntry(task_frame, textvariable=start_var, width=12, initial_date=task_data.get("start", ""))
        start_date_entry.grid(row=0, column=3, padx=5)
        
        # End date
        ttk.Label(task_frame, text="End:").grid(row=0, column=4, sticky=tk.W, padx=5)
        end_var = tk.StringVar(value=task_data.get("end", ""))
        end_date_entry = DateEntry(task_frame, textvariable=end_var, width=12, initial_date=task_data.get("end", ""))
        end_date_entry.grid(row=0, column=5, padx=5)
        
        # Status
        ttk.Label(task_frame, text="Status:").grid(row=1, column=0, sticky=tk.W, padx=5)
        status_var = tk.StringVar(value=task_data.get("status", ""))
        status_combo = ttk.Combobox(task_frame, textvariable=status_var, width=15)
        status_combo['values'] = ("Planned", "In Progress", "Complete")
        status_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # Lane
        ttk.Label(task_frame, text="Lane:").grid(row=1, column=2, sticky=tk.W, padx=5)
        lane_var = tk.StringVar(value=task_data.get("lane", ""))
        lane_combo = ttk.Combobox(task_frame, textvariable=lane_var, width=15)
        lane_combo['values'] = ("Design", "Manufacturing", "M&P", "Quality")
        lane_combo.grid(row=1, column=3, padx=5, pady=2)
        
        # Funding Type
        ttk.Label(task_frame, text="Funding:").grid(row=1, column=4, sticky=tk.W, padx=5)
        funding_var = tk.StringVar(value=task_data.get("fundingType", ""))
        funding_combo = ttk.Combobox(task_frame, textvariable=funding_var, width=15)
        funding_combo['values'] = ("Division IRAD", "Sector IRAD", "CRAD", "Planned")
        funding_combo.grid(row=1, column=5, padx=5, pady=2)
        
        # Remove button
        def remove_task():
            task_frame.destroy()
            self.roadmap_entries.remove(entry_data)
        
        remove_btn = ttk.Button(task_frame, text="Remove", command=remove_task)
        remove_btn.grid(row=0, column=6, rowspan=2, padx=5)
        
        # Store entry data
        entry_data = {
            "task_var": task_var,
            "start_var": start_var,
            "end_var": end_var,
            "status_var": status_var,
            "lane_var": lane_var,
            "funding_var": funding_var,
            "frame": task_frame,
            "start_date_entry": start_date_entry,
            "end_date_entry": end_date_entry
        }
        self.roadmap_entries.append(entry_data)
        
        # Move the add button to the bottom
        self.frame.children['!button'].grid(row=row_idx + 1, column=0, sticky=tk.W, padx=5, pady=10)
    
    def collect_data(self):
        """Collect data from the tab"""
        # Get roadmap tasks
        roadmap_tasks = []
        for entry in self.roadmap_entries:
            task = entry["task_var"].get()
            if task:
                # Get dates directly from DateEntry widgets
                start_date = entry["start_date_entry"].get_date()
                end_date = entry["end_date_entry"].get_date()
                
                task_data = {
                    "task": task,
                    "start": start_date,
                    "end": end_date,
                    "status": entry["status_var"].get()
                }
                
                # Add optional fields if they exist
                if entry["lane_var"].get():
                    task_data["lane"] = entry["lane_var"].get()
                
                if entry["funding_var"].get():
                    task_data["fundingType"] = entry["funding_var"].get()
                
                roadmap_tasks.append(task_data)
        self.product["roadmap"] = roadmap_tasks
        
        # Return True to indicate validation passed
        return True 