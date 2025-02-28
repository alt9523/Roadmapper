import tkinter as tk
from tkinter import ttk
from ...date_entry import DateEntry
from .form_tabs.basic_info_tab import BasicInfoTab
from .form_tabs.requirements_tab import RequirementsTab
from .form_tabs.post_processing_tab import PostProcessingTab
from .form_tabs.design_tools_tab import DesignToolsTab
from .form_tabs.documentation_tab import DocumentationTab
from .form_tabs.special_ndt_tab import SpecialNDTTab
from .form_tabs.part_acceptance_tab import PartAcceptanceTab
from .form_tabs.roadmap_tab import RoadmapTab
from .form_tabs.milestones_tab import MilestonesTab
from .form_tabs.business_case_tab import BusinessCaseTab
import platform

class ProductForm:
    """Form for adding or editing a product"""
    
    def __init__(self, model, product, is_new=False):
        self.model = model
        self.product = product
        self.is_new = is_new
        
        # Create the form window
        self.window = tk.Toplevel(self.model.manager.root)
        self.window.title(f"{'Add' if is_new else 'Edit'} Product")
        self.window.geometry("800x600")
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
        self.tabs = {}
        
        # Initialize all tabs with proper error handling
        try:
            # Create tab instances
            self.tabs['basic_info'] = BasicInfoTab(self)
            self.tabs['requirements'] = RequirementsTab(self)
            self.tabs['post_processing'] = PostProcessingTab(self)
            self.tabs['design_tools'] = DesignToolsTab(self)
            self.tabs['documentation'] = DocumentationTab(self)
            self.tabs['special_ndt'] = SpecialNDTTab(self)
            self.tabs['part_acceptance'] = PartAcceptanceTab(self)
            self.tabs['roadmap'] = RoadmapTab(self)
            self.tabs['milestones'] = MilestonesTab(self)
            self.tabs['business_case'] = BusinessCaseTab(self)
            
            # Initialize all tabs after they've been created
            for tab_name, tab in self.tabs.items():
                try:
                    # Initialize the tab content
                    tab.initialize()
                    
                    # Bind mouse wheel events to the tab frame
                    if hasattr(tab, 'frame'):
                        system = platform.system()
                        if system == "Windows":
                            tab.frame.bind("<MouseWheel>", self._on_mousewheel_windows)
                        else:
                            tab.frame.bind("<Button-4>", self._on_mousewheel_linux_up)
                            tab.frame.bind("<Button-5>", self._on_mousewheel_linux_down)
                        
                        # Also bind to all children of the tab frame
                        self._bind_mousewheel_to_all_children(tab.frame)
                except Exception as e:
                    print(f"Error initializing tab {tab_name}: {str(e)}")
                    # Continue with other tabs even if one fails
        except Exception as e:
            print(f"Error creating tabs: {str(e)}")
        
        # Add buttons at the bottom
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=2, column=0, sticky=tk.E, pady=10)
        
        ttk.Button(self.button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        
        if not is_new:
            ttk.Button(self.button_frame, text="Delete", command=self.delete).pack(side=tk.LEFT, padx=5)
            
        ttk.Button(self.button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
    
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
            
            # Also bind to each tab as they're created
            for tab_name, tab in getattr(self, 'tabs', {}).items():
                if hasattr(tab, 'frame'):
                    tab.frame.bind("<MouseWheel>", self._on_mousewheel_windows)
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
            
            # Also bind to each tab as they're created
            for tab_name, tab in getattr(self, 'tabs', {}).items():
                if hasattr(tab, 'frame'):
                    tab.frame.bind("<Button-4>", self._on_mousewheel_linux_up)
                    tab.frame.bind("<Button-5>", self._on_mousewheel_linux_down)
        
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
    
    def save(self):
        """Save the product data"""
        print("Starting to save product data")
        print(f"Before collecting data - Design Tools: {self.product.get('designTools', [])}")
        print(f"Before collecting data - Documentation: {self.product.get('documentation', [])}")
        
        # Collect data from all tabs first
        for tab_name, tab in self.tabs.items():
            print(f"Collecting data from tab: {tab_name}")
            try:
                tab.collect_data()
                print(f"After {tab_name} - Design Tools: {self.product.get('designTools', [])}")
                print(f"After {tab_name} - Documentation: {self.product.get('documentation', [])}")
            except Exception as e:
                print(f"Error collecting data from {tab_name}: {str(e)}")
        
        print(f"After collecting all data - Design Tools: {self.product.get('designTools', [])}")
        print(f"After collecting all data - Documentation: {self.product.get('documentation', [])}")
        
        # Validate required fields after collecting data
        if not self.product["id"] or not self.product["name"]:
            self.model.show_error("Error", "ID and Name are required fields")
            return
        
        # Save the product
        self.model.save_product(self.product, self.is_new)
        
        # Close the window
        self.window.destroy()
    
    def delete(self):
        """Delete the product"""
        if self.model.delete_product(self.product):
            self.window.destroy() 