import tkinter as tk
from tkinter import ttk
from datetime import datetime
import re

class DateEntry(ttk.Frame):
    """A simple date entry widget using a single textbox with YYYY-MM-DD format"""
    def __init__(self, master=None, width=10, textvariable=None, initial_date=None, **kw):
        super().__init__(master, **kw)
        
        # Create StringVar if not provided
        if textvariable is None:
            self.date_var = tk.StringVar()
        else:
            self.date_var = textvariable
        
        # Default to current date if no initial date provided
        if initial_date is None:
            initial_date = datetime.now().strftime("%Y-%m-%d")
        elif isinstance(initial_date, datetime):
            initial_date = initial_date.strftime("%Y-%m-%d")
            
        self.date_var.set(initial_date)
        
        # Create entry widget
        vcmd = (self.register(self._validate), '%P')
        self.entry = ttk.Entry(self, width=width, textvariable=self.date_var, validate="focusout", validatecommand=vcmd)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add a calendar button (just for visual consistency)
        self.calendar_button = ttk.Button(self, text="📅", width=2, command=self._show_today)
        self.calendar_button.pack(side=tk.LEFT, padx=(2, 0))
        
        # Bind events
        self.entry.bind("<FocusOut>", self._on_focus_out)
    
    def _show_today(self):
        """Set the date to today when calendar button is clicked"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_var.set(today)
        
    def _validate(self, value):
        """Validate and format the date string"""
        if not value:
            return True
            
        # Try to parse the date
        try:
            # Handle different formats
            if re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$', value):  # MM-DD-YYYY or MM/DD/YYYY
                parts = re.split(r'[-/]', value)
                month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                if year < 100:
                    year += 2000
            elif re.match(r'^\d{2,4}[-/]\d{1,2}[-/]\d{1,2}$', value):  # YYYY-MM-DD or YYYY/MM/DD
                parts = re.split(r'[-/]', value)
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                if year < 100:
                    year += 2000
            else:
                # Try direct parsing
                date_obj = datetime.strptime(value, "%Y-%m-%d")
                year, month, day = date_obj.year, date_obj.month, date_obj.day
                
            # Validate date
            date_obj = datetime(year, month, day)
            formatted_date = date_obj.strftime("%Y-%m-%d")
            self.date_var.set(formatted_date)
            return True
        except (ValueError, IndexError):
            # If invalid, revert to current date
            self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
            return False
            
    def _on_focus_out(self, event):
        """Validate date when focus leaves the entry"""
        self._validate(self.date_var.get())
    
    def get_date(self):
        """Return the date string in YYYY-MM-DD format"""
        return self.date_var.get()
    
    def set_date(self, date):
        """Set the date"""
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
        self.date_var.set(date)
        self._validate(date) 