import tkinter as tk
from tkinter import ttk
import datetime
from ....date_entry import DateEntry
from .base_tab import BaseTab

class DesignToolsTab(BaseTab):
    """Tab for design tools information"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.tool_entries = []
        super().__init__(form, "Design Tools")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure designTools exists and is a list
        if "designTools" not in self.product or not isinstance(self.product["designTools"], list):
            self.product["designTools"] = []
            print("Initialized empty designTools list")
        else:
            print(f"Found existing designTools: {self.product['designTools']}")
        
        # Create a frame for the design tools list
        self.tools_frame = ttk.Frame(self.frame)
        self.tools_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create headers for the tool entries
        headers_frame = ttk.Frame(self.tools_frame)
        headers_frame.pack(fill=tk.X)
        
        # Define column widths that match the entry fields
        col_widths = {
            0: 30,  # Tool Name
            1: 12,  # Start Date
            2: 12,  # End Date
            3: 15,  # Status
            4: 15,  # Funding
            5: 5,   # Float
            6: 10   # Remove button
        }
        
        # Create headers with proper alignment
        ttk.Label(headers_frame, text="Tool Name", font=("TkDefaultFont", 9, "bold"), width=col_widths[0]).grid(row=0, column=0, padx=5)
        ttk.Label(headers_frame, text="Start Date", font=("TkDefaultFont", 9, "bold"), width=col_widths[1]).grid(row=0, column=1, padx=5)
        ttk.Label(headers_frame, text="End Date", font=("TkDefaultFont", 9, "bold"), width=col_widths[2]).grid(row=0, column=2, padx=5)
        ttk.Label(headers_frame, text="Status", font=("TkDefaultFont", 9, "bold"), width=col_widths[3]).grid(row=0, column=3, padx=5)
        ttk.Label(headers_frame, text="Funding", font=("TkDefaultFont", 9, "bold"), width=col_widths[4]).grid(row=0, column=4, padx=5)
        ttk.Label(headers_frame, text="Float", font=("TkDefaultFont", 9, "bold"), width=col_widths[5]).grid(row=0, column=5, padx=5)
        
        # Create a frame for existing tools
        self.existing_tools_frame = ttk.Frame(self.tools_frame)
        self.existing_tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # Store the last save date for floating functionality
        self.last_save_date = datetime.datetime.now().strftime("%Y-%m-%d")
        if "lastSaveDate" in self.product:
            self.last_save_date = self.product["lastSaveDate"]
        
        # Add existing design tool entries
        for tool in self.product["designTools"]:
            if isinstance(tool, dict):
                name = tool.get("name", "")
                start_date = tool.get("start", "")
                end_date = tool.get("end", "")
                status = tool.get("status", "")
                funding = tool.get("funding", "")
                float_on_roadmap = tool.get("float", False)
                float_date = tool.get("floatDate", "")
                additional_details = tool.get("additionalDetails", "")
                print(f"Adding existing tool: {name}")
                self.add_tool_entry(name, start_date, end_date, status, funding, float_on_roadmap, float_date, additional_details)
            elif isinstance(tool, str):
                print(f"Adding existing tool (string): {tool}")
                self.add_tool_entry(tool)
            else:
                print(f"Skipping non-dict/non-string tool: {tool}")
        
        # Add button for new design tool at the bottom
        add_btn = ttk.Button(self.tools_frame, text="Add Design Tool", 
                           command=lambda: self.add_tool_entry())
        add_btn.pack(anchor=tk.W, pady=5)
    
    def add_tool_entry(self, name="", start_date="", end_date="", status="", funding="", float_on_roadmap=False, float_date="", additional_details=""):
        """Add a design tool entry to the form"""
        print(f"Adding tool entry with name={name}")
        
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
        row_idx = len(self.tool_entries)
        tool_frame = ttk.Frame(self.existing_tools_frame)
        tool_frame.pack(fill=tk.X, pady=2)
        
        # Tool name
        name_var = tk.StringVar(value=name)
        name_entry = ttk.Entry(tool_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=0, padx=5)
        
        # Start date
        start_var = tk.StringVar(value=start_date)
        start_date_entry = DateEntry(tool_frame, textvariable=start_var, width=12, initial_date=start_date)
        start_date_entry.grid(row=0, column=1, padx=5)
        
        # End date
        end_var = tk.StringVar(value=end_date)
        end_date_entry = DateEntry(tool_frame, textvariable=end_var, width=12, initial_date=end_date)
        end_date_entry.grid(row=0, column=2, padx=5)
        
        # Status
        status_var = tk.StringVar(value=status)
        status_combo = ttk.Combobox(tool_frame, textvariable=status_var, width=15)
        status_combo['values'] = ("Planned", "In Progress", "Complete")
        status_combo.grid(row=0, column=3, padx=5)
        
        # Funding
        funding_var = tk.StringVar(value=funding)
        funding_combo = ttk.Combobox(tool_frame, textvariable=funding_var, width=15)
        funding_combo['values'] = ("Unfunded", "Division IRAD", "Sector IRAD", "CRAD", "Program Funded", "External Task")
        funding_combo.grid(row=0, column=4, padx=5)
        
        # Float on roadmap checkbox
        float_var = tk.BooleanVar(value=float_on_roadmap)
        float_check = ttk.Checkbutton(tool_frame, variable=float_var, text="")
        float_check.grid(row=0, column=5, padx=5)
        
        # Store float date (hidden)
        float_date_var = tk.StringVar(value=float_date)
        
        # Remove button
        def remove_entry():
            tool_frame.destroy()
            self.tool_entries.remove(entry_data)
        
        remove_btn = ttk.Button(tool_frame, text="Remove", command=remove_entry)
        remove_btn.grid(row=0, column=6, padx=5)
        
        # Additional Details section (second row)
        details_frame = ttk.Frame(tool_frame)
        details_frame.grid(row=1, column=0, columnspan=7, sticky=tk.W+tk.E, padx=5, pady=(2, 5))
        
        ttk.Label(details_frame, text="Additional Details:", font=("TkDefaultFont", 8, "bold")).pack(anchor=tk.W, pady=(5, 2))
        
        # Text box for additional details
        details_text = tk.Text(details_frame, height=3, width=80, wrap=tk.WORD)
        details_text.pack(fill=tk.X, expand=True)
        if additional_details:
            details_text.insert("1.0", additional_details)
        
        # Store entry data
        entry_data = {
            "name_var": name_var,
            "start_var": start_var,
            "end_var": end_var,
            "status_var": status_var,
            "funding_var": funding_var,
            "float_var": float_var,
            "float_date_var": float_date_var,
            "details_text": details_text,
            "start_date_entry": start_date_entry,
            "end_date_entry": end_date_entry,
            "frame": tool_frame
        }
        self.tool_entries.append(entry_data)
        print(f"Added tool entry: {name}")
        return entry_data  # Return the entry data for testing/debugging
    
    def collect_data(self):
        """Collect data from the form and update the product"""
        print("Collecting design tools data...")
        
        # Get the design tools
        design_tools = []
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Iterate through the tool entries
        for i, entry in enumerate(self.tool_entries):
            print(f"Processing design tool entry {i}")
            
            # Get the values
            tool_name = entry["name_var"].get().strip()
            
            print(f"  Tool Name: '{tool_name}'")
            
            # Only add if name is filled
            if tool_name:
                # Get dates directly from DateEntry widgets
                start_date = entry["start_date_entry"].get_date()
                end_date = entry["end_date_entry"].get_date()
                float_on_roadmap = entry["float_var"].get()
                additional_details = entry["details_text"].get("1.0", tk.END).strip()
                
                # If float is checked and float_date is empty, set it to today
                float_date = entry["float_date_var"].get()
                if float_on_roadmap and not float_date:
                    float_date = today
                
                tool_data = {
                    "name": tool_name,
                    "start": start_date,
                    "end": end_date,
                    "status": entry["status_var"].get(),
                    "funding": entry["funding_var"].get(),
                    "float": float_on_roadmap,
                    "floatDate": float_date,
                    "additionalDetails": additional_details
                }
                
                design_tools.append(tool_data)
                print(f"  Added tool to design_tools list")
            else:
                print(f"  Skipping empty tool entry")
        
        # Update the product
        self.product["designTools"] = design_tools
        
        # Store the current date as last save date
        self.product["lastSaveDate"] = today
        
        print(f"Updated product design tools: {self.product['designTools']}")
        
        # Return True to indicate validation passed
        return True 