import tkinter as tk
from tkinter import ttk
from .base import BaseModel
from ..date_entry import DateEntry

class FundingModel(BaseModel):
    """Model for managing funding opportunities"""
    
    def __init__(self, manager):
        super().__init__(manager)
        self.funding_opps_tree = None
    
    def create_funding_opps_tab(self, notebook):
        """Create the Funding Opportunities tab in the notebook"""
        funding_frame = ttk.Frame(notebook)
        notebook.add(funding_frame, text="Funding Opportunities")
        
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
        """Populate the funding opportunities treeview with data"""
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
        """Open a window to add a new funding opportunity"""
        # Create a new window for adding an opportunity
        add_window = tk.Toplevel(self.manager.root)
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
                self.show_error("Error", "ID and Announcement Name are required fields")
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
            
            self.update_status(f"Added funding opportunity: {new_opp['announcementName']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(add_window)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_opp).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side=tk.LEFT, padx=5)
    
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
        
        # Create edit window
        edit_window = tk.Toplevel(self.manager.root)
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
                self.show_error("Error", "Announcement Name is required")
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
            
            self.update_status(f"Updated funding opportunity: {opp['announcementName']}")
        
        # Delete button
        def delete_opp():
            if self.confirm_delete(opp['announcementName']):
                # Remove opportunity from data
                self.data["fundingOpps"].remove(opp)
                
                # Refresh treeview
                self.populate_funding_opps_tree()
                
                # Close window
                edit_window.destroy()
                
                self.update_status(f"Deleted funding opportunity: {opp['announcementName']}")
        
        # Buttons at the bottom
        button_frame = ttk.Frame(edit_window)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_opp).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_opp).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5) 