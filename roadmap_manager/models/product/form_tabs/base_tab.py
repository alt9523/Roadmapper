import tkinter as tk
from tkinter import ttk

class BaseTab:
    """Base class for all form tabs"""
    
    def __init__(self, form, tab_name="Tab"):
        print(f"Initializing {self.__class__.__name__} with tab_name={tab_name}")
        self.form = form
        self.product = form.product
        self.model = form.model
        
        # Create the tab frame
        self.frame = ttk.Frame(form.notebook)
        form.notebook.add(self.frame, text=tab_name)
        
        # Note: initialize() is now called explicitly from ProductForm
        print(f"Added {tab_name} tab to notebook")
    
    def initialize(self):
        """Initialize the tab content - to be overridden by subclasses"""
        print(f"Base initialize method called for {self.__class__.__name__}")
        pass
    
    def collect_data(self):
        """Collect data from the tab - to be overridden by subclasses"""
        print(f"Base collect_data method called for {self.__class__.__name__}")
        pass 