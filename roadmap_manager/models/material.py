import tkinter as tk
from tkinter import ttk
from .base import BaseModel
from ..date_entry import DateEntry

class MaterialModel(BaseModel):
    """Model for managing material systems"""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.materials_tree = None
    
    def create_materials_tab(self, notebook):
        """Create the Material Systems tab in the notebook"""
        materials_frame = ttk.Frame(notebook)
        notebook.add(materials_frame, text="Material Systems")
        
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
        """Populate the materials treeview with data"""
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
                self.show_error("Error", "ID and Name are required fields")
                return
            
            # Get roadmap tasks
            roadmap_tasks = []
            for entry in task_entries:
                if not entry["task"].get():  # Skip empty tasks
                    continue
                    
                task = {
                    "task": entry["task"].get(),
                    "start": entry["start"].get_date(),
                    "end": entry["end"].get_date(),
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
                    "date": entry["date"].get_date(),
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
            
            self.update_status(f"Added material system: {new_material['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def edit_material(self, event):
        """Open a window to edit an existing material system"""
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
        edit_window = tk.Toplevel(self.manager.root)
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
                    start_entry.set_date(task["start"])
                except (ValueError, TypeError):
                    pass
            start_entry.grid(row=0, column=3, sticky=tk.W)
            
            ttk.Label(task_frame, text="End:").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
            end_entry = DateEntry(task_frame, width=10)
            if task:
                try:
                    end_entry.set_date(task["end"])
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
                    date_entry.set_date(milestone["date"])
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
                self.show_error("Error", "Name is required")
                return
            
            # Get roadmap tasks
            roadmap_tasks = []
            for entry in task_entries:
                if not entry["task"].get():  # Skip empty tasks
                    continue
                    
                task = {
                    "task": entry["task"].get(),
                    "start": entry["start"].get_date(),
                    "end": entry["end"].get_date(),
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
                    "date": entry["date"].get_date(),
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
            
            # Update the existing material instead of adding a new one
            material.update(new_material)
            
            # Refresh treeview
            self.populate_materials_tree()
            
            # Close window
            edit_window.destroy()
            
            self.update_status(f"Updated material system: {new_material['name']}")
        
        # Delete button function
        def delete_material():
            if self.confirm_delete(material['name']):
                # Remove material from data
                self.data["materialSystems"].remove(material)
                
                # Refresh treeview
                self.populate_materials_tree()
                
                # Close window
                edit_window.destroy()
                
                self.update_status(f"Deleted material system: {material['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_material).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5) 