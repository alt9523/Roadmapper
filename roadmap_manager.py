import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import re
# Removing tkcalendar dependency
# from tkcalendar import DateEntry  # You'll need to install this: pip install tkcalendar

class DateEntry(ttk.Frame):
    """A simple date entry widget using a single textbox with YYYY-MM-DD format"""
    def __init__(self, master=None, width=10, textvariable=None, initial_date=None, **kw):
        super().__init__(master, **kw)
        
        # Create StringVar if not provided
        if textvariable is None:
            self.date_var = tk.StringVar()
        else:
            self.date_var = textvariable
        
        # Default to current date if no initial date provided
        if initial_date is None:
            initial_date = datetime.now().strftime("%Y-%m-%d")
        elif isinstance(initial_date, datetime):
            initial_date = initial_date.strftime("%Y-%m-%d")
            
        self.date_var.set(initial_date)
        
        # Create entry widget
        vcmd = (self.register(self._validate), '%P')
        self.entry = ttk.Entry(self, width=width, textvariable=self.date_var, validate="focusout", validatecommand=vcmd)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add a calendar button (just for visual consistency)
        self.calendar_button = ttk.Button(self, text="📅", width=2, command=self._show_today)
        self.calendar_button.pack(side=tk.LEFT, padx=(2, 0))
        
        # Bind events
        self.entry.bind("<FocusOut>", self._on_focus_out)
    
    def _show_today(self):
        """Set the date to today when calendar button is clicked"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_var.set(today)
        
    def _validate(self, value):
        """Validate and format the date string"""
        if not value:
            return True
            
        # Try to parse the date
        try:
            # Handle different formats
            if re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$', value):  # MM-DD-YYYY or MM/DD/YYYY
                parts = re.split(r'[-/]', value)
                month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                if year < 100:
                    year += 2000
            elif re.match(r'^\d{2,4}[-/]\d{1,2}[-/]\d{1,2}$', value):  # YYYY-MM-DD or YYYY/MM/DD
                parts = re.split(r'[-/]', value)
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                if year < 100:
                    year += 2000
            else:
                # Try direct parsing
                date_obj = datetime.strptime(value, "%Y-%m-%d")
                year, month, day = date_obj.year, date_obj.month, date_obj.day
                
            # Validate date
            date_obj = datetime(year, month, day)
            formatted_date = date_obj.strftime("%Y-%m-%d")
            self.date_var.set(formatted_date)
            return True
        except (ValueError, IndexError):
            # If invalid, revert to current date
            self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
            return False
            
    def _on_focus_out(self, event):
        """Validate date when focus leaves the entry"""
        self._validate(self.date_var.get())
    
    def get_date(self):
        """Return the date string in YYYY-MM-DD format"""
        return self.date_var.get()
    
    def set_date(self, date):
        """Set the date"""
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
        self.date_var.set(date)
        self._validate(date)

class RoadmapManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Roadmap Manager")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize status_var attribute
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Load data
        self.data_file = "roadmap.json"
        self.load_data()
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_programs_tab()
        self.create_products_tab()
        self.create_materials_tab()
        self.create_printing_suppliers_tab()
        self.create_post_processing_suppliers_tab()
        self.create_funding_opps_tab()
        
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
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
            
            # Ensure all required sections exist
            if "programs" not in self.data:
                self.data["programs"] = []
            if "products" not in self.data:
                self.data["products"] = []
            if "materialSystems" not in self.data:
                self.data["materialSystems"] = []
            if "printingSuppliers" not in self.data:
                self.data["printingSuppliers"] = []
            if "postProcessingSuppliers" not in self.data:
                self.data["postProcessingSuppliers"] = []
            if "fundingOpps" not in self.data:
                self.data["fundingOpps"] = []
                
            self.status_var.set(f"Data loaded from {self.data_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.data = {
                "programs": [], 
                "products": [], 
                "materialSystems": [], 
                "printingSuppliers": [],
                "postProcessingSuppliers": [],
                "fundingOpps": []
            }

    def reload_data(self):
        self.load_data()
        # Refresh all tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        self.create_programs_tab()
        self.create_products_tab()
        self.create_materials_tab()
        self.create_printing_suppliers_tab()
        self.create_post_processing_suppliers_tab()
        self.create_funding_opps_tab()
        self.status_var.set("Data reloaded successfully")

    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            self.status_var.set(f"Data saved to {self.data_file}")
            messagebox.showinfo("Success", "Data saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    def create_programs_tab(self):
        programs_frame = ttk.Frame(self.notebook)
        self.notebook.add(programs_frame, text="Programs")
        
        # Create top frame with buttons
        top_frame = ttk.Frame(programs_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Program", command=self.add_program)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ("ID", "Name", "Sector", "Division", "Customer", "Mission Class")
        self.programs_tree = ttk.Treeview(programs_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.programs_tree.heading(col, text=col)
            self.programs_tree.column(col, width=100)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(programs_frame, orient=tk.VERTICAL, command=self.programs_tree.yview)
        self.programs_tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.programs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.programs_tree.bind("<Double-1>", self.edit_program)
        
        # Populate treeview
        self.populate_programs_tree()

    def populate_programs_tree(self):
        # Clear existing items
        for item in self.programs_tree.get_children():
            self.programs_tree.delete(item)
        
        # Add programs to treeview
        for program in self.data["programs"]:
            values = (
                program["id"],
                program["name"],
                program.get("sector", ""),
                program.get("division", ""),
                program.get("customerName", ""),
                program.get("missionClass", "")
            )
            self.programs_tree.insert("", tk.END, values=values)

    def add_program(self):
        # Create a new window for adding a program
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Program")
        add_window.geometry("500x400")
        add_window.grab_set()  # Make window modal
        
        # Create form fields
        ttk.Label(add_window, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=id_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Sector:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        sector_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=sector_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Division:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        division_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=division_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Customer Name:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        customer_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=customer_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Mission Class:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        mission_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=mission_var).grid(row=5, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Save button
        def save_program():
            # Validate required fields
            if not id_var.get() or not name_var.get():
                messagebox.showerror("Error", "ID and Name are required fields")
                return
            
            # Create new program
            new_program = {
                "id": id_var.get(),
                "name": name_var.get(),
                "sector": sector_var.get(),
                "division": division_var.get(),
                "customerName": customer_var.get(),
                "missionClass": mission_var.get()
            }
            
            # Add to data
            self.data["programs"].append(new_program)
            
            # Refresh treeview
            self.populate_programs_tree()
            
            # Close window
            add_window.destroy()
            
            self.status_var.set(f"Added program: {new_program['name']}")
        
        ttk.Button(add_window, text="Save", command=save_program).grid(row=6, column=1, sticky=tk.E, padx=10, pady=20)
        ttk.Button(add_window, text="Cancel", command=add_window.destroy).grid(row=6, column=0, sticky=tk.W, padx=10, pady=20)

    def edit_program(self, event):
        # Get selected item
        selected_item = self.programs_tree.selection()
        if not selected_item:
            return
        
        # Get values
        values = self.programs_tree.item(selected_item, "values")
        program_id = values[0]
        
        # Find program in data
        program = next((p for p in self.data["programs"] if p["id"] == program_id), None)
        if not program:
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Program: {program['name']}")
        edit_window.geometry("500x400")
        edit_window.grab_set()  # Make window modal
        
        # Create form fields
        ttk.Label(edit_window, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=program["id"])
        ttk.Entry(edit_window, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=program["name"])
        ttk.Entry(edit_window, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Sector:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        sector_var = tk.StringVar(value=program.get("sector", ""))
        ttk.Entry(edit_window, textvariable=sector_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Division:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        division_var = tk.StringVar(value=program.get("division", ""))
        ttk.Entry(edit_window, textvariable=division_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Customer Name:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        customer_var = tk.StringVar(value=program.get("customerName", ""))
        ttk.Entry(edit_window, textvariable=customer_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Mission Class:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        mission_var = tk.StringVar(value=program.get("missionClass", ""))
        ttk.Entry(edit_window, textvariable=mission_var).grid(row=5, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Save button
        def save_program():
            # Validate required fields
            if not name_var.get():
                messagebox.showerror("Error", "Name is required")
                return
            
            # Update program
            program["name"] = name_var.get()
            program["sector"] = sector_var.get()
            program["division"] = division_var.get()
            program["customerName"] = customer_var.get()
            program["missionClass"] = mission_var.get()
            
            # Refresh treeview
            self.populate_programs_tree()
            
            # Close window
            edit_window.destroy()
            
            self.status_var.set(f"Updated program: {program['name']}")
        
        # Delete button
        def delete_program():
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete program '{program['name']}'?"):
                # Remove program from data
                self.data["programs"].remove(program)
                
                # Refresh treeview
                self.populate_programs_tree()
                
                # Close window
                edit_window.destroy()
                
                self.status_var.set(f"Deleted program: {program['name']}")
        
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_program).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_program).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)

    def create_products_tab(self):
        products_frame = ttk.Frame(self.notebook)
        self.notebook.add(products_frame, text="Products")
        
        # Create top frame with buttons
        top_frame = ttk.Frame(products_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Product", command=self.add_product)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ("ID", "Name", "TRL", "Programs", "Material Systems")
        self.products_tree = ttk.Treeview(products_frame, columns=columns, show="headings")
        
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
        self.products_tree.bind("<Double-1>", self.edit_product)
        
        # Populate treeview
        self.populate_products_tree()

    def populate_products_tree(self):
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Add products to treeview
        for product in self.data["products"]:
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

    def edit_product(self, event):
        # Get selected item
        selected_item = self.products_tree.selection()
        if not selected_item:
            return
        
        # Get values
        values = self.products_tree.item(selected_item, "values")
        product_id = values[0]
        
        # Find product in data
        product = None
        for p in self.data["products"]:
            if p["id"] == product_id:
                product = p
                break
        
        if not product:
            return
            
        # Create a new window for editing a product
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Product")
        edit_window.geometry("800x600")
        edit_window.grab_set()  # Make window modal
        
        # Create basic info frame
        basic_frame = ttk.Frame(edit_window)
        basic_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create variables for form fields
        id_var = tk.StringVar(value=product.get("id", ""))
        name_var = tk.StringVar(value=product.get("name", ""))
        trl_var = tk.StringVar(value=str(product.get("trl", "")))
        
        # Create entry widgets
        ttk.Label(basic_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(basic_frame, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(basic_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(basic_frame, textvariable=name_var, width=40).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(basic_frame, text="TRL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(basic_frame, textvariable=trl_var, values=["1", "2", "3", "4", "5", "6", "7", "8", "9"]).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Save function
        def save_product():
            # Validate required fields
            if not id_var.get() or not name_var.get():
                messagebox.showerror("Error", "ID and Name are required fields")
                return
            
            # Update product
            product["name"] = name_var.get()
            product["trl"] = int(trl_var.get()) if trl_var.get() else None
            
            # Refresh treeview
            self.populate_products_tree()
            
            # Close window
            edit_window.destroy()
            
            self.status_var.set(f"Updated product: {product['name']}")
        
        # Delete button
        def delete_product():
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product '{product['name']}'?"):
                # Remove product from data
                self.data["products"].remove(product)
                
                # Refresh treeview
                self.populate_products_tree()
                
                # Close window
                edit_window.destroy()
                
                self.status_var.set(f"Deleted product: {product['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)

    def add_product(self):
        # Create a new window for adding a product
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Product")
        add_window.geometry("500x400")
        add_window.grab_set()  # Make window modal
        
        # Create form fields
        ttk.Label(add_window, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=id_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="TRL:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        trl_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=trl_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Programs:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        programs_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=programs_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Material Systems:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        materials_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=materials_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Save button
        def save_product():
            # Validate required fields
            if not id_var.get() or not name_var.get():
                messagebox.showerror("Error", "ID and Name are required fields")
                return
            
            # Create new product
            new_product = {
                "id": id_var.get(),
                "name": name_var.get(),
                "trl": int(trl_var.get()) if trl_var.get() else None,
                "programs": [{"programID": program_id.strip()} for program_id in programs_var.get().split(",")],
                "materialSystems": [{"materialID": material_id.strip()} for material_id in materials_var.get().split(",")],
                "requirements": {}
            }
            
            # Add to data
            self.data["products"].append(new_product)
            
            # Refresh treeview
            self.populate_products_tree()
            
            # Close window
            add_window.destroy()
            
            self.status_var.set(f"Added product: {new_product['name']}")
        
        ttk.Button(add_window, text="Save", command=save_product).grid(row=5, column=1, sticky=tk.E, padx=10, pady=20)
        ttk.Button(add_window, text="Cancel", command=add_window.destroy).grid(row=5, column=0, sticky=tk.W, padx=10, pady=20)

    def create_materials_tab(self):
        materials_frame = ttk.Frame(self.notebook)
        self.notebook.add(materials_frame, text="Material Systems")
        
        # Create top frame with buttons
        top_frame = ttk.Frame(materials_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Material System", command=self.add_material)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ("ID", "Name", "Process", "Material", "MRL", "Qualification")
        self.materials_tree = ttk.Treeview(materials_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.materials_tree.heading(col, text=col)
            self.materials_tree.column(col, width=100)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(materials_frame, orient=tk.VERTICAL, command=self.materials_tree.yview)
        self.materials_tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.materials_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.materials_tree.bind("<Double-1>", self.edit_material)
        
        # Populate treeview
        self.populate_materials_tree()

    def populate_materials_tree(self):
        # Clear existing items
        for item in self.materials_tree.get_children():
            self.materials_tree.delete(item)
        
        # Add material systems to treeview
        for material in self.data["materialSystems"]:
            values = (
                material["id"],
                material["name"],
                material.get("process", ""),
                material.get("material", ""),
                material.get("mrl", ""),
                material.get("qualification", "")
            )
            self.materials_tree.insert("", tk.END, values=values)

    def add_material(self):
        # Create a new window for adding a material system
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Material System")
        add_window.geometry("600x700")
        add_window.grab_set()  # Make window modal
        
        # Create a notebook for material details
        material_notebook = ttk.Notebook(add_window)
        material_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic info tab
        basic_frame = ttk.Frame(material_notebook)
        material_notebook.add(basic_frame, text="Basic Info")
        
        # Create form fields for basic info
        ttk.Label(basic_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=id_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Process:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        process_var = tk.StringVar()
        ttk.Combobox(basic_frame, textvariable=process_var, values=["Laser Powder Bed Fusion", "Electron Beam Melting", "Directed Energy Deposition", "Binder Jetting"]).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Material:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        material_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=material_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="MRL:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        mrl_var = tk.StringVar()
        ttk.Combobox(basic_frame, textvariable=mrl_var, values=list(range(1, 11))).grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Qualification:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        qualification_var = tk.StringVar()
        ttk.Combobox(basic_frame, textvariable=qualification_var, values=["Qualified", "In Progress", "Pending"]).grid(row=5, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Qualification Class:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        qual_class_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=qual_class_var).grid(row=6, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Statistical Basis:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
        stat_basis_var = tk.StringVar()
        ttk.Combobox(basic_frame, textvariable=stat_basis_var, values=["S", "A", "B", "C", "D", "None"]).grid(row=7, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Roadmap tab
        roadmap_frame = ttk.Frame(material_notebook)
        material_notebook.add(roadmap_frame, text="Roadmap")
        
        # Roadmap tasks list
        ttk.Label(roadmap_frame, text="Roadmap Tasks:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Create a frame for the task list
        tasks_frame = ttk.Frame(roadmap_frame)
        tasks_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store task entries
        task_entries = []
        
        # Function to add a new task entry
        def add_task_entry():
            task_frame = ttk.Frame(tasks_frame)
            task_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(task_frame, text="Task:").grid(row=0, column=0, sticky=tk.W)
            task_var = tk.StringVar()
            ttk.Entry(task_frame, textvariable=task_var, width=20).grid(row=0, column=1, sticky=tk.W)
            
            ttk.Label(task_frame, text="Start:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
            start_entry = DateEntry(task_frame, width=10)
            start_entry.grid(row=0, column=3, sticky=tk.W)
            
            ttk.Label(task_frame, text="End:").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
            end_entry = DateEntry(task_frame, width=10)
            end_entry.grid(row=0, column=5, sticky=tk.W)
            
            ttk.Label(task_frame, text="Status:").grid(row=0, column=6, sticky=tk.W, padx=(10, 0))
            status_var = tk.StringVar()
            ttk.Combobox(task_frame, textvariable=status_var, values=["Planned", "In Progress", "Complete"], width=10).grid(row=0, column=7, sticky=tk.W)
            
            ttk.Label(task_frame, text="Funding:").grid(row=0, column=8, sticky=tk.W, padx=(10, 0))
            funding_var = tk.StringVar()
            ttk.Combobox(task_frame, textvariable=funding_var, values=["Division IRAD", "Sector IRAD", "CRAD", ""], width=12).grid(row=0, column=9, sticky=tk.W)
            
            # Button to remove this task
            def remove_task():
                task_frame.destroy()
                task_entries.remove(entry_data)
            
            ttk.Button(task_frame, text="X", width=2, command=remove_task).grid(row=0, column=10, padx=5)
            
            # Store the entry data
            entry_data = {
                "frame": task_frame,
                "task": task_var,
                "start": start_entry,
                "end": end_entry,
                "status": status_var,
                "fundingType": funding_var
            }
            task_entries.append(entry_data)
        
        # Add button for tasks
        ttk.Button(roadmap_frame, text="Add Task", command=add_task_entry).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Milestones tab
        milestones_frame = ttk.Frame(material_notebook)
        material_notebook.add(milestones_frame, text="Milestones")
        
        # Milestones list
        ttk.Label(milestones_frame, text="Milestones:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Create a frame for the milestone list
        ms_frame = ttk.Frame(milestones_frame)
        ms_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store milestone entries
        milestone_entries = []
        
        # Function to add a new milestone entry
        def add_milestone_entry():
            ms_entry_frame = ttk.Frame(ms_frame)
            ms_entry_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(ms_entry_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
            name_var = tk.StringVar()
            ttk.Entry(ms_entry_frame, textvariable=name_var, width=20).grid(row=0, column=1, sticky=tk.W)
            
            ttk.Label(ms_entry_frame, text="Date:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
            date_entry = DateEntry(ms_entry_frame, width=10)
            date_entry.grid(row=0, column=3, sticky=tk.W)
            
            ttk.Label(ms_entry_frame, text="Description:").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
            desc_var = tk.StringVar()
            ttk.Entry(ms_entry_frame, textvariable=desc_var, width=30).grid(row=0, column=5, sticky=tk.W)
            
            # Button to remove this milestone
            def remove_milestone():
                ms_entry_frame.destroy()
                milestone_entries.remove(entry_data)
            
            ttk.Button(ms_entry_frame, text="X", width=2, command=remove_milestone).grid(row=0, column=6, padx=5)
            
            # Store the entry data
            entry_data = {
                "frame": ms_entry_frame,
                "name": name_var,
                "date": date_entry,
                "description": desc_var
            }
            milestone_entries.append(entry_data)
        
        # Add button for milestones
        ttk.Button(milestones_frame, text="Add Milestone", command=add_milestone_entry).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Save button
        def save_material():
            # Validate required fields
            if not id_var.get() or not name_var.get():
                messagebox.showerror("Error", "ID and Name are required fields")
                return
            
            # Get roadmap tasks
            roadmap_tasks = []
            for entry in task_entries:
                if not entry["task"].get():  # Skip empty tasks
                    continue
                    
                task = {
                    "task": entry["task"].get(),
                    "start": entry["start"].get_date().strftime("%Y-%m-%d"),
                    "end": entry["end"].get_date().strftime("%Y-%m-%d"),
                    "status": entry["status"].get()
                }
                
                # Add funding type if provided
                if entry["fundingType"].get():
                    task["fundingType"] = entry["fundingType"].get()
                
                roadmap_tasks.append(task)
            
            # Get milestones
            milestones = []
            for entry in milestone_entries:
                if not entry["name"].get():  # Skip empty milestones
                    continue
                    
                milestone = {
                    "name": entry["name"].get(),
                    "date": entry["date"].get_date().strftime("%Y-%m-%d"),
                    "description": entry["description"].get()
                }
                milestones.append(milestone)
            
            # Create new material system
            new_material = {
                "id": id_var.get(),
                "name": name_var.get(),
                "process": process_var.get(),
                "material": material_var.get(),
                "mrl": int(mrl_var.get()) if mrl_var.get() else None,
                "qualification": qualification_var.get(),
                "qualificationClass": qual_class_var.get(),
                "statisticalBasis": stat_basis_var.get(),
                "roadmap": roadmap_tasks,
                "milestones": milestones
            }
            
            # Add to data
            self.data["materialSystems"].append(new_material)
            
            # Refresh treeview
            self.populate_materials_tree()
            
            # Close window
            add_window.destroy()
            
            self.status_var.set(f"Added material system: {new_material['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side=tk.LEFT, padx=5)

    def edit_material(self, event):
        # Get selected item
        selected_item = self.materials_tree.selection()
        if not selected_item:
            return
        
        # Get values
        values = self.materials_tree.item(selected_item, "values")
        material_id = values[0]
        
        # Find material in data
        material = next((m for m in self.data["materialSystems"] if m["id"] == material_id), None)
        if not material:
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Material System: {material['name']}")
        edit_window.geometry("600x700")
        edit_window.grab_set()  # Make window modal
        
        # Create a notebook for material details
        material_notebook = ttk.Notebook(edit_window)
        material_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic info tab
        basic_frame = ttk.Frame(material_notebook)
        material_notebook.add(basic_frame, text="Basic Info")
        
        # Create form fields for basic info
        ttk.Label(basic_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=material["id"])
        ttk.Entry(basic_frame, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=material["name"])
        ttk.Entry(basic_frame, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Process:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        process_var = tk.StringVar(value=material.get("process", ""))
        ttk.Combobox(basic_frame, textvariable=process_var, values=["Laser Powder Bed Fusion", "Electron Beam Melting", "Directed Energy Deposition", "Binder Jetting"]).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Material:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        material_var = tk.StringVar(value=material.get("material", ""))
        ttk.Entry(basic_frame, textvariable=material_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="MRL:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        mrl_var = tk.StringVar(value=str(material.get("mrl", "")))
        ttk.Combobox(basic_frame, textvariable=mrl_var, values=list(range(1, 11))).grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Qualification:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        qualification_var = tk.StringVar(value=material.get("qualification", ""))
        ttk.Combobox(basic_frame, textvariable=qualification_var, values=["Qualified", "In Progress", "Pending"]).grid(row=5, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Qualification Class:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        qual_class_var = tk.StringVar(value=material.get("qualificationClass", ""))
        ttk.Entry(basic_frame, textvariable=qual_class_var).grid(row=6, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Statistical Basis:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
        stat_basis_var = tk.StringVar(value=material.get("statisticalBasis", ""))
        ttk.Combobox(basic_frame, textvariable=stat_basis_var, values=["S", "A", "B", "C", "D", "None"]).grid(row=7, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Roadmap tab
        roadmap_frame = ttk.Frame(material_notebook)
        material_notebook.add(roadmap_frame, text="Roadmap")
        
        # Roadmap tasks list
        ttk.Label(roadmap_frame, text="Roadmap Tasks:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Create a frame for the task list
        tasks_frame = ttk.Frame(roadmap_frame)
        tasks_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store task entries
        task_entries = []
        
        # Function to add a new task entry
        def add_task_entry(task=None):
            task_frame = ttk.Frame(tasks_frame)
            task_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(task_frame, text="Task:").grid(row=0, column=0, sticky=tk.W)
            task_var = tk.StringVar(value=task["task"] if task else "")
            ttk.Entry(task_frame, textvariable=task_var, width=20).grid(row=0, column=1, sticky=tk.W)
            
            ttk.Label(task_frame, text="Start:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
            start_entry = DateEntry(task_frame, width=10)
            if task:
                try:
                    start_date = datetime.strptime(task["start"], "%Y-%m-%d")
                    start_entry.set_date(start_date)
                except (ValueError, TypeError):
                    pass
            start_entry.grid(row=0, column=3, sticky=tk.W)
            
            ttk.Label(task_frame, text="End:").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
            end_entry = DateEntry(task_frame, width=10)
            if task:
                try:
                    end_date = datetime.strptime(task["end"], "%Y-%m-%d")
                    end_entry.set_date(end_date)
                except (ValueError, TypeError):
                    pass
            end_entry.grid(row=0, column=5, sticky=tk.W)
            
            ttk.Label(task_frame, text="Status:").grid(row=0, column=6, sticky=tk.W, padx=(10, 0))
            status_var = tk.StringVar(value=task["status"] if task else "")
            ttk.Combobox(task_frame, textvariable=status_var, values=["Planned", "In Progress", "Complete"], width=10).grid(row=0, column=7, sticky=tk.W)
            
            ttk.Label(task_frame, text="Funding:").grid(row=0, column=8, sticky=tk.W, padx=(10, 0))
            funding_var = tk.StringVar(value=task.get("fundingType", "") if task else "")
            ttk.Combobox(task_frame, textvariable=funding_var, values=["Division IRAD", "Sector IRAD", "CRAD", ""], width=12).grid(row=0, column=9, sticky=tk.W)
            
            # Button to remove this task
            def remove_task():
                task_frame.destroy()
                task_entries.remove(entry_data)
            
            ttk.Button(task_frame, text="X", width=2, command=remove_task).grid(row=0, column=10, padx=5)
            
            # Store the entry data
            entry_data = {
                "frame": task_frame,
                "task": task_var,
                "start": start_entry,
                "end": end_entry,
                "status": status_var,
                "fundingType": funding_var
            }
            task_entries.append(entry_data)
            
            return entry_data
        
        # Add existing tasks
        for task in material.get("roadmap", []):
            add_task_entry(task)
        
        # Add button for tasks
        ttk.Button(roadmap_frame, text="Add Task", command=lambda: add_task_entry()).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Milestones tab
        milestones_frame = ttk.Frame(material_notebook)
        material_notebook.add(milestones_frame, text="Milestones")
        
        # Milestones list
        ttk.Label(milestones_frame, text="Milestones:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Create a frame for the milestone list
        ms_frame = ttk.Frame(milestones_frame)
        ms_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store milestone entries
        milestone_entries = []
        
        # Function to add a new milestone entry
        def add_milestone_entry(milestone=None):
            ms_entry_frame = ttk.Frame(ms_frame)
            ms_entry_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(ms_entry_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
            name_var = tk.StringVar(value=milestone["name"] if milestone else "")
            ttk.Entry(ms_entry_frame, textvariable=name_var, width=20).grid(row=0, column=1, sticky=tk.W)
            
            ttk.Label(ms_entry_frame, text="Date:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
            date_entry = DateEntry(ms_entry_frame, width=10)
            if milestone:
                try:
                    milestone_date = datetime.strptime(milestone["date"], "%Y-%m-%d")
                    date_entry.set_date(milestone_date)
                except (ValueError, TypeError):
                    pass
            date_entry.grid(row=0, column=3, sticky=tk.W)
            
            ttk.Label(ms_entry_frame, text="Description:").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
            desc_var = tk.StringVar(value=milestone.get("description", "") if milestone else "")
            ttk.Entry(ms_entry_frame, textvariable=desc_var, width=30).grid(row=0, column=5, sticky=tk.W)
            
            # Button to remove this milestone
            def remove_milestone():
                ms_entry_frame.destroy()
                milestone_entries.remove(entry_data)
            
            ttk.Button(ms_entry_frame, text="X", width=2, command=remove_milestone).grid(row=0, column=6, padx=5)
            
            # Store the entry data
            entry_data = {
                "frame": ms_entry_frame,
                "name": name_var,
                "date": date_entry,
                "description": desc_var
            }
            milestone_entries.append(entry_data)
        
        # Add existing milestones
        for milestone in material.get("milestones", []):
            add_milestone_entry(milestone)
        
        # Add button for milestones
        ttk.Button(milestones_frame, text="Add Milestone", command=lambda: add_milestone_entry()).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Save button
        def save_material():
            # Validate required fields
            if not name_var.get():
                messagebox.showerror("Error", "Name is required")
                return
            
            # Get roadmap tasks
            roadmap_tasks = []
            for entry in task_entries:
                if not entry["task"].get():  # Skip empty tasks
                    continue
                    
                task = {
                    "task": entry["task"].get(),
                    "start": entry["start"].get_date().strftime("%Y-%m-%d"),
                    "end": entry["end"].get_date().strftime("%Y-%m-%d"),
                    "status": entry["status"].get()
                }
                
                # Add funding type if provided
                if entry["fundingType"].get():
                    task["fundingType"] = entry["fundingType"].get()
                
                roadmap_tasks.append(task)
            
            # Get milestones
            milestones = []
            for entry in milestone_entries:
                if not entry["name"].get():  # Skip empty milestones
                    continue
                    
                milestone = {
                    "name": entry["name"].get(),
                    "date": entry["date"].get_date().strftime("%Y-%m-%d"),
                    "description": entry["description"].get()
                }
                milestones.append(milestone)
            
            # Update material
            material["name"] = name_var.get()
            material["process"] = process_var.get()
            material["material"] = material_var.get()
            material["mrl"] = int(mrl_var.get()) if mrl_var.get() else None
            material["qualification"] = qualification_var.get()
            material["qualificationClass"] = qual_class_var.get()
            material["statisticalBasis"] = stat_basis_var.get()
            material["roadmap"] = roadmap_tasks
            material["milestones"] = milestones
            
            # Refresh treeview
            self.populate_materials_tree()
            
            # Close window
            edit_window.destroy()
            
            self.status_var.set(f"Updated material system: {material['name']}")
        
        # Delete button
        def delete_material():
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete material system '{material['name']}'?"):
                # Remove material from data
                self.data["materialSystems"].remove(material)
                
                # Refresh treeview
                self.populate_materials_tree()
                
                # Close window
                edit_window.destroy()
                
                self.status_var.set(f"Deleted material system: {material['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)

    def create_printing_suppliers_tab(self):
        suppliers_frame = ttk.Frame(self.notebook)
        self.notebook.add(suppliers_frame, text="Printing Suppliers")
        
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

    def add_printing_supplier(self):
        # Create a new window for adding a supplier
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Supplier")
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
                messagebox.showerror("Error", "ID and Name are required fields")
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
            
            self.status_var.set(f"Added printing supplier: {new_supplier['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side=tk.LEFT, padx=5)

    def edit_printing_supplier(self, event):
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
        edit_window = tk.Toplevel(self.root)
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
                messagebox.showerror("Error", "Name is required")
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
            
            self.status_var.set(f"Updated printing supplier: {supplier['name']}")
        
        # Delete button
        def delete_supplier():
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete printing supplier '{supplier['name']}'?"):
                # Remove supplier from data
                self.data["printingSuppliers"].remove(supplier)
                
                # Refresh treeview
                self.populate_printing_suppliers_tree()
                
                # Close window
                edit_window.destroy()
                
                self.status_var.set(f"Deleted printing supplier: {supplier['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(edit_window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)

    def create_post_processing_suppliers_tab(self):
        suppliers_frame = ttk.Frame(self.notebook)
        self.notebook.add(suppliers_frame, text="Post-Processing Suppliers")
        
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

    def add_post_processing_supplier(self):
        # Create a new window for adding a supplier
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Supplier")
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
                messagebox.showerror("Error", "ID and Name are required fields")
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
            
            self.status_var.set(f"Added post-processing supplier: {new_supplier['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side=tk.LEFT, padx=5)

    def edit_post_processing_supplier(self, event):
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
        edit_window = tk.Toplevel(self.root)
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
                messagebox.showerror("Error", "Name is required")
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
            
            self.status_var.set(f"Updated post-processing supplier: {supplier['name']}")
        
        # Delete button
        def delete_supplier():
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete post-processing supplier '{supplier['name']}'?"):
                # Remove supplier from data
                self.data["postProcessingSuppliers"].remove(supplier)
                
                # Refresh treeview
                self.populate_post_processing_suppliers_tree()
                
                # Close window
                edit_window.destroy()
                
                self.status_var.set(f"Deleted post-processing supplier: {supplier['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(edit_window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)

    def create_funding_opps_tab(self):
        funding_frame = ttk.Frame(self.notebook)
        self.notebook.add(funding_frame, text="Funding Opportunities")
        
        # Create top frame with buttons
        top_frame = ttk.Frame(funding_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Opportunity", command=self.add_funding_opp)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ("ID", "Announcement Name", "Description", "Pursuit Type", "Close Date", "End Date")
        self.funding_opps_tree = ttk.Treeview(funding_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.funding_opps_tree.heading(col, text=col)
            self.funding_opps_tree.column(col, width=100)
        
        # Adjust column widths
        self.funding_opps_tree.column("Description", width=200)
        self.funding_opps_tree.column("Announcement Name", width=150)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(funding_frame, orient=tk.VERTICAL, command=self.funding_opps_tree.yview)
        self.funding_opps_tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.funding_opps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.funding_opps_tree.bind("<Double-1>", self.edit_funding_opp)
        
        # Populate treeview
        self.populate_funding_opps_tree()

    def populate_funding_opps_tree(self):
        # Clear existing items
        for item in self.funding_opps_tree.get_children():
            self.funding_opps_tree.delete(item)
        
        # Add opportunities to treeview
        for opp in self.data["fundingOpps"]:
            values = (
                opp["id"],
                opp.get("announcementName", ""),
                opp.get("description", ""),
                opp.get("pursuitType", ""),
                opp.get("closeDate", ""),
                opp.get("endDate", "")
            )
            self.funding_opps_tree.insert("", tk.END, values=values)

    def add_funding_opp(self):
        # Create a new window for adding an opportunity
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Funding Opportunity")
        add_window.geometry("500x500")
        add_window.grab_set()  # Make window modal
        
        # Create form fields
        ttk.Label(add_window, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=id_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Announcement Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Description:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        description_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=description_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Pursuit Type:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        pursuit_type_var = tk.StringVar()
        ttk.Combobox(add_window, textvariable=pursuit_type_var, values=["Division IRAD", "Sector IRAD", "CRAD"]).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Close Date:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        close_date_var = tk.StringVar()
        DateEntry(add_window, textvariable=close_date_var).grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(add_window, text="End Date:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        end_date_var = tk.StringVar()
        DateEntry(add_window, textvariable=end_date_var).grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(add_window, text="Solicitation Number:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        solicitation_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=solicitation_var).grid(row=6, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Funding Amount:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
        amount_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=amount_var).grid(row=7, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(add_window, text="Customer:").grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
        customer_var = tk.StringVar()
        ttk.Entry(add_window, textvariable=customer_var).grid(row=8, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Save button
        def save_opp():
            # Validate required fields
            if not id_var.get() or not name_var.get():
                messagebox.showerror("Error", "ID and Announcement Name are required fields")
                return
            
            # Create new opportunity
            new_opp = {
                "id": id_var.get(),
                "announcementName": name_var.get(),
                "description": description_var.get(),
                "pursuitType": pursuit_type_var.get(),
                "closeDate": close_date_var.get(),
                "endDate": end_date_var.get(),
                "solicitationNumber": solicitation_var.get(),
                "fundingAmount": amount_var.get(),
                "customer": customer_var.get(),
                "pursuits": []
            }
            
            # Add to data
            self.data["fundingOpps"].append(new_opp)
            
            # Refresh treeview
            self.populate_funding_opps_tree()
            
            # Close window
            add_window.destroy()
            
            self.status_var.set(f"Added funding opportunity: {new_opp['announcementName']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_opp).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side=tk.LEFT, padx=5)

    def edit_funding_opp(self, event):
        # Get selected item
        selected_item = self.funding_opps_tree.selection()
        if not selected_item:
            return
        
        # Get values
        values = self.funding_opps_tree.item(selected_item, "values")
        opp_id = values[0]
        
        # Find opportunity in data
        opp = next((o for o in self.data["fundingOpps"] if o["id"] == opp_id), None)
        if not opp:
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Funding Opportunity: {opp.get('announcementName', '')}")
        edit_window.geometry("500x500")
        edit_window.grab_set()  # Make window modal
        
        # Create form fields
        ttk.Label(edit_window, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=opp["id"])
        ttk.Entry(edit_window, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Announcement Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=opp.get("announcementName", ""))
        ttk.Entry(edit_window, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Description:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        description_var = tk.StringVar(value=opp.get("description", ""))
        ttk.Entry(edit_window, textvariable=description_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Pursuit Type:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        pursuit_type_var = tk.StringVar(value=opp.get("pursuitType", ""))
        ttk.Combobox(edit_window, textvariable=pursuit_type_var, values=["Division IRAD", "Sector IRAD", "CRAD"]).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Close Date:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        close_date_var = tk.StringVar(value=opp.get("closeDate", ""))
        DateEntry(edit_window, textvariable=close_date_var).grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(edit_window, text="End Date:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        end_date_var = tk.StringVar(value=opp.get("endDate", ""))
        DateEntry(edit_window, textvariable=end_date_var).grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Solicitation Number:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        solicitation_var = tk.StringVar(value=opp.get("solicitationNumber", ""))
        ttk.Entry(edit_window, textvariable=solicitation_var).grid(row=6, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Funding Amount:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
        amount_var = tk.StringVar(value=opp.get("fundingAmount", ""))
        ttk.Entry(edit_window, textvariable=amount_var).grid(row=7, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(edit_window, text="Customer:").grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
        customer_var = tk.StringVar(value=opp.get("customer", ""))
        ttk.Entry(edit_window, textvariable=customer_var).grid(row=8, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Save button
        def save_opp():
            # Validate required fields
            if not name_var.get():
                messagebox.showerror("Error", "Announcement Name is required")
                return
            
            # Update opportunity
            opp["announcementName"] = name_var.get()
            opp["description"] = description_var.get()
            opp["pursuitType"] = pursuit_type_var.get()
            opp["closeDate"] = close_date_var.get()
            opp["endDate"] = end_date_var.get()
            opp["solicitationNumber"] = solicitation_var.get()
            opp["fundingAmount"] = amount_var.get()
            opp["customer"] = customer_var.get()
            
            # Refresh treeview
            self.populate_funding_opps_tree()
            
            # Close window
            edit_window.destroy()
            
            self.status_var.set(f"Updated funding opportunity: {opp['announcementName']}")
        
        # Delete button
        def delete_opp():
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete funding opportunity '{opp['announcementName']}'?"):
                # Remove opportunity from data
                self.data["fundingOpps"].remove(opp)
                
                # Refresh treeview
                self.populate_funding_opps_tree()
                
                # Close window
                edit_window.destroy()
                
                self.status_var.set(f"Deleted funding opportunity: {opp['announcementName']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(edit_window)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_opp).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_opp).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = RoadmapManager(root)
    root.mainloop()