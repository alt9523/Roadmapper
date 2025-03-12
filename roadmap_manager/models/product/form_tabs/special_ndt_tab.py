import tkinter as tk
from tkinter import ttk
import datetime
from .base_tab import BaseTab
from ....date_entry import DateEntry

class SpecialNDTTab(BaseTab):
    """Tab for special NDT information"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.ndt_entries = []
        super().__init__(form, "Special NDT")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure specialNDT exists and is a list
        if "specialNDT" not in self.product or not isinstance(self.product["specialNDT"], list):
            self.product["specialNDT"] = []
            print("Initialized empty specialNDT list")
        else:
            print(f"Found existing specialNDT: {self.product['specialNDT']}")
        
        # Create a frame for the special NDT list
        self.ndt_frame = ttk.Frame(self.frame)
        self.ndt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create headers for the NDT entries
        headers_frame = ttk.Frame(self.ndt_frame)
        headers_frame.pack(fill=tk.X)
        
        # Define column widths that match the entry fields
        col_widths = {
            0: 30,  # NDT Name
            1: 12,  # Start Date
            2: 12,  # End Date
            3: 15,  # Status
            4: 15,  # Funding
            5: 5,   # Float
            6: 10   # Remove button
        }
        
        # Create headers with proper alignment
        ttk.Label(headers_frame, text="NDT Name", font=("TkDefaultFont", 9, "bold"), width=col_widths[0]).grid(row=0, column=0, padx=5)
        ttk.Label(headers_frame, text="Start Date", font=("TkDefaultFont", 9, "bold"), width=col_widths[1]).grid(row=0, column=1, padx=5)
        ttk.Label(headers_frame, text="End Date", font=("TkDefaultFont", 9, "bold"), width=col_widths[2]).grid(row=0, column=2, padx=5)
        ttk.Label(headers_frame, text="Status", font=("TkDefaultFont", 9, "bold"), width=col_widths[3]).grid(row=0, column=3, padx=5)
        ttk.Label(headers_frame, text="Funding", font=("TkDefaultFont", 9, "bold"), width=col_widths[4]).grid(row=0, column=4, padx=5)
        ttk.Label(headers_frame, text="Float", font=("TkDefaultFont", 9, "bold"), width=col_widths[5]).grid(row=0, column=5, padx=5)
        
        # Create a frame for existing NDT entries
        self.existing_ndt_frame = ttk.Frame(self.ndt_frame)
        self.existing_ndt_frame.pack(fill=tk.BOTH, expand=True)
        
        # Store the last save date for floating functionality
        self.last_save_date = datetime.datetime.now().strftime("%Y-%m-%d")
        if "lastSaveDate" in self.product:
            self.last_save_date = self.product["lastSaveDate"]
        
        # Add existing special NDT entries
        for ndt in self.product["specialNDT"]:
            if isinstance(ndt, dict):
                print(f"Adding existing NDT: {ndt}")
                self.add_ndt_entry(
                    ndt_value=ndt.get("name", ""),
                    start_date=ndt.get("startDate", ""),
                    end_date=ndt.get("endDate", ""),
                    status=ndt.get("status", ""),
                    funding=ndt.get("funding", ""),
                    float_on_roadmap=ndt.get("float", False),
                    float_date=ndt.get("floatDate", ""),
                    additional_details=ndt.get("additionalDetails", "")
                )
            elif isinstance(ndt, str):
                print(f"Adding existing NDT as name only: {ndt}")
                self.add_ndt_entry(ndt_value=ndt)
            else:
                print(f"Skipping invalid NDT: {ndt}")
        
        # Add button for new special NDT at the bottom
        add_btn = ttk.Button(self.ndt_frame, text="Add Special NDT", 
                           command=lambda: self.add_ndt_entry())
        add_btn.pack(anchor=tk.W, pady=5)
    
    def add_ndt_entry(self, ndt_value="", start_date="", end_date="", status="", funding="", float_on_roadmap=False, float_date="", additional_details=""):
        """Add a special NDT entry to the form"""
        print(f"Adding NDT entry: {ndt_value}")
        
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
        row_idx = len(self.ndt_entries)
        ndt_frame = ttk.Frame(self.existing_ndt_frame)
        ndt_frame.pack(fill=tk.X, pady=2)
        
        # NDT value
        value_var = tk.StringVar(value=ndt_value)
        value_entry = ttk.Entry(ndt_frame, textvariable=value_var, width=30)
        value_entry.grid(row=0, column=0, padx=5)
        
        # Start date
        start_date_entry = DateEntry(ndt_frame, width=12, initial_date=start_date)
        start_date_entry.grid(row=0, column=1, padx=5)
        
        # End date
        end_date_entry = DateEntry(ndt_frame, width=12, initial_date=end_date)
        end_date_entry.grid(row=0, column=2, padx=5)
        
        # Status dropdown
        status_var = tk.StringVar(value=status)
        status_options = ["Not Started", "In Progress", "Complete", "On Hold", "Cancelled"]
        status_dropdown = ttk.Combobox(ndt_frame, textvariable=status_var, values=status_options, width=15)
        status_dropdown.grid(row=0, column=3, padx=5)
        
        # Funding dropdown
        funding_var = tk.StringVar(value=funding)
        funding_options = ["Unfunded", "Division IRAD", "Sector IRAD", "CRAD", "Program Funded", "External Task"]
        funding_dropdown = ttk.Combobox(ndt_frame, textvariable=funding_var, values=funding_options, width=15)
        funding_dropdown.grid(row=0, column=4, padx=5)
        
        # Float on roadmap checkbox
        float_var = tk.BooleanVar(value=float_on_roadmap)
        float_check = ttk.Checkbutton(ndt_frame, variable=float_var, text="")
        float_check.grid(row=0, column=5, padx=5)
        
        # Store float date (hidden)
        float_date_var = tk.StringVar(value=float_date)
        
        # Remove button
        def remove_entry():
            ndt_frame.destroy()
            self.ndt_entries.remove(entry_data)
        
        remove_btn = ttk.Button(ndt_frame, text="Remove", command=remove_entry)
        remove_btn.grid(row=0, column=6, padx=5)
        
        # Additional Details section (second row)
        details_frame = ttk.Frame(ndt_frame)
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
            "frame": ndt_frame
        }
        self.ndt_entries.append(entry_data)
        return entry_data  # Return for testing/debugging
    
    def collect_data(self):
        """Collect data from the tab"""
        print("Collecting special NDT data...")
        
        special_ndt = []
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        for i, entry in enumerate(self.ndt_entries):
            print(f"Processing NDT entry {i}")
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
            
            print(f"  NDT Value: '{value}'")
            print(f"  Start Date: '{start_date}'")
            print(f"  End Date: '{end_date}'")
            print(f"  Status: '{status}'")
            print(f"  Funding: '{funding}'")
            print(f"  Float on Roadmap: '{float_on_roadmap}'")
            
            if value:  # Only add if name is not empty
                ndt_data = {
                    "name": value,
                    "startDate": start_date,
                    "endDate": end_date,
                    "status": status,
                    "funding": funding,
                    "float": float_on_roadmap,
                    "floatDate": float_date,
                    "additionalDetails": additional_details
                }
                special_ndt.append(ndt_data)
                print(f"  Added NDT to specialNDT list")
            else:
                print(f"  Skipping empty NDT entry")
        
        print(f"Setting product['specialNDT'] to {special_ndt}")
        self.product["specialNDT"] = special_ndt
        
        # Store the current date as last save date
        self.product["lastSaveDate"] = today
        
        print(f"After update: product['specialNDT'] = {self.product.get('specialNDT', [])}")
        
        # Return True to indicate validation passed
        return True 