import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ui.input_panel import InputPanel
from ui.chart_panel import ChartPanel
from data.manager import DataManager

class ChartApplication:
    """Main application window with client tabs and chart management."""
    
    def __init__(self, root=None):
        """Initialize the application with a tkinter root window."""
        # Create root window if not provided
        if root is None:
            self.root = tk.Tk()
            self.root.title("Financial Charts - Client Dashboard")
            self.root.geometry("900x700")
        else:
            self.root = root
            
        # Track open client tabs
        self.client_tabs = {}
        
        # Create tab control first
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both")
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Initialize UI components
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main UI components."""
        # Add welcome tab
        welcome_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(welcome_frame, text="Welcome")
        
        # Add welcome content
        welcome_label = tk.Label(
            welcome_frame, 
            text="Welcome to Financial Charts!\n\nSelect a client tab or create a new one.",
            font=("Arial", 14)
        )
        welcome_label.pack(pady=20)
        
        # Add new client button
        new_client_btn = tk.Button(
            welcome_frame, 
            text="Create New Client", 
            command=self.create_new_client_tab,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11),
            padx=10,
            pady=5
        )
        new_client_btn.pack(pady=10)
        
        # Add client list frame
        client_list_frame = ttk.LabelFrame(welcome_frame, text="Existing Clients")
        client_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add client list
        self.client_listbox = tk.Listbox(client_list_frame, font=("Arial", 11), height=10)
        self.client_listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(client_list_frame, orient="vertical", command=self.client_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.client_listbox.config(yscrollcommand=scrollbar.set)
        
        # Add client list buttons
        client_buttons_frame = tk.Frame(client_list_frame)
        client_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        open_client_btn = tk.Button(
            client_buttons_frame,
            text="Open Selected Client",
            command=self.open_selected_client
        )
        open_client_btn.pack(side=tk.LEFT, padx=5)
        
        delete_client_btn = tk.Button(
            client_buttons_frame,
            text="Delete Selected Client",
            command=self.delete_selected_client
        )
        delete_client_btn.pack(side=tk.RIGHT, padx=5)
        
        # Double click to open client
        self.client_listbox.bind("<Double-1>", lambda event: self.open_selected_client())
        
        # Populate client list
        self.update_client_list()
    
    def update_client_list(self):
        """Update the client list with current clients."""
        self.client_listbox.delete(0, tk.END)
        client_list = self.data_manager.get_client_list()
        for client_id, client_name in client_list:
            self.client_listbox.insert(tk.END, f"{client_name} ({client_id})")
    
    def open_selected_client(self):
        """Open the selected client from the listbox."""
        selection = self.client_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a client to open.")
            return
        
        # Get the client info from the selection text
        client_text = self.client_listbox.get(selection[0])
        
        try:
            # Try to parse the client ID and name
            # The format is expected to be: "Client Name (client_id)"
            if '(' in client_text and ')' in client_text:
                client_id = client_text.split('(')[-1].strip(')')
                client_name = client_text.split(' (')[0] if ' (' in client_text else client_text.split('(')[0].strip()
            else:
                # Fallback if the format is not as expected
                client_id = client_text.lower().replace(' ', '_').replace('-', '_')
                client_name = client_text
            
            # Verify client exists
            if client_id not in self.data_manager.clients:
                messagebox.showerror("Error", f"Client '{client_name}' (ID: {client_id}) not found.")
                return
            
            # Open the client tab
            self.open_client_tab(client_id, client_name)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open client: {e}")
            import traceback
            traceback.print_exc()
    
    def delete_selected_client(self):
        """Delete the selected client from the data manager."""
        selection = self.client_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a client to delete.")
            return
        
        # Get the client info from the selection text
        client_text = self.client_listbox.get(selection[0])
        
        try:
            # Try to parse the client ID and name
            # The format is expected to be: "Client Name (client_id)"
            if '(' in client_text and ')' in client_text:
                client_id = client_text.split('(')[-1].strip(')')
                client_name = client_text.split(' (')[0] if ' (' in client_text else client_text.split('(')[0].strip()
            else:
                # Fallback if the format is not as expected
                client_id = client_text.lower().replace(' ', '_').replace('-', '_')
                client_name = client_text
            
            # Verify client exists
            if client_id not in self.data_manager.clients:
                messagebox.showerror("Error", f"Client '{client_name}' (ID: {client_id}) not found.")
                return
            
            # Confirm deletion
            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete client '{client_name}'? This cannot be undone."
            )
            if confirm:
                # Check if the client tab is open
                if client_id in self.client_tabs:
                    # Close the tab
                    tab_idx = self.tab_control.index(self.client_tabs[client_id]["frame"])
                    self.tab_control.forget(tab_idx)
                    del self.client_tabs[client_id]
                
                # Delete the client from the data manager
                self.data_manager.delete_client(client_id)
                self.data_manager.save_data()
                
                # Update the client list
                self.update_client_list()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete client: {e}")
            import traceback
            traceback.print_exc()
    
    def create_new_client_tab(self):
        """Create a new client tab."""
        # Ask for client name
        client_name = simpledialog.askstring(
            "New Client", 
            "Enter client name:",
            parent=self.root
        )
        
        if not client_name:
            return  # User cancelled or entered empty name
        
        # Create a client ID based on the name (lowercase, spaces to underscores)
        base_client_id = client_name.lower().replace(' ', '_').replace('-', '_')
        client_id = base_client_id
        
        # Check if client ID already exists and make it unique if needed
        counter = 1
        while client_id in self.data_manager.clients:
            client_id = f"{base_client_id}_{counter}"
            counter += 1
        
        # Add the client to the data manager
        self.data_manager.add_client(client_id, client_name)
        self.data_manager.save_data()
        
        # Update the client list
        self.update_client_list()
        
        # Open the client tab
        self.open_client_tab(client_id, client_name)
        
    def open_client_tab(self, client_id, client_name):
        """Open a tab for the specified client."""
        # Check if already open
        if client_id in self.client_tabs:
            # Select the existing tab
            tab_index = self.tab_control.index(self.client_tabs[client_id]["frame"])
            self.tab_control.select(tab_index)
            return
        
        try:
            # Validate client exists
            if client_id not in self.data_manager.clients:
                messagebox.showerror("Error", f"Client '{client_name}' (ID: {client_id}) not found.")
                return
            
            # Ensure client data structure is valid
            if 'datasets' not in self.data_manager.clients[client_id]:
                self.data_manager.clients[client_id]['datasets'] = {}
                self.data_manager.save_data()
            
            # Create new tab frame
            client_frame = ttk.Frame(self.tab_control)
            self.tab_control.add(client_frame, text=client_name)
            
            # Add client components
            input_panel = InputPanel(client_frame, self.data_manager, client_id)
            chart_panel = ChartPanel(client_frame, self.data_manager, client_id)
            
            # Connect input panel to chart panel
            input_panel.set_chart_panel(chart_panel)
            
            # Store reference
            self.client_tabs[client_id] = {
                "frame": client_frame,
                "input_panel": input_panel,
                "chart_panel": chart_panel
            }
            
            # Select the new tab
            tab_index = self.tab_control.index(client_frame)
            self.tab_control.select(tab_index)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open client tab: {e}")
            import traceback
            traceback.print_exc()
    
    def detach_tab(self, client_id):
        """Detach a client tab to a separate window."""
        if client_id not in self.client_tabs:
            return
            
        # Get the tab info
        tab_info = self.client_tabs[client_id]
        client_name = self.data_manager.clients[client_id]["name"]
        
        # Create a new toplevel window
        detached_window = tk.Toplevel(self.root)
        detached_window.title(f"{client_name} - Detached View")
        detached_window.geometry("900x700")
        
        # Create new components in the detached window
        new_frame = ttk.Frame(detached_window)
        new_frame.pack(fill="both", expand=True)
        
        input_panel = InputPanel(new_frame, self.data_manager, client_id)
        chart_panel = ChartPanel(new_frame, self.data_manager, client_id)
        
        # Connect input panel to chart panel
        input_panel.set_chart_panel(chart_panel)
        
        # Add a button to re-attach the window
        reattach_btn = tk.Button(
            detached_window,
            text="Re-attach Tab",
            command=lambda: self.reattach_tab(detached_window, client_id)
        )
        reattach_btn.pack(side=tk.BOTTOM, pady=5)
        
        # Remove the tab from the notebook
        tab_index = self.tab_control.index(tab_info["frame"])
        self.tab_control.forget(tab_index)
        
        # Update tab info
        self.client_tabs[client_id] = {
            "frame": new_frame,
            "input_panel": input_panel,
            "chart_panel": chart_panel,
            "detached_window": detached_window,
            "is_detached": True
        }
        
        # Handle window close event
        detached_window.protocol("WM_DELETE_WINDOW", 
                               lambda: self.reattach_tab(detached_window, client_id))
    
    def reattach_tab(self, detached_window, client_id):
        """Re-attach a detached tab to the main window."""
        if client_id not in self.client_tabs or "is_detached" not in self.client_tabs[client_id]:
            return
            
        # Get client name
        client_name = self.data_manager.clients[client_id]["name"]
        
        # Create new tab frame
        client_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(client_frame, text=client_name)
        
        # Add client components
        input_panel = InputPanel(client_frame, self.data_manager, client_id)
        chart_panel = ChartPanel(client_frame, self.data_manager, client_id)
        
        # Connect input panel to chart panel
        input_panel.set_chart_panel(chart_panel)
        
        # Update tab info
        self.client_tabs[client_id] = {
            "frame": client_frame,
            "input_panel": input_panel,
            "chart_panel": chart_panel
        }
        
        # Select the new tab
        tab_index = self.tab_control.index(client_frame)
        self.tab_control.select(tab_index)
        
        # Close the detached window
        detached_window.destroy()
    
    def run(self):
        """Start the main application loop."""
        self.root.mainloop() 