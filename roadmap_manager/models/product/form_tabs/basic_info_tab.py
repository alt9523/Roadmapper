import tkinter as tk
from tkinter import ttk
from ....date_entry import DateEntry
from .base_tab import BaseTab

class BasicInfoTab(BaseTab):
    """Tab for basic product information"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.program_entries = []
        self.material_entries = []
        super().__init__(form, "Basic Info")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure programs and materialSystems exist and are lists
        if "programs" not in self.product or not isinstance(self.product["programs"], list):
            self.product["programs"] = []
        
        if "materialSystems" not in self.product or not isinstance(self.product["materialSystems"], list):
            self.product["materialSystems"] = []
        
        # Create form fields for basic info
        ttk.Label(self.frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.id_var = tk.StringVar(value=self.product["id"])
        ttk.Entry(self.frame, textvariable=self.id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(self.frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar(value=self.product["name"])
        ttk.Entry(self.frame, textvariable=self.name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(self.frame, text="TRL:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.trl_var = tk.StringVar(value=self.product.get("trl", ""))
        ttk.Combobox(self.frame, textvariable=self.trl_var, values=list(range(1, 10))).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Programs selection
        ttk.Label(self.frame, text="Programs:").grid(row=3, column=0, sticky=tk.NW, padx=10, pady=5)
        self.programs_frame = ttk.Frame(self.frame)
        self.programs_frame.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Add button for new program
        add_prog_btn = ttk.Button(self.programs_frame, text="Add Program", 
                                command=lambda: self.add_program_entry())
        add_prog_btn.grid(row=100, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Add existing program entries
        for prog_entry in self.product["programs"]:
            if isinstance(prog_entry, dict):
                program_id = prog_entry.get("programID", "")
                need_date = prog_entry.get("needDate", "")
                self.add_program_entry(program_id, need_date)
        
        # Material systems selection
        ttk.Label(self.frame, text="Material Systems:").grid(row=4, column=0, sticky=tk.NW, padx=10, pady=5)
        self.materials_frame = ttk.Frame(self.frame)
        self.materials_frame.grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Add button for new material system
        add_mat_btn = ttk.Button(self.materials_frame, text="Add Material System", 
                               command=lambda: self.add_material_entry())
        add_mat_btn.grid(row=100, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Add existing material system entries
        for mat_entry in self.product["materialSystems"]:
            if isinstance(mat_entry, dict):
                material_id = mat_entry.get("materialID", "")
                printers = mat_entry.get("printer", [])
                self.add_material_entry(material_id, printers)
    
    def add_program_entry(self, program_id="", need_date=""):
        """Add a program entry to the form"""
        # Create a frame for this entry
        row_idx = len(self.program_entries)
        prog_frame = ttk.Frame(self.programs_frame)
        prog_frame.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Program dropdown
        program_var = tk.StringVar(value=program_id)
        program_combo = ttk.Combobox(prog_frame, textvariable=program_var, width=30)
        
        # Create program options list
        program_options = []
        for p in self.model.data.get("programs", []):
            if isinstance(p, dict) and "id" in p and "name" in p:
                program_options.append(f"{p['id']} - {p['name']}")
        
        program_combo['values'] = program_options
        program_combo.grid(row=0, column=0, padx=5)
        
        # Need date entry
        ttk.Label(prog_frame, text="Need Date:").grid(row=0, column=1, padx=5)
        date_var = tk.StringVar(value=need_date)
        
        # Create the DateEntry widget with the correct initial value
        date_entry = DateEntry(prog_frame, textvariable=date_var, width=12)
        
        # Explicitly set the date if provided
        if need_date:
            date_entry.set_date(need_date)
            
        date_entry.grid(row=0, column=2, padx=5)
        
        # Remove button
        def remove_entry():
            prog_frame.destroy()
            self.program_entries.remove(entry_data)
        
        remove_btn = ttk.Button(prog_frame, text="Remove", command=remove_entry)
        remove_btn.grid(row=0, column=3, padx=5)
        
        # Store entry data
        entry_data = {
            "program_var": program_var,
            "date_var": date_var,
            "date_entry": date_entry,  # Store the actual DateEntry widget
            "frame": prog_frame
        }
        self.program_entries.append(entry_data)
    
    def add_material_entry(self, material_id="", printers=None):
        """Add a material system entry to the form"""
        if printers is None:
            printers = []
        
        # Create a frame for this entry
        row_idx = len(self.material_entries)
        mat_frame = ttk.Frame(self.materials_frame)
        mat_frame.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Material system dropdown
        material_var = tk.StringVar(value=material_id)
        material_combo = ttk.Combobox(mat_frame, textvariable=material_var, width=30)
        
        # Create material options list
        material_options = []
        for m in self.model.data.get("materialSystems", []):
            if isinstance(m, dict) and "id" in m and "name" in m:
                material_options.append(f"{m['id']} - {m['name']}")
        
        material_combo['values'] = material_options
        material_combo.grid(row=0, column=0, padx=5)
        
        # Create a frame for printers
        printers_frame = ttk.LabelFrame(mat_frame, text="Printers")
        printers_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # List to store printer entries
        printer_entries = []
        
        # Function to add a printer entry
        def add_printer(printer=""):
            # Create a frame for this printer
            row_idx = len(printer_entries)
            printer_frame = ttk.Frame(printers_frame)
            printer_frame.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
            
            # Printer entry
            printer_var = tk.StringVar(value=printer)
            printer_entry = ttk.Entry(printer_frame, textvariable=printer_var, width=30)
            printer_entry.grid(row=0, column=0, padx=5)
            
            # Remove button
            def remove_printer():
                printer_frame.destroy()
                printer_entries.remove(printer_data)
            
            remove_btn = ttk.Button(printer_frame, text="Remove", command=remove_printer)
            remove_btn.grid(row=0, column=1, padx=5)
            
            # Store printer data
            printer_data = {
                "printer_var": printer_var,
                "frame": printer_frame
            }
            printer_entries.append(printer_data)
        
        # Add existing printers
        for printer in printers:
            add_printer(printer)
        
        # Add button for new printer
        add_printer_btn = ttk.Button(printers_frame, text="Add Printer", 
                                  command=lambda: add_printer())
        add_printer_btn.grid(row=100, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Remove button for material system
        def remove_entry():
            mat_frame.destroy()
            self.material_entries.remove(entry_data)
        
        remove_btn = ttk.Button(mat_frame, text="Remove Material", command=remove_entry)
        remove_btn.grid(row=0, column=3, padx=5)
        
        # Store entry data
        entry_data = {
            "material_var": material_var,
            "printer_entries": printer_entries,
            "frame": mat_frame
        }
        self.material_entries.append(entry_data)
    
    def collect_data(self):
        """Collect data from the tab"""
        # Update basic info
        self.product["name"] = self.name_var.get()
        self.product["trl"] = self.trl_var.get()
        
        # Get selected programs
        selected_programs = []
        for entry in self.program_entries:
            program_full = entry["program_var"].get()
            if program_full:
                # Extract program ID from the dropdown value (format: "ID - Name")
                program_id = program_full.split(" - ")[0] if " - " in program_full else program_full
                
                # Get the date directly from the DateEntry widget to ensure we have the most up-to-date value
                need_date = entry["date_entry"].get_date() if hasattr(entry, "date_entry") and entry["date_entry"] else entry["date_var"].get()
                
                selected_programs.append({
                    "programID": program_id,
                    "needDate": need_date
                })
        self.product["programs"] = selected_programs
        
        # Get selected material systems
        selected_materials = []
        for entry in self.material_entries:
            material_full = entry["material_var"].get()
            if material_full:
                # Extract material ID from the dropdown value (format: "ID - Name")
                material_id = material_full.split(" - ")[0] if " - " in material_full else material_full
                
                # Get printers from printer entries
                printers = []
                for printer_entry in entry["printer_entries"]:
                    printer = printer_entry["printer_var"].get()
                    if printer:
                        printers.append(printer)
                
                selected_materials.append({
                    "materialID": material_id,
                    "printer": printers
                })
        self.product["materialSystems"] = selected_materials 