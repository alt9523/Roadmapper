import tkinter as tk
from tkinter import ttk
from .base import BaseModel

class SupplierModel(BaseModel):
    """Model for managing suppliers (both printing and post-processing)"""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.printing_suppliers_tree = None
        self.post_processing_suppliers_tree = None
        self.printing_search_var = None
        self.post_processing_search_var = None
    
    def create_printing_suppliers_tab(self, notebook):
        """Create the Printing Suppliers tab in the notebook"""
        suppliers_frame = ttk.Frame(notebook)
        notebook.add(suppliers_frame, text="Printing Suppliers")
        
        # Create top frame with buttons
        top_frame = ttk.Frame(suppliers_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Supplier", command=self.add_printing_supplier)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Add search functionality
        search_label = ttk.Label(top_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.printing_search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.printing_search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", lambda event: self.search_printing_suppliers())
        
        search_button = ttk.Button(top_frame, text="Search", command=self.search_printing_suppliers)
        search_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(top_frame, text="Clear", command=self.clear_printing_search)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ("ID", "Name", "Supplier Number", "NDA Status", "Material Systems", "Additional Capabilities")
        self.printing_suppliers_tree = ttk.Treeview(suppliers_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.printing_suppliers_tree.heading(col, text=col)
            self.printing_suppliers_tree.column(col, width=100)
        
        # Adjust column widths
        self.printing_suppliers_tree.column("Name", width=150)
        self.printing_suppliers_tree.column("Material Systems", width=200)
        self.printing_suppliers_tree.column("Additional Capabilities", width=300)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(suppliers_frame, orient=tk.VERTICAL, command=self.printing_suppliers_tree.yview)
        self.printing_suppliers_tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.printing_suppliers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.printing_suppliers_tree.bind("<Double-1>", self.edit_printing_supplier)
        
        # Populate treeview
        self.populate_printing_suppliers_tree()
    
    def populate_printing_suppliers_tree(self):
        """Populate the printing suppliers treeview with data"""
        # Clear existing items
        for item in self.printing_suppliers_tree.get_children():
            self.printing_suppliers_tree.delete(item)
        
        # Add suppliers to treeview
        for supplier in self.data["printingSuppliers"]:
            # Extract material systems
            material_systems = []
            if "materialSystems" in supplier:
                for ms in supplier["materialSystems"]:
                    material_id = ms.get("materialID", "")
                    # Find material name from ID
                    material_name = self.get_material_name_by_id(material_id)
                    if material_name:
                        material_systems.append(material_name)
            
            # Format additional capabilities
            capabilities = ", ".join(supplier.get("additionalCapabilities", []))
            
            # Format NDA status
            nda_status = "None"
            if "ndaStatus" in supplier:
                status = supplier["ndaStatus"].get("status", "")
                date = supplier["ndaStatus"].get("date", "")
                if status and date:
                    nda_status = f"{status} ({date})"
                elif status:
                    nda_status = status
            
            values = (
                supplier["id"],
                supplier["name"],
                supplier.get("supplierNumber", ""),
                nda_status,
                ", ".join(material_systems),
                capabilities
            )
            self.printing_suppliers_tree.insert("", tk.END, values=values)
    
    def get_material_name_by_id(self, material_id):
        """Get material name from material ID"""
        for material in self.data["materialSystems"]:
            if material["id"] == material_id:
                return material["name"]
        return ""
    
    def create_post_processing_suppliers_tab(self, notebook):
        """Create the Post-Processing Suppliers tab in the notebook"""
        suppliers_frame = ttk.Frame(notebook)
        notebook.add(suppliers_frame, text="Post-Processing Suppliers")
        
        # Create top frame with buttons
        top_frame = ttk.Frame(suppliers_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Supplier", command=self.add_post_processing_supplier)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Add search functionality
        search_label = ttk.Label(top_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.post_processing_search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.post_processing_search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", lambda event: self.search_post_processing_suppliers())
        
        search_button = ttk.Button(top_frame, text="Search", command=self.search_post_processing_suppliers)
        search_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(top_frame, text="Clear", command=self.clear_post_processing_search)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ("ID", "Name", "Supplier Number", "NDA Status", "Processes")
        self.post_processing_suppliers_tree = ttk.Treeview(suppliers_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.post_processing_suppliers_tree.heading(col, text=col)
            self.post_processing_suppliers_tree.column(col, width=100)
        
        # Adjust column widths
        self.post_processing_suppliers_tree.column("Name", width=150)
        self.post_processing_suppliers_tree.column("Processes", width=300)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(suppliers_frame, orient=tk.VERTICAL, command=self.post_processing_suppliers_tree.yview)
        self.post_processing_suppliers_tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.post_processing_suppliers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.post_processing_suppliers_tree.bind("<Double-1>", self.edit_post_processing_supplier)
        
        # Populate treeview
        self.populate_post_processing_suppliers_tree()
    
    def populate_post_processing_suppliers_tree(self):
        """Populate the post-processing suppliers treeview with data"""
        # Clear existing items
        for item in self.post_processing_suppliers_tree.get_children():
            self.post_processing_suppliers_tree.delete(item)
        
        # Add suppliers to treeview
        for supplier in self.data["postProcessingSuppliers"]:
            # Format processes
            processes = ", ".join(supplier.get("processs", []))
            
            # Format NDA status
            nda_status = "None"
            if "ndaStatus" in supplier:
                status = supplier["ndaStatus"].get("status", "")
                date = supplier["ndaStatus"].get("date", "")
                if status and date:
                    nda_status = f"{status} ({date})"
                elif status:
                    nda_status = status
            
            values = (
                supplier["id"],
                supplier["name"],
                supplier.get("supplierNumber", ""),
                nda_status,
                processes
            )
            self.post_processing_suppliers_tree.insert("", tk.END, values=values)
    
    def get_next_supplier_id(self, supplier_type="printing"):
        """Get the next available supplier ID"""
        suppliers = self.data["printingSuppliers"] if supplier_type == "printing" else self.data["postProcessingSuppliers"]
        
        # Get existing IDs
        existing_ids = []
        prefix = "SUP" if supplier_type == "printing" else "PSUP"
        
        for supplier in suppliers:
            supplier_id = supplier["id"]
            if supplier_id.startswith(prefix):
                try:
                    # Extract the numeric part
                    num_part = supplier_id[len(prefix):]
                    if num_part.isdigit():
                        existing_ids.append(int(num_part))
                except (ValueError, IndexError):
                    pass
        
        # Find the next available number
        if not existing_ids:
            next_num = 1
        else:
            next_num = max(existing_ids) + 1
        
        return f"{prefix}{next_num}"
    
    def add_printing_supplier(self):
        """Open a window to add a new printing supplier"""
        # Create a new window for adding a supplier
        add_window = tk.Toplevel(self.manager.root)
        add_window.title("Add Printing Supplier")
        add_window.geometry("600x700")
        add_window.grab_set()  # Make window modal
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(add_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic Info tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Info")
        
        # Create form fields for basic info
        ttk.Label(basic_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=self.get_next_supplier_id("printing"))
        ttk.Entry(basic_frame, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Supplier Number:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        supplier_number_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=supplier_number_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # NDA Status
        ttk.Label(basic_frame, text="NDA Status:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        nda_status_var = tk.StringVar()
        ttk.Combobox(basic_frame, textvariable=nda_status_var, values=["None", "Signed", "Pending", "Expired"]).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="NDA Date:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        nda_date_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=nda_date_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        ttk.Label(basic_frame, text="(YYYY-MM-DD)").grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Material Systems tab
        materials_frame = ttk.Frame(notebook)
        notebook.add(materials_frame, text="Material Systems")
        
        # Create a frame for the material systems list
        materials_list_frame = ttk.Frame(materials_frame)
        materials_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a list to store material system entries
        material_entries = []
        
        # Function to add a material system entry
        def add_material_system():
            # Create a frame for this material system
            ms_frame = ttk.LabelFrame(materials_list_frame, text=f"Material System {len(material_entries) + 1}")
            ms_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Material System selection
            ttk.Label(ms_frame, text="Material System:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            ms_var = tk.StringVar()
            
            # Get material system options
            ms_options = []
            ms_id_map = {}
            for ms in self.data["materialSystems"]:
                ms_options.append(ms["name"])
                ms_id_map[ms["name"]] = ms["id"]
            
            ms_combo = ttk.Combobox(ms_frame, textvariable=ms_var, values=ms_options)
            ms_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
            
            # Printers list
            ttk.Label(ms_frame, text="Printers:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            printers_frame = ttk.Frame(ms_frame)
            printers_frame.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
            
            # List to store printer entries
            printer_entries = []
            
            # Function to add a printer entry
            def add_printer():
                printer_frame = ttk.Frame(printers_frame)
                printer_frame.pack(fill=tk.X, pady=2)
                
                printer_var = tk.StringVar()
                printer_entry = ttk.Entry(printer_frame, textvariable=printer_var)
                printer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                qual_status_var = tk.StringVar(value="Qualified")
                qual_combo = ttk.Combobox(printer_frame, textvariable=qual_status_var, 
                                         values=["Qualified", "in-development", "planned"])
                qual_combo.pack(side=tk.LEFT, padx=5)
                
                # Button to remove this printer
                remove_btn = ttk.Button(printer_frame, text="X", width=2,
                                       command=lambda f=printer_frame: f.destroy())
                remove_btn.pack(side=tk.LEFT)
                
                printer_entries.append((printer_var, qual_status_var))
            
            # Button to add a printer
            add_printer_btn = ttk.Button(printers_frame, text="Add Printer", command=add_printer)
            add_printer_btn.pack(anchor=tk.W)
            
            # Add one printer entry by default
            add_printer()
            
            # Button to remove this material system
            remove_ms_btn = ttk.Button(ms_frame, text="Remove Material System", 
                                     command=lambda f=ms_frame: f.destroy())
            remove_ms_btn.grid(row=2, column=0, columnspan=2, pady=5)
            
            material_entries.append((ms_var, ms_id_map, printer_entries))
        
        # Button to add a material system
        add_ms_btn = ttk.Button(materials_frame, text="Add Material System", command=add_material_system)
        add_ms_btn.pack(anchor=tk.W, padx=10, pady=5)
        
        # Add one material system by default
        add_material_system()
        
        # Additional Capabilities tab
        capabilities_frame = ttk.Frame(notebook)
        notebook.add(capabilities_frame, text="Additional Capabilities")
        
        # Create a frame for the capabilities list
        capabilities_list_frame = ttk.Frame(capabilities_frame)
        capabilities_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # List to store capability entries
        capability_entries = []
        
        # Function to add a capability entry
        def add_capability():
            capability_frame = ttk.Frame(capabilities_list_frame)
            capability_frame.pack(fill=tk.X, pady=2)
            
            capability_var = tk.StringVar()
            capability_entry = ttk.Entry(capability_frame, textvariable=capability_var, width=50)
            capability_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Button to remove this capability
            remove_btn = ttk.Button(capability_frame, text="X", width=2,
                                   command=lambda f=capability_frame: f.destroy())
            remove_btn.pack(side=tk.LEFT)
            
            capability_entries.append(capability_var)
        
        # Button to add a capability
        add_capability_btn = ttk.Button(capabilities_frame, text="Add Capability", command=add_capability)
        add_capability_btn.pack(anchor=tk.W, padx=10, pady=5)
        
        # Add one capability entry by default
        add_capability()
        
        # Save button
        def save_supplier():
            # Validate required fields
            if not id_var.get() or not name_var.get():
                self.show_error("Error", "ID and Name are required fields")
                return
            
            # Create NDA status
            nda_status = {}
            if nda_status_var.get() and nda_status_var.get() != "None":
                nda_status["status"] = nda_status_var.get()
                if nda_date_var.get():
                    nda_status["date"] = nda_date_var.get()
            
            # Get material systems
            material_systems = []
            for ms_var, ms_id_map, printer_entries in material_entries:
                if ms_var.get():  # If a material system is selected
                    ms_id = ms_id_map.get(ms_var.get())
                    if ms_id:
                        # Get printers for this material system
                        printers = []
                        for printer_var, qual_status_var in printer_entries:
                            if printer_var.get():  # If a printer is entered
                                printer = {
                                    "name": printer_var.get(),
                                    "qualStatus": qual_status_var.get()
                                }
                                printers.append(printer)
                        
                        if printers:  # If there are printers for this material system
                            material_system = {
                                "materialID": ms_id,
                                "printer": printers
                            }
                            material_systems.append(material_system)
            
            # Get additional capabilities
            additional_capabilities = []
            for capability_var in capability_entries:
                if capability_var.get():  # If a capability is entered
                    additional_capabilities.append(capability_var.get())
            
            # Create new supplier
            new_supplier = {
                "id": id_var.get(),
                "name": name_var.get(),
                "supplierNumber": supplier_number_var.get(),
                "materialSystems": material_systems,
                "additionalCapabilities": additional_capabilities,
                "supplierRoadmap": {"tasks": []}  # Initialize empty roadmap
            }
            
            # Add NDA status if present
            if nda_status:
                new_supplier["ndaStatus"] = nda_status
            
            # Add to data
            self.data["printingSuppliers"].append(new_supplier)
            
            # Refresh treeview
            self.populate_printing_suppliers_tree()
            
            # Close window
            add_window.destroy()
            
            self.update_status(f"Added printing supplier: {new_supplier['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def edit_printing_supplier(self, event):
        """Open a window to edit an existing printing supplier"""
        # Get selected item
        selected_item = self.printing_suppliers_tree.selection()
        if not selected_item:
            return
        
        # Get values
        values = self.printing_suppliers_tree.item(selected_item, "values")
        supplier_id = values[0]
        
        # Find supplier in data
        supplier = next((s for s in self.data["printingSuppliers"] if s["id"] == supplier_id), None)
        if not supplier:
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.manager.root)
        edit_window.title(f"Edit Printing Supplier: {supplier['name']}")
        edit_window.geometry("600x700")
        edit_window.grab_set()  # Make window modal
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(edit_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic Info tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Info")
        
        # Create form fields for basic info
        ttk.Label(basic_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=supplier["id"])
        ttk.Entry(basic_frame, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=supplier["name"])
        ttk.Entry(basic_frame, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Supplier Number:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        supplier_number_var = tk.StringVar(value=supplier.get("supplierNumber", ""))
        ttk.Entry(basic_frame, textvariable=supplier_number_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # NDA Status
        nda_status = supplier.get("ndaStatus", {})
        ttk.Label(basic_frame, text="NDA Status:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        nda_status_var = tk.StringVar(value=nda_status.get("status", "None"))
        ttk.Combobox(basic_frame, textvariable=nda_status_var, values=["None", "Signed", "Pending", "Expired"]).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="NDA Date:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        nda_date_var = tk.StringVar(value=nda_status.get("date", ""))
        ttk.Entry(basic_frame, textvariable=nda_date_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        ttk.Label(basic_frame, text="(YYYY-MM-DD)").grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Material Systems tab
        materials_frame = ttk.Frame(notebook)
        notebook.add(materials_frame, text="Material Systems")
        
        # Create a frame for the material systems list
        materials_list_frame = ttk.Frame(materials_frame)
        materials_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a list to store material system entries
        material_entries = []
        
        # Function to add a material system entry
        def add_material_system(existing_ms=None):
            # Create a frame for this material system
            ms_frame = ttk.LabelFrame(materials_list_frame, text=f"Material System {len(material_entries) + 1}")
            ms_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Material System selection
            ttk.Label(ms_frame, text="Material System:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            ms_var = tk.StringVar()
            
            # Get material system options
            ms_options = []
            ms_id_map = {}
            for ms in self.data["materialSystems"]:
                ms_options.append(ms["name"])
                ms_id_map[ms["name"]] = ms["id"]
                # If this is an existing material system, set the selected value
                if existing_ms and ms["id"] == existing_ms.get("materialID"):
                    ms_var.set(ms["name"])
            
            ms_combo = ttk.Combobox(ms_frame, textvariable=ms_var, values=ms_options)
            ms_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
            
            # Printers list
            ttk.Label(ms_frame, text="Printers:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            printers_frame = ttk.Frame(ms_frame)
            printers_frame.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
            
            # List to store printer entries
            printer_entries = []
            
            # Function to add a printer entry
            def add_printer(name="", qual_status="Qualified"):
                printer_frame = ttk.Frame(printers_frame)
                printer_frame.pack(fill=tk.X, pady=2)
                
                printer_var = tk.StringVar(value=name)
                printer_entry = ttk.Entry(printer_frame, textvariable=printer_var)
                printer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                qual_status_var = tk.StringVar(value=qual_status)
                qual_combo = ttk.Combobox(printer_frame, textvariable=qual_status_var, 
                                         values=["Qualified", "in-development", "planned"])
                qual_combo.pack(side=tk.LEFT, padx=5)
                
                # Button to remove this printer
                remove_btn = ttk.Button(printer_frame, text="X", width=2,
                                       command=lambda f=printer_frame: f.destroy())
                remove_btn.pack(side=tk.LEFT)
                
                printer_entries.append((printer_var, qual_status_var))
            
            # Button to add a printer
            add_printer_btn = ttk.Button(printers_frame, text="Add Printer", command=add_printer)
            add_printer_btn.pack(anchor=tk.W)
            
            # If this is an existing material system, add its printers
            if existing_ms and "printer" in existing_ms:
                for printer in existing_ms["printer"]:
                    if isinstance(printer, dict):
                        # New format with name and qualStatus
                        add_printer(printer.get("name", ""), printer.get("qualStatus", "Qualified"))
                    else:
                        # Old format with just printer name
                        add_printer(printer)
            else:
                # Add one printer entry by default
                add_printer()
            
            # Button to remove this material system
            remove_ms_btn = ttk.Button(ms_frame, text="Remove Material System", 
                                     command=lambda f=ms_frame: f.destroy())
            remove_ms_btn.grid(row=2, column=0, columnspan=2, pady=5)
            
            material_entries.append((ms_var, ms_id_map, printer_entries))
        
        # Button to add a material system
        add_ms_btn = ttk.Button(materials_frame, text="Add Material System", command=add_material_system)
        add_ms_btn.pack(anchor=tk.W, padx=10, pady=5)
        
        # Add existing material systems
        if "materialSystems" in supplier:
            for ms in supplier["materialSystems"]:
                add_material_system(ms)
        else:
            # Add one material system by default
            add_material_system()
        
        # Additional Capabilities tab
        capabilities_frame = ttk.Frame(notebook)
        notebook.add(capabilities_frame, text="Additional Capabilities")
        
        # Create a frame for the capabilities list
        capabilities_list_frame = ttk.Frame(capabilities_frame)
        capabilities_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # List to store capability entries
        capability_entries = []
        
        # Function to add a capability entry
        def add_capability(capability=""):
            capability_frame = ttk.Frame(capabilities_list_frame)
            capability_frame.pack(fill=tk.X, pady=2)
            
            capability_var = tk.StringVar(value=capability)
            capability_entry = ttk.Entry(capability_frame, textvariable=capability_var, width=50)
            capability_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Button to remove this capability
            remove_btn = ttk.Button(capability_frame, text="X", width=2,
                                   command=lambda f=capability_frame: f.destroy())
            remove_btn.pack(side=tk.LEFT)
            
            capability_entries.append(capability_var)
        
        # Button to add a capability
        add_capability_btn = ttk.Button(capabilities_frame, text="Add Capability", command=add_capability)
        add_capability_btn.pack(anchor=tk.W, padx=10, pady=5)
        
        # Add existing capabilities
        if "additionalCapabilities" in supplier:
            for capability in supplier["additionalCapabilities"]:
                add_capability(capability)
        else:
            # Add one capability entry by default
            add_capability()
        
        # Save button
        def save_supplier():
            # Validate required fields
            if not name_var.get():
                self.show_error("Error", "Name is required")
                return
            
            # Create NDA status
            nda_status = {}
            if nda_status_var.get() and nda_status_var.get() != "None":
                nda_status["status"] = nda_status_var.get()
                if nda_date_var.get():
                    nda_status["date"] = nda_date_var.get()
            
            # Get material systems
            material_systems = []
            for ms_var, ms_id_map, printer_entries in material_entries:
                if ms_var.get():  # If a material system is selected
                    ms_id = ms_id_map.get(ms_var.get())
                    if ms_id:
                        # Get printers for this material system
                        printers = []
                        for printer_var, qual_status_var in printer_entries:
                            if printer_var.get():  # If a printer is entered
                                printer = {
                                    "name": printer_var.get(),
                                    "qualStatus": qual_status_var.get()
                                }
                                printers.append(printer)
                        
                        if printers:  # If there are printers for this material system
                            material_system = {
                                "materialID": ms_id,
                                "printer": printers
                            }
                            material_systems.append(material_system)
            
            # Get additional capabilities
            additional_capabilities = []
            for capability_var in capability_entries:
                if capability_var.get():  # If a capability is entered
                    additional_capabilities.append(capability_var.get())
            
            # Create new supplier
            new_supplier = {
                "id": id_var.get(),
                "name": name_var.get(),
                "supplierNumber": supplier_number_var.get(),
                "materialSystems": material_systems,
                "additionalCapabilities": additional_capabilities,
                "supplierRoadmap": supplier.get("supplierRoadmap", {"tasks": []})  # Preserve existing roadmap data
            }
            
            # Add NDA status if present
            if nda_status:
                new_supplier["ndaStatus"] = nda_status
            
            # Update supplier in data
            for i, s in enumerate(self.data["printingSuppliers"]):
                if s["id"] == supplier_id:
                    self.data["printingSuppliers"][i] = new_supplier
                    break
            
            # Refresh treeview
            self.populate_printing_suppliers_tree()
            
            # Close window
            edit_window.destroy()
            
            self.update_status(f"Updated printing supplier: {new_supplier['name']}")
        
        # Delete button
        def delete_supplier():
            if self.confirm_delete(supplier['name']):
                # Remove supplier from data
                self.data["printingSuppliers"].remove(supplier)
                
                # Refresh treeview
                self.populate_printing_suppliers_tree()
                
                # Close window
                edit_window.destroy()
                
                self.update_status(f"Deleted printing supplier: {supplier['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_post_processing_supplier(self):
        """Open a window to add a new post-processing supplier"""
        # Create a new window for adding a supplier
        add_window = tk.Toplevel(self.manager.root)
        add_window.title("Add Post-Processing Supplier")
        add_window.geometry("600x600")
        add_window.grab_set()  # Make window modal
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(add_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic Info tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Info")
        
        # Create form fields for basic info
        ttk.Label(basic_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=self.get_next_supplier_id("post_processing"))
        ttk.Entry(basic_frame, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Supplier Number:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        supplier_number_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=supplier_number_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # NDA Status
        ttk.Label(basic_frame, text="NDA Status:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        nda_status_var = tk.StringVar()
        ttk.Combobox(basic_frame, textvariable=nda_status_var, values=["None", "Signed", "Pending", "Expired"]).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="NDA Date:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        nda_date_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=nda_date_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        ttk.Label(basic_frame, text="(YYYY-MM-DD)").grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Processes tab
        processes_frame = ttk.Frame(notebook)
        notebook.add(processes_frame, text="Processes")
        
        # Create a frame for the processes list
        processes_list_frame = ttk.Frame(processes_frame)
        processes_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # List to store process entries
        process_entries = []
        
        # Function to add a process entry
        def add_process():
            process_frame = ttk.Frame(processes_list_frame)
            process_frame.pack(fill=tk.X, pady=2)
            
            process_var = tk.StringVar()
            process_entry = ttk.Entry(process_frame, textvariable=process_var, width=50)
            process_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Button to remove this process
            remove_btn = ttk.Button(process_frame, text="X", width=2,
                                   command=lambda f=process_frame: f.destroy())
            remove_btn.pack(side=tk.LEFT)
            
            process_entries.append(process_var)
        
        # Button to add a process
        add_process_btn = ttk.Button(processes_frame, text="Add Process", command=add_process)
        add_process_btn.pack(anchor=tk.W, padx=10, pady=5)
        
        # Add one process entry by default
        add_process()
        
        # Save button
        def save_supplier():
            # Validate required fields
            if not id_var.get() or not name_var.get():
                self.show_error("Error", "ID and Name are required fields")
                return
            
            # Create NDA status
            nda_status = {}
            if nda_status_var.get() and nda_status_var.get() != "None":
                nda_status["status"] = nda_status_var.get()
                if nda_date_var.get():
                    nda_status["date"] = nda_date_var.get()
            
            # Get processes
            processes = []
            for process_var in process_entries:
                if process_var.get():  # If a process is entered
                    processes.append(process_var.get())
            
            # Create new supplier
            new_supplier = {
                "id": id_var.get(),
                "name": name_var.get(),
                "supplierNumber": supplier_number_var.get(),
                "processs": processes,  # Note: The JSON has a typo "processs" instead of "processes"
                "supplierRoadmap": {"tasks": []}  # Initialize empty roadmap
            }
            
            # Add NDA status if present
            if nda_status:
                new_supplier["ndaStatus"] = nda_status
            
            # Add to data
            self.data["postProcessingSuppliers"].append(new_supplier)
            
            # Refresh treeview
            self.populate_post_processing_suppliers_tree()
            
            # Close window
            add_window.destroy()
            
            self.update_status(f"Added post-processing supplier: {new_supplier['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def edit_post_processing_supplier(self, event):
        """Open a window to edit an existing post-processing supplier"""
        # Get selected item
        selected_item = self.post_processing_suppliers_tree.selection()
        if not selected_item:
            return
        
        # Get values
        values = self.post_processing_suppliers_tree.item(selected_item, "values")
        supplier_id = values[0]
        
        # Find supplier in data
        supplier = next((s for s in self.data["postProcessingSuppliers"] if s["id"] == supplier_id), None)
        if not supplier:
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.manager.root)
        edit_window.title(f"Edit Post-Processing Supplier: {supplier['name']}")
        edit_window.geometry("600x600")
        edit_window.grab_set()  # Make window modal
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(edit_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic Info tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Info")
        
        # Create form fields for basic info
        ttk.Label(basic_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=supplier["id"])
        ttk.Entry(basic_frame, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=supplier["name"])
        ttk.Entry(basic_frame, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Supplier Number:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        supplier_number_var = tk.StringVar(value=supplier.get("supplierNumber", ""))
        ttk.Entry(basic_frame, textvariable=supplier_number_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # NDA Status
        nda_status = supplier.get("ndaStatus", {})
        ttk.Label(basic_frame, text="NDA Status:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        nda_status_var = tk.StringVar(value=nda_status.get("status", "None"))
        ttk.Combobox(basic_frame, textvariable=nda_status_var, values=["None", "Signed", "Pending", "Expired"]).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="NDA Date:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        nda_date_var = tk.StringVar(value=nda_status.get("date", ""))
        ttk.Entry(basic_frame, textvariable=nda_date_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        ttk.Label(basic_frame, text="(YYYY-MM-DD)").grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Processes tab
        processes_frame = ttk.Frame(notebook)
        notebook.add(processes_frame, text="Processes")
        
        # Create a frame for the processes list
        processes_list_frame = ttk.Frame(processes_frame)
        processes_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # List to store process entries
        process_entries = []
        
        # Function to add a process entry
        def add_process(process=""):
            process_frame = ttk.Frame(processes_list_frame)
            process_frame.pack(fill=tk.X, pady=2)
            
            process_var = tk.StringVar(value=process)
            process_entry = ttk.Entry(process_frame, textvariable=process_var, width=50)
            process_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Button to remove this process
            remove_btn = ttk.Button(process_frame, text="X", width=2,
                                   command=lambda f=process_frame: f.destroy())
            remove_btn.pack(side=tk.LEFT)
            
            process_entries.append(process_var)
        
        # Button to add a process
        add_process_btn = ttk.Button(processes_frame, text="Add Process", command=add_process)
        add_process_btn.pack(anchor=tk.W, padx=10, pady=5)
        
        # Add existing processes
        if "processs" in supplier:
            for process in supplier["processs"]:
                add_process(process)
        else:
            # Add one process entry by default
            add_process()
        
        # Save button
        def save_supplier():
            # Validate required fields
            if not name_var.get():
                self.show_error("Error", "Name is required")
                return
            
            # Create NDA status
            nda_status = {}
            if nda_status_var.get() and nda_status_var.get() != "None":
                nda_status["status"] = nda_status_var.get()
                if nda_date_var.get():
                    nda_status["date"] = nda_date_var.get()
            
            # Get processes
            processes = []
            for process_var in process_entries:
                if process_var.get():  # If a process is entered
                    processes.append(process_var.get())
            
            # Preserve existing roadmap data
            supplier_roadmap = supplier.get("supplierRoadmap", {"tasks": []})
            
            # Update supplier
            supplier["name"] = name_var.get()
            supplier["supplierNumber"] = supplier_number_var.get()
            supplier["processs"] = processes  # Note: The JSON has a typo "processs" instead of "processes"
            supplier["supplierRoadmap"] = supplier_roadmap
            
            # Update NDA status
            if nda_status:
                supplier["ndaStatus"] = nda_status
            elif "ndaStatus" in supplier:
                del supplier["ndaStatus"]
            
            # Refresh treeview
            self.populate_post_processing_suppliers_tree()
            
            # Close window
            edit_window.destroy()
            
            self.update_status(f"Updated post-processing supplier: {supplier['name']}")
        
        # Delete button
        def delete_supplier():
            if self.confirm_delete(supplier['name']):
                # Remove supplier from data
                self.data["postProcessingSuppliers"].remove(supplier)
                
                # Refresh treeview
                self.populate_post_processing_suppliers_tree()
                
                # Close window
                edit_window.destroy()
                
                self.update_status(f"Deleted post-processing supplier: {supplier['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def get_supplier_roadmap(self, supplier_id, supplier_type="printing"):
        """Get the roadmap data for a supplier"""
        suppliers = self.data["printingSuppliers"] if supplier_type == "printing" else self.data["postProcessingSuppliers"]
        supplier = next((s for s in suppliers if s["id"] == supplier_id), None)
        
        if supplier and "supplierRoadmap" in supplier:
            return supplier["supplierRoadmap"]
        return {"tasks": []}
    
    def save_supplier_roadmap(self, supplier_id, roadmap_data, supplier_type="printing"):
        """Save the roadmap data for a supplier"""
        suppliers = self.data["printingSuppliers"] if supplier_type == "printing" else self.data["postProcessingSuppliers"]
        supplier = next((s for s in suppliers if s["id"] == supplier_id), None)
        
        if supplier:
            supplier["supplierRoadmap"] = roadmap_data
            return True
        return False
    
    def search_printing_suppliers(self):
        """Search printing suppliers based on the search term"""
        search_term = self.printing_search_var.get().lower()
        if not search_term:
            self.clear_printing_search()
            return
        
        # Clear existing items
        for item in self.printing_suppliers_tree.get_children():
            self.printing_suppliers_tree.delete(item)
        
        # Add matching suppliers to treeview
        for supplier in self.data["printingSuppliers"]:
            # Check if search term is in any of the supplier attributes
            if (search_term in supplier["id"].lower() or
                search_term in supplier["name"].lower() or
                search_term in supplier.get("supplierNumber", "").lower()):
                
                # Also check in material systems
                material_systems = []
                if "materialSystems" in supplier:
                    for ms in supplier["materialSystems"]:
                        material_id = ms.get("materialID", "")
                        # Find material name from ID
                        material_name = self.get_material_name_by_id(material_id)
                        if material_name:
                            material_systems.append(material_name)
                
                # Check if search term is in material systems
                material_match = False
                for ms_name in material_systems:
                    if search_term in ms_name.lower():
                        material_match = True
                        break
                
                # Check if search term is in additional capabilities
                capability_match = False
                for capability in supplier.get("additionalCapabilities", []):
                    if search_term in capability.lower():
                        capability_match = True
                        break
                
                # If any match, add to treeview
                if (search_term in supplier["id"].lower() or
                    search_term in supplier["name"].lower() or
                    search_term in supplier.get("supplierNumber", "").lower() or
                    material_match or capability_match):
                    
                    # Format NDA status
                    nda_status = "None"
                    if "ndaStatus" in supplier:
                        status = supplier["ndaStatus"].get("status", "")
                        date = supplier["ndaStatus"].get("date", "")
                        if status and date:
                            nda_status = f"{status} ({date})"
                        elif status:
                            nda_status = status
                    
                    # Format additional capabilities
                    capabilities = ", ".join(supplier.get("additionalCapabilities", []))
                    
                    values = (
                        supplier["id"],
                        supplier["name"],
                        supplier.get("supplierNumber", ""),
                        nda_status,
                        ", ".join(material_systems),
                        capabilities
                    )
                    self.printing_suppliers_tree.insert("", tk.END, values=values)
    
    def clear_printing_search(self):
        """Clear search and show all printing suppliers"""
        self.printing_search_var.set("")
        self.populate_printing_suppliers_tree()
    
    def search_post_processing_suppliers(self):
        """Search post-processing suppliers based on the search term"""
        search_term = self.post_processing_search_var.get().lower()
        if not search_term:
            self.clear_post_processing_search()
            return
        
        # Clear existing items
        for item in self.post_processing_suppliers_tree.get_children():
            self.post_processing_suppliers_tree.delete(item)
        
        # Add matching suppliers to treeview
        for supplier in self.data["postProcessingSuppliers"]:
            # Check if search term is in any of the supplier attributes
            if (search_term in supplier["id"].lower() or
                search_term in supplier["name"].lower() or
                search_term in supplier.get("supplierNumber", "").lower()):
                
                # Format NDA status
                nda_status = "None"
                if "ndaStatus" in supplier:
                    status = supplier["ndaStatus"].get("status", "")
                    date = supplier["ndaStatus"].get("date", "")
                    if status and date:
                        nda_status = f"{status} ({date})"
                    elif status:
                        nda_status = status
                
                values = (
                    supplier["id"],
                    supplier["name"],
                    supplier.get("supplierNumber", ""),
                    nda_status,
                    ", ".join(supplier.get("processs", []))
                )
                self.post_processing_suppliers_tree.insert("", tk.END, values=values)
                continue  # Skip further checks if already matched
            
            # Check if search term is in processes
            process_match = False
            for process in supplier.get("processs", []):
                if search_term in process.lower():
                    process_match = True
                    break
            
            if process_match:
                # Format NDA status
                nda_status = "None"
                if "ndaStatus" in supplier:
                    status = supplier["ndaStatus"].get("status", "")
                    date = supplier["ndaStatus"].get("date", "")
                    if status and date:
                        nda_status = f"{status} ({date})"
                    elif status:
                        nda_status = status
                
                values = (
                    supplier["id"],
                    supplier["name"],
                    supplier.get("supplierNumber", ""),
                    nda_status,
                    ", ".join(supplier.get("processs", []))
                )
                self.post_processing_suppliers_tree.insert("", tk.END, values=values)
    
    def clear_post_processing_search(self):
        """Clear search and show all post-processing suppliers"""
        self.post_processing_search_var.set("")
        self.populate_post_processing_suppliers_tree() 