import tkinter as tk
from tkinter import ttk
from ..base import BaseModel
from .product_view import ProductView
from .product_form import ProductForm

class ProductModel(BaseModel):
    """Model for managing products"""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.products_tree = None
        self.view = ProductView(self)
    
    def create_products_tab(self, notebook):
        """Create the Products tab in the notebook"""
        self.view.create_products_tab(notebook)
    
    def populate_products_tree(self):
        """Populate the products treeview with data"""
        self.view.populate_products_tree()
    
    def get_empty_product_template(self, product_id):
        """Create an empty product template with all required fields"""
        return {
            "id": product_id,
            "name": "",
            "trl": "",
            "programs": [],
            "materialSystems": [],
            "requirements": {},
            "postProcessingSuppliers": [],
            "designTools": [],
            "documentation": [],
            "specialNDT": [],
            "partAcceptance": [],
            "roadmap": [],
            "milestones": [],
            "businessCase": {
                "costSavings": "",
                "scheduleSavings": "",
                "performanceGains": ""
            }
        }
    
    def ensure_product_structure(self, product):
        """Ensure the product has all required fields"""
        template = self.get_empty_product_template(product["id"])
        
        # Ensure all keys from template exist in product
        for key, default_value in template.items():
            if key not in product:
                product[key] = default_value
        
        # Ensure businessCase structure
        if "businessCase" not in product or not isinstance(product["businessCase"], dict):
            product["businessCase"] = template["businessCase"]
        else:
            for key, default_value in template["businessCase"].items():
                if key not in product["businessCase"]:
                    product["businessCase"][key] = default_value
        
        # Explicitly ensure designTools and documentation are lists
        if not isinstance(product["designTools"], list):
            product["designTools"] = []
        
        # No need to convert string designTools to dictionary format anymore
        # We're now using simple strings for designTools
            
        if not isinstance(product["documentation"], list):
            product["documentation"] = []
            
        # No need to convert string documentation to dictionary format anymore
        # We're now using simple strings for documentation
        
        return product
    
    def add_product(self):
        """Open a window to add a new product"""
        # Generate next available ID
        next_id = self.get_next_product_id()
        
        # Create an empty product template
        product = self.get_empty_product_template(next_id)
        
        # Open the product form
        ProductForm(self, product, is_new=True)
    
    def edit_product(self, event):
        """Open a window to edit an existing product"""
        # Get selected item
        selected_item = self.products_tree.selection()
        if not selected_item:
            return
        
        # Get values
        values = self.products_tree.item(selected_item, "values")
        product_id = values[0]
        print(f"Editing product with ID: {product_id}")
        
        # Find product in data
        product = next((p for p in self.data["products"] if p["id"] == product_id), None)
        if not product:
            print(f"Product with ID {product_id} not found")
            return
        
        print(f"Original product data: {product}")
        
        # Ensure product has all required fields
        product = self.ensure_product_structure(product)
        
        print(f"Product data after structure check: {product}")
        print(f"Design Tools: {product.get('designTools', [])}")
        print(f"Documentation: {product.get('documentation', [])}")
        
        # Open the product form
        ProductForm(self, product, is_new=False)
    
    def get_next_product_id(self):
        """Generate the next available product ID"""
        # Get existing IDs
        existing_ids = [p["id"] for p in self.data["products"] if isinstance(p, dict) and "id" in p]
        
        # Find the highest numeric ID
        highest_id = 0
        for id_str in existing_ids:
            try:
                id_num = int(id_str.replace("P", ""))
                highest_id = max(highest_id, id_num)
            except (ValueError, AttributeError):
                pass
        
        # Generate next ID
        next_id = f"P{highest_id + 1:03d}"
        return next_id
    
    def save_product(self, product, is_new=False):
        """Save a product to the data store"""
        print(f"Saving product with ID: {product['id']}")
        print(f"Design Tools before save: {product.get('designTools', [])}")
        print(f"Documentation before save: {product.get('documentation', [])}")
        
        if is_new:
            # Add to data
            self.data["products"].append(product)
            self.update_status(f"Added new product: {product['name']}")
        else:
            # Find and update the existing product in the data
            for i, p in enumerate(self.data["products"]):
                if p["id"] == product["id"]:
                    self.data["products"][i] = product
                    break
            self.update_status(f"Updated product: {product['name']}")
        
        # Refresh treeview
        self.populate_products_tree()
    
    def delete_product(self, product):
        """Delete a product from the data store"""
        if self.confirm_delete(product['name']):
            # Remove product from data
            self.data["products"].remove(product)
            
            # Refresh treeview
            self.populate_products_tree()
            
            self.update_status(f"Deleted product: {product['name']}")
            return True
        return False 