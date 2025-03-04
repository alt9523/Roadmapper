import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab

class BusinessCaseTab(BaseTab):
    """Tab for business case information"""
    
    def __init__(self, form):
        super().__init__(form, "Business Case")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure businessCase exists and is a dictionary
        if "businessCase" not in self.product or not isinstance(self.product["businessCase"], dict):
            self.product["businessCase"] = {
                "costSavings": {"title": "Cost Savings", "description": "", "value": ""},
                "scheduleSavings": {"title": "Schedule Savings", "description": "", "value": ""},
                "performanceGains": {"title": "Performance Gains", "description": "", "value": ""}
            }
        
        # Convert old format to new format if needed
        if "businessCase" in self.product:
            for key in ["costSavings", "scheduleSavings", "performanceGains"]:
                if key in self.product["businessCase"] and isinstance(self.product["businessCase"][key], str):
                    # Convert string to dictionary with description and empty value
                    old_text = self.product["businessCase"][key]
                    self.product["businessCase"][key] = {
                        "title": key.replace("Savings", " Savings").replace("Gains", " Gains"),
                        "description": old_text,
                        "value": ""
                    }
        
        # Create header row
        ttk.Label(self.frame, text="Title", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(self.frame, text="Description", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Label(self.frame, text="Value (%)", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        
        # Row 1: Cost Savings
        row = 1
        
        # Title
        self.cost_title_var = tk.StringVar(value=self.product["businessCase"].get("costSavings", {}).get("title", "Cost Savings"))
        ttk.Entry(self.frame, textvariable=self.cost_title_var, width=20).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        
        # Description
        self.cost_text = tk.Text(self.frame, height=3, width=40)
        self.cost_text.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        # Set existing description if available
        cost_desc = self.product["businessCase"].get("costSavings", {}).get("description", "")
        if cost_desc:
            self.cost_text.insert("1.0", cost_desc)
        
        # Value percentage
        self.cost_value_var = tk.StringVar(value=self.product["businessCase"].get("costSavings", {}).get("value", ""))
        cost_value_entry = ttk.Entry(self.frame, textvariable=self.cost_value_var, width=10)
        cost_value_entry.grid(row=row, column=2, padx=10, pady=5, sticky=tk.W)
        ttk.Label(self.frame, text="%").grid(row=row, column=3, padx=0, pady=5, sticky=tk.W)
        
        # Row 2: Schedule Savings
        row = 2
        
        # Title
        self.schedule_title_var = tk.StringVar(value=self.product["businessCase"].get("scheduleSavings", {}).get("title", "Schedule Savings"))
        ttk.Entry(self.frame, textvariable=self.schedule_title_var, width=20).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        
        # Description
        self.schedule_text = tk.Text(self.frame, height=3, width=40)
        self.schedule_text.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        # Set existing description if available
        schedule_desc = self.product["businessCase"].get("scheduleSavings", {}).get("description", "")
        if schedule_desc:
            self.schedule_text.insert("1.0", schedule_desc)
        
        # Value percentage
        self.schedule_value_var = tk.StringVar(value=self.product["businessCase"].get("scheduleSavings", {}).get("value", ""))
        schedule_value_entry = ttk.Entry(self.frame, textvariable=self.schedule_value_var, width=10)
        schedule_value_entry.grid(row=row, column=2, padx=10, pady=5, sticky=tk.W)
        ttk.Label(self.frame, text="%").grid(row=row, column=3, padx=0, pady=5, sticky=tk.W)
        
        # Row 3: Performance Gains
        row = 3
        
        # Title
        self.performance_title_var = tk.StringVar(value=self.product["businessCase"].get("performanceGains", {}).get("title", "Performance Gains"))
        ttk.Entry(self.frame, textvariable=self.performance_title_var, width=20).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
        
        # Description
        self.performance_text = tk.Text(self.frame, height=3, width=40)
        self.performance_text.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        # Set existing description if available
        performance_desc = self.product["businessCase"].get("performanceGains", {}).get("description", "")
        if performance_desc:
            self.performance_text.insert("1.0", performance_desc)
        
        # Value percentage
        self.performance_value_var = tk.StringVar(value=self.product["businessCase"].get("performanceGains", {}).get("value", ""))
        performance_value_entry = ttk.Entry(self.frame, textvariable=self.performance_value_var, width=10)
        performance_value_entry.grid(row=row, column=2, padx=10, pady=5, sticky=tk.W)
        ttk.Label(self.frame, text="%").grid(row=row, column=3, padx=0, pady=5, sticky=tk.W)
    
    def collect_data(self):
        """Collect data from the tab"""
        # Get business case data with title, description, and value
        business_case = {
            "costSavings": {
                "title": self.cost_title_var.get(),
                "description": self.cost_text.get("1.0", tk.END).strip(),
                "value": self.cost_value_var.get().strip()
            },
            "scheduleSavings": {
                "title": self.schedule_title_var.get(),
                "description": self.schedule_text.get("1.0", tk.END).strip(),
                "value": self.schedule_value_var.get().strip()
            },
            "performanceGains": {
                "title": self.performance_title_var.get(),
                "description": self.performance_text.get("1.0", tk.END).strip(),
                "value": self.performance_value_var.get().strip()
            }
        }
        self.product["businessCase"] = business_case
        
        # Return True to indicate validation passed
        return True 