import tkinter as tk
from tkinter import ttk, messagebox

class BaseModel:
    """Base class for all models with common functionality"""
    
    def __init__(self, manager):
        self.manager = manager
        self.data = manager.data
        self.status_var = manager.status_var
    
    def update_status(self, message):
        """Update the status bar message"""
        self.status_var.set(message)
    
    def show_error(self, title, message):
        """Show an error message dialog"""
        messagebox.showerror(title, message)
    
    def show_info(self, title, message):
        """Show an information message dialog"""
        messagebox.showinfo(title, message)
    
    def confirm_delete(self, name):
        """Show a confirmation dialog for deletion"""
        return messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?") 