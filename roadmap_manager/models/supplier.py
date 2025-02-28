import tkinter as tk
from tkinter import ttk
from .base import BaseModel

class SupplierModel(BaseModel):
    """Model for managing suppliers (both printing and post-processing)"""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.printing_suppliers_tree = None
        self.post_processing_suppliers_tree = None
    
    def create_printing_suppliers_tab(self, notebook):
        """Create the Printing Suppliers tab in the notebook"""
        suppliers_frame = ttk.Frame(notebook)
        notebook.add(suppliers_frame, text="Printing Suppliers")
        
        # Create top frame with buttons
        top_frame = ttk.Frame(suppliers_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Supplier", command=self.add_printing_supplier)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ("ID", "Name", "Materials", "Additional Capabilities")
        self.printing_suppliers_tree = ttk.Treeview(suppliers_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.printing_suppliers_tree.heading(col, text=col)
            self.printing_suppliers_tree.column(col, width=100)
        
        # Adjust column widths
        self.printing_suppliers_tree.column("Materials", width=150)
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
            materials = ", ".join(supplier.get("materials", []))
            
            values = (
                supplier["id"],
                supplier["name"],
                materials,
                supplier.get("additionalCapabilities", "")
            )
            self.printing_suppliers_tree.insert("", tk.END, values=values)
    
    def create_post_processing_suppliers_tab(self, notebook):
        """Create the Post-Processing Suppliers tab in the notebook"""
        suppliers_frame = ttk.Frame(notebook)
        notebook.add(suppliers_frame, text="Post-Processing Suppliers")
        
        # Create top frame with buttons
        top_frame = ttk.Frame(suppliers_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Supplier", command=self.add_post_processing_supplier)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ("ID", "Name", "Materials", "Additional Capabilities")
        self.post_processing_suppliers_tree = ttk.Treeview(suppliers_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.post_processing_suppliers_tree.heading(col, text=col)
            self.post_processing_suppliers_tree.column(col, width=100)
        
        # Adjust column widths
        self.post_processing_suppliers_tree.column("Materials", width=150)
        self.post_processing_suppliers_tree.column("Additional Capabilities", width=300)
        
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
            materials = ", ".join(supplier.get("materials", []))
            
            values = (
                supplier["id"],
                supplier["name"],
                materials,
                supplier.get("additionalCapabilities", "")
            )
            self.post_processing_suppliers_tree.insert("", tk.END, values=values)
    
    def add_printing_supplier(self):
        """Open a window to add a new printing supplier"""
        # Create a new window for adding a supplier
        add_window = tk.Toplevel(self.manager.root)
        add_window.title("Add Printing Supplier")
        add_window.geometry("500x500")
        add_window.grab_set()  # Make window modal
        
        # Create form fields
        ttk.Label(add_window, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=id_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Additional Capabilities:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        capabilities_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=capabilities_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Materials selection
        ttk.Label(add_window, text="Materials:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        materials_frame = ttk.Frame(add_window)
        materials_frame.grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store material checkboxes
        material_vars = []
        
        # Function to add a material checkbox
        def add_material_checkbox(material):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(materials_frame, text=material, variable=var)
            chk.pack(anchor=tk.W)
            material_vars.append((material, var))
        
        # Add material checkboxes
        for material in self.data["materialSystems"]:
            add_material_checkbox(material["name"])
        
        # Save button
        def save_supplier():
            # Validate required fields
            if not id_var.get() or not name_var.get():
                self.show_error("Error", "ID and Name are required fields")
                return
            
            # Get selected materials
            selected_materials = [material for material, var in material_vars if var.get()]
            
            # Create new supplier
            new_supplier = {
                "id": id_var.get(),
                "name": name_var.get(),
                "materials": selected_materials,
                "additionalCapabilities": capabilities_var.get()
            }
            
            # Add to data
            self.data["printingSuppliers"].append(new_supplier)
            
            # Refresh treeview
            self.populate_printing_suppliers_tree()
            
            # Close window
            add_window.destroy()
            
            self.update_status(f"Added printing supplier: {new_supplier['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
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
        edit_window.geometry("500x500")
        edit_window.grab_set()  # Make window modal
        
        # Create form fields
        ttk.Label(edit_window, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=supplier["id"])
        ttk.Entry(edit_window, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=supplier["name"])
        ttk.Entry(edit_window, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Additional Capabilities:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        capabilities_var = tk.StringVar(value=supplier.get("additionalCapabilities", ""))
        ttk.Entry(edit_window, textvariable=capabilities_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Materials selection
        ttk.Label(edit_window, text="Materials:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        materials_frame = ttk.Frame(edit_window)
        materials_frame.grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store material checkboxes
        material_vars = []
        
        # Function to add a material checkbox
        def add_material_checkbox(material, selected=False):
            var = tk.BooleanVar(value=selected)
            chk = ttk.Checkbutton(materials_frame, text=material, variable=var)
            chk.pack(anchor=tk.W)
            material_vars.append((material, var))
        
        # Add material checkboxes
        for material in self.data["materialSystems"]:
            selected = material["name"] in supplier.get("materials", [])
            add_material_checkbox(material["name"], selected)
        
        # Save button
        def save_supplier():
            # Validate required fields
            if not name_var.get():
                self.show_error("Error", "Name is required")
                return
            
            # Get selected materials
            selected_materials = [material for material, var in material_vars if var.get()]
            
            # Update supplier
            supplier["name"] = name_var.get()
            supplier["materials"] = selected_materials
            supplier["additionalCapabilities"] = capabilities_var.get()
            
            # Refresh treeview
            self.populate_printing_suppliers_tree()
            
            # Close window
            edit_window.destroy()
            
            self.update_status(f"Updated printing supplier: {supplier['name']}")
        
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
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_post_processing_supplier(self):
        """Open a window to add a new post-processing supplier"""
        # Create a new window for adding a supplier
        add_window = tk.Toplevel(self.manager.root)
        add_window.title("Add Post-Processing Supplier")
        add_window.geometry("500x500")
        add_window.grab_set()  # Make window modal
        
        # Create form fields
        ttk.Label(add_window, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=id_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Additional Capabilities:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        capabilities_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=capabilities_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Materials selection
        ttk.Label(add_window, text="Materials:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        materials_frame = ttk.Frame(add_window)
        materials_frame.grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store material checkboxes
        material_vars = []
        
        # Function to add a material checkbox
        def add_material_checkbox(material):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(materials_frame, text=material, variable=var)
            chk.pack(anchor=tk.W)
            material_vars.append((material, var))
        
        # Add material checkboxes
        for material in self.data["materialSystems"]:
            add_material_checkbox(material["name"])
        
        # Save button
        def save_supplier():
            # Validate required fields
            if not id_var.get() or not name_var.get():
                self.show_error("Error", "ID and Name are required fields")
                return
            
            # Get selected materials
            selected_materials = [material for material, var in material_vars if var.get()]
            
            # Create new supplier
            new_supplier = {
                "id": id_var.get(),
                "name": name_var.get(),
                "materials": selected_materials,
                "additionalCapabilities": capabilities_var.get()
            }
            
            # Add to data
            self.data["postProcessingSuppliers"].append(new_supplier)
            
            # Refresh treeview
            self.populate_post_processing_suppliers_tree()
            
            # Close window
            add_window.destroy()
            
            self.update_status(f"Added post-processing supplier: {new_supplier['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
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
        edit_window.geometry("500x500")
        edit_window.grab_set()  # Make window modal
        
        # Create form fields
        ttk.Label(edit_window, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=supplier["id"])
        ttk.Entry(edit_window, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=supplier["name"])
        ttk.Entry(edit_window, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Additional Capabilities:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        capabilities_var = tk.StringVar(value=supplier.get("additionalCapabilities", ""))
        ttk.Entry(edit_window, textvariable=capabilities_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Materials selection
        ttk.Label(edit_window, text="Materials:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        materials_frame = ttk.Frame(edit_window)
        materials_frame.grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store material checkboxes
        material_vars = []
        
        # Function to add a material checkbox
        def add_material_checkbox(material, selected=False):
            var = tk.BooleanVar(value=selected)
            chk = ttk.Checkbutton(materials_frame, text=material, variable=var)
            chk.pack(anchor=tk.W)
            material_vars.append((material, var))
        
        # Add material checkboxes
        for material in self.data["materialSystems"]:
            selected = material["name"] in supplier.get("materials", [])
            add_material_checkbox(material["name"], selected)
        
        # Save button
        def save_supplier():
            # Validate required fields
            if not name_var.get():
                self.show_error("Error", "Name is required")
                return
            
            # Get selected materials
            selected_materials = [material for material, var in material_vars if var.get()]
            
            # Update supplier
            supplier["name"] = name_var.get()
            supplier["materials"] = selected_materials
            supplier["additionalCapabilities"] = capabilities_var.get()
            
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
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5) 