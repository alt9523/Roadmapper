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
                "costSavings": "",
                "scheduleSavings": "",
                "performanceGains": ""
            }
        
        # Cost Savings
        ttk.Label(self.frame, text="Cost Savings:").grid(row=0, column=0, sticky=tk.NW, padx=10, pady=5)
        self.cost_text = tk.Text(self.frame, height=4, width=50)
        self.cost_text.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Set existing value if available
        if "costSavings" in self.product["businessCase"]:
            self.cost_text.insert("1.0", self.product["businessCase"]["costSavings"])
        
        # Schedule Savings
        ttk.Label(self.frame, text="Schedule Savings:").grid(row=1, column=0, sticky=tk.NW, padx=10, pady=5)
        self.schedule_text = tk.Text(self.frame, height=4, width=50)
        self.schedule_text.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Set existing value if available
        if "scheduleSavings" in self.product["businessCase"]:
            self.schedule_text.insert("1.0", self.product["businessCase"]["scheduleSavings"])
        
        # Performance Gains
        ttk.Label(self.frame, text="Performance Gains:").grid(row=2, column=0, sticky=tk.NW, padx=10, pady=5)
        self.performance_text = tk.Text(self.frame, height=4, width=50)
        self.performance_text.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Set existing value if available
        if "performanceGains" in self.product["businessCase"]:
            self.performance_text.insert("1.0", self.product["businessCase"]["performanceGains"])
    
    def collect_data(self):
        """Collect data from the tab"""
        # Get business case
        business_case = {
            "costSavings": self.cost_text.get("1.0", tk.END).strip(),
            "scheduleSavings": self.schedule_text.get("1.0", tk.END).strip(),
            "performanceGains": self.performance_text.get("1.0", tk.END).strip()
        }
        self.product["businessCase"] = business_case 