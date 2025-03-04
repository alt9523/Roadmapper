import tkinter as tk
from tkinter import ttk
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
        
        # Create a frame for existing tools
        self.existing_tools_frame = ttk.Frame(self.tools_frame)
        self.existing_tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add existing design tool entries
        for tool in self.product["designTools"]:
            if isinstance(tool, dict):
                name = tool.get("name", "")
                print(f"Adding existing tool: {name}")
                self.add_tool_entry(name)
            elif isinstance(tool, str):
                print(f"Adding existing tool (string): {tool}")
                self.add_tool_entry(tool)
            else:
                print(f"Skipping non-dict/non-string tool: {tool}")
        
        # Add button for new design tool at the bottom
        add_btn = ttk.Button(self.tools_frame, text="Add Design Tool", 
                           command=lambda: self.add_tool_entry())
        add_btn.pack(anchor=tk.W, pady=5)
    
    def add_tool_entry(self, name=""):
        """Add a design tool entry to the form"""
        print(f"Adding tool entry with name={name}")
        
        # Create a frame for this entry
        row_idx = len(self.tool_entries)
        tool_frame = ttk.Frame(self.existing_tools_frame)
        tool_frame.pack(fill=tk.X, pady=2)
        
        # Tool name
        name_var = tk.StringVar(value=name)
        name_entry = ttk.Entry(tool_frame, textvariable=name_var, width=50)
        name_entry.grid(row=0, column=0, padx=5)
        
        # Remove button
        def remove_entry():
            tool_frame.destroy()
            self.tool_entries.remove(entry_data)
        
        remove_btn = ttk.Button(tool_frame, text="Remove", command=remove_entry)
        remove_btn.grid(row=0, column=1, padx=5)
        
        # Store entry data
        entry_data = {
            "name": name_var,
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
        
        # Iterate through the tool entries
        for i, entry_widgets in enumerate(self.tool_entries):
            print(f"Processing design tool entry {i}")
            
            # Get the values
            tool_name = entry_widgets["name"].get().strip()
            
            print(f"  Tool Name: '{tool_name}'")
            
            # Only add if name is filled
            if tool_name:
                design_tools.append(tool_name)
                print(f"  Added tool to design_tools list")
            else:
                print(f"  Skipping empty tool entry")
        
        # Update the product
        self.product["designTools"] = design_tools
        print(f"Updated product design tools: {self.product['designTools']}")
        
        # Return True to indicate validation passed
        return True 