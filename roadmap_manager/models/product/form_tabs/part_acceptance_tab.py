import tkinter as tk
from tkinter import ttk
import datetime
from .base_tab import BaseTab
from ....date_entry import DateEntry

class PartAcceptanceTab(BaseTab):
    """Tab for part acceptance information"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.acceptance_entries = []
        super().__init__(form, "Part Acceptance")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure partAcceptance exists and is a list
        if "partAcceptance" not in self.product or not isinstance(self.product["partAcceptance"], list):
            self.product["partAcceptance"] = []
            print("Initialized empty partAcceptance list")
        else:
            print(f"Found existing partAcceptance: {self.product['partAcceptance']}")
        
        # Create a frame for the part acceptance list
        self.acceptance_frame = ttk.Frame(self.frame)
        self.acceptance_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create headers for the acceptance entries
        headers_frame = ttk.Frame(self.acceptance_frame)
        headers_frame.pack(fill=tk.X)
        
        # Define column widths that match the entry fields
        col_widths = {
            0: 30,  # Acceptance Criteria
            1: 12,  # Start Date
            2: 12,  # End Date
            3: 15,  # Status
            4: 15,  # Funding
            5: 5,   # Float
            6: 10   # Remove button
        }
        
        # Create headers with proper alignment
        ttk.Label(headers_frame, text="Acceptance Criteria", font=("TkDefaultFont", 9, "bold"), width=col_widths[0]).grid(row=0, column=0, padx=5)
        ttk.Label(headers_frame, text="Start Date", font=("TkDefaultFont", 9, "bold"), width=col_widths[1]).grid(row=0, column=1, padx=5)
        ttk.Label(headers_frame, text="End Date", font=("TkDefaultFont", 9, "bold"), width=col_widths[2]).grid(row=0, column=2, padx=5)
        ttk.Label(headers_frame, text="Status", font=("TkDefaultFont", 9, "bold"), width=col_widths[3]).grid(row=0, column=3, padx=5)
        ttk.Label(headers_frame, text="Funding", font=("TkDefaultFont", 9, "bold"), width=col_widths[4]).grid(row=0, column=4, padx=5)
        ttk.Label(headers_frame, text="Float", font=("TkDefaultFont", 9, "bold"), width=col_widths[5]).grid(row=0, column=5, padx=5)
        
        # Create a frame for existing acceptance entries
        self.existing_acceptance_frame = ttk.Frame(self.acceptance_frame)
        self.existing_acceptance_frame.pack(fill=tk.BOTH, expand=True)
        
        # Store the last save date for floating functionality
        self.last_save_date = datetime.datetime.now().strftime("%Y-%m-%d")
        if "lastSaveDate" in self.product:
            self.last_save_date = self.product["lastSaveDate"]
        
        # Add existing part acceptance entries
        for acceptance in self.product["partAcceptance"]:
            if isinstance(acceptance, dict):
                print(f"Adding existing acceptance: {acceptance}")
                self.add_acceptance_entry(
                    acceptance_value=acceptance.get("name", ""),
                    start_date=acceptance.get("startDate", ""),
                    end_date=acceptance.get("endDate", ""),
                    status=acceptance.get("status", ""),
                    funding=acceptance.get("funding", ""),
                    float_on_roadmap=acceptance.get("float", False),
                    float_date=acceptance.get("floatDate", ""),
                    additional_details=acceptance.get("additionalDetails", "")
                )
            elif isinstance(acceptance, str):
                print(f"Adding existing acceptance as name only: {acceptance}")
                self.add_acceptance_entry(acceptance_value=acceptance)
            else:
                print(f"Skipping invalid acceptance: {acceptance}")
        
        # Add button for new part acceptance at the bottom
        add_btn = ttk.Button(self.acceptance_frame, text="Add Part Acceptance", 
                           command=lambda: self.add_acceptance_entry())
        add_btn.pack(anchor=tk.W, pady=5)
    
    def add_acceptance_entry(self, acceptance_value="", start_date="", end_date="", status="", funding="", float_on_roadmap=False, float_date="", additional_details=""):
        """Add a part acceptance entry to the form"""
        print(f"Adding acceptance entry: {acceptance_value}")
        
        # If this is a floating task, adjust the dates based on time elapsed since last save
        if float_on_roadmap and float_date and start_date:
            try:
                # Calculate days elapsed since float date
                float_dt = datetime.datetime.strptime(float_date, "%Y-%m-%d")
                today = datetime.datetime.now()
                days_elapsed = (today - float_dt).days
                
                if days_elapsed > 0 and start_date:
                    # Adjust start date
                    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                    start_dt = start_dt + datetime.timedelta(days=days_elapsed)
                    start_date = start_dt.strftime("%Y-%m-%d")
                    
                    # Adjust end date if it exists
                    if end_date:
                        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                        end_dt = end_dt + datetime.timedelta(days=days_elapsed)
                        end_date = end_dt.strftime("%Y-%m-%d")
            except Exception as e:
                print(f"Error adjusting floating dates: {str(e)}")
        
        # Create a frame for this entry
        row_idx = len(self.acceptance_entries)
        acceptance_frame = ttk.Frame(self.existing_acceptance_frame)
        acceptance_frame.pack(fill=tk.X, pady=2)
        
        # Acceptance value
        value_var = tk.StringVar(value=acceptance_value)
        value_entry = ttk.Entry(acceptance_frame, textvariable=value_var, width=30)
        value_entry.grid(row=0, column=0, padx=5)
        
        # Start date
        start_date_entry = DateEntry(acceptance_frame, width=12, initial_date=start_date)
        start_date_entry.grid(row=0, column=1, padx=5)
        
        # End date
        end_date_entry = DateEntry(acceptance_frame, width=12, initial_date=end_date)
        end_date_entry.grid(row=0, column=2, padx=5)
        
        # Status dropdown
        status_var = tk.StringVar(value=status)
        status_options = ["Not Started", "In Progress", "Complete", "On Hold", "Cancelled"]
        status_dropdown = ttk.Combobox(acceptance_frame, textvariable=status_var, values=status_options, width=15)
        status_dropdown.grid(row=0, column=3, padx=5)
        
        # Funding dropdown
        funding_var = tk.StringVar(value=funding)
        funding_options = ["Unfunded", "Division IRAD", "Sector IRAD", "CRAD", "Program Funded", "External Task"]
        funding_dropdown = ttk.Combobox(acceptance_frame, textvariable=funding_var, values=funding_options, width=15)
        funding_dropdown.grid(row=0, column=4, padx=5)
        
        # Float on roadmap checkbox
        float_var = tk.BooleanVar(value=float_on_roadmap)
        float_check = ttk.Checkbutton(acceptance_frame, variable=float_var, text="")
        float_check.grid(row=0, column=5, padx=5)
        
        # Store float date (hidden)
        float_date_var = tk.StringVar(value=float_date)
        
        # Remove button
        def remove_entry():
            acceptance_frame.destroy()
            self.acceptance_entries.remove(entry_data)
        
        remove_btn = ttk.Button(acceptance_frame, text="Remove", command=remove_entry)
        remove_btn.grid(row=0, column=6, padx=5)
        
        # Additional Details section (second row)
        details_frame = ttk.Frame(acceptance_frame)
        details_frame.grid(row=1, column=0, columnspan=7, sticky=tk.W+tk.E, padx=5, pady=(2, 5))
        
        ttk.Label(details_frame, text="Additional Details:", font=("TkDefaultFont", 8, "bold")).pack(anchor=tk.W, pady=(5, 2))
        
        # Text box for additional details
        details_text = tk.Text(details_frame, height=3, width=80, wrap=tk.WORD)
        details_text.pack(fill=tk.X, expand=True)
        if additional_details:
            details_text.insert("1.0", additional_details)
        
        # Store entry data
        entry_data = {
            "value_var": value_var,
            "start_date_entry": start_date_entry,
            "end_date_entry": end_date_entry,
            "status_var": status_var,
            "funding_var": funding_var,
            "float_var": float_var,
            "float_date_var": float_date_var,
            "details_text": details_text,
            "frame": acceptance_frame
        }
        self.acceptance_entries.append(entry_data)
        return entry_data  # Return for testing/debugging
    
    def collect_data(self):
        """Collect data from the tab"""
        print("Collecting part acceptance data...")
        
        part_acceptance = []
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        for i, entry in enumerate(self.acceptance_entries):
            print(f"Processing acceptance entry {i}")
            value = entry["value_var"].get().strip()
            start_date = entry["start_date_entry"].get_date()
            end_date = entry["end_date_entry"].get_date()
            status = entry["status_var"].get()
            funding = entry["funding_var"].get()
            float_on_roadmap = entry["float_var"].get()
            additional_details = entry["details_text"].get("1.0", tk.END).strip()
            
            # If float is checked and float_date is empty, set it to today
            float_date = entry["float_date_var"].get()
            if float_on_roadmap and not float_date:
                float_date = today
            
            print(f"  Acceptance Value: '{value}'")
            print(f"  Start Date: '{start_date}'")
            print(f"  End Date: '{end_date}'")
            print(f"  Status: '{status}'")
            print(f"  Funding: '{funding}'")
            print(f"  Float on Roadmap: '{float_on_roadmap}'")
            
            if value:  # Only add if name is not empty
                acceptance_data = {
                    "name": value,
                    "startDate": start_date,
                    "endDate": end_date,
                    "status": status,
                    "funding": funding,
                    "float": float_on_roadmap,
                    "floatDate": float_date,
                    "additionalDetails": additional_details
                }
                part_acceptance.append(acceptance_data)
                print(f"  Added acceptance to partAcceptance list")
            else:
                print(f"  Skipping empty acceptance entry")
                
        print(f"Setting product['partAcceptance'] to {part_acceptance}")
        self.product["partAcceptance"] = part_acceptance
        
        # Store the current date as last save date
        self.product["lastSaveDate"] = today
        
        print(f"After update: product['partAcceptance'] = {self.product.get('partAcceptance', [])}")
        
        # Return True to indicate validation passed
        return True 