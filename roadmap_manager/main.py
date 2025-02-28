import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from roadmap_manager.models.program import ProgramModel
from roadmap_manager.models.material import MaterialModel
from roadmap_manager.models.supplier import SupplierModel
from roadmap_manager.models.funding import FundingModel
from roadmap_manager.models.product import ProductModel
from roadmap_manager.utils import load_json_data, save_json_data

class RoadmapManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Roadmap Manager")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize status_var attribute
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Load data - use absolute path to ensure file can be found
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_file = os.path.join(base_dir, "roadmap.json")
        self.load_data()
        
        # Initialize models
        self.program_model = ProgramModel(self)
        self.material_model = MaterialModel(self)
        self.supplier_model = SupplierModel(self)
        self.funding_model = FundingModel(self)
        self.product_model = ProductModel(self)
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_tabs()
        
        # Create bottom frame with save button
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.X, pady=10)
        
        self.save_button = ttk.Button(self.bottom_frame, text="Save Changes", command=self.save_data)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        self.reload_button = ttk.Button(self.bottom_frame, text="Reload Data", command=self.reload_data)
        self.reload_button.pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_data(self):
        """Load data from the JSON file"""
        self.data, error = load_json_data(self.data_file)
        if error:
            messagebox.showerror("Error", error)
        else:
            self.status_var.set(f"Data loaded from {self.data_file}")

    def reload_data(self):
        """Reload data and refresh all tabs"""
        self.load_data()
        # Refresh all tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        self.create_tabs()
        self.status_var.set("Data reloaded successfully")

    def save_data(self):
        """Save data to the JSON file"""
        success, error = save_json_data(self.data_file, self.data)
        if success:
            self.status_var.set(f"Data saved to {self.data_file}")
            messagebox.showinfo("Success", "Data saved successfully")
        else:
            messagebox.showerror("Error", error)

    def create_tabs(self):
        """Create all tabs in the notebook"""
        # Programs tab
        self.program_model.create_programs_tab(self.notebook)
        
        # Products tab
        self.product_model.create_products_tab(self.notebook)
        
        # Materials tab
        self.material_model.create_materials_tab(self.notebook)
        
        # Suppliers tabs
        self.supplier_model.create_printing_suppliers_tab(self.notebook)
        self.supplier_model.create_post_processing_suppliers_tab(self.notebook)
        
        # Funding opportunities tab
        self.funding_model.create_funding_opps_tab(self.notebook)
        
        # TODO: Add other tabs as they are implemented
        # self.create_products_tab()

def main():
    """Main entry point for the application"""
    try:
        # Set up the Tkinter root window
        root = tk.Tk()
        
        # Create the application
        app = RoadmapManager(root)
        
        # Start the main event loop
        root.mainloop()
    except Exception as e:
        # Show error message if something goes wrong
        import traceback
        error_message = f"An error occurred: {str(e)}\n\n{traceback.format_exc()}"
        
        try:
            # Try to show a GUI error message
            messagebox.showerror("Error", error_message)
        except:
            # Fall back to console error message
            print("ERROR:", error_message)
        
        # Exit with error code
        sys.exit(1)

if __name__ == "__main__":
    main() 