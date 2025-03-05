import tkinter as tk
from tkinter import ttk
from ..date_entry import DateEntry
import platform

class FundingForm:
    """Form for adding or editing a funding opportunity"""
    
    def __init__(self, model, opportunity, is_new=False):
        self.model = model
        self.opportunity = opportunity
        self.is_new = is_new
        self.pursuit_entries = []
        
        # Get product list for related products selection
        self.product_list = [f"{p['id']}: {p['name']}" for p in self.model.data.get("products", [])]
        
        # Create product ID to name mapping
        self.product_id_to_name = {}
        for product in self.model.data.get("products", []):
            if "id" in product and "name" in product:
                self.product_id_to_name[product["id"]] = product["name"]
        
        # Get material systems list
        self.material_systems_list = [f"{ms['id']}: {ms['name']}" for ms in self.model.data.get("materialSystems", [])]
        
        # Create material system ID to name mapping
        self.material_id_to_name = {}
        for ms in self.model.data.get("materialSystems", []):
            if "id" in ms and "name" in ms:
                self.material_id_to_name[ms["id"]] = ms["name"]
        
        # Create a mapping of product IDs to their associated material systems
        self.product_material_map = {}
        for product in self.model.data.get("products", []):
            product_id = product["id"]
            material_systems = []
            if "materialSystems" in product and isinstance(product["materialSystems"], list):
                for ms_entry in product["materialSystems"]:
                    if "materialID" in ms_entry:
                        # Find the material system name
                        ms_id = ms_entry["materialID"]
                        for ms in self.model.data.get("materialSystems", []):
                            if ms["id"] == ms_id:
                                material_systems.append(f"{ms['id']}: {ms.get('name', '')}")
                                break
            self.product_material_map[product_id] = material_systems
        
        # Create the form window
        self.window = tk.Toplevel(self.model.manager.root)
        self.window.title(f"{'Add' if is_new else 'Edit'} Funding Opportunity")
        self.window.geometry("1000x900")  # Taller window size
        self.window.grab_set()  # Make window modal
        
        # Make window resizable
        self.window.resizable(True, True)
        
        # Configure window to be resizable
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        # Bind mouse wheel events directly to the window
        system = platform.system()
        if system == "Windows":
            self.window.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        else:
            self.window.bind_all("<Button-4>", self._on_mousewheel_linux_up)
            self.window.bind_all("<Button-5>", self._on_mousewheel_linux_down)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Create a canvas with scrollbars for the notebook
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Add vertical scrollbar
        self.v_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
        
        # Add horizontal scrollbar
        self.h_scrollbar = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set)
        
        # Create a frame inside the canvas to hold the notebook
        self.notebook_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.notebook_frame, anchor="nw")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Configure canvas scrolling
        self.notebook_frame.bind("<Configure>", self._configure_canvas)
        self.canvas.bind("<Configure>", self._configure_canvas_window)
        
        # Setup mouse wheel scrolling based on platform
        self._setup_mousewheel_scrolling()
        
        # Create tabs
        self.create_basic_info_tab()
        self.create_pursuits_tab()
        
        # Create a frame for buttons at the bottom of the window
        self.button_frame = ttk.Frame(self.window)
        self.button_frame.grid(row=1, column=0, sticky="se", padx=10, pady=10)
        
        # Create a prominent save button
        save_button = ttk.Button(self.button_frame, text="Save", command=self.save, width=10)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Add Delete button if editing an existing opportunity
        if not self.is_new:
            delete_button = ttk.Button(self.button_frame, text="Delete", command=self.delete, width=10)
            delete_button.pack(side=tk.LEFT, padx=5)
        
        # Add Cancel button
        cancel_button = ttk.Button(self.button_frame, text="Cancel", command=self.window.destroy, width=10)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def _setup_mousewheel_scrolling(self):
        """Setup mouse wheel scrolling based on the platform"""
        # Determine the OS
        system = platform.system()
        
        # Bind mouse wheel events to the window, canvas, and notebook
        if system == "Windows":
            # Windows uses MouseWheel event
            self.window.bind("<MouseWheel>", self._on_mousewheel_windows)
            self.canvas.bind("<MouseWheel>", self._on_mousewheel_windows)
            self.notebook_frame.bind("<MouseWheel>", self._on_mousewheel_windows)
            self.notebook.bind("<MouseWheel>", self._on_mousewheel_windows)
        else:
            # Linux/Mac use Button-4 and Button-5 for scroll up/down
            self.window.bind("<Button-4>", self._on_mousewheel_linux_up)
            self.window.bind("<Button-5>", self._on_mousewheel_linux_down)
            self.canvas.bind("<Button-4>", self._on_mousewheel_linux_up)
            self.canvas.bind("<Button-5>", self._on_mousewheel_linux_down)
            self.notebook_frame.bind("<Button-4>", self._on_mousewheel_linux_up)
            self.notebook_frame.bind("<Button-5>", self._on_mousewheel_linux_down)
            self.notebook.bind("<Button-4>", self._on_mousewheel_linux_up)
            self.notebook.bind("<Button-5>", self._on_mousewheel_linux_down)
        
        # Bind to all widgets in the window
        self._bind_mousewheel_to_all_children(self.window)
    
    def _bind_mousewheel_to_all_children(self, widget):
        """Recursively bind mouse wheel events to all children of a widget"""
        system = platform.system()
        
        if system == "Windows":
            widget.bind("<MouseWheel>", self._on_mousewheel_windows)
        else:
            widget.bind("<Button-4>", self._on_mousewheel_linux_up)
            widget.bind("<Button-5>", self._on_mousewheel_linux_down)
        
        # Recursively bind to all children
        for child in widget.winfo_children():
            self._bind_mousewheel_to_all_children(child)
    
    def _on_mousewheel_windows(self, event):
        """Handle mouse wheel scrolling on Windows"""
        # Windows: event.delta is positive when scrolling up, negative when scrolling down
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # Prevent the event from propagating
        return "break"
    
    def _on_mousewheel_linux_up(self, event):
        """Handle mouse wheel scrolling up on Linux"""
        self.canvas.yview_scroll(-1, "units")
        # Prevent the event from propagating
        return "break"
    
    def _on_mousewheel_linux_down(self, event):
        """Handle mouse wheel scrolling down on Linux"""
        self.canvas.yview_scroll(1, "units")
        # Prevent the event from propagating
        return "break"
    
    def _configure_canvas(self, event):
        """Configure the canvas scrollregion when the notebook frame changes size"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _configure_canvas_window(self, event):
        """Resize the canvas window when the canvas changes size"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def create_basic_info_tab(self):
        """Create the Basic Information tab"""
        basic_info_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_info_frame, text="Basic Information")
        
        # Configure grid
        for i in range(10):
            basic_info_frame.grid_columnconfigure(1, weight=1)
        
        # Create form fields
        row = 0
        
        ttk.Label(basic_info_frame, text="ID:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.id_var = tk.StringVar(value=self.opportunity.get("id", ""))
        id_entry = ttk.Entry(basic_info_frame, textvariable=self.id_var)
        id_entry.grid(row=row, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        if not self.is_new:
            id_entry.configure(state="readonly")
        row += 1
        
        ttk.Label(basic_info_frame, text="Announcement Name:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar(value=self.opportunity.get("announcementName", ""))
        ttk.Entry(basic_info_frame, textvariable=self.name_var).grid(row=row, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        row += 1
        
        ttk.Label(basic_info_frame, text="Type:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.pursuit_type_var = tk.StringVar(value=self.opportunity.get("pursuitType", ""))
        ttk.Combobox(basic_info_frame, textvariable=self.pursuit_type_var, 
                    values=["CRAD - RFI", "CRAD - RFP", "CRAD - RFWP", "BAA", "Follow On", "Shaping", "Division IRAD", "Sector IRAD"]).grid(row=row, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        row += 1
        
        ttk.Label(basic_info_frame, text="Status:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.status_var = tk.StringVar(value=self.opportunity.get("status", ""))
        ttk.Combobox(basic_info_frame, textvariable=self.status_var, 
                    values=["Considering", "Pursuing", "Closed", "Awarded", "Reshaping"]).grid(row=row, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        row += 1
        
        ttk.Label(basic_info_frame, text="Close Date:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.close_date_var = tk.StringVar(value=self.opportunity.get("closeDate", ""))
        
        # Debug the date value
        close_date_value = self.opportunity.get("closeDate", "")
        print(f"Loading close date: '{close_date_value}'")
        
        date_entry = DateEntry(basic_info_frame, textvariable=self.close_date_var, initial_date=close_date_value)
        date_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        row += 1
        
        ttk.Label(basic_info_frame, text="Period of Performance:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.period_of_performance_var = tk.StringVar(value=self.opportunity.get("periodOfPerformance", ""))
        ttk.Entry(basic_info_frame, textvariable=self.period_of_performance_var).grid(row=row, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        row += 1
        
        ttk.Label(basic_info_frame, text="Solicitation Number:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.solicitation_var = tk.StringVar(value=self.opportunity.get("solicitationNumber", ""))
        ttk.Entry(basic_info_frame, textvariable=self.solicitation_var).grid(row=row, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        row += 1
        
        ttk.Label(basic_info_frame, text="Funding Amount:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.amount_var = tk.StringVar()
        
        # Create a frame for the dollar sign and entry
        amount_frame = ttk.Frame(basic_info_frame)
        amount_frame.grid(row=row, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Add dollar sign label
        ttk.Label(amount_frame, text="$").pack(side=tk.LEFT)
        
        # Set the amount value, removing any existing dollar sign
        amount_value = self.opportunity.get("fundingAmount", "")
        if isinstance(amount_value, str) and amount_value.startswith("$"):
            amount_value = amount_value[1:]
        self.amount_var.set(amount_value)
        
        ttk.Entry(amount_frame, textvariable=self.amount_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        row += 1
        
        ttk.Label(basic_info_frame, text="Cost Share Percentage:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.cost_share_var = tk.StringVar()
        
        # Create a frame for the percentage
        cost_share_frame = ttk.Frame(basic_info_frame)
        cost_share_frame.grid(row=row, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Set the cost share value, removing any existing percentage sign
        cost_share_value = self.opportunity.get("costSharePercentage", "")
        if isinstance(cost_share_value, str) and cost_share_value.endswith("%"):
            cost_share_value = cost_share_value[:-1]
        self.cost_share_var.set(cost_share_value)
        
        # Add a validator for numeric values
        vcmd = (self.window.register(self._validate_numeric), '%P')
        ttk.Entry(cost_share_frame, textvariable=self.cost_share_var, validate="key", validatecommand=vcmd).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add percentage sign label
        ttk.Label(cost_share_frame, text="%").pack(side=tk.LEFT)
        row += 1
        
        ttk.Label(basic_info_frame, text="Customer:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        self.customer_var = tk.StringVar(value=self.opportunity.get("customer", ""))
        ttk.Entry(basic_info_frame, textvariable=self.customer_var).grid(row=row, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        row += 1
    
    def create_pursuits_tab(self):
        """Create the Pursuits tab"""
        self.pursuits_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pursuits_frame, text="Pursuits")
        
        # Create a canvas with scrollbar for pursuits
        pursuits_canvas_frame = ttk.Frame(self.pursuits_frame)
        pursuits_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid
        pursuits_canvas_frame.grid_columnconfigure(0, weight=1)
        pursuits_canvas_frame.grid_rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        self.pursuits_canvas = tk.Canvas(pursuits_canvas_frame, height=700)  # Set a taller canvas height
        self.pursuits_canvas.grid(row=0, column=0, sticky="nsew")
        
        pursuits_scrollbar = ttk.Scrollbar(pursuits_canvas_frame, orient=tk.VERTICAL, command=self.pursuits_canvas.yview)
        pursuits_scrollbar.grid(row=0, column=1, sticky="ns")
        self.pursuits_canvas.configure(yscrollcommand=pursuits_scrollbar.set)
        
        # Create a frame inside the canvas for pursuits
        self.pursuits_content_frame = ttk.Frame(self.pursuits_canvas)
        self.pursuits_canvas_window = self.pursuits_canvas.create_window((0, 0), window=self.pursuits_content_frame, anchor="nw", width=self.pursuits_canvas.winfo_width())
        
        # Configure canvas scrolling
        self.pursuits_content_frame.bind("<Configure>", self._configure_pursuits_canvas)
        self.pursuits_canvas.bind("<Configure>", self._configure_pursuits_canvas_window)
        
        # Add button to add a new pursuit
        add_pursuit_button = ttk.Button(self.pursuits_frame, text="Add Pursuit", command=self.add_pursuit)
        add_pursuit_button.pack(side=tk.BOTTOM, pady=10)
        
        # Load existing pursuits
        if "pursuits" in self.opportunity and isinstance(self.opportunity["pursuits"], list):
            for pursuit in self.opportunity["pursuits"]:
                self.add_pursuit(pursuit)
    
    def _configure_pursuits_canvas(self, event):
        """Configure the pursuits canvas scrollregion"""
        self.pursuits_canvas.configure(scrollregion=self.pursuits_canvas.bbox("all"))
    
    def _configure_pursuits_canvas_window(self, event):
        """Resize the pursuits canvas window"""
        self.pursuits_canvas.itemconfig(self.pursuits_canvas_window, width=event.width)
    
    def generate_pursuit_id(self):
        """Generate a unique pursuit ID"""
        # Get all existing pursuit IDs
        existing_ids = []
        for entry in self.pursuit_entries:
            pursuit_id = entry["pursuitID"].get()
            if pursuit_id and pursuit_id.startswith("PUR"):
                existing_ids.append(pursuit_id)
        
        # Also check pursuits in the opportunity
        if "pursuits" in self.opportunity and isinstance(self.opportunity["pursuits"], list):
            for pursuit in self.opportunity["pursuits"]:
                if "pursuitID" in pursuit and pursuit["pursuitID"].startswith("PUR"):
                    existing_ids.append(pursuit["pursuitID"])
        
        # Find the highest numeric part
        highest_num = 0
        for id_str in existing_ids:
            try:
                num = int(id_str[3:])
                highest_num = max(highest_num, num)
            except ValueError:
                pass
        
        # Generate the next ID
        next_id = f"PUR{highest_num + 1}"
        return next_id
    
    def add_pursuit(self, pursuit=None):
        """Add a pursuit entry to the pursuits tab"""
        # Create a frame for this pursuit with a larger size
        pursuit_number = len(self.pursuit_entries) + 1
        pursuit_frame = ttk.LabelFrame(self.pursuits_content_frame, text=f"Pursuit {pursuit_number}")
        pursuit_frame.pack(fill=tk.X, expand=True, padx=5, pady=15)
        
        # Configure grid
        for i in range(2):
            pursuit_frame.grid_columnconfigure(i, weight=1)
        
        # Generate a new pursuit ID if not provided
        if pursuit and "pursuitID" in pursuit and pursuit["pursuitID"]:
            pursuit_id = pursuit["pursuitID"]
        else:
            pursuit_id = self.generate_pursuit_id()
        
        # Create variables for pursuit fields
        pursuit_id_var = tk.StringVar(value=pursuit_id)
        pursuit_name_var = tk.StringVar(value=pursuit.get("pursuitName", "") if pursuit else "")
        
        # Get the submission date value and prepare it for display
        submission_date_value = pursuit.get("targetedSubmissionDate", "") if pursuit else ""
        print(f"Loading pursuit {pursuit_id} submission date: '{submission_date_value}'")
        
        submission_date_var = tk.StringVar(value=submission_date_value)
        related_products_var = tk.StringVar()
        other_relevance_var = tk.StringVar(value=pursuit.get("otherRelevance", "") if pursuit else "")
        
        # Create variables for potential value by year
        fy_years = ["FY25", "FY26", "FY27", "FY28", "FY29", "FY30"]
        potential_value_vars = {}
        
        # Initialize potential value variables
        for year in fy_years:
            # Check if potential_value is a list of dictionaries
            if pursuit and "potentialValue" in pursuit:
                if isinstance(pursuit["potentialValue"], list) and len(pursuit["potentialValue"]) > 0:
                    # Try to find the year in the first dictionary
                    if isinstance(pursuit["potentialValue"][0], dict) and year in pursuit["potentialValue"][0]:
                        value = pursuit["potentialValue"][0].get(year, "")
                        # Remove any existing dollar sign for storage
                        if isinstance(value, str) and value.startswith("$"):
                            value = value[1:]
                        potential_value_vars[year] = tk.StringVar(value=str(value))
                    else:
                        potential_value_vars[year] = tk.StringVar(value="")
                else:
                    potential_value_vars[year] = tk.StringVar(value="")
            else:
                potential_value_vars[year] = tk.StringVar(value="")
        
        pcap_var = tk.StringVar(value=pursuit.get("Pcap", "") if pursuit else "")
        pgo_var = tk.StringVar(value=pursuit.get("Pgo", "") if pursuit else "")
        
        # Create form fields
        row = 0
        
        ttk.Label(pursuit_frame, text="Pursuit ID:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(pursuit_frame, textvariable=pursuit_id_var, state="readonly").grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        row += 1
        
        ttk.Label(pursuit_frame, text="Pursuit Name:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(pursuit_frame, textvariable=pursuit_name_var).grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        row += 1
        
        ttk.Label(pursuit_frame, text="Point of Contact:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        point_of_contact_var = tk.StringVar(value=pursuit.get("pointOfContact", "") if pursuit else "")
        ttk.Entry(pursuit_frame, textvariable=point_of_contact_var).grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        row += 1
        
        ttk.Label(pursuit_frame, text="Targeted Submission Date:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        date_entry = DateEntry(pursuit_frame, textvariable=submission_date_var, initial_date=submission_date_value)
        date_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1
        
        ttk.Label(pursuit_frame, text="Related Products:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Create a frame for the related products selection
        products_frame = ttk.Frame(pursuit_frame)
        products_frame.grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        products_frame.columnconfigure(0, weight=1)
        
        # Create a frame for the product and material system selection
        selection_frame = ttk.Frame(products_frame)
        selection_frame.grid(row=0, column=0, sticky=tk.W+tk.E, padx=0, pady=2)
        
        # Create a label and combobox for product selection
        ttk.Label(selection_frame, text="Product:").pack(side=tk.LEFT, padx=2)
        product_var = tk.StringVar()
        products_combo = ttk.Combobox(selection_frame, textvariable=product_var, values=self.product_list, width=40)
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
            filtered_products = [p for p in self.product_list if search_term in p.lower()]
            products_combo['values'] = filtered_products
        
        # Bind the KeyRelease event to filter products
        products_combo.bind('<KeyRelease>', filter_products)
        
        # Create a listbox to display selected product-material combinations
        products_listbox = tk.Listbox(products_frame, height=6)
        products_listbox.grid(row=1, column=0, sticky=tk.W+tk.E, padx=0, pady=2)
        
        # Add a scrollbar to the listbox
        products_scrollbar = ttk.Scrollbar(products_frame, orient=tk.VERTICAL, command=products_listbox.yview)
        products_scrollbar.grid(row=1, column=1, sticky=tk.NS)
        products_listbox.configure(yscrollcommand=products_scrollbar.set)
        
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
                
                if display_text not in [item.split(" [")[0] for item in products_listbox.get(0, tk.END)]:
                    # Add to listbox with display text and hidden storage text
                    products_listbox.insert(tk.END, f"{display_text} [{storage_text}]")
                    # Update the related_products_var with all selected combinations
                    update_related_products()
        
        # Function to remove a product-material combination from the listbox
        def remove_combination():
            selected = products_listbox.curselection()
            if selected:
                products_listbox.delete(selected)
                # Update the related_products_var with remaining combinations
                update_related_products()
        
        # Function to update the related_products_var with all selected combinations
        def update_related_products():
            # Extract the storage text from each listbox item
            selected_combinations = []
            for i in range(products_listbox.size()):
                item = products_listbox.get(i)
                if "[" in item and "]" in item:
                    storage_text = item.split("[")[1].split("]")[0]
                    selected_combinations.append(storage_text)
                else:
                    selected_combinations.append(item)
            
            related_products_var.set(", ".join(selected_combinations))
        
        # Add buttons
        ttk.Button(buttons_frame, text="Add Combination", command=add_combination).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Remove Selected", command=remove_combination).pack(side=tk.LEFT, padx=2)
        
        # If there are existing related products, add them to the listbox
        if pursuit and "relatedProducts" in pursuit:
            # Handle both string and list formats
            existing_combinations = []
            if isinstance(pursuit["relatedProducts"], str):
                existing_combinations = [p.strip() for p in pursuit["relatedProducts"].split(",")]
            elif isinstance(pursuit["relatedProducts"], list):
                existing_combinations = pursuit["relatedProducts"]
            
            for combination in existing_combinations:
                if not combination:
                    continue
                
                # Try to parse the combination
                if " | " in combination:
                    product_id, material_id = combination.split(" | ")
                    
                    # Get product and material names
                    product_name = self.product_id_to_name.get(product_id, product_id)
                    material_name = self.material_id_to_name.get(material_id, material_id)
                    
                    # Format for display
                    display_text = f"{product_name} | {material_name}"
                    
                    # Add to listbox
                    products_listbox.insert(tk.END, f"{display_text} [{combination}]")
                else:
                    # Just add the original text if we can't parse it
                    products_listbox.insert(tk.END, combination)
            
            # Update the related_products_var
            update_related_products()
        
        row += 1
        
        # Other Relevance field
        ttk.Label(pursuit_frame, text="Other Relevance:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(pursuit_frame, textvariable=other_relevance_var).grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        row += 1
        
        # Potential Value field - create a frame with individual year inputs
        ttk.Label(pursuit_frame, text="Potential Value:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Create a frame for the potential value fields
        potential_value_frame = ttk.Frame(pursuit_frame)
        potential_value_frame.grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Create a StringVar for the total
        total_var = tk.StringVar(value="$0")
        
        # Function to validate numeric input
        def validate_numeric(action, value_if_allowed):
            # Allow empty strings and only digits
            if action == '1':  # Insert
                if value_if_allowed == "":
                    return True
                if value_if_allowed.isdigit():
                    return True
                return False
            return True
        
        # Register the validation command
        vcmd = (self.window.register(validate_numeric), '%d', '%P')
        
        # Function to update the total
        def update_total(*args):
            total = 0
            for year, var in potential_value_vars.items():
                try:
                    value = var.get().strip()
                    if value:
                        total += int(value)
                except ValueError:
                    pass
            total_var.set(f"${total:,}")
        
        # Add labels and entry fields for each year
        for i, year in enumerate(fy_years):
            ttk.Label(potential_value_frame, text=year + ":").grid(row=0, column=i*2, padx=2, pady=2)
            
            # Create a frame for the dollar sign and entry
            value_frame = ttk.Frame(potential_value_frame)
            value_frame.grid(row=0, column=i*2+1, padx=2, pady=2)
            
            # Add dollar sign label
            ttk.Label(value_frame, text="$").pack(side=tk.LEFT, padx=0, pady=0)
            
            # Add entry with validation
            entry = ttk.Entry(value_frame, textvariable=potential_value_vars[year], width=8, validate="key", validatecommand=vcmd)
            entry.pack(side=tk.LEFT, padx=0, pady=0)
            
            # Bind the entry to update the total
            potential_value_vars[year].trace_add("write", update_total)
        
        # Add total label and value
        ttk.Label(potential_value_frame, text="Total:").grid(row=0, column=len(fy_years)*2, padx=5, pady=2)
        ttk.Label(potential_value_frame, textvariable=total_var, width=12, anchor="e").grid(row=0, column=len(fy_years)*2+1, padx=2, pady=2)
        
        # Initialize the total
        update_total()
        
        row += 1
        
        # Pcap and Pgo fields in the same row
        ttk.Label(pursuit_frame, text="Pcap:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Create a frame for Pcap and Pgo
        pcap_pgo_frame = ttk.Frame(pursuit_frame)
        pcap_pgo_frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Entry(pcap_pgo_frame, textvariable=pcap_var, width=10).grid(row=0, column=0, padx=5, pady=0)
        ttk.Label(pcap_pgo_frame, text="Pgo:").grid(row=0, column=1, sticky=tk.W, padx=15, pady=0)
        ttk.Entry(pcap_pgo_frame, textvariable=pgo_var, width=10).grid(row=0, column=2, padx=5, pady=0)
        
        row += 1
        
        # Details field
        ttk.Label(pursuit_frame, text="Details:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Create a text widget for details
        details_frame = ttk.Frame(pursuit_frame)
        details_frame.grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        details_frame.columnconfigure(0, weight=1)
        
        details_text = tk.Text(details_frame, height=6, width=60, wrap=tk.WORD)
        details_text.grid(row=0, column=0, sticky=tk.W+tk.E)
        
        # Add a scrollbar to the text widget
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=details_text.yview)
        details_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        details_text.configure(yscrollcommand=details_scrollbar.set)
        
        # Insert existing details if available
        if pursuit and "details" in pursuit:
            details_text.insert(tk.END, pursuit.get("details", ""))
        
        row += 1
        
        # Add a remove button
        remove_button = ttk.Button(pursuit_frame, text="Remove Pursuit", 
                                  command=lambda frame=pursuit_frame, entry_data=None: self.remove_pursuit(frame, entry_data))
        remove_button.grid(row=row, column=0, columnspan=2, pady=5)
        
        # Store all the variables and widgets for this pursuit
        entry_data = {
            "pursuitID": pursuit_id_var,
            "pursuitName": pursuit_name_var,
            "pointOfContact": point_of_contact_var,
            "targetedSubmissionDate": submission_date_var,
            "date_entry": date_entry,  # Store the actual DateEntry widget
            "relatedProducts": related_products_var,
            "otherRelevance": other_relevance_var,
            "potentialValue_vars": potential_value_vars,
            "Pcap": pcap_var,
            "Pgo": pgo_var,
            "details_text": details_text,
            "frame": pursuit_frame
        }
        self.pursuit_entries.append(entry_data)
        
        # Bind mouse wheel events to the pursuit frame
        system = platform.system()
        if system == "Windows":
            pursuit_frame.bind("<MouseWheel>", self._on_mousewheel_windows)
        else:
            pursuit_frame.bind("<Button-4>", self._on_mousewheel_linux_up)
            pursuit_frame.bind("<Button-5>", self._on_mousewheel_linux_down)
        
        # Also bind to all children of the pursuit frame
        self._bind_mousewheel_to_all_children(pursuit_frame)
        
        # Update the canvas scroll region
        self._configure_pursuits_canvas(None)
        
        return entry_data
    
    def remove_pursuit(self, frame, entry_data):
        """Remove a pursuit entry"""
        if entry_data in self.pursuit_entries:
            self.pursuit_entries.remove(entry_data)
        
        frame.destroy()
        
        # Renumber the remaining pursuits
        for i, entry in enumerate(self.pursuit_entries):
            entry["frame"].configure(text=f"Pursuit {i + 1}")
        
        # Update the canvas scroll region
        self._configure_pursuits_canvas(None)
    
    def collect_data(self):
        """Collect data from all form fields"""
        # Basic info
        self.opportunity["id"] = self.id_var.get()
        self.opportunity["announcementName"] = self.name_var.get()
        self.opportunity["pursuitType"] = self.pursuit_type_var.get()
        self.opportunity["status"] = self.status_var.get()
        self.opportunity["closeDate"] = self.close_date_var.get()
        self.opportunity["periodOfPerformance"] = self.period_of_performance_var.get()
        self.opportunity["solicitationNumber"] = self.solicitation_var.get()
        
        # Format funding amount with dollar sign if not already present
        funding_amount = self.amount_var.get().strip()
        if funding_amount and not funding_amount.startswith("$"):
            funding_amount = f"${funding_amount}"
        self.opportunity["fundingAmount"] = funding_amount
        
        # Format cost share percentage with % sign if not already present
        cost_share = self.cost_share_var.get().strip()
        if cost_share and not cost_share.endswith("%"):
            cost_share = f"{cost_share}%"
        self.opportunity["costSharePercentage"] = cost_share
        
        self.opportunity["customer"] = self.customer_var.get()
        
        # Pursuits
        pursuits = []
        for entry in self.pursuit_entries:
            # Create potential value dictionary
            potential_value = {}
            for year, var in entry["potentialValue_vars"].items():
                value = var.get().strip()
                if value:
                    try:
                        # Try to convert to integer if possible
                        potential_value[year] = int(value)
                    except ValueError:
                        # Otherwise keep as string with dollar sign
                        potential_value[year] = f"${value}"
            
            # Get the date directly from the DateEntry widget to ensure we have the most up-to-date value
            submission_date = entry["date_entry"].get_date() if "date_entry" in entry else entry["targetedSubmissionDate"].get()
            print(f"Saving submission date: '{submission_date}'")
            
            # Create pursuit dictionary
            pursuit = {
                "pursuitID": entry["pursuitID"].get(),
                "pursuitName": entry["pursuitName"].get(),
                "pointOfContact": entry["pointOfContact"].get(),
                "targetedSubmissionDate": submission_date,
                "relatedProducts": entry["relatedProducts"].get(),
                "otherRelevance": entry["otherRelevance"].get(),
                "potentialValue": [potential_value] if potential_value else [],
                "Pcap": entry["Pcap"].get(),
                "Pgo": entry["Pgo"].get(),
                "details": entry["details_text"].get("1.0", tk.END).strip()  # Get text from the text widget
            }
            pursuits.append(pursuit)
        
        self.opportunity["pursuits"] = pursuits
    
    def save(self):
        """Save the funding opportunity data"""
        # Collect data from all form fields
        self.collect_data()
        
        # Print debug info about what we're saving
        print(f"Opportunity ID: {self.opportunity['id']}")
        print(f"Close Date: '{self.opportunity['closeDate']}'")
        print(f"Pursuits: {len(self.opportunity['pursuits'])}")
        for pursuit in self.opportunity['pursuits']:
            print(f"  Pursuit ID: {pursuit['pursuitID']}")
            print(f"  Submission Date: '{pursuit['targetedSubmissionDate']}'")
        
        # Validate required fields
        if not self.opportunity["id"] or not self.opportunity["announcementName"]:
            self.model.show_error("Error", "ID and Announcement Name are required fields")
            return
        
        # Save the opportunity
        if self.is_new:
            self.model.data["fundingOpps"].append(self.opportunity)
            self.model.update_status(f"Added funding opportunity: {self.opportunity['announcementName']}")
        else:
            # Find and update the existing opportunity
            for i, opp in enumerate(self.model.data["fundingOpps"]):
                if opp["id"] == self.opportunity["id"]:
                    self.model.data["fundingOpps"][i] = self.opportunity
                    break
            self.model.update_status(f"Updated funding opportunity: {self.opportunity['announcementName']}")
        
        # Refresh the treeview
        self.model.populate_funding_opps_tree()
        
        # Close the window
        self.window.destroy()
    
    def delete(self):
        """Delete the funding opportunity"""
        if self.model.confirm_delete(self.opportunity['announcementName']):
            # Remove opportunity from data
            self.model.data["fundingOpps"].remove(self.opportunity)
            
            # Refresh treeview
            self.model.populate_funding_opps_tree()
            
            # Close window
            self.window.destroy()
            
            self.model.update_status(f"Deleted funding opportunity: {self.opportunity['announcementName']}")
    
    def _validate_numeric(self, value_if_allowed):
        """Validate that input is numeric (for cost share percentage)"""
        # Allow empty string
        if value_if_allowed == "":
            return True
            
        # Check if the value is numeric
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False 