import tkinter as tk
from tkinter import ttk
from .base import BaseModel

class ProgramModel(BaseModel):
    """Model for managing programs"""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.programs_tree = None
        self.search_entry = None
    
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
                
                values = (
                    program["id"],
                    program["name"],
                    program.get("sector", ""),
                    program.get("division", ""),
                    program.get("customerName", ""),
                    program.get("missionClass", "")
                )
                self.programs_tree.insert("", tk.END, values=values)
    
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
            values = (
                program["id"],
                program["name"],
                program.get("sector", ""),
                program.get("division", ""),
                program.get("customerName", ""),
                program.get("missionClass", "")
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
        add_window.geometry("500x400")
        add_window.grab_set()  # Make window modal
        
        # Use grid layout for the entire window
        main_frame = ttk.Frame(add_window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        add_window.grid_rowconfigure(0, weight=1)
        add_window.grid_columnconfigure(0, weight=1)
        
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
        
        # Save button
        def save_program():
            # Validate required fields
            if not name_var.get():
                self.show_error("Error", "Name is required")
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
            
            self.update_status(f"Added program: {new_program['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_program).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).grid(row=0, column=1, padx=5)
    
    def edit_program(self, event):
        """Open a window to edit an existing program"""
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
        edit_window = tk.Toplevel(self.manager.root)
        edit_window.title(f"Edit Program: {program['name']}")
        edit_window.geometry("500x400")
        edit_window.grab_set()  # Make window modal
        
        # Use grid layout for the entire window
        main_frame = ttk.Frame(edit_window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        edit_window.grid_rowconfigure(0, weight=1)
        edit_window.grid_columnconfigure(0, weight=1)
        
        # Create form fields
        ttk.Label(main_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        id_var = tk.StringVar(value=program["id"])
        ttk.Entry(main_frame, textvariable=id_var, state="readonly").grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        ttk.Label(main_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=program["name"])
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
        
        # Save button
        def save_program():
            # Validate required fields
            if not name_var.get():
                self.show_error("Error", "Name is required")
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
            
            self.update_status(f"Updated program: {program['name']}")
        
        # Delete button
        def delete_program():
            if self.confirm_delete(program['name']):
                # Remove program from data
                self.data["programs"].remove(program)
                
                # Refresh treeview
                self.populate_programs_tree()
                
                # Close window
                edit_window.destroy()
                
                self.update_status(f"Deleted program: {program['name']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_program).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_program).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).grid(row=0, column=2, padx=5) 