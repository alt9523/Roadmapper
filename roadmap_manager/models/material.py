import tkinter as tk
from tkinter import ttk, messagebox
from .base import BaseModel
from ..date_entry import DateEntry
from datetime import datetime, timedelta

class MaterialModel(BaseModel):
    """Model for managing material systems"""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.materials_tree = None
    
    def create_materials_tab(self, notebook):
        """Create the Material Systems tab in the notebook"""
        materials_frame = ttk.Frame(notebook)
        notebook.add(materials_frame, text="Material Systems")
        
        # Add buttons
        buttons_frame = ttk.Frame(materials_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="Add Material System", command=self.add_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Edit Material System", command=self.edit_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete Material System", command=self.delete_material).pack(side=tk.LEFT, padx=5)
        
        # Add search field
        ttk.Label(buttons_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(buttons_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Add search button
        ttk.Button(buttons_frame, text="Search", command=self.search_materials).pack(side=tk.LEFT, padx=5)
        
        # Add clear button
        ttk.Button(buttons_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Bind the Enter key to the search function
        search_entry.bind("<Return>", lambda event: self.search_materials())
        
        # Create treeview
        columns = ("ID", "Name", "Process", "Material", "MRL", "Qualification", "Post-Processing", "Qualified Machines", "Funding Opportunities")
        self.materials_tree = ttk.Treeview(materials_frame, columns=columns, show="headings")
        
        # Configure columns
        self.materials_tree.heading("ID", text="ID")
        self.materials_tree.heading("Name", text="Name")
        self.materials_tree.heading("Process", text="Process")
        self.materials_tree.heading("Material", text="Material")
        self.materials_tree.heading("MRL", text="MRL")
        self.materials_tree.heading("Qualification", text="Qualification")
        self.materials_tree.heading("Post-Processing", text="Post-Processing")
        self.materials_tree.heading("Qualified Machines", text="Qualified Machines")
        self.materials_tree.heading("Funding Opportunities", text="Funding Opportunities")
        
        self.materials_tree.column("ID", width=80, minwidth=80)
        self.materials_tree.column("Name", width=150, minwidth=100)
        self.materials_tree.column("Process", width=150, minwidth=100)
        self.materials_tree.column("Material", width=120, minwidth=100)
        self.materials_tree.column("MRL", width=50, minwidth=50)
        self.materials_tree.column("Qualification", width=100, minwidth=80)
        self.materials_tree.column("Post-Processing", width=200, minwidth=150)
        self.materials_tree.column("Qualified Machines", width=200, minwidth=150)
        self.materials_tree.column("Funding Opportunities", width=200, minwidth=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(materials_frame, orient=tk.VERTICAL, command=self.materials_tree.yview)
        self.materials_tree.configure(yscroll=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.materials_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.materials_tree.bind("<Double-1>", lambda event: self.edit_material())
        
        # Populate treeview
        self.populate_materials_tree()
    
    def populate_materials_tree(self):
        """Populate the materials treeview with data"""
        # Clear existing items
        for item in self.materials_tree.get_children():
            self.materials_tree.delete(item)
        
        # Get the materials data (handle both "materials" and "materialSystems" keys)
        materials_data = self.data.get("materials", self.data.get("materialSystems", []))
        
        # Create a mapping of funding opportunity IDs to names
        funding_id_to_name = {}
        for opp in self.data.get("fundingOpps", []):
            if "id" in opp and "announcementName" in opp:
                funding_id_to_name[opp["id"]] = opp["announcementName"]
        
        # Add materials to the tree
        for material in materials_data:
            # Get process and material values
            process = material.get("process", "")
            material_name = material.get("material", "")
            
            # Get post-processing methods
            post_processing = []
            for pp in material.get("postProcessing", []):
                if "name" in pp:
                    post_processing.append(pp["name"])
                elif "process" in pp:
                    post_processing.append(pp["process"])
            
            # Get qualified machines
            qualified_machines = []
            for qm in material.get("qualifiedMachines", []):
                if "machine" in qm:
                    qualified_machines.append(qm["machine"])
            
            # Get funding opportunities (display names instead of IDs)
            funding_opps = []
            for opp_data in material.get("relatedFundingOpps", []):
                if isinstance(opp_data, dict) and "opportunityID" in opp_data:
                    opp_id = opp_data["opportunityID"]
                    if opp_id in funding_id_to_name:
                        # Add opportunity name and pursuit name if available
                        opp_name = funding_id_to_name[opp_id]
                        if "pursuitID" in opp_data:
                            # Try to find the pursuit name
                            pursuit_name = self.get_pursuit_name(opp_id, opp_data["pursuitID"])
                            if pursuit_name:
                                funding_opps.append(f"{opp_name} - {pursuit_name}")
                            else:
                                funding_opps.append(opp_name)
                        else:
                            funding_opps.append(opp_name)
                    else:
                        # Opportunity not found, just use the ID
                        if "pursuitID" in opp_data:
                            funding_opps.append(f"{opp_id} - {opp_data['pursuitID']}")
                        else:
                            funding_opps.append(opp_id)
                elif isinstance(opp_data, str):
                    # Handle string IDs for backward compatibility
                    opp_id = opp_data
                    if opp_id in funding_id_to_name:
                        opp_name = funding_id_to_name[opp_id]
                        
                        # Try to find the first pursuit for this opportunity
                        for opp in self.data.get("fundingOpps", []):
                            if opp.get("id") == opp_id and opp.get("pursuits"):
                                first_pursuit = opp["pursuits"][0]
                                if "pursuitName" in first_pursuit:
                                    funding_opps.append(f"{opp_name} - {first_pursuit['pursuitName']}")
                                    break
                        else:
                            # No pursuit found, just use the opportunity name
                            funding_opps.append(opp_name)
                    else:
                        funding_opps.append(opp_id)  # Fallback to ID if name not found
            
            # Format for display
            pp_display = ", ".join(post_processing) if post_processing else ""
            qm_display = ", ".join(qualified_machines) if qualified_machines else ""
            funding_display = ", ".join(funding_opps) if funding_opps else ""
            
            # Add to tree
            self.materials_tree.insert(
                "", "end",
                values=(
                    material.get("id", ""),
                    material.get("name", ""),
                    process,
                    material_name,
                    material.get("mrl", ""),
                    material.get("qualification", ""),
                    pp_display,
                    qm_display,
                    funding_display
                )
            )
    
    def add_material(self, material=None):
        """Open a window to add a new material system"""
        # Create a new window for adding a material system
        add_window = tk.Toplevel(self.manager.root)
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
        id_entry = ttk.Entry(basic_frame, textvariable=id_var)
        id_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # If editing, use existing ID, otherwise generate next available ID
        if material:
            id_var.set(material.get("id", ""))
            # Make ID field read-only if editing
            id_entry.configure(state="readonly")
        else:
            # Generate next available ID
            next_id = self.get_next_material_id()
            id_var.set(next_id)
            # Make ID field read-only for new materials too
            id_entry.configure(state="readonly")
        
        ttk.Label(basic_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=material.get("name", "") if material else "")
        ttk.Entry(basic_frame, textvariable=name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Process:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        process_var = tk.StringVar(value=material.get("process", "") if material else "")
        ttk.Combobox(basic_frame, textvariable=process_var, values=["Laser Powder Bed Fusion", "Electron Beam Melting", "Directed Energy Deposition", "Binder Jetting"]).grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Material:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        material_var = tk.StringVar(value=material.get("material", "") if material else "")
        ttk.Entry(basic_frame, textvariable=material_var).grid(row=3, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="MRL:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        mrl_var = tk.StringVar(value=material.get("mrl", "") if material else "")
        ttk.Combobox(basic_frame, textvariable=mrl_var, values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]).grid(row=4, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Qualification:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        qualification_var = tk.StringVar(value=material.get("qualification", "") if material else "")
        ttk.Combobox(basic_frame, textvariable=qualification_var, values=["None", "In Progress", "Qualified"]).grid(row=5, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Qualification Class:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        qualification_class_var = tk.StringVar(value=material.get("qualificationClass", "") if material else "")
        ttk.Combobox(basic_frame, textvariable=qualification_class_var, values=["Class 1", "Class 2", "Class 3", "Class 4", "Class 5"]).grid(row=6, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Statistical Basis:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
        statistical_basis_var = tk.StringVar(value=material.get("statisticalBasis", "") if material else "")
        ttk.Combobox(basic_frame, textvariable=statistical_basis_var, values=["A-Basis", "B-Basis", "S-Basis", "None"]).grid(row=7, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Roadmap tab
        roadmap_frame = ttk.Frame(material_notebook)
        material_notebook.add(roadmap_frame, text="Roadmap")
        
        # Roadmap tasks list
        ttk.Label(roadmap_frame, text="Roadmap Tasks:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Create a frame for the task list
        tasks_frame = ttk.Frame(roadmap_frame)
        tasks_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Add headers for task fields
        task_header_frame = ttk.Frame(tasks_frame)
        task_header_frame.pack(fill=tk.X, pady=2)
        
        # Add more descriptive headers with bold font and standardized widths
        ttk.Label(task_header_frame, text="Task Name", width=20, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ttk.Label(task_header_frame, text="Start Date", width=15, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ttk.Label(task_header_frame, text="End Date", width=15, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ttk.Label(task_header_frame, text="Status", width=12, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ttk.Label(task_header_frame, text="Funding Type", width=15, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ttk.Label(task_header_frame, text="Float", width=8, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=2)
        
        # Create a frame for task entries
        task_entries_frame = ttk.Frame(tasks_frame)
        task_entries_frame.pack(fill=tk.X, pady=2)
        
        # List to store task entries
        task_entries = []
        
        # Store the last save date for floating functionality
        last_save_date = datetime.now()
        
        # Function to add a new task entry
        def add_task_entry(task_data=None):
            task_frame = ttk.Frame(task_entries_frame)
            task_frame.pack(fill=tk.X, pady=2)
            
            # Task name
            task_var = tk.StringVar(value=task_data.get("task", "") if task_data else "")
            ttk.Entry(task_frame, textvariable=task_var, width=20).pack(side=tk.LEFT, padx=2)
            
            # Start date
            start_date = task_data.get("startDate", "") if task_data else ""
            start_entry = DateEntry(task_frame, width=15, initial_date=start_date)
            start_entry.pack(side=tk.LEFT, padx=2)
            
            # End date
            end_date = task_data.get("endDate", "") if task_data else ""
            end_entry = DateEntry(task_frame, width=15, initial_date=end_date)
            end_entry.pack(side=tk.LEFT, padx=2)
            
            # Status dropdown
            status_options = ["Not Started", "In Progress", "Complete", "Delayed"]
            status_var = tk.StringVar(value=task_data.get("status", "") if task_data else "")
            ttk.Combobox(task_frame, textvariable=status_var, values=status_options, width=12).pack(side=tk.LEFT, padx=2)
            
            # Funding dropdown with updated options
            funding_options = ["Unfunded", "Division IRAD", "Sector IRAD", "CRAD", "Program Funded", "External Task"]
            funding_var = tk.StringVar(value=task_data.get("fundingType", "") if task_data else "")
            ttk.Combobox(task_frame, textvariable=funding_var, values=funding_options, width=15).pack(side=tk.LEFT, padx=2)
            
            # Float on roadmap checkbox
            float_var = tk.BooleanVar(value=task_data.get("floatOnRoadmap", False) if task_data else False)
            ttk.Checkbutton(task_frame, variable=float_var, width=5).pack(side=tk.LEFT, padx=2)
            
            # Hidden variable to store the float date
            float_date = task_data.get("floatDate", "") if task_data else ""
            
            # Button to remove this task
            remove_btn = ttk.Button(task_frame, text="X", width=2,
                                  command=lambda f=task_frame: [f.destroy(), task_entries.remove(entry_data)])
            remove_btn.pack(side=tk.LEFT, padx=2)
            
            # Create a frame for additional details
            details_frame = ttk.Frame(task_entries_frame)
            details_frame.pack(fill=tk.X, pady=(0, 5))
            
            # Add additional details text box
            ttk.Label(details_frame, text="Additional Details:", width=15).pack(side=tk.LEFT, padx=2)
            additional_details_var = tk.StringVar(value=task_data.get("additionalDetails", "") if task_data else "")
            ttk.Entry(details_frame, textvariable=additional_details_var, width=70).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
            
            # Store the entry data
            entry_data = {
                "frame": task_frame,
                "details_frame": details_frame,
                "task": task_var,
                "start_date": start_entry,
                "end_date": end_entry,
                "status": status_var,
                "fundingType": funding_var,
                "float_on_roadmap": float_var,
                "float_date": float_date,
                "additional_details": additional_details_var
            }
            task_entries.append(entry_data)
            
            return entry_data
        
        # Add existing tasks
        for task in material.get("roadmap", []) if material else []:
            add_task_entry(task)
        
        # Add button for tasks
        add_task_button = ttk.Button(tasks_frame, text="Add Task", command=lambda: add_task_entry())
        add_task_button.pack(anchor=tk.W, pady=5)
        
        # Milestones section
        ttk.Label(roadmap_frame, text="Milestones:", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=10, pady=(20, 5))
        
        # Create a frame for the milestones list
        milestones_frame = ttk.Frame(roadmap_frame)
        milestones_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Add headers for milestone fields
        milestone_header_frame = ttk.Frame(milestones_frame)
        milestone_header_frame.pack(fill=tk.X, pady=2)
        
        # Add more descriptive headers with bold font and standardized widths
        ttk.Label(milestone_header_frame, text="Milestone Name", width=20, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ttk.Label(milestone_header_frame, text="Date", width=15, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ttk.Label(milestone_header_frame, text="Description", width=30, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=2)
        ttk.Label(milestone_header_frame, text="Float", width=8, font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=2)
        
        # Create a frame for milestone entries
        milestone_entries_frame = ttk.Frame(milestones_frame)
        milestone_entries_frame.pack(fill=tk.X, pady=2)
        
        # List to store milestone entries
        milestone_entries = []
        
        # Function to add a new milestone entry
        def add_milestone_entry(milestone_data=None):
            ms_entry_frame = ttk.Frame(milestone_entries_frame)
            ms_entry_frame.pack(fill=tk.X, pady=2)
            
            # Milestone name
            name_var = tk.StringVar(value=milestone_data.get("name", "") if milestone_data else "")
            ttk.Entry(ms_entry_frame, textvariable=name_var, width=20).pack(side=tk.LEFT, padx=2)
            
            # Milestone date
            milestone_date = milestone_data.get("date", "") if milestone_data else ""
            date_entry = DateEntry(ms_entry_frame, width=15, initial_date=milestone_date)
            date_entry.pack(side=tk.LEFT, padx=2)
            
            # Description
            desc_var = tk.StringVar(value=milestone_data.get("description", "") if milestone_data else "")
            ttk.Entry(ms_entry_frame, textvariable=desc_var, width=30).pack(side=tk.LEFT, padx=2)
            
            # Float on roadmap checkbox
            float_var = tk.BooleanVar(value=milestone_data.get("floatOnRoadmap", False) if milestone_data else False)
            ttk.Checkbutton(ms_entry_frame, variable=float_var, width=5).pack(side=tk.LEFT, padx=2)
            
            # Hidden variable to store the float date
            float_date = milestone_data.get("floatDate", "") if milestone_data else ""
            
            # Button to remove this milestone
            remove_btn = ttk.Button(ms_entry_frame, text="X", width=2,
                                  command=lambda f=ms_entry_frame: [f.destroy(), milestone_entries.remove(entry_data)])
            remove_btn.pack(side=tk.LEFT, padx=2)
            
            # Create a frame for additional details
            details_frame = ttk.Frame(milestone_entries_frame)
            details_frame.pack(fill=tk.X, pady=(0, 5))
            
            # Add additional details text box
            ttk.Label(details_frame, text="Additional Details:", width=15).pack(side=tk.LEFT, padx=2)
            additional_details_var = tk.StringVar(value=milestone_data.get("additionalDetails", "") if milestone_data else "")
            ttk.Entry(details_frame, textvariable=additional_details_var, width=70).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
            
            # Store the entry data
            entry_data = {
                "frame": ms_entry_frame,
                "details_frame": details_frame,
                "name": name_var,
                "date": date_entry,
                "description": desc_var,
                "float_on_roadmap": float_var,
                "float_date": float_date,
                "additional_details": additional_details_var
            }
            milestone_entries.append(entry_data)
            
            return entry_data
        
        # Add existing milestones
        for milestone in material.get("milestones", []) if material else []:
            add_milestone_entry(milestone)
        
        # Add button for milestones
        add_milestone_button = ttk.Button(milestones_frame, text="Add Milestone", command=lambda: add_milestone_entry())
        add_milestone_button.pack(anchor=tk.W, pady=5)
        
        # Post-Processing and Qualified Machines tab
        processing_frame = ttk.Frame(material_notebook)
        material_notebook.add(processing_frame, text="Processing & Machines")
        
        # Post-Processing section
        ttk.Label(processing_frame, text="Post-Processing Methods:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 5))
        
        # Create a frame for the post-processing list
        pp_frame = ttk.Frame(processing_frame)
        pp_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store post-processing entries
        pp_entries = []
        
        # Function to add a new post-processing entry
        def add_pp_entry(existing_pp=None):
            pp_entry_frame = ttk.Frame(pp_frame)
            pp_entry_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(pp_entry_frame, text="Name/Process:").grid(row=0, column=0, sticky=tk.W)
            
            # Determine the name/process value
            name_value = ""
            if existing_pp:
                if "name" in existing_pp:
                    name_value = existing_pp["name"]
                elif "process" in existing_pp:
                    name_value = existing_pp["process"]
            
            name_var = tk.StringVar(value=name_value)
            ttk.Entry(pp_entry_frame, textvariable=name_var, width=20).grid(row=0, column=1, sticky=tk.W)
            
            ttk.Label(pp_entry_frame, text="Suppliers:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
            
            # Create a frame for suppliers
            suppliers_frame = ttk.Frame(pp_entry_frame)
            suppliers_frame.grid(row=0, column=3, sticky=tk.W)
            
            # List to store supplier entries
            supplier_entries = []
            
            # Function to add a supplier entry
            def add_supplier(supplier_id=None):
                supplier_frame = ttk.Frame(suppliers_frame)
                supplier_frame.pack(fill=tk.X, pady=2)
                
                # Get post-processing suppliers
                supplier_options = []
                supplier_id_to_option = {}
                for supplier in self.data["postProcessingSuppliers"]:
                    option = f"{supplier['id']}: {supplier['name']}"
                    supplier_options.append(option)
                    supplier_id_to_option[supplier['id']] = option
                
                supplier_var = tk.StringVar()
                if supplier_id and supplier_id in supplier_id_to_option:
                    supplier_var.set(supplier_id_to_option[supplier_id])
                
                supplier_combo = ttk.Combobox(supplier_frame, textvariable=supplier_var, values=supplier_options, width=20)
                supplier_combo.pack(side=tk.LEFT)
                
                # Button to remove this supplier
                remove_btn = ttk.Button(supplier_frame, text="X", width=2,
                                      command=lambda f=supplier_frame, s=supplier_var: [f.destroy(), supplier_entries.remove(s)])
                remove_btn.pack(side=tk.LEFT, padx=2)
                
                supplier_entries.append(supplier_var)
            
            # Add existing suppliers if available
            if existing_pp and "Supplier" in existing_pp:
                for supplier_id in existing_pp["Supplier"]:
                    add_supplier(supplier_id)
            else:
                # Add one supplier by default
                add_supplier()
            
            # Button to add a supplier
            add_supplier_btn = ttk.Button(suppliers_frame, text="+", width=2, command=lambda: add_supplier())
            add_supplier_btn.pack(anchor=tk.W, pady=2)
            
            # Button to remove this post-processing entry
            remove_btn = ttk.Button(pp_entry_frame, text="X", width=2,
                                  command=lambda f=pp_entry_frame: [f.destroy(), pp_entries.remove(entry_data)])
            remove_btn.grid(row=0, column=4, padx=5)
            
            # Store the entry data
            entry_data = {
                "frame": pp_entry_frame,
                "name": name_var,
                "suppliers": supplier_entries
            }
            pp_entries.append(entry_data)
            
            return entry_data
        
        # Add existing post-processing methods
        for pp in material.get("postProcessing", []) if material else []:
            add_pp_entry(pp)
        
        # Add button for post-processing
        ttk.Button(processing_frame, text="Add Post-Processing Method", command=lambda: add_pp_entry()).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Qualified Machines section
        ttk.Label(processing_frame, text="Qualified Machines:", font=("TkDefaultFont", 10, "bold")).grid(row=3, column=0, sticky=tk.W, padx=10, pady=(20, 5))
        
        # Create a frame for the qualified machines list
        qm_frame = ttk.Frame(processing_frame)
        qm_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store qualified machine entries
        qm_entries = []
        
        # Function to add a new qualified machine entry
        def add_qm_entry(existing_qm=None):
            qm_entry_frame = ttk.Frame(qm_frame)
            qm_entry_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(qm_entry_frame, text="Machine:").grid(row=0, column=0, sticky=tk.W)
            machine_var = tk.StringVar(value=existing_qm.get("machine", "") if existing_qm else "")
            ttk.Entry(qm_entry_frame, textvariable=machine_var, width=20).grid(row=0, column=1, sticky=tk.W)
            
            ttk.Label(qm_entry_frame, text="Suppliers:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
            
            # Create a frame for suppliers
            suppliers_frame = ttk.Frame(qm_entry_frame)
            suppliers_frame.grid(row=0, column=3, sticky=tk.W)
            
            # List to store supplier entries
            supplier_entries = []
            
            # Function to add a supplier entry
            def add_supplier(supplier_id=None):
                supplier_frame = ttk.Frame(suppliers_frame)
                supplier_frame.pack(fill=tk.X, pady=2)
                
                # Get printing suppliers
                supplier_options = []
                supplier_id_to_option = {}
                for supplier in self.data["printingSuppliers"]:
                    option = f"{supplier['id']}: {supplier['name']}"
                    supplier_options.append(option)
                    supplier_id_to_option[supplier['id']] = option
                
                supplier_var = tk.StringVar()
                if supplier_id and supplier_id in supplier_id_to_option:
                    supplier_var.set(supplier_id_to_option[supplier_id])
                
                supplier_combo = ttk.Combobox(supplier_frame, textvariable=supplier_var, values=supplier_options, width=20)
                supplier_combo.pack(side=tk.LEFT)
                
                # Button to remove this supplier
                remove_btn = ttk.Button(supplier_frame, text="X", width=2,
                                      command=lambda f=supplier_frame, s=supplier_var: [f.destroy(), supplier_entries.remove(s)])
                remove_btn.pack(side=tk.LEFT, padx=2)
                
                supplier_entries.append(supplier_var)
            
            # Add existing suppliers if available
            if existing_qm and "Supplier" in existing_qm:
                for supplier_id in existing_qm["Supplier"]:
                    add_supplier(supplier_id)
            else:
                # Add one supplier by default
                add_supplier()
            
            # Button to add a supplier
            add_supplier_btn = ttk.Button(suppliers_frame, text="+", width=2, command=lambda: add_supplier())
            add_supplier_btn.pack(anchor=tk.W, pady=2)
            
            # Button to remove this qualified machine entry
            remove_btn = ttk.Button(qm_entry_frame, text="X", width=2,
                                  command=lambda f=qm_entry_frame: [f.destroy(), qm_entries.remove(entry_data)])
            remove_btn.grid(row=0, column=4, padx=5)
            
            # Store the entry data
            entry_data = {
                "frame": qm_entry_frame,
                "machine": machine_var,
                "suppliers": supplier_entries
            }
            qm_entries.append(entry_data)
            
            return entry_data
        
        # Add existing qualified machines
        for qm in material.get("qualifiedMachines", []) if material else []:
            add_qm_entry(qm)
        
        # Add button for qualified machines
        ttk.Button(processing_frame, text="Add Qualified Machine", command=lambda: add_qm_entry()).grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Additional Info tab
        additional_frame = ttk.Frame(material_notebook)
        material_notebook.add(additional_frame, text="Additional Info")
        
        # Standard NDT section
        ttk.Label(additional_frame, text="Standard NDT Methods:", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 5))
        
        # Create a frame for the NDT methods list
        ndt_frame = ttk.Frame(additional_frame)
        ndt_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store NDT method entries
        ndt_entries = []
        
        # Function to add a new NDT method entry
        def add_ndt_entry(method=""):
            ndt_entry_frame = ttk.Frame(ndt_frame)
            ndt_entry_frame.pack(fill=tk.X, pady=2)
            
            ndt_var = tk.StringVar(value=method)
            ndt_entry = ttk.Entry(ndt_entry_frame, textvariable=ndt_var, width=40)
            ndt_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Button to remove this NDT method
            remove_btn = ttk.Button(ndt_entry_frame, text="X", width=2,
                                  command=lambda f=ndt_entry_frame: [f.destroy(), ndt_entries.remove(ndt_var)])
            remove_btn.pack(side=tk.LEFT, padx=5)
            
            ndt_entries.append(ndt_var)
        
        # Add existing NDT methods
        for method in material.get("standardNDT", []) if material else []:
            add_ndt_entry(method)
        
        # Add button for NDT methods
        ttk.Button(additional_frame, text="Add NDT Method", command=lambda: add_ndt_entry()).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Related Funding Opportunities section
        ttk.Label(additional_frame, text="Related Funding Opportunities:", font=("TkDefaultFont", 10, "bold")).grid(row=3, column=0, sticky=tk.W, padx=10, pady=(20, 5))
        
        # Create a frame for the funding opportunities list
        funding_frame = ttk.Frame(additional_frame)
        funding_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # List to store funding opportunity entries
        funding_entries = []
        
        # Function to add a new funding opportunity entry
        def add_funding_entry(opp_id=None, pursuit_id=None):
            funding_entry_frame = ttk.Frame(funding_frame)
            funding_entry_frame.pack(fill=tk.X, pady=2)
            
            # Get funding opportunities
            funding_options = []
            funding_id_to_option = {}
            funding_id_map = {}  # Map to store ID to name mapping
            
            for opp in self.data.get("fundingOpps", []):
                if "id" in opp and "announcementName" in opp:
                    option = f"{opp['id']}: {opp['announcementName']}"
                    funding_options.append(option)
                    funding_id_to_option[opp['id']] = option
                    funding_id_map[opp['id']] = opp
            
            # Create opportunity combobox first
            ttk.Label(funding_entry_frame, text="Opportunity:").pack(side=tk.LEFT, padx=2)
            funding_var = tk.StringVar()
            funding_combo = ttk.Combobox(funding_entry_frame, textvariable=funding_var, values=funding_options, width=30)
            funding_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            if opp_id and opp_id in funding_id_to_option:
                funding_var.set(funding_id_to_option[opp_id])
            
            # Create pursuit combobox second
            ttk.Label(funding_entry_frame, text="Pursuit:").pack(side=tk.LEFT, padx=2)
            pursuit_var = tk.StringVar()
            pursuit_combo = ttk.Combobox(funding_entry_frame, textvariable=pursuit_var, width=30)
            pursuit_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            
            # Function to update pursuits when opportunity changes
            def update_pursuits(*args):
                selected = funding_var.get()
                if selected:
                    opp_id = selected.split(":")[0].strip()
                    if opp_id in funding_id_map:
                        opp = funding_id_map[opp_id]
                        pursuit_options = []
                        pursuit_id_to_option = {}
                        
                        for pursuit in opp.get("pursuits", []):
                            if "pursuitID" in pursuit and "pursuitName" in pursuit:
                                option = f"{pursuit['pursuitID']}: {pursuit['pursuitName']}"
                                pursuit_options.append(option)
                                pursuit_id_to_option[pursuit['pursuitID']] = option
                        
                        pursuit_combo['values'] = pursuit_options
                        
                        # Set the pursuit value if provided
                        if pursuit_id and pursuit_id in pursuit_id_to_option:
                            pursuit_var.set(pursuit_id_to_option[pursuit_id])
                        elif pursuit_options:
                            # Automatically select the first pursuit if none is specified
                            pursuit_var.set(pursuit_options[0])
                        else:
                            pursuit_var.set("")
            
            # Bind the update_pursuits function to the funding_var
            funding_var.trace_add("write", update_pursuits)
            
            # Initialize pursuits if opportunity is provided
            if opp_id:
                update_pursuits()
            
            # Button to remove this funding opportunity
            remove_btn = ttk.Button(funding_entry_frame, text="X", width=2,
                                  command=lambda f=funding_entry_frame: [f.destroy(), funding_entries.remove(entry_data)])
            remove_btn.pack(side=tk.LEFT, padx=5)
            
            # Store the entry data
            entry_data = {
                "frame": funding_entry_frame,
                "opportunity": funding_var,
                "pursuit": pursuit_var
            }
            funding_entries.append(entry_data)
            
            return entry_data
        
        # Add existing funding opportunities
        for opp_data in material.get("relatedFundingOpps", []) if material else []:
            if isinstance(opp_data, dict) and "opportunityID" in opp_data and "pursuitID" in opp_data:
                add_funding_entry(opp_data["opportunityID"], opp_data["pursuitID"])
            elif isinstance(opp_data, str):
                add_funding_entry(opp_data)
        
        # Add button for funding opportunities
        ttk.Button(additional_frame, text="Add Funding Opportunity", command=lambda: add_funding_entry()).grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Save button
        def save_material():
            # Validate required fields
            if not id_var.get() or not name_var.get():
                messagebox.showerror("Error", "ID and Name are required fields.")
                return
            
            # Collect roadmap tasks
            roadmap_tasks = []
            for task_entry in task_entries:
                if not task_entry["task"].get():  # Skip empty tasks
                    continue
                
                # Get the start and end dates
                start_date = task_entry["start_date"].get_date()
                end_date = task_entry["end_date"].get_date()
                
                # Check if this task should float on the roadmap
                float_on_roadmap = task_entry["float_on_roadmap"].get()
                float_date = task_entry["float_date"]
                
                # If floating is enabled, adjust dates based on time elapsed since last save
                if float_on_roadmap and start_date and end_date:
                    # If this is the first time floating, store the current date
                    if not float_date:
                        float_date = datetime.now().strftime("%Y-%m-%d")
                    
                    # Calculate time elapsed since last float date
                    try:
                        last_float = datetime.strptime(float_date, "%Y-%m-%d")
                        now = datetime.now()
                        days_elapsed = (now - last_float).days
                        
                        # Adjust dates if there's been elapsed time
                        if days_elapsed > 0:
                            if start_date:
                                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                                start_date_obj += timedelta(days=days_elapsed)
                                start_date = start_date_obj.strftime("%Y-%m-%d")
                                task_entry["start_date"].set_date(start_date)
                            
                            if end_date:
                                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                                end_date_obj += timedelta(days=days_elapsed)
                                end_date = end_date_obj.strftime("%Y-%m-%d")
                                task_entry["end_date"].set_date(end_date)
                        
                        # Update the float date to now
                        float_date = now.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        # If there's an error parsing dates, just use the current dates
                        float_date = datetime.now().strftime("%Y-%m-%d")
                
                task_data = {
                    "task": task_entry["task"].get(),
                    "startDate": start_date,
                    "endDate": end_date,
                    "status": task_entry["status"].get(),
                    "floatOnRoadmap": float_on_roadmap,
                    "floatDate": float_date,
                    "additionalDetails": task_entry["additional_details"].get()
                }
                
                # Add funding type if provided
                if task_entry["fundingType"].get():
                    task_data["fundingType"] = task_entry["fundingType"].get()
                
                roadmap_tasks.append(task_data)
            
            # Collect milestones
            milestones = []
            for milestone_entry in milestone_entries:
                if not milestone_entry["name"].get():  # Skip empty milestones
                    continue
                
                # Get the milestone date
                milestone_date = milestone_entry["date"].get_date()
                
                # Check if this milestone should float on the roadmap
                float_on_roadmap = milestone_entry["float_on_roadmap"].get()
                float_date = milestone_entry["float_date"]
                
                # If floating is enabled, adjust date based on time elapsed since last save
                if float_on_roadmap and milestone_date:
                    # If this is the first time floating, store the current date
                    if not float_date:
                        float_date = datetime.now().strftime("%Y-%m-%d")
                    
                    # Calculate time elapsed since last float date
                    try:
                        last_float = datetime.strptime(float_date, "%Y-%m-%d")
                        now = datetime.now()
                        days_elapsed = (now - last_float).days
                        
                        # Adjust date if there's been elapsed time
                        if days_elapsed > 0:
                            if milestone_date:
                                date_obj = datetime.strptime(milestone_date, "%Y-%m-%d")
                                date_obj += timedelta(days=days_elapsed)
                                milestone_date = date_obj.strftime("%Y-%m-%d")
                                milestone_entry["date"].set_date(milestone_date)
                        
                        # Update the float date to now
                        float_date = now.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        # If there's an error parsing dates, just use the current date
                        float_date = datetime.now().strftime("%Y-%m-%d")
                
                milestone_data = {
                    "name": milestone_entry["name"].get(),
                    "date": milestone_date,
                    "description": milestone_entry["description"].get(),
                    "floatOnRoadmap": float_on_roadmap,
                    "floatDate": float_date,
                    "additionalDetails": milestone_entry["additional_details"].get()
                }
                milestones.append(milestone_data)
            
            # Collect post-processing methods
            post_processing = []
            for pp_entry in pp_entries:
                suppliers = []
                for supplier_var in pp_entry["suppliers"]:
                    if supplier_var.get():
                        # Extract supplier ID from the selection
                        supplier_id = supplier_var.get().split(":")[0].strip()
                        suppliers.append(supplier_id)
                
                pp_data = {
                    "name": pp_entry["name"].get(),
                    "Supplier": suppliers
                }
                post_processing.append(pp_data)
            
            # Collect qualified machines
            qualified_machines = []
            for qm_entry in qm_entries:
                suppliers = []
                for supplier_var in qm_entry["suppliers"]:
                    if supplier_var.get():
                        # Extract supplier ID from the selection
                        supplier_id = supplier_var.get().split(":")[0].strip()
                        suppliers.append(supplier_id)
                
                qm_data = {
                    "machine": qm_entry["machine"].get(),
                    "Supplier": suppliers
                }
                qualified_machines.append(qm_data)
            
            # Collect NDT methods
            standard_ndt = []
            for ndt_var in ndt_entries:
                if ndt_var.get():
                    standard_ndt.append(ndt_var.get())
            
            # Collect funding opportunities
            related_funding_opps = []
            for funding_entry in funding_entries:
                if funding_entry["opportunity"].get():
                    # Extract opportunity ID from the selection
                    opp_id = funding_entry["opportunity"].get().split(":")[0].strip()
                    
                    # Check if pursuit is selected
                    if funding_entry["pursuit"].get():
                        # Extract pursuit ID from the selection
                        pursuit_id = funding_entry["pursuit"].get().split(":")[0].strip()
                        
                        # Add as a dictionary with both IDs
                        related_funding_opps.append({
                            "opportunityID": opp_id,
                            "pursuitID": pursuit_id
                        })
                    else:
                        # Try to find the first pursuit for this opportunity
                        for opp in self.data.get("fundingOpps", []):
                            if opp.get("id") == opp_id and opp.get("pursuits"):
                                first_pursuit = opp["pursuits"][0]
                                if "pursuitID" in first_pursuit:
                                    # Add as a dictionary with both IDs
                                    related_funding_opps.append({
                                        "opportunityID": opp_id,
                                        "pursuitID": first_pursuit["pursuitID"]
                                    })
                                    break
                        else:
                            # No pursuit found, add just the opportunity ID for backward compatibility
                            related_funding_opps.append(opp_id)
            
            # Create material object
            new_material = {
                "id": id_var.get(),
                "name": name_var.get(),
                "process": process_var.get(),
                "material": material_var.get(),
                "mrl": int(mrl_var.get()) if mrl_var.get() else None,
                "qualification": qualification_var.get(),
                "qualificationClass": qualification_class_var.get(),
                "statisticalBasis": statistical_basis_var.get(),
                "roadmap": roadmap_tasks,
                "milestones": milestones,
                "postProcessing": post_processing,
                "qualifiedMachines": qualified_machines,
                "standardNDT": standard_ndt,
                "relatedFundingOpps": related_funding_opps
            }
            
            # Determine which key to use
            materials_key = "materials" if "materials" in self.data else "materialSystems"
            
            # Check if we're editing an existing material
            if material:
                # Find the material index
                material_index = None
                for i, m in enumerate(self.data[materials_key]):
                    if m["id"] == material["id"]:
                        material_index = i
                        break
                
                if material_index is not None:
                    # Update existing material
                    self.data[materials_key][material_index] = new_material
                else:
                    # Material not found, add as new
                    self.data[materials_key].append(new_material)
            else:
                # Add new material
                if materials_key not in self.data:
                    self.data[materials_key] = []
                self.data[materials_key].append(new_material)
            
            # Save data
            self.manager.save_data()
            
            # Refresh treeview
            self.populate_materials_tree()
            
            # Close window
            add_window.destroy()
            
            # Show success message
            messagebox.showinfo("Success", "Material system saved successfully.")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Ensure the save button is correctly linked to the save_material function
        save_button = ttk.Button(button_frame, text="Save", command=save_material)
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=add_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def edit_material(self):
        # Get selected item
        selected_item = self.materials_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a material system to edit.")
            return
        
        # Get material ID
        material_id = self.materials_tree.item(selected_item[0], "values")[0]
        
        # Find material
        material = None
        materials_data = self.data.get("materials", self.data.get("materialSystems", []))
        for m in materials_data:
            if m["id"] == material_id:
                material = m
                break
        
        if not material:
            messagebox.showerror("Error", "Material system not found.")
            return
        
        # Create edit window
        self.add_material(material)
    
    def delete_material(self):
        # Get selected item
        selected_item = self.materials_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a material system to delete.")
            return
        
        # Get material ID
        material_id = self.materials_tree.item(selected_item[0], "values")[0]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this material system?"):
            return
        
        # Determine which key to use
        materials_key = "materials" if "materials" in self.data else "materialSystems"
        
        # Find material index
        material_index = None
        for i, material in enumerate(self.data[materials_key]):
            if material["id"] == material_id:
                material_index = i
                break
        
        if material_index is not None:
            # Delete material
            del self.data[materials_key][material_index]
            
            # Save data
            self.manager.save_data()
            
            # Refresh treeview
            self.populate_materials_tree()
            
            messagebox.showinfo("Success", "Material system deleted successfully.")
        else:
            messagebox.showerror("Error", "Material system not found.")
    
    def get_next_material_id(self):
        """Generate the next available material ID"""
        # Determine which key to use
        materials_key = "materials" if "materials" in self.data else "materialSystems"
        
        # Get existing IDs
        existing_ids = []
        for material in self.data.get(materials_key, []):
            if "id" in material:
                existing_ids.append(material["id"])
        
        # Find the highest numeric ID
        highest_num = 0
        for id_str in existing_ids:
            if id_str.startswith("MS"):
                try:
                    num = int(id_str[2:])
                    highest_num = max(highest_num, num)
                except ValueError:
                    pass
        
        # Generate next ID
        return f"MS{highest_num + 1}"
    
    def get_pursuit_name(self, opportunity_id, pursuit_id):
        """Get the name of a pursuit given its ID and the opportunity ID"""
        for opp in self.data.get("fundingOpps", []):
            if opp.get("id") == opportunity_id:
                for pursuit in opp.get("pursuits", []):
                    if pursuit.get("pursuitID") == pursuit_id:
                        return pursuit.get("pursuitName", "")
        return ""
    
    def search_materials(self):
        """Search material systems based on the search term"""
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.materials_tree.get_children():
            self.materials_tree.delete(item)
        
        # If search term is empty, show all materials
        if not search_term:
            self.populate_materials_tree()
            return
        
        # Get the materials data (handle both "materials" and "materialSystems" keys)
        materials_data = self.data.get("materials", self.data.get("materialSystems", []))
        
        # Create a mapping of funding opportunity IDs to names
        funding_id_to_name = {}
        for opp in self.data.get("fundingOpps", []):
            if "id" in opp and "announcementName" in opp:
                funding_id_to_name[opp["id"]] = opp["announcementName"]
        
        # Add matching materials to the tree
        for material in materials_data:
            # Check if search term is in any of the fields
            if (search_term in material.get("id", "").lower() or
                search_term in material.get("name", "").lower() or
                search_term in material.get("process", "").lower() or
                search_term in material.get("material", "").lower() or
                search_term in str(material.get("mrl", "")).lower() or
                search_term in material.get("qualification", "").lower()):
                
                # Get process and material values
                process = material.get("process", "")
                material_name = material.get("material", "")
                
                # Get post-processing methods
                post_processing = []
                for pp in material.get("postProcessing", []):
                    if "name" in pp:
                        post_processing.append(pp["name"])
                    elif "process" in pp:
                        post_processing.append(pp["process"])
                
                # Get qualified machines
                qualified_machines = []
                for qm in material.get("qualifiedMachines", []):
                    if "machine" in qm:
                        qualified_machines.append(qm["machine"])
                
                # Get funding opportunities (display names instead of IDs)
                funding_opps = []
                for opp_data in material.get("relatedFundingOpps", []):
                    if isinstance(opp_data, dict) and "opportunityID" in opp_data:
                        opp_id = opp_data["opportunityID"]
                        if opp_id in funding_id_to_name:
                            # Add opportunity name and pursuit name if available
                            opp_name = funding_id_to_name[opp_id]
                            if "pursuitID" in opp_data:
                                # Try to find the pursuit name
                                pursuit_name = self.get_pursuit_name(opp_id, opp_data["pursuitID"])
                                if pursuit_name:
                                    funding_opps.append(f"{opp_name} - {pursuit_name}")
                                else:
                                    funding_opps.append(opp_name)
                            else:
                                funding_opps.append(opp_name)
                        else:
                            # Opportunity not found, just use the ID
                            if "pursuitID" in opp_data:
                                funding_opps.append(f"{opp_id} - {opp_data['pursuitID']}")
                            else:
                                funding_opps.append(opp_id)
                    elif isinstance(opp_data, str):
                        # Handle string IDs for backward compatibility
                        opp_id = opp_data
                        if opp_id in funding_id_to_name:
                            opp_name = funding_id_to_name[opp_id]
                            
                            # Try to find the first pursuit for this opportunity
                            for opp in self.data.get("fundingOpps", []):
                                if opp.get("id") == opp_id and opp.get("pursuits"):
                                    first_pursuit = opp["pursuits"][0]
                                    if "pursuitName" in first_pursuit:
                                        funding_opps.append(f"{opp_name} - {first_pursuit['pursuitName']}")
                                        break
                            else:
                                # No pursuit found, just use the opportunity name
                                funding_opps.append(opp_name)
                        else:
                            funding_opps.append(opp_id)  # Fallback to ID if name not found
                
                # Format for display
                pp_display = ", ".join(post_processing) if post_processing else ""
                qm_display = ", ".join(qualified_machines) if qualified_machines else ""
                funding_display = ", ".join(funding_opps) if funding_opps else ""
                
                # Add to tree
                self.materials_tree.insert(
                    "", "end",
                    values=(
                        material.get("id", ""),
                        material.get("name", ""),
                        process,
                        material_name,
                        material.get("mrl", ""),
                        material.get("qualification", ""),
                        pp_display,
                        qm_display,
                        funding_display
                    )
                )
        
        # Update status
        count = len(self.materials_tree.get_children())
        self.update_status(f"Found {count} matching material systems")
    
    def clear_search(self):
        """Clear the search field and show all material systems"""
        self.search_var.set("")
        self.populate_materials_tree()
        self.update_status("Showing all material systems") 