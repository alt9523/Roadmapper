import tkinter as tk
from tkinter import ttk
from .base import BaseModel
from ..date_entry import DateEntry
from .funding_form import FundingForm

class FundingModel(BaseModel):
    """Model for managing funding opportunities"""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.funding_opps_tree = None
    
    def create_funding_opps_tab(self, notebook):
        """Create the Funding Opportunities tab in the notebook"""
        funding_frame = ttk.Frame(notebook)
        notebook.add(funding_frame, text="Funding Opportunities")
        
        # Create top frame with buttons and search
        top_frame = ttk.Frame(funding_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        add_button = ttk.Button(top_frame, text="Add Opportunity", command=self.add_funding_opp)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Add search field
        ttk.Label(top_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Add search button
        ttk.Button(top_frame, text="Search", command=self.search_funding_opps).pack(side=tk.LEFT, padx=5)
        
        # Add clear button
        ttk.Button(top_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Bind the Enter key to the search function
        search_entry.bind("<Return>", lambda event: self.search_funding_opps())
        
        # Create treeview
        columns = ("ID", "Announcement Name", "Pursuit Type", "Close Date", "Solicitation Number", "Customer")
        self.funding_opps_tree = ttk.Treeview(funding_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.funding_opps_tree.heading(col, text=col)
            self.funding_opps_tree.column(col, width=100)
        
        # Adjust column widths
        self.funding_opps_tree.column("Announcement Name", width=200)
        self.funding_opps_tree.column("Solicitation Number", width=150)
        
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
        """Populate the funding opportunities treeview with data"""
        # Clear existing items
        for item in self.funding_opps_tree.get_children():
            self.funding_opps_tree.delete(item)
        
        # Add opportunities to treeview
        for opp in self.data["fundingOpps"]:
            values = (
                opp["id"],
                opp.get("announcementName", ""),
                opp.get("pursuitType", ""),
                opp.get("closeDate", ""),
                opp.get("solicitationNumber", ""),
                opp.get("customer", "")
            )
            self.funding_opps_tree.insert("", tk.END, values=values)
    
    def add_funding_opp(self):
        """Open a window to add a new funding opportunity"""
        # Generate the next available ID
        next_id = self.generate_next_id()
        
        # Create a new empty opportunity
        new_opp = {
            "id": next_id,
            "announcementName": "",
            "pursuitType": "",
            "closeDate": "",
            "solicitationNumber": "",
            "fundingAmount": "",
            "customer": "",
            "pursuits": []
        }
        
        # Open the funding form
        FundingForm(self, new_opp, is_new=True)
    
    def generate_next_id(self):
        """Generate the next available ID for a funding opportunity"""
        # Get all existing IDs
        existing_ids = [opp["id"] for opp in self.data["fundingOpps"]]
        
        # Find the highest numeric part of the IDs
        highest_num = 0
        for id_str in existing_ids:
            if id_str.startswith("OPP"):
                try:
                    num = int(id_str[3:])
                    highest_num = max(highest_num, num)
                except ValueError:
                    pass
        
        # Generate the next ID
        next_id = f"OPP{highest_num + 1}"
        return next_id
    
    def edit_funding_opp(self, event):
        """Open a window to edit an existing funding opportunity"""
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
        
        # Open the funding form
        FundingForm(self, opp, is_new=False)
    
    def search_funding_opps(self):
        """Search funding opportunities based on the search term"""
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.funding_opps_tree.get_children():
            self.funding_opps_tree.delete(item)
        
        # If search term is empty, show all opportunities
        if not search_term:
            self.populate_funding_opps_tree()
            return
        
        # Add matching opportunities to treeview
        for opp in self.data["fundingOpps"]:
            # Check if search term is in ID, name, or other fields
            if (search_term in opp["id"].lower() or 
                search_term in opp.get("announcementName", "").lower() or 
                search_term in opp.get("pursuitType", "").lower() or
                search_term in opp.get("solicitationNumber", "").lower() or
                search_term in opp.get("customer", "").lower()):
                
                values = (
                    opp["id"],
                    opp.get("announcementName", ""),
                    opp.get("pursuitType", ""),
                    opp.get("closeDate", ""),
                    opp.get("solicitationNumber", ""),
                    opp.get("customer", "")
                )
                self.funding_opps_tree.insert("", tk.END, values=values)
        
        # Update status
        count = len(self.funding_opps_tree.get_children())
        self.update_status(f"Found {count} matching funding opportunities")
    
    def clear_search(self):
        """Clear the search field and show all opportunities"""
        self.search_var.set("")
        self.populate_funding_opps_tree()
        self.update_status("Showing all funding opportunities") 