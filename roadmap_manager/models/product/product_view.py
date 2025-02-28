import tkinter as tk
from tkinter import ttk

class ProductView:
    """View class for product UI components"""
    
    def __init__(self, model):
        self.model = model
        self.products_tree = None
        self.search_entry = None
    
    def create_products_tab(self, notebook):
        """Create the Products tab in the notebook"""
        products_frame = ttk.Frame(notebook)
        notebook.add(products_frame, text="Products")
        
        # Create top frame with buttons
        top_frame = ttk.Frame(products_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Product", command=self.model.add_product)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Add search functionality
        search_label = ttk.Label(top_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.search_entry = ttk.Entry(top_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda event: self.model.search_products())
        
        search_button = ttk.Button(top_frame, text="Search", command=self.model.search_products)
        search_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(top_frame, text="Clear", command=self.model.clear_search)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ("ID", "Name", "TRL", "Programs", "Material Systems")
        self.products_tree = ttk.Treeview(products_frame, columns=columns, show="headings")
        self.model.products_tree = self.products_tree  # Set reference in model
        
        # Define headings
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        
        # Adjust column widths
        self.products_tree.column("Programs", width=150)
        self.products_tree.column("Material Systems", width=150)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(products_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.products_tree.bind("<Double-1>", self.model.edit_product)
        
        # Populate treeview
        self.populate_products_tree()
    
    def populate_products_tree(self):
        """Populate the products treeview with data"""
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Add products to treeview
        for product in self.model.data["products"]:
            # Format program IDs
            program_ids = []
            for program_entry in product.get("programs", []):
                if isinstance(program_entry, dict) and "programID" in program_entry:
                    program_ids.append(program_entry["programID"])
                elif isinstance(program_entry, str):
                    program_ids.append(program_entry)
            programs = ", ".join(program_ids)
            
            # Format material system IDs
            material_ids = []
            for material_entry in product.get("materialSystems", []):
                if isinstance(material_entry, dict) and "materialID" in material_entry:
                    material_ids.append(material_entry["materialID"])
                elif isinstance(material_entry, str):
                    material_ids.append(material_entry)
            materials = ", ".join(material_ids)
            
            values = (
                product["id"],
                product["name"],
                product.get("trl", ""),
                programs,
                materials
            )
            self.products_tree.insert("", tk.END, values=values) 