import tkinter as tk
from tkinter import ttk, messagebox
from .base import BaseModel
from ..date_entry import DateEntry

class ProgramModel(BaseModel):
    """Model for managing programs"""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.programs_tree = None
        self.search_entry = None
        
        # Create product ID to name mapping
        self.product_id_to_name = {}
        for product in self.data.get("products", []):
            if "id" in product and "name" in product:
                self.product_id_to_name[product["id"]] = product["name"]
        
        # Create material system ID to name mapping
        self.material_id_to_name = {}
        for ms in self.data.get("materialSystems", []):
            if "id" in ms and "name" in ms:
                self.material_id_to_name[ms["id"]] = ms["name"]
        
        # Create a mapping of product IDs to their associated material systems
        self.product_material_map = {}
        for product in self.data.get("products", []):
            product_id = product["id"]
            material_systems = []
            if "materialSystems" in product and isinstance(product["materialSystems"], list):
                for ms_entry in product["materialSystems"]:
                    if "materialID" in ms_entry:
                        # Find the material system name
                        ms_id = ms_entry["materialID"]
                        for ms in self.data.get("materialSystems", []):
                            if ms["id"] == ms_id:
                                material_systems.append(f"{ms['id']}: {ms.get('name', '')}")
                                break
            self.product_material_map[product_id] = material_systems
    
    def create_programs_tab(self, notebook):
        """Create the Programs tab in the notebook"""
        programs_frame = ttk.Frame(notebook)
        notebook.add(programs_frame, text="Programs")
        
        # Create top frame with buttons
        top_frame = ttk.Frame(programs_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Program", command=self.add_program)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Add search functionality
        search_label = ttk.Label(top_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.search_entry = ttk.Entry(top_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search_programs())
        
        search_button = ttk.Button(top_frame, text="Search", command=self.search_programs)
        search_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(top_frame, text="Clear", command=self.clear_search)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview
        columns = ("ID", "Name", "Sector", "Division", "Customer", "Mission Class", "Product-Material Combinations")
        self.programs_tree = ttk.Treeview(programs_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.programs_tree.heading(col, text=col)
            self.programs_tree.column(col, width=100)
        
        # Adjust column widths
        self.programs_tree.column("ID", width=60)
        self.programs_tree.column("Name", width=150)
        self.programs_tree.column("Product-Material Combinations", width=250)
        
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
    
    def search_programs(self):
        """Search programs based on the search term"""
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.clear_search()
            return
        
        # Clear existing items
        for item in self.programs_tree.get_children():
            self.programs_tree.delete(item)
        
        # Add matching programs to treeview
        for program in self.data["programs"]:
            # Check if search term is in any of the program attributes
            if (search_term in program["id"].lower() or
                search_term in program["name"].lower() or
                search_term in program.get("sector", "").lower() or
                search_term in program.get("division", "").lower() or
                search_term in program.get("customerName", "").lower() or
                search_term in program.get("missionClass", "").lower()):
                
                # Get product-material combinations
                product_material_info = ""
                if "productMaterialCombinations" in program and isinstance(program["productMaterialCombinations"], list):
                    combinations = []
                    for combo in program["productMaterialCombinations"]:
                        product_id = combo.get("productID", "")
                        material_id = combo.get("materialID", "")
                        
                        # Find product and material names
                        product_name = self.product_id_to_name.get(product_id, product_id)
                        material_name = self.material_id_to_name.get(material_id, material_id)
                        
                        combinations.append(f"{product_name} | {material_name}")
                    
                    product_material_info = "; ".join(combinations)
                
                values = (
                    program["id"],
                    program["name"],
                    program.get("sector", ""),
                    program.get("division", ""),
                    program.get("customerName", ""),
                    program.get("missionClass", ""),
                    product_material_info
                )
                self.programs_tree.insert("", tk.END, values=values)
            # Also search in product-material combinations
            elif "productMaterialCombinations" in program and isinstance(program["productMaterialCombinations"], list):
                for combo in program["productMaterialCombinations"]:
                    product_id = combo.get("productID", "")
                    material_id = combo.get("materialID", "")
                    part_name = combo.get("partName", "")
                    part_number = combo.get("partNumber", "")
                    
                    # Find product and material names
                    product_name = self.product_id_to_name.get(product_id, product_id)
                    material_name = self.material_id_to_name.get(material_id, material_id)
                    
                    # Check if search term is in any of the product-material attributes
                    if (search_term in product_id.lower() or
                        search_term in product_name.lower() or
                        search_term in material_id.lower() or
                        search_term in material_name.lower() or
                        search_term in part_name.lower() or
                        search_term in part_number.lower()):
                        
                        # Get all product-material combinations
                        combinations = []
                        for c in program["productMaterialCombinations"]:
                            p_id = c.get("productID", "")
                            m_id = c.get("materialID", "")
                            
                            # Find product and material names
                            p_name = self.product_id_to_name.get(p_id, p_id)
                            m_name = self.material_id_to_name.get(m_id, m_id)
                            
                            combinations.append(f"{p_name} | {m_name}")
                        
                        product_material_info = "; ".join(combinations)
                        
                        values = (
                            program["id"],
                            program["name"],
                            program.get("sector", ""),
                            program.get("division", ""),
                            program.get("customerName", ""),
                            program.get("missionClass", ""),
                            product_material_info
                        )
                        self.programs_tree.insert("", tk.END, values=values)
                        break  # Only add the program once
    
    def clear_search(self):
        """Clear search and show all programs"""
        self.search_entry.delete(0, tk.END)
        self.populate_programs_tree()
    
    def populate_programs_tree(self):
        """Populate the programs treeview with data"""
        # Clear existing items
        for item in self.programs_tree.get_children():
            self.programs_tree.delete(item)
        
        # Add programs to treeview
        for program in self.data["programs"]:
            # Get product-material combinations
            product_material_info = ""
            if "productMaterialCombinations" in program and isinstance(program["productMaterialCombinations"], list):
                combinations = []
                for combo in program["productMaterialCombinations"]:
                    product_id = combo.get("productID", "")
                    material_id = combo.get("materialID", "")
                    
                    # Find product and material names
                    product_name = self.product_id_to_name.get(product_id, product_id)
                    material_name = self.material_id_to_name.get(material_id, material_id)
                    
                    combinations.append(f"{product_name} | {material_name}")
                
                product_material_info = "; ".join(combinations)
            
            values = (
                program["id"],
                program["name"],
                program.get("sector", ""),
                program.get("division", ""),
                program.get("customerName", ""),
                program.get("missionClass", ""),
                product_material_info
            )
            self.programs_tree.insert("", tk.END, values=values)
    
    def get_next_program_id(self):
        """Generate the next available program ID"""
        # Get existing IDs
        existing_ids = []
        for program in self.data["programs"]:
            if "id" in program and program["id"].startswith("PRG"):
                try:
                    # Extract the numeric part
                    num_part = program["id"][3:]
                    if num_part.isdigit():
                        existing_ids.append(int(num_part))
                except (ValueError, IndexError):
                    pass
        
        # Find the next available number
        if not existing_ids:
            next_num = 1
        else:
            next_num = max(existing_ids) + 1
        
        return f"PRG{next_num}"
    
    def add_program(self):
        """Open a window to add a new program"""
        # Create a new window for adding a program
        add_window = tk.Toplevel(self.manager.root)
        add_window.title("Add Program")
        add_window.geometry("800x700")  # Increased size to accommodate new fields
        add_window.grab_set()  # Make window modal
        
        # Make window resizable
        add_window.resizable(True, True)
        
        # Configure window to be resizable
        add_window.grid_rowconfigure(0, weight=1)
        add_window.grid_columnconfigure(0, weight=1)
        
        # Create a canvas with scrollbars for the form
        canvas = tk.Canvas(add_window)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        # Add vertical scrollbar
        v_scrollbar = ttk.Scrollbar(add_window, orient="vertical", command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Create a frame inside the canvas for the form
        main_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Configure canvas scrolling
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def configure_canvas_window(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        main_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", configure_canvas_window)
        
        # Create form fields
        ttk.Label(main_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=self.get_next_program_id())
        id_entry = ttk.Entry(main_frame, textvariable=id_var, state="readonly")
        id_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Sector:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        sector_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=sector_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Division:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        division_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=division_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Customer Name:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        customer_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=customer_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Mission Class:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        mission_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=mission_var).grid(row=5, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Create a separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=6, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=10)
        
        # Create a frame for product-material system combinations
        products_frame = ttk.LabelFrame(main_frame, text="Products and Material Systems")
        products_frame.grid(row=7, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        products_frame.columnconfigure(0, weight=1)
        
        # Get product list for selection
        product_list = [f"{p['id']}: {p['name']}" for p in self.data.get("products", [])]
        
        # Create a frame for the product and material system selection
        selection_frame = ttk.Frame(products_frame)
        selection_frame.grid(row=0, column=0, sticky=tk.W+tk.E, padx=0, pady=2)
        
        # Create a label and combobox for product selection
        ttk.Label(selection_frame, text="Product:").pack(side=tk.LEFT, padx=2)
        product_var = tk.StringVar()
        products_combo = ttk.Combobox(selection_frame, textvariable=product_var, values=product_list, width=40)
        products_combo.pack(side=tk.LEFT, padx=2)
        
        # Create a label and combobox for material system selection
        ttk.Label(selection_frame, text="Material System:").pack(side=tk.LEFT, padx=2)
        material_var = tk.StringVar()
        materials_combo = ttk.Combobox(selection_frame, textvariable=material_var, width=30)
        materials_combo.pack(side=tk.LEFT, padx=2)
        
        # Function to update material systems based on selected product
        def update_material_systems(*args):
            selected_product = product_var.get()
            if selected_product:
                # Extract product ID from the selection
                product_id = selected_product.split(":")[0].strip()
                # Get associated material systems
                associated_materials = self.product_material_map.get(product_id, [])
                materials_combo['values'] = associated_materials
                if associated_materials:
                    materials_combo.current(0)  # Select the first material system
                else:
                    material_var.set("")  # Clear the selection if no materials are available
        
        # Bind the product selection to update material systems
        product_var.trace_add("write", update_material_systems)
        
        # Add search functionality to the product combobox
        def filter_products(event):
            search_term = products_combo.get().lower()
            filtered_products = [p for p in product_list if search_term in p.lower()]
            products_combo['values'] = filtered_products
        
        # Bind the KeyRelease event to filter products
        products_combo.bind('<KeyRelease>', filter_products)
        
        # Create a frame for part details
        parts_frame = ttk.LabelFrame(products_frame, text="Part Details")
        parts_frame.grid(row=1, column=0, sticky=tk.W+tk.E, padx=0, pady=5)
        parts_frame.columnconfigure(1, weight=1)
        
        # Part details fields
        ttk.Label(parts_frame, text="Part Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        part_name_var = tk.StringVar()
        ttk.Entry(parts_frame, textvariable=part_name_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Part Number:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        part_number_var = tk.StringVar()
        ttk.Entry(parts_frame, textvariable=part_number_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Lifetime Demand:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        lifetime_demand_var = tk.StringVar()
        ttk.Entry(parts_frame, textvariable=lifetime_demand_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Unit Cost Savings ($):").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        cost_savings_var = tk.StringVar()
        ttk.Entry(parts_frame, textvariable=cost_savings_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Unit Schedule Savings (days):").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        schedule_savings_var = tk.StringVar()
        ttk.Entry(parts_frame, textvariable=schedule_savings_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Need Date:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        need_date_var = tk.StringVar()
        date_entry = DateEntry(parts_frame, textvariable=need_date_var)
        date_entry.grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Adoption Status:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        adoption_status_var = tk.StringVar()
        adoption_status_combo = ttk.Combobox(parts_frame, textvariable=adoption_status_var, 
                                            values=["Targeting", "Developing", "Prototyping", "Baselined", 
                                                   "Production", "Complete", "Closed"])
        adoption_status_combo.grid(row=6, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Dictionary to store part details for each product-material combination
        combination_details = {}
        
        # Add buttons to add/remove product-material combinations
        buttons_frame = ttk.Frame(products_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=2)
        
        # Function to add a product-material combination to the listbox
        def add_combination():
            product = product_var.get()
            material = material_var.get()
            if product and material:
                # Extract IDs and names
                product_id = product.split(":")[0].strip()
                product_name = product.split(":", 1)[1].strip() if ":" in product else product
                
                material_id = material.split(":")[0].strip()
                material_name = material.split(":", 1)[1].strip() if ":" in material else material
                
                # Format for display: "Product Name | Material Name"
                display_text = f"{product_name} | {material_name}"
                # Format for storage: "Product ID | Material ID"
                storage_text = f"{product_id} | {material_id}"
                
                # Check if this combination already exists
                for i in range(products_listbox.size()):
                    item = products_listbox.get(i)
                    if display_text in item:
                        messagebox.showinfo("Info", "This product-material combination already exists.")
                        return
                
                # Get current date for status tracking
                import datetime
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                current_status = adoption_status_var.get()
                
                # Store part details for this combination
                combination_details[storage_text] = {
                    "partName": part_name_var.get(),
                    "partNumber": part_number_var.get(),
                    "lifetimeDemand": lifetime_demand_var.get(),
                    "unitCostSavings": cost_savings_var.get(),
                    "unitScheduleSavings": schedule_savings_var.get(),
                    "needDate": need_date_var.get(),
                    "adoptionStatus": current_status,
                    "statusHistory": [{
                        "status": current_status,
                        "date": current_date,
                        "previousStatus": ""
                    }]
                }
                
                # Add to listbox with display text and hidden storage text
                products_listbox.insert(tk.END, f"{display_text} [{storage_text}]")
                
                # Clear part details fields for next entry
                part_name_var.set("")
                part_number_var.set("")
                lifetime_demand_var.set("")
                cost_savings_var.set("")
                schedule_savings_var.set("")
                need_date_var.set("")
                adoption_status_var.set("")
        
        # Function to remove a product-material combination from the listbox
        def remove_combination():
            selected = products_listbox.curselection()
            if selected:
                item = products_listbox.get(selected)
                if "[" in item and "]" in item:
                    storage_text = item.split("[")[1].split("]")[0]
                    # Remove the combination details
                    if storage_text in combination_details:
                        del combination_details[storage_text]
                # Remove from listbox
                products_listbox.delete(selected)
        
        # Function to edit a product-material combination
        def edit_combination():
            selected = products_listbox.curselection()
            if selected:
                item = products_listbox.get(selected)
                if "[" in item and "]" in item:
                    storage_text = item.split("[")[1].split("]")[0]
                    # Load the combination details
                    if storage_text in combination_details:
                        details = combination_details[storage_text]
                        part_name_var.set(details.get("partName", ""))
                        part_number_var.set(details.get("partNumber", ""))
                        lifetime_demand_var.set(details.get("lifetimeDemand", ""))
                        cost_savings_var.set(details.get("unitCostSavings", ""))
                        schedule_savings_var.set(details.get("unitScheduleSavings", ""))
                        need_date_var.set(details.get("needDate", ""))
                        adoption_status_var.set(details.get("adoptionStatus", ""))
                        
                        # Extract product and material IDs from storage_text
                        product_id, material_id = storage_text.split(" | ")
                        
                        # Find and select the product in the dropdown
                        for i, product in enumerate(products_combo['values']):
                            if product.startswith(f"{product_id}:"):
                                products_combo.current(i)
                                break
                        
                        # Update material systems based on selected product
                        update_material_systems()
                        
                        # Find and select the material in the dropdown
                        for i, material in enumerate(materials_combo['values']):
                            if material.startswith(f"{material_id}:"):
                                materials_combo.current(i)
                                break
        
        # Function to update a product-material combination
        def update_combination():
            selected = products_listbox.curselection()
            if selected:
                item = products_listbox.get(selected)
                if "[" in item and "]" in item:
                    storage_text = item.split("[")[1].split("]")[0]
                    # Update the combination details
                    if storage_text in combination_details:
                        # Get current date for status tracking
                        import datetime
                        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                        new_status = adoption_status_var.get()
                        previous_status = combination_details[storage_text].get("adoptionStatus", "")
                        
                        # Only add to history if status has changed
                        status_history = combination_details[storage_text].get("statusHistory", [])
                        if new_status != previous_status:
                            status_history.append({
                                "status": new_status,
                                "date": current_date,
                                "previousStatus": previous_status
                            })
                        
                        combination_details[storage_text] = {
                            "partName": part_name_var.get(),
                            "partNumber": part_number_var.get(),
                            "lifetimeDemand": lifetime_demand_var.get(),
                            "unitCostSavings": cost_savings_var.get(),
                            "unitScheduleSavings": schedule_savings_var.get(),
                            "needDate": need_date_var.get(),
                            "adoptionStatus": new_status,
                            "statusHistory": status_history
                        }
                        messagebox.showinfo("Info", "Combination details updated.")
        
        # Create a listbox to display selected product-material combinations
        combinations_frame = ttk.LabelFrame(products_frame, text="Selected Combinations")
        combinations_frame.grid(row=3, column=0, sticky=tk.W+tk.E, padx=0, pady=5)
        combinations_frame.columnconfigure(0, weight=1)
        
        products_listbox = tk.Listbox(combinations_frame, height=6)
        products_listbox.grid(row=0, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Add a scrollbar to the listbox
        products_scrollbar = ttk.Scrollbar(combinations_frame, orient=tk.VERTICAL, command=products_listbox.yview)
        products_scrollbar.grid(row=0, column=1, sticky=tk.NS, pady=5)
        products_listbox.configure(yscrollcommand=products_scrollbar.set)
        
        # Bind double-click event to edit combination
        products_listbox.bind("<Double-1>", lambda event: edit_combination())
        
        # Load existing product-material combinations
        if "productMaterialCombinations" in program and isinstance(program["productMaterialCombinations"], list):
            for combo in program["productMaterialCombinations"]:
                product_id = combo.get("productID", "")
                material_id = combo.get("materialID", "")
                
                # Find product and material names
                product_name = self.product_id_to_name.get(product_id, product_id)
                material_name = self.material_id_to_name.get(material_id, material_id)
                
                # Format for display and storage
                display_text = f"{product_name} | {material_name}"
                storage_text = f"{product_id} | {material_id}"
                
                # Store part details for this combination
                status_history = combo.get("statusHistory", [])
                if not status_history and combo.get("adoptionStatus"):
                    # Create initial status history if it doesn't exist
                    import datetime
                    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    status_history = [{
                        "status": combo.get("adoptionStatus", ""),
                        "date": current_date,
                        "previousStatus": ""
                    }]
                
                combination_details[storage_text] = {
                    "partName": combo.get("partName", ""),
                    "partNumber": combo.get("partNumber", ""),
                    "lifetimeDemand": combo.get("lifetimeDemand", ""),
                    "unitCostSavings": combo.get("unitCostSavings", ""),
                    "unitScheduleSavings": combo.get("unitScheduleSavings", ""),
                    "needDate": combo.get("needDate", ""),
                    "adoptionStatus": combo.get("adoptionStatus", ""),
                    "statusHistory": status_history
                }
                
                # Add to listbox
                products_listbox.insert(tk.END, f"{display_text} [{storage_text}]")
        
        # Add buttons for adding, removing, editing, and updating combinations
        ttk.Button(buttons_frame, text="Add Combination", command=add_combination).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Remove Combination", command=remove_combination).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Edit Combination", command=edit_combination).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Update Combination", command=update_combination).pack(side=tk.LEFT, padx=5)
        
        # Create a frame for buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        # Save button
        def save_program():
            # Validate required fields
            if not name_var.get():
                messagebox.showerror("Error", "Name is required")
                return
            
            # Get selected product-material combinations
            product_material_combinations = []
            for i in range(products_listbox.size()):
                item = products_listbox.get(i)
                if "[" in item and "]" in item:
                    storage_text = item.split("[")[1].split("]")[0]
                    product_id, material_id = storage_text.split(" | ")
                    
                    # Get the details for this combination
                    details = combination_details.get(storage_text, {})
                    
                    product_material_combinations.append({
                        "productID": product_id,
                        "materialID": material_id,
                        "partName": details.get("partName", ""),
                        "partNumber": details.get("partNumber", ""),
                        "lifetimeDemand": details.get("lifetimeDemand", ""),
                        "unitCostSavings": details.get("unitCostSavings", ""),
                        "unitScheduleSavings": details.get("unitScheduleSavings", ""),
                        "needDate": details.get("needDate", ""),
                        "adoptionStatus": details.get("adoptionStatus", ""),
                        "statusHistory": details.get("statusHistory", [])
                    })
            
            # Create new program
            new_program = {
                "id": id_var.get(),
                "name": name_var.get(),
                "sector": sector_var.get(),
                "division": division_var.get(),
                "customerName": customer_var.get(),
                "missionClass": mission_var.get(),
                "productMaterialCombinations": product_material_combinations
            }
            
            # Add to data
            self.data["programs"].append(new_program)
            
            # Refresh treeview
            self.populate_programs_tree()
            
            # Save data to file
            self.manager.save_data()
            
            # Close window
            add_window.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_program).pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def edit_program(self, event):
        """Open a window to edit the selected program"""
        # Get selected item
        selected_item = self.programs_tree.selection()
        if not selected_item:
            return
        
        # Get program data
        program_id = self.programs_tree.item(selected_item, "values")[0]
        program = None
        for p in self.data["programs"]:
            if p["id"] == program_id:
                program = p
                break
        
        if not program:
            return
        
        # Create a new window for editing the program
        edit_window = tk.Toplevel(self.manager.root)
        edit_window.title("Edit Program")
        edit_window.geometry("800x700")  # Increased size to accommodate new fields
        edit_window.grab_set()  # Make window modal
        
        # Make window resizable
        edit_window.resizable(True, True)
        
        # Configure window to be resizable
        edit_window.grid_rowconfigure(0, weight=1)
        edit_window.grid_columnconfigure(0, weight=1)
        
        # Create a canvas with scrollbars for the form
        canvas = tk.Canvas(edit_window)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        # Add vertical scrollbar
        v_scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Create a frame inside the canvas for the form
        main_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Configure canvas scrolling
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def configure_canvas_window(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        main_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", configure_canvas_window)
        
        # Create form fields
        ttk.Label(main_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=program["id"])
        id_entry = ttk.Entry(main_frame, textvariable=id_var, state="readonly")
        id_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=program.get("name", ""))
        ttk.Entry(main_frame, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Sector:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        sector_var = tk.StringVar(value=program.get("sector", ""))
        ttk.Entry(main_frame, textvariable=sector_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Division:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        division_var = tk.StringVar(value=program.get("division", ""))
        ttk.Entry(main_frame, textvariable=division_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Customer Name:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        customer_var = tk.StringVar(value=program.get("customerName", ""))
        ttk.Entry(main_frame, textvariable=customer_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Mission Class:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        mission_var = tk.StringVar(value=program.get("missionClass", ""))
        ttk.Entry(main_frame, textvariable=mission_var).grid(row=5, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Create a separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=6, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=10)
        
        # Create a frame for product-material system combinations
        products_frame = ttk.LabelFrame(main_frame, text="Products and Material Systems")
        products_frame.grid(row=7, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        products_frame.columnconfigure(0, weight=1)
        
        # Get product list for selection
        product_list = [f"{p['id']}: {p['name']}" for p in self.data.get("products", [])]
        
        # Create a frame for the product and material system selection
        selection_frame = ttk.Frame(products_frame)
        selection_frame.grid(row=0, column=0, sticky=tk.W+tk.E, padx=0, pady=2)
        
        # Create a label and combobox for product selection
        ttk.Label(selection_frame, text="Product:").pack(side=tk.LEFT, padx=2)
        product_var = tk.StringVar()
        products_combo = ttk.Combobox(selection_frame, textvariable=product_var, values=product_list, width=40)
        products_combo.pack(side=tk.LEFT, padx=2)
        
        # Create a label and combobox for material system selection
        ttk.Label(selection_frame, text="Material System:").pack(side=tk.LEFT, padx=2)
        material_var = tk.StringVar()
        materials_combo = ttk.Combobox(selection_frame, textvariable=material_var, width=30)
        materials_combo.pack(side=tk.LEFT, padx=2)
        
        # Function to update material systems based on selected product
        def update_material_systems(*args):
            selected_product = product_var.get()
            if selected_product:
                # Extract product ID from the selection
                product_id = selected_product.split(":")[0].strip()
                # Get associated material systems
                associated_materials = self.product_material_map.get(product_id, [])
                materials_combo['values'] = associated_materials
                if associated_materials:
                    materials_combo.current(0)  # Select the first material system
                else:
                    material_var.set("")  # Clear the selection if no materials are available
        
        # Bind the product selection to update material systems
        product_var.trace_add("write", update_material_systems)
        
        # Add search functionality to the product combobox
        def filter_products(event):
            search_term = products_combo.get().lower()
            filtered_products = [p for p in product_list if search_term in p.lower()]
            products_combo['values'] = filtered_products
        
        # Bind the KeyRelease event to filter products
        products_combo.bind('<KeyRelease>', filter_products)
        
        # Create a frame for part details
        parts_frame = ttk.LabelFrame(products_frame, text="Part Details")
        parts_frame.grid(row=1, column=0, sticky=tk.W+tk.E, padx=0, pady=5)
        parts_frame.columnconfigure(1, weight=1)
        
        # Part details fields
        ttk.Label(parts_frame, text="Part Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        part_name_var = tk.StringVar()
        ttk.Entry(parts_frame, textvariable=part_name_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Part Number:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        part_number_var = tk.StringVar()
        ttk.Entry(parts_frame, textvariable=part_number_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Lifetime Demand:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        lifetime_demand_var = tk.StringVar()
        ttk.Entry(parts_frame, textvariable=lifetime_demand_var).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Unit Cost Savings ($):").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        cost_savings_var = tk.StringVar()
        ttk.Entry(parts_frame, textvariable=cost_savings_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Unit Schedule Savings (days):").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        schedule_savings_var = tk.StringVar()
        ttk.Entry(parts_frame, textvariable=schedule_savings_var).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Need Date:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        need_date_var = tk.StringVar()
        date_entry = DateEntry(parts_frame, textvariable=need_date_var)
        date_entry.grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
        
        ttk.Label(parts_frame, text="Adoption Status:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        adoption_status_var = tk.StringVar()
        adoption_status_combo = ttk.Combobox(parts_frame, textvariable=adoption_status_var, 
                                            values=["Targeting", "Developing", "Prototyping", "Baselined", 
                                                   "Production", "Complete", "Closed"])
        adoption_status_combo.grid(row=6, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Dictionary to store part details for each product-material combination
        combination_details = {}
        
        # Add buttons to add/remove product-material combinations
        buttons_frame = ttk.Frame(products_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=2)
        
        # Function to add a product-material combination to the listbox
        def add_combination():
            product = product_var.get()
            material = material_var.get()
            if product and material:
                # Extract IDs and names
                product_id = product.split(":")[0].strip()
                product_name = product.split(":", 1)[1].strip() if ":" in product else product
                
                material_id = material.split(":")[0].strip()
                material_name = material.split(":", 1)[1].strip() if ":" in material else material
                
                # Format for display: "Product Name | Material Name"
                display_text = f"{product_name} | {material_name}"
                # Format for storage: "Product ID | Material ID"
                storage_text = f"{product_id} | {material_id}"
                
                # Check if this combination already exists
                for i in range(products_listbox.size()):
                    item = products_listbox.get(i)
                    if display_text in item:
                        messagebox.showinfo("Info", "This product-material combination already exists.")
                        return
                
                # Get current date for status tracking
                import datetime
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                current_status = adoption_status_var.get()
                
                # Store part details for this combination
                combination_details[storage_text] = {
                    "partName": part_name_var.get(),
                    "partNumber": part_number_var.get(),
                    "lifetimeDemand": lifetime_demand_var.get(),
                    "unitCostSavings": cost_savings_var.get(),
                    "unitScheduleSavings": schedule_savings_var.get(),
                    "needDate": need_date_var.get(),
                    "adoptionStatus": current_status,
                    "statusHistory": [{
                        "status": current_status,
                        "date": current_date,
                        "previousStatus": ""
                    }]
                }
                
                # Add to listbox with display text and hidden storage text
                products_listbox.insert(tk.END, f"{display_text} [{storage_text}]")
                
                # Clear part details fields for next entry
                part_name_var.set("")
                part_number_var.set("")
                lifetime_demand_var.set("")
                cost_savings_var.set("")
                schedule_savings_var.set("")
                need_date_var.set("")
                adoption_status_var.set("")
        
        # Function to remove a product-material combination from the listbox
        def remove_combination():
            selected = products_listbox.curselection()
            if selected:
                item = products_listbox.get(selected)
                if "[" in item and "]" in item:
                    storage_text = item.split("[")[1].split("]")[0]
                    # Remove the combination details
                    if storage_text in combination_details:
                        del combination_details[storage_text]
                # Remove from listbox
                products_listbox.delete(selected)
        
        # Function to edit a product-material combination
        def edit_combination():
            selected = products_listbox.curselection()
            if selected:
                item = products_listbox.get(selected)
                if "[" in item and "]" in item:
                    storage_text = item.split("[")[1].split("]")[0]
                    # Load the combination details
                    if storage_text in combination_details:
                        details = combination_details[storage_text]
                        part_name_var.set(details.get("partName", ""))
                        part_number_var.set(details.get("partNumber", ""))
                        lifetime_demand_var.set(details.get("lifetimeDemand", ""))
                        cost_savings_var.set(details.get("unitCostSavings", ""))
                        schedule_savings_var.set(details.get("unitScheduleSavings", ""))
                        need_date_var.set(details.get("needDate", ""))
                        adoption_status_var.set(details.get("adoptionStatus", ""))
                        
                        # Extract product and material IDs from storage_text
                        product_id, material_id = storage_text.split(" | ")
                        
                        # Find and select the product in the dropdown
                        for i, product in enumerate(products_combo['values']):
                            if product.startswith(f"{product_id}:"):
                                products_combo.current(i)
                                break
                        
                        # Update material systems based on selected product
                        update_material_systems()
                        
                        # Find and select the material in the dropdown
                        for i, material in enumerate(materials_combo['values']):
                            if material.startswith(f"{material_id}:"):
                                materials_combo.current(i)
                                break
        
        # Function to update a product-material combination
        def update_combination():
            selected = products_listbox.curselection()
            if selected:
                item = products_listbox.get(selected)
                if "[" in item and "]" in item:
                    storage_text = item.split("[")[1].split("]")[0]
                    # Update the combination details
                    if storage_text in combination_details:
                        # Get current date for status tracking
                        import datetime
                        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                        new_status = adoption_status_var.get()
                        previous_status = combination_details[storage_text].get("adoptionStatus", "")
                        
                        # Only add to history if status has changed
                        status_history = combination_details[storage_text].get("statusHistory", [])
                        if new_status != previous_status:
                            status_history.append({
                                "status": new_status,
                                "date": current_date,
                                "previousStatus": previous_status
                            })
                        
                        combination_details[storage_text] = {
                            "partName": part_name_var.get(),
                            "partNumber": part_number_var.get(),
                            "lifetimeDemand": lifetime_demand_var.get(),
                            "unitCostSavings": cost_savings_var.get(),
                            "unitScheduleSavings": schedule_savings_var.get(),
                            "needDate": need_date_var.get(),
                            "adoptionStatus": new_status,
                            "statusHistory": status_history
                        }
                        messagebox.showinfo("Info", "Combination details updated.")
        
        # Create a listbox to display selected product-material combinations
        combinations_frame = ttk.LabelFrame(products_frame, text="Selected Combinations")
        combinations_frame.grid(row=3, column=0, sticky=tk.W+tk.E, padx=0, pady=5)
        combinations_frame.columnconfigure(0, weight=1)
        
        products_listbox = tk.Listbox(combinations_frame, height=6)
        products_listbox.grid(row=0, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Add a scrollbar to the listbox
        products_scrollbar = ttk.Scrollbar(combinations_frame, orient=tk.VERTICAL, command=products_listbox.yview)
        products_scrollbar.grid(row=0, column=1, sticky=tk.NS, pady=5)
        products_listbox.configure(yscrollcommand=products_scrollbar.set)
        
        # Bind double-click event to edit combination
        products_listbox.bind("<Double-1>", lambda event: edit_combination())
        
        # Load existing product-material combinations
        if "productMaterialCombinations" in program and isinstance(program["productMaterialCombinations"], list):
            for combo in program["productMaterialCombinations"]:
                product_id = combo.get("productID", "")
                material_id = combo.get("materialID", "")
                
                # Find product and material names
                product_name = self.product_id_to_name.get(product_id, product_id)
                material_name = self.material_id_to_name.get(material_id, material_id)
                
                # Format for display and storage
                display_text = f"{product_name} | {material_name}"
                storage_text = f"{product_id} | {material_id}"
                
                # Store part details for this combination
                status_history = combo.get("statusHistory", [])
                if not status_history and combo.get("adoptionStatus"):
                    # Create initial status history if it doesn't exist
                    import datetime
                    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    status_history = [{
                        "status": combo.get("adoptionStatus", ""),
                        "date": current_date,
                        "previousStatus": ""
                    }]
                
                combination_details[storage_text] = {
                    "partName": combo.get("partName", ""),
                    "partNumber": combo.get("partNumber", ""),
                    "lifetimeDemand": combo.get("lifetimeDemand", ""),
                    "unitCostSavings": combo.get("unitCostSavings", ""),
                    "unitScheduleSavings": combo.get("unitScheduleSavings", ""),
                    "needDate": combo.get("needDate", ""),
                    "adoptionStatus": combo.get("adoptionStatus", ""),
                    "statusHistory": status_history
                }
                
                # Add to listbox
                products_listbox.insert(tk.END, f"{display_text} [{storage_text}]")
        
        # Add buttons for adding, removing, editing, and updating combinations
        ttk.Button(buttons_frame, text="Add Combination", command=add_combination).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Remove Combination", command=remove_combination).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Edit Combination", command=edit_combination).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Update Combination", command=update_combination).pack(side=tk.LEFT, padx=5)
        
        # Create a frame for buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        # Save button
        def save_program():
            # Validate required fields
            if not name_var.get():
                messagebox.showerror("Error", "Name is required")
                return
            
            # Get selected product-material combinations
            product_material_combinations = []
            for i in range(products_listbox.size()):
                item = products_listbox.get(i)
                if "[" in item and "]" in item:
                    storage_text = item.split("[")[1].split("]")[0]
                    product_id, material_id = storage_text.split(" | ")
                    
                    # Get the details for this combination
                    details = combination_details.get(storage_text, {})
                    
                    product_material_combinations.append({
                        "productID": product_id,
                        "materialID": material_id,
                        "partName": details.get("partName", ""),
                        "partNumber": details.get("partNumber", ""),
                        "lifetimeDemand": details.get("lifetimeDemand", ""),
                        "unitCostSavings": details.get("unitCostSavings", ""),
                        "unitScheduleSavings": details.get("unitScheduleSavings", ""),
                        "needDate": details.get("needDate", ""),
                        "adoptionStatus": details.get("adoptionStatus", ""),
                        "statusHistory": details.get("statusHistory", [])
                    })
            
            # Update program
            program["name"] = name_var.get()
            program["sector"] = sector_var.get()
            program["division"] = division_var.get()
            program["customerName"] = customer_var.get()
            program["missionClass"] = mission_var.get()
            program["productMaterialCombinations"] = product_material_combinations
            
            # Refresh treeview
            self.populate_programs_tree()
            
            # Save data to file
            self.manager.save_data()
            
            # Close window
            edit_window.destroy()
        
        # Add Delete button
        def delete_program():
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete program {program['name']}?"):
                # Remove from data
                self.data["programs"].remove(program)
                
                # Refresh treeview
                self.populate_programs_tree()
                
                # Save data to file
                self.manager.save_data()
                
                # Close window
                edit_window.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_program).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_program).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5) 