import tkinter as tk
from tkinter import filedialog, messagebox
import os

class InputPanel:
    """Panel for data input via clipboard, CSV upload, or other methods."""
    
    def __init__(self, parent, data_manager, client_id):
        """Initialize the input panel.
        
        Args:
            parent: The parent frame/container
            data_manager: Reference to the central data manager
            client_id: The ID of the client this panel belongs to
        """
        self.parent = parent
        self.data_manager = data_manager
        self.client_id = client_id
        self.chart_panel = None
        
        # Create main frame
        self.frame = tk.LabelFrame(parent, text="Data Input")
        self.frame.pack(fill="x", padx=10, pady=5)
        
        # Create UI components
        self.create_widgets()
    
    def set_chart_panel(self, chart_panel):
        """Set the chart panel reference for communication."""
        self.chart_panel = chart_panel
        # Update instructions based on current chart type
        self.update_instructions(chart_panel.chart_type.get())
    
    def create_widgets(self):
        """Create all widgets for the input panel."""
        # Instructions
        self.instructions_var = tk.StringVar()
        self.instructions_var.set(
            "Copy data from Excel/Google Sheets and paste below.\n"
            "Format depends on selected chart type."
        )
        instructions_label = tk.Label(
            self.frame, 
            textvariable=self.instructions_var,
            justify=tk.LEFT, 
            anchor="w",
            wraplength=500
        )
        instructions_label.pack(fill="x", padx=10, pady=5)
        
        # Text area for pasting data
        self.text_area = tk.Text(self.frame, height=8, width=80)
        self.text_area.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Buttons frame
        buttons_frame = tk.Frame(self.frame)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # Clipboard actions
        paste_btn = tk.Button(
            buttons_frame, 
            text="Paste from Clipboard", 
            command=self.paste_from_clipboard
        )
        paste_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            buttons_frame, 
            text="Clear", 
            command=self.clear_text
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # File actions
        upload_csv_btn = tk.Button(
            buttons_frame, 
            text="Upload CSV", 
            command=self.upload_csv
        )
        upload_csv_btn.pack(side=tk.LEFT, padx=5)
        
        # Process button
        process_btn = tk.Button(
            buttons_frame, 
            text="Process Data", 
            command=self.process_data,
            bg="#4CAF50",
            fg="white"
        )
        process_btn.pack(side=tk.RIGHT, padx=5)
        
        # Dataset name
        dataset_frame = tk.Frame(self.frame)
        dataset_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(dataset_frame, text="Dataset Name:").pack(side=tk.LEFT)
        self.dataset_entry = tk.Entry(dataset_frame, width=30)
        self.dataset_entry.pack(side=tk.LEFT, padx=5)
        self.dataset_entry.insert(0, "new_dataset")
    
    def paste_from_clipboard(self):
        """Paste data from clipboard into the text area."""
        try:
            self.text_area.delete(1.0, tk.END)
            # Get the root window
            root = self.parent
            while root.master is not None:
                root = root.master
            clipboard_content = root.clipboard_get()
            self.text_area.insert(tk.END, clipboard_content)
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Error accessing clipboard: {e}")
    
    def clear_text(self):
        """Clear the text area."""
        self.text_area.delete(1.0, tk.END)
    
    def upload_csv(self):
        """Open a file dialog to upload a CSV file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            # Extract filename for dataset name suggestion
            filename = os.path.basename(file_path)
            dataset_name = os.path.splitext(filename)[0]
            self.dataset_entry.delete(0, tk.END)
            self.dataset_entry.insert(0, dataset_name)
            
            # Load and display file preview
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("File Error", f"Error reading file: {e}")
    
    def process_data(self):
        """Process the data in the text area based on selected chart type."""
        if not self.chart_panel:
            messagebox.showerror("Error", "Chart panel not connected.")
            return
            
        # Get the data from the text area
        data_text = self.text_area.get(1.0, tk.END)
        if not data_text.strip():
            messagebox.showwarning("Empty Data", "Please enter or paste data first.")
            return
            
        # Get the dataset name
        dataset_name = self.dataset_entry.get().strip()
        if not dataset_name:
            messagebox.showwarning("Dataset Name", "Please enter a dataset name.")
            return
            
        # Get the chart type from the chart panel
        chart_type = self.chart_panel.chart_type.get()
        
        try:
            # Process the data through the data manager
            result = self.data_manager.process_data(
                data_text, 
                dataset_name, 
                self.client_id, 
                chart_type
            )
            
            if result:
                # Save the data
                self.data_manager.save_data()
                
                # Update the chart panel's dataset list
                self.chart_panel.update_dataset_list()
                
                # Update the dataset dropdown value to the new dataset
                self.chart_panel.dataset_var.set(dataset_name)
                
                # Display success message
                messagebox.showinfo(
                    "Success", 
                    f"Data processed successfully as '{dataset_name}'."
                )
                
                # Update the chart display
                if self.chart_panel:
                    chart_data = self.data_manager.get_dataset(dataset_name, self.client_id)
                    self.chart_panel.display_chart(chart_data)
                    
        except Exception as e:
            messagebox.showerror("Processing Error", f"Error processing data: {e}")
            import traceback
            traceback.print_exc()
    
    def update_instructions(self, chart_type):
        """Update the instructions box based on the selected chart type."""
        # Clear existing instructions
        self.instructions_var.set("")
        
        # Set new instructions based on chart type
        if chart_type == "bar":
            instructions = (
                "Instructions for Bar Chart data:\n\n"
                "Paste data with columns for categories and values.\n\n"
                "Example format:\n"
                "Category    Value\n"
                "Marketing   5000\n"
                "Sales       7000\n"
                "Operations  4500"
            )
        elif chart_type == "monthly":
            instructions = (
                "Instructions for Monthly data:\n\n"
                "Paste data with columns for Month, Income, and Expenses.\n\n"
                "Example format:\n"
                "Month      Income    Expenses\n"
                "January    10000     8000\n"
                "February   12000     7500\n"
                "March      11000     9000"
            )
        elif chart_type == "daily_cash":
            instructions = (
                "Instructions for Daily Cash Balance data:\n\n"
                "The system accepts two formats:\n\n"
                "Format 1 (one account per row):\n"
                "Date         Account    Balance\n"
                "9/30/2024    Checking   5000\n"
                "10/1/2024    Checking   4800\n"
                "9/30/2024    Savings    10000\n"
                "10/1/2024    Savings    10050\n\n"
                "Format 2 (accounts as columns):\n"
                "Date         Checking   Savings   Business\n"
                "9/30/2024    5000       10000     15000\n"
                "10/1/2024    4800       10050     14500\n"
                "10/2/2024    5200       10100     14800\n\n"
                "The system will automatically detect the format."
            )
        elif chart_type == "cash_flow":
            instructions = (
                "Instructions for Cash Flow data:\n\n"
                "Paste data with columns for Date, Category, and Amount.\n\n"
                "Example format:\n"
                "Date        Category      Amount\n"
                "2023-01-15  Sales         5000\n"
                "2023-01-20  Rent          -2000\n"
                "2023-02-01  Utilities     -500"
            )
        elif chart_type == "pie":
            instructions = (
                "Instructions for Pie Chart data:\n\n"
                "Paste data with columns for categories and values.\n\n"
                "Example format:\n"
                "Category    Value\n"
                "Marketing   5000\n"
                "Sales       7000\n"
                "Operations  4500"
            )
        elif chart_type == "scatter":
            instructions = (
                "Instructions for Scatter Plot data:\n\n"
                "Paste data with columns for X and Y values.\n\n"
                "Example format:\n"
                "X       Y\n"
                "1.2     3.4\n"
                "2.5     4.1\n"
                "3.7     2.8"
            )
        elif chart_type == "line":
            instructions = (
                "Instructions for Line Chart data:\n\n"
                "Paste data with columns for X and Y values.\n\n"
                "Example format:\n"
                "X       Y\n"
                "Jan     100\n"
                "Feb     150\n"
                "Mar     200"
            )
        else:
            instructions = (
                "Select a chart type and paste your data in the box below.\n\n"
                "Then click the 'Process Data' button to generate your chart."
            )
        
        # Insert instructions
        self.instructions_var.set(instructions)
        
        # Enable editing of text area that was previously disabled
        self.text_area.config(state=tk.NORMAL)
        # Clear any previous content
        self.text_area.delete(1.0, tk.END) 