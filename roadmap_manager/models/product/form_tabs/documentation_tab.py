import tkinter as tk
from tkinter import ttk
from .base_tab import BaseTab

class DocumentationTab(BaseTab):
    """Tab for documentation information"""
    
    def __init__(self, form):
        # Initialize attributes before calling parent constructor
        self.doc_entries = []
        super().__init__(form, "Documentation")
    
    def initialize(self):
        """Initialize the tab content"""
        # Ensure documentation exists and is a list
        if "documentation" not in self.product or not isinstance(self.product["documentation"], list):
            self.product["documentation"] = []
            print("Initialized empty documentation list")
        else:
            print(f"Found existing documentation: {self.product['documentation']}")
        
        # Create a frame for the documentation list
        self.docs_frame = ttk.Frame(self.frame)
        self.docs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a frame for existing documentation
        self.existing_docs_frame = ttk.Frame(self.docs_frame)
        self.existing_docs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add existing documentation entries
        for doc in self.product["documentation"]:
            if isinstance(doc, dict):
                doc_name = doc.get("name", "")
                print(f"Adding existing doc: {doc_name}")
                self.add_doc_entry(doc_name)
            elif isinstance(doc, str):
                print(f"Adding existing doc (string): {doc}")
                self.add_doc_entry(doc)
            else:
                print(f"Skipping non-dict/non-string doc: {doc}")
        
        # Add button for new documentation at the bottom
        add_btn = ttk.Button(self.docs_frame, text="Add Documentation", 
                           command=lambda: self.add_doc_entry())
        add_btn.pack(anchor=tk.W, pady=5)
    
    def add_doc_entry(self, doc_name=""):
        """Add a documentation entry to the form"""
        print(f"Adding doc entry with name={doc_name}")
        
        # Create a frame for this entry
        row_idx = len(self.doc_entries)
        doc_frame = ttk.Frame(self.existing_docs_frame)
        doc_frame.pack(fill=tk.X, pady=2)
        
        # Documentation name
        name_var = tk.StringVar(value=doc_name)
        name_entry = ttk.Entry(doc_frame, textvariable=name_var, width=50)
        name_entry.grid(row=0, column=0, padx=5)
        
        # Remove button
        def remove_entry():
            doc_frame.destroy()
            self.doc_entries.remove(entry_data)
        
        remove_btn = ttk.Button(doc_frame, text="Remove", command=remove_entry)
        remove_btn.grid(row=0, column=1, padx=5)
        
        # Store entry data
        entry_data = {
            "name": name_var,
            "frame": doc_frame
        }
        self.doc_entries.append(entry_data)
        print(f"Added doc entry: {doc_name}")
        return entry_data  # Return the entry data for testing/debugging
    
    def collect_data(self):
        """Collect data from the form and update the product"""
        print("Collecting documentation data...")
        
        # Get the documentation entries
        documentation = []
        
        # Iterate through the documentation entries
        for i, entry_widgets in enumerate(self.doc_entries):
            print(f"Processing documentation entry {i}")
            
            # Get the values
            doc_name = entry_widgets["name"].get().strip()
            
            print(f"  Doc Name: '{doc_name}'")
            
            # Only add if name is filled
            if doc_name:
                documentation.append(doc_name)
                print(f"  Added doc to documentation list")
            else:
                print(f"  Skipping entry with empty name")
        
        # Update the product
        self.product["documentation"] = documentation
        print(f"Updated product documentation: {self.product['documentation']}")
        
        # Return True to indicate validation passed
        return True 