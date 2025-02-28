import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab

class PostProcessingTab(BaseTab):
    """Tab for post-processing suppliers"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.post_proc_entries = []
        super().__init__(form, "Post-Processing Suppliers")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure postProcessingSuppliers exists and is a list
        if "postProcessingSuppliers" not in self.product or not isinstance(self.product["postProcessingSuppliers"], list):
            self.product["postProcessingSuppliers"] = []
        
        # Add button for new post-processing entry
        add_pp_btn = ttk.Button(self.frame, text="Add Post-Processing", 
                               command=lambda: self.add_post_proc_entry())
        add_pp_btn.grid(row=100, column=0, sticky=tk.W, padx=5, pady=10)
        
        # Add existing post-processing entries
        for pp_entry in self.product["postProcessingSuppliers"]:
            if isinstance(pp_entry, dict):
                process = pp_entry.get("process", "")
                suppliers = pp_entry.get("supplier", [])
                self.add_post_proc_entry(process, suppliers)
    
    def add_post_proc_entry(self, process="", suppliers=None):
        """Add a post-processing entry to the form"""
        if suppliers is None:
            suppliers = []
        
        # Create a frame for this entry
        row_idx = len(self.post_proc_entries)
        pp_frame = ttk.Frame(self.frame)
        pp_frame.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Process entry
        ttk.Label(pp_frame, text="Process:").grid(row=0, column=0, padx=5)
        process_var = tk.StringVar(value=process)
        process_entry = ttk.Entry(pp_frame, textvariable=process_var, width=30)
        process_entry.grid(row=0, column=1, padx=5)
        
        # Create a frame for supplier selection
        supplier_frame = ttk.Frame(pp_frame)
        supplier_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # List to store supplier entries
        supplier_entries = []
        
        # Function to add a supplier entry
        def add_supplier(supplier_id=""):
            # Create a frame for this supplier
            row_idx = len(supplier_entries)
            supplier_row_frame = ttk.Frame(supplier_frame)
            supplier_row_frame.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
            
            # Supplier dropdown
            supplier_var = tk.StringVar(value=supplier_id)
            supplier_combo = ttk.Combobox(supplier_row_frame, textvariable=supplier_var, width=30)
            
            # Create supplier options list
            supplier_options = []
            for s in self.model.data.get("postProcessingSuppliers", []):
                if isinstance(s, dict) and "id" in s and "name" in s:
                    supplier_options.append(f"{s['id']} - {s['name']}")
            
            supplier_combo['values'] = supplier_options
            supplier_combo.grid(row=0, column=0, padx=5)
            
            # Remove button
            def remove_supplier():
                supplier_row_frame.destroy()
                supplier_entries.remove(supplier_data)
            
            remove_btn = ttk.Button(supplier_row_frame, text="Remove", command=remove_supplier)
            remove_btn.grid(row=0, column=1, padx=5)
            
            # Store supplier data
            supplier_data = {
                "supplier_var": supplier_var,
                "frame": supplier_row_frame
            }
            supplier_entries.append(supplier_data)
        
        # Add existing suppliers
        for supplier_id in suppliers:
            # Find the full supplier name for display
            supplier_full = supplier_id
            for s in self.model.data.get("postProcessingSuppliers", []):
                if s["id"] == supplier_id:
                    supplier_full = f"{supplier_id} - {s['name']}"
                    break
            
            add_supplier(supplier_full)
        
        # Add button for new supplier
        add_supplier_btn = ttk.Button(supplier_frame, text="Add Supplier", 
                                   command=lambda: add_supplier())
        add_supplier_btn.grid(row=100, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Remove button for process
        def remove_entry():
            pp_frame.destroy()
            self.post_proc_entries.remove(entry_data)
        
        remove_btn = ttk.Button(pp_frame, text="Remove Process", command=remove_entry)
        remove_btn.grid(row=0, column=2, padx=5)
        
        # Store entry data
        entry_data = {
            "process_var": process_var,
            "supplier_entries": supplier_entries,
            "frame": pp_frame
        }
        self.post_proc_entries.append(entry_data)
        
        # Move the add button to the bottom
        self.frame.children['!button'].grid(row=row_idx + 1, column=0, sticky=tk.W, padx=5, pady=10)
    
    def collect_data(self):
        """Collect data from the tab"""
        # Get post-processing suppliers
        post_proc_suppliers = []
        for entry in self.post_proc_entries:
            process = entry["process_var"].get()
            if process:
                selected_suppliers = []
                for supplier_entry in entry["supplier_entries"]:
                    supplier_full = supplier_entry["supplier_var"].get()
                    if supplier_full:
                        # Extract supplier ID from the dropdown value (format: "ID - Name")
                        supplier_id = supplier_full.split(" - ")[0] if " - " in supplier_full else supplier_full
                        selected_suppliers.append(supplier_id)
                
                if selected_suppliers:
                    post_proc_suppliers.append({
                        "process": process,
                        "supplier": selected_suppliers
                    })
        self.product["postProcessingSuppliers"] = post_proc_suppliers 