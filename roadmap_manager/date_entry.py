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
        
        # Print for debugging
        print(f"DateEntry initialization with initial_date: '{initial_date}', type: {type(initial_date)}")
        
        # Handle initial date correctly
        if initial_date and isinstance(initial_date, str) and initial_date.strip():
            # Try to convert the date string to YYYY-MM-DD format
            try:
                # Handle different formats
                if re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$', initial_date):  # MM-DD-YYYY or MM/DD/YYYY
                    parts = re.split(r'[-/]', initial_date)
                    month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                    if year < 100:
                        year += 2000
                    date_obj = datetime(year, month, day)
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    print(f"Converted MM/DD/YYYY date to: '{formatted_date}'")
                    self.date_var.set(formatted_date)
                elif re.match(r'^\d{2,4}[-/]\d{1,2}[-/]\d{1,2}$', initial_date):  # YYYY-MM-DD or YYYY/MM/DD
                    parts = re.split(r'[-/]', initial_date)
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    if year < 100:
                        year += 2000
                    date_obj = datetime(year, month, day)
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    print(f"Converted YYYY/MM/DD date to: '{formatted_date}'")
                    self.date_var.set(formatted_date)
                else:
                    # Try multiple formats
                    try:
                        # Try YYYY-MM-DD first (already in correct format)
                        date_obj = datetime.strptime(initial_date, "%Y-%m-%d")
                        self.date_var.set(initial_date)
                        print(f"Using existing YYYY-MM-DD date: '{initial_date}'")
                    except ValueError:
                        try:
                            # Try MM/DD/YYYY
                            date_obj = datetime.strptime(initial_date, "%m/%d/%Y")
                            formatted_date = date_obj.strftime("%Y-%m-%d")
                            self.date_var.set(formatted_date)
                            print(f"Converted MM/DD/YYYY date to: '{formatted_date}'")
                        except ValueError:
                            # If all else fails, just use the string as is
                            print(f"Using date string as-is: '{initial_date}'")
                            self.date_var.set(initial_date)
            except (ValueError, IndexError) as e:
                print(f"Date parsing error: {e}, using original string")
                self.date_var.set(initial_date)
        elif initial_date and isinstance(initial_date, datetime):
            # Convert datetime to string
            date_str = initial_date.strftime("%Y-%m-%d")
            print(f"Setting date from datetime: '{date_str}'")
            self.date_var.set(date_str)
        else:
            # Leave empty if no date provided
            print("No initial date provided, leaving empty")
            self.date_var.set("")
        
        # Create entry widget
        vcmd = (self.register(self._validate), '%P')
        self.entry = ttk.Entry(self, width=width, textvariable=self.date_var, validate="focusout", validatecommand=vcmd)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add a calendar button (just for visual consistency)
        self.calendar_button = ttk.Button(self, text="📅", width=2, command=self._show_today)
        self.calendar_button.pack(side=tk.LEFT, padx=(2, 0))
        
        # Bind events
        self.entry.bind("<FocusOut>", self._on_focus_out)
        
        # Print current value for debugging
        print(f"DateEntry initialized with value: '{self.date_var.get()}'")
    
    def _show_today(self):
        """Set the date to today when calendar button is clicked"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_var.set(today)
        print(f"Set date to today: '{today}'")
        
    def _validate(self, value):
        """Validate and format the date string"""
        print(f"Validating date: '{value}'")
        
        if not value or value.strip() == "":
            # Allow empty values
            print("Empty value, keeping empty")
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
                # Try direct parsing with multiple formats
                try:
                    # Try YYYY-MM-DD first
                    date_obj = datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    try:
                        # Try MM/DD/YYYY
                        date_obj = datetime.strptime(value, "%m/%d/%Y")
                    except ValueError:
                        # Try DD/MM/YYYY
                        date_obj = datetime.strptime(value, "%d/%m/%Y")
                year, month, day = date_obj.year, date_obj.month, date_obj.day
                
            # Validate date
            date_obj = datetime(year, month, day)
            formatted_date = date_obj.strftime("%Y-%m-%d")
            print(f"Formatted date: '{formatted_date}'")
            self.date_var.set(formatted_date)
            return True
        except (ValueError, IndexError) as e:
            print(f"Date validation error: {e}")
            # Only reset to current date if the value is not empty and looks like a date attempt
            if value.strip() and any(c.isdigit() for c in value):
                print(f"Invalid date format, setting to today")
                self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
            return False
            
    def _on_focus_out(self, event):
        """Validate date when focus leaves the entry"""
        value = self.date_var.get()
        print(f"Focus out with value: '{value}'")
        
        if value.strip():  # Only validate non-empty values
            self._validate(value)
    
    def get_date(self):
        """Return the date string in YYYY-MM-DD format or empty string"""
        date_val = self.date_var.get().strip()
        print(f"get_date returning: '{date_val}'")
        return date_val
    
    def set_date(self, date):
        """Set the date"""
        print(f"set_date called with: '{date}'")
        
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
            
        if date and isinstance(date, str) and date.strip():
            # Try to convert the date string to YYYY-MM-DD format
            try:
                # Handle different formats
                if re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$', date):  # MM-DD-YYYY or MM/DD/YYYY
                    parts = re.split(r'[-/]', date)
                    month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                    if year < 100:
                        year += 2000
                    date_obj = datetime(year, month, day)
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    print(f"Converted MM/DD/YYYY date to: '{formatted_date}'")
                    self.date_var.set(formatted_date)
                elif re.match(r'^\d{2,4}[-/]\d{1,2}[-/]\d{1,2}$', date):  # YYYY-MM-DD or YYYY/MM/DD
                    parts = re.split(r'[-/]', date)
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    if year < 100:
                        year += 2000
                    date_obj = datetime(year, month, day)
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    print(f"Converted YYYY/MM/DD date to: '{formatted_date}'")
                    self.date_var.set(formatted_date)
                else:
                    # Try multiple formats
                    try:
                        # Try YYYY-MM-DD first (already in correct format)
                        date_obj = datetime.strptime(date, "%Y-%m-%d")
                        self.date_var.set(date)
                        print(f"Using existing YYYY-MM-DD date: '{date}'")
                    except ValueError:
                        try:
                            # Try MM/DD/YYYY
                            date_obj = datetime.strptime(date, "%m/%d/%Y")
                            formatted_date = date_obj.strftime("%Y-%m-%d")
                            self.date_var.set(formatted_date)
                            print(f"Converted MM/DD/YYYY date to: '{formatted_date}'")
                        except ValueError:
                            # If all else fails, just use the string as is
                            print(f"Using date string as-is: '{date}'")
                            self.date_var.set(date)
                # Validate the date
                self._validate(self.date_var.get())
            except (ValueError, IndexError) as e:
                print(f"Date parsing error: {e}, using original string")
                self.date_var.set(date)
                # Validate the date
                self._validate(date)
        else:
            print("Setting empty date")
            self.date_var.set("") 