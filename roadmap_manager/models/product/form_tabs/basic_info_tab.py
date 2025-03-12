import tkinter as tk
from tkinter import ttk
import datetime
from ....date_entry import DateEntry
from .base_tab import BaseTab

class BasicInfoTab(BaseTab):
    """Tab for basic product information"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.material_entries = []
        self.trl_history_entries = []
        super().__init__(form, "Basic Info")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure materialSystems exist and are lists
        if "materialSystems" not in self.product or not isinstance(self.product["materialSystems"], list):
            self.product["materialSystems"] = []
        
        # Ensure trlHistory exists and is a list
        if "trlHistory" not in self.product or not isinstance(self.product["trlHistory"], list):
            self.product["trlHistory"] = []
        
        # Create form fields for basic info
        ttk.Label(self.frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.id_var = tk.StringVar(value=self.product["id"])
        ttk.Entry(self.frame, textvariable=self.id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(self.frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar(value=self.product["name"])
        ttk.Entry(self.frame, textvariable=self.name_var).grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(self.frame, text="TRL:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.trl_var = tk.StringVar(value=self.product.get("trl", ""))
        
        # Create a frame for TRL selection and history
        trl_frame = ttk.Frame(self.frame)
        trl_frame.grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # TRL dropdown
        trl_combo = ttk.Combobox(trl_frame, textvariable=self.trl_var, values=list(range(1, 10)), width=5)
        trl_combo.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Add button to record TRL change
        add_trl_btn = ttk.Button(trl_frame, text="Record TRL Change", 
                               command=self.record_trl_change)
        add_trl_btn.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Create a frame for TRL history
        self.trl_history_frame = ttk.LabelFrame(self.frame, text="TRL History")
        self.trl_history_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Add headers for TRL history
        ttk.Label(self.trl_history_frame, text="TRL Level").grid(row=0, column=0, sticky=tk.W, padx=10, pady=2)
        ttk.Label(self.trl_history_frame, text="Date").grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)
        ttk.Label(self.trl_history_frame, text="Actions").grid(row=0, column=2, sticky=tk.W, padx=10, pady=2)
        
        # Add existing TRL history entries
        for i, entry in enumerate(self.product.get("trlHistory", [])):
            if isinstance(entry, dict):
                trl_level = entry.get("level", "")
                trl_date = entry.get("date", "")
                self.add_trl_history_entry(trl_level, trl_date, i+1)
        
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
    
    def record_trl_change(self):
        """Record a change in TRL level"""
        current_trl = self.trl_var.get()
        if not current_trl:
            return
            
        # Get current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Add to history
        row_idx = len(self.trl_history_entries) + 1  # +1 for header row
        self.add_trl_history_entry(current_trl, current_date, row_idx)
    
    def add_trl_history_entry(self, trl_level, trl_date, row_idx):
        """Add a TRL history entry to the form"""
        # TRL level
        trl_level_var = tk.StringVar(value=trl_level)
        trl_level_entry = ttk.Entry(self.trl_history_frame, textvariable=trl_level_var, width=5)
        trl_level_entry.grid(row=row_idx, column=0, padx=10, pady=2)
        
        # TRL date
        trl_date_var = tk.StringVar(value=trl_date)
        trl_date_entry = DateEntry(self.trl_history_frame, textvariable=trl_date_var, width=12)
        trl_date_entry.grid(row=row_idx, column=1, padx=10, pady=2)
        
        # Remove button
        def remove_entry():
            # Remove widgets from grid
            trl_level_entry.grid_forget()
            trl_date_entry.grid_forget()
            remove_btn.grid_forget()
            
            # Remove from list
            self.trl_history_entries.remove(entry_data)
            
            # Reindex remaining entries
            for i, entry in enumerate(self.trl_history_entries):
                entry["trl_level_entry"].grid(row=i+1, column=0)
                entry["trl_date_entry"].grid(row=i+1, column=1)
                entry["remove_btn"].grid(row=i+1, column=2)
        
        remove_btn = ttk.Button(self.trl_history_frame, text="Remove", command=remove_entry)
        remove_btn.grid(row=row_idx, column=2, padx=10, pady=2)
        
        # Store entry data
        entry_data = {
            "trl_level_var": trl_level_var,
            "trl_date_var": trl_date_var,
            "trl_level_entry": trl_level_entry,
            "trl_date_entry": trl_date_entry,
            "remove_btn": remove_btn
        }
        self.trl_history_entries.append(entry_data)
    
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
        
        # Create material options list and a mapping for display to ID
        material_options = []
        material_id_to_name = {}
        material_name_to_id = {}
        material_id_to_printers = {}  # Map to store qualified printers for each material
        
        for m in self.model.data.get("materialSystems", []):
            if isinstance(m, dict) and "id" in m and "name" in m:
                display_text = f"{m['id']} - {m['name']}"
                material_options.append(display_text)
                material_id_to_name[m['id']] = m['name']
                material_name_to_id[m['name']] = m['id']
                
                # Store qualified printers for this material
                if "qualifiedPrinters" in m and isinstance(m["qualifiedPrinters"], list):
                    material_id_to_printers[m['id']] = m["qualifiedPrinters"]
        
        material_combo['values'] = material_options
        
        # If we have a material ID, set the display to show the name
        if material_id and material_id in material_id_to_name:
            material_var.set(material_id_to_name[material_id])
        
        material_combo.grid(row=0, column=0, padx=5)
        
        # Create a frame for printers
        printers_frame = ttk.LabelFrame(mat_frame, text="Printers")
        printers_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # List to store printer entries
        printer_entries = []
        
        # Function to get qualified printers for the selected material
        def get_qualified_printers():
            selected_material = material_var.get()
            material_id = None
            
            # First check if it's in ID-Name format
            if " - " in selected_material:
                material_id = selected_material.split(" - ")[0]
            else:
                # Look up by name
                material_id = material_name_to_id.get(selected_material)
            
            if material_id and material_id in material_id_to_printers:
                return material_id_to_printers[material_id]
            return []
        
        # Function to update printer dropdowns when material changes
        def update_printer_options(*args):
            qualified_printers = get_qualified_printers()
            for entry in printer_entries:
                entry["printer_combo"]['values'] = qualified_printers
        
        # Bind material selection to update printer options
        material_var.trace_add("write", update_printer_options)
        
        # Function to add a printer entry
        def add_printer(printer=""):
            # Create a frame for this printer
            row_idx = len(printer_entries)
            printer_frame = ttk.Frame(printers_frame)
            printer_frame.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
            
            # Printer dropdown
            printer_var = tk.StringVar(value=printer)
            qualified_printers = get_qualified_printers()
            
            printer_combo = ttk.Combobox(printer_frame, textvariable=printer_var, width=30)
            printer_combo['values'] = qualified_printers
            printer_combo.grid(row=0, column=0, padx=5)
            
            # Remove button
            def remove_printer():
                printer_frame.destroy()
                printer_entries.remove(printer_data)
            
            remove_btn = ttk.Button(printer_frame, text="Remove", command=remove_printer)
            remove_btn.grid(row=0, column=1, padx=5)
            
            # Store printer data
            printer_data = {
                "printer_var": printer_var,
                "printer_combo": printer_combo,
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
        
        # Get TRL history
        trl_history = []
        for entry in self.trl_history_entries:
            trl_level = entry["trl_level_var"].get()
            trl_date = entry["trl_date_var"].get()
            
            if trl_level and trl_date:
                trl_history.append({
                    "level": trl_level,
                    "date": trl_date
                })
        
        # Sort TRL history by date
        trl_history.sort(key=lambda x: x["date"] if x["date"] else "")
        self.product["trlHistory"] = trl_history
        
        # Get selected material systems
        selected_materials = []
        for entry in self.material_entries:
            material_name = entry["material_var"].get()
            if material_name:
                # Find the material ID for this name
                material_id = None
                
                # First check if it's already in ID format
                if " - " in material_name:
                    material_id = material_name.split(" - ")[0]
                else:
                    # Look up the ID by name
                    for m in self.model.data.get("materialSystems", []):
                        if isinstance(m, dict) and "id" in m and "name" in m and m["name"] == material_name:
                            material_id = m["id"]
                            break
                
                # If we couldn't find an ID, use the name as is (might be a direct ID)
                if not material_id:
                    material_id = material_name
                
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
        
        # Return True to indicate validation passed
        return True 