import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import datetime
from charts.stacked_bar import StackedBarIncomeChart
from charts.daily_cash_line import DailyCashBalanceChart

class ChartPanel:
    """Panel for chart selection, configuration, and display."""
    
    def __init__(self, parent, data_manager, client_id):
        """Initialize the chart panel.
        
        Args:
            parent: The parent frame/container
            data_manager: Reference to the central data manager
            client_id: The ID of the client this panel belongs to
        """
        try:
            self.parent = parent
            self.data_manager = data_manager
            self.client_id = client_id
            
            # Initialize chart type
            self.chart_type = tk.StringVar(value="stacked_bar")
            
            # Initialize threshold values for cash balance chart
            self.use_lower_threshold = tk.BooleanVar(value=False)
            self.lower_threshold_value = tk.StringVar(value="0")
            self.lower_threshold_name = tk.StringVar(value="Minimum Balance")
            
            self.use_upper_threshold = tk.BooleanVar(value=False)
            self.upper_threshold_value = tk.StringVar(value="0")
            self.upper_threshold_name = tk.StringVar(value="Target Balance")
            
            # Create main frame
            self.frame = tk.Frame(parent)
            self.frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Canvas for chart display
            self.canvas = None
            self.figure = None
            
            # Track the current dataset
            self.current_dataset = None
            
            # Create UI components
            self.create_widgets()
        except Exception as e:
            print(f"Error initializing ChartPanel: {e}")
            import traceback
            traceback.print_exc()
            
            # Create a minimal frame with error message
            self.frame = tk.Frame(parent)
            self.frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            error_label = tk.Label(
                self.frame,
                text=f"Error initializing chart panel: {e}\nPlease restart the application.",
                fg="red",
                wraplength=400
            )
            error_label.pack(pady=20)
    
    def create_widgets(self):
        """Create all widgets for the chart panel."""
        # Top controls frame
        controls_frame = tk.LabelFrame(self.frame, text="Chart Settings")
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Chart type selection
        chart_type_frame = tk.Frame(controls_frame)
        chart_type_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(chart_type_frame, text="Chart Type:").pack(side=tk.LEFT)
        
        chart_types = [
            ("Income/Expense Bar Chart", "stacked_bar"),
            ("Daily Cash Balance Line Chart", "daily_cash"),
            ("Cash Flow Area Chart", "cash_flow")
        ]
        
        for i, (text, value) in enumerate(chart_types):
            rb = tk.Radiobutton(
                chart_type_frame, 
                text=text, 
                variable=self.chart_type, 
                value=value,
                command=self.on_chart_type_changed
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Dataset selection frame
        dataset_frame = tk.Frame(controls_frame)
        dataset_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(dataset_frame, text="Dataset:").pack(side=tk.LEFT)
        
        # Create dataset dropdown
        self.dataset_var = tk.StringVar()
        self.dataset_dropdown = ttk.Combobox(
            dataset_frame, 
            textvariable=self.dataset_var,
            state="readonly",
            width=30
        )
        self.dataset_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Button to load selected dataset
        load_dataset_btn = tk.Button(
            dataset_frame,
            text="Load Dataset",
            command=self.load_selected_dataset
        )
        load_dataset_btn.pack(side=tk.LEFT, padx=5)
        
        # Chart configuration frame (will adapt based on chart type)
        self.config_frame = tk.LabelFrame(self.frame, text="Chart Configuration")
        self.config_frame.pack(fill="x", padx=10, pady=5)
        
        # Initial config is empty, will be populated based on chart type
        self.update_config_frame()
        
        # Chart display frame
        self.chart_frame = tk.LabelFrame(self.frame, text="Chart Preview")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Welcome message instead of immediately trying to load charts
        welcome_frame = tk.Frame(self.chart_frame)
        welcome_frame.pack(fill="both", expand=True)
        
        # Get client name safely
        client_name = "Client"
        try:
            if (self.client_id in self.data_manager.clients and 
                'name' in self.data_manager.clients[self.client_id]):
                client_name = self.data_manager.clients[self.client_id]['name']
        except:
            pass
        
        welcome_label = tk.Label(
            welcome_frame,
            text=f"Welcome to {client_name}'s dashboard!\n\n" +
                 "To get started:\n" +
                 "1. Paste data in the input panel above\n" +
                 "2. Click 'Process Data' to generate a chart\n" +
                 "3. Or select an existing dataset from the dropdown",
            font=("Arial", 12),
            justify=tk.LEFT,
            padx=20,
            pady=20
        )
        welcome_label.pack(fill="both", expand=True)
        
        # Action buttons frame
        action_frame = tk.Frame(self.frame)
        action_frame.pack(fill="x", padx=10, pady=5)
        
        # Save chart button
        save_btn = tk.Button(
            action_frame, 
            text="Save Chart", 
            command=self.save_chart
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Populate dataset dropdown
        self.update_dataset_list()
    
    def on_chart_type_changed(self):
        """Handle chart type selection change."""
        self.update_config_frame()
        
        # Notify input panel to update instructions
        try:
            # Try to find the app instance
            root = self.parent
            found_app = None
            client_tabs = None
            
            # Navigate up the widget hierarchy to find client_tabs
            while root is not None:
                if hasattr(root, 'client_tabs'):
                    found_app = root
                    client_tabs = root.client_tabs
                    break
                if hasattr(root, 'master'):
                    root = root.master
                else:
                    break
            
            if found_app and client_tabs:
                # Find the input panel for this client
                for client_id, tab_info in client_tabs.items():
                    if tab_info["frame"] == self.parent or tab_info["chart_panel"] == self:
                        input_panel = tab_info["input_panel"]
                        input_panel.update_instructions(self.chart_type.get())
                        break
        except Exception as e:
            print(f"Error updating input instructions: {e}")
    
    def update_config_frame(self):
        """Update configuration options based on selected chart type."""
        # Clear existing config widgets
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        
        chart_type = self.chart_type.get()
        
        if chart_type == "stacked_bar":
            self._setup_stacked_bar_config()
        elif chart_type == "daily_cash":
            self._setup_daily_cash_config()
        elif chart_type == "cash_flow":
            self._setup_cash_flow_config()
    
    def _setup_stacked_bar_config(self):
        """Set up configuration options for stacked bar chart."""
        label = tk.Label(
            self.config_frame, 
            text="No additional configuration required for stacked bar chart."
        )
        label.pack(padx=10, pady=10)
    
    def _setup_daily_cash_config(self):
        """Set up configuration options for daily cash balance chart."""
        # Lower threshold (red line)
        lower_threshold_frame = tk.Frame(self.config_frame)
        lower_threshold_frame.pack(fill="x", padx=5, pady=5)
        
        lower_check = tk.Checkbutton(
            lower_threshold_frame, 
            text="Lower Threshold (Red)",
            variable=self.use_lower_threshold
        )
        lower_check.pack(side=tk.LEFT)
        
        tk.Label(lower_threshold_frame, text="Value:").pack(side=tk.LEFT, padx=(10, 2))
        lower_entry = tk.Entry(
            lower_threshold_frame, 
            width=10, 
            textvariable=self.lower_threshold_value
        )
        lower_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(lower_threshold_frame, text="Label:").pack(side=tk.LEFT, padx=(10, 2))
        lower_name_entry = tk.Entry(
            lower_threshold_frame, 
            width=15, 
            textvariable=self.lower_threshold_name
        )
        lower_name_entry.pack(side=tk.LEFT, padx=2)
        
        # Upper threshold (green line)
        upper_threshold_frame = tk.Frame(self.config_frame)
        upper_threshold_frame.pack(fill="x", padx=5, pady=5)
        
        upper_check = tk.Checkbutton(
            upper_threshold_frame, 
            text="Upper Threshold (Green)",
            variable=self.use_upper_threshold
        )
        upper_check.pack(side=tk.LEFT)
        
        tk.Label(upper_threshold_frame, text="Value:").pack(side=tk.LEFT, padx=(10, 2))
        upper_entry = tk.Entry(
            upper_threshold_frame, 
            width=10, 
            textvariable=self.upper_threshold_value
        )
        upper_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(upper_threshold_frame, text="Label:").pack(side=tk.LEFT, padx=(10, 2))
        upper_name_entry = tk.Entry(
            upper_threshold_frame, 
            width=15, 
            textvariable=self.upper_threshold_name
        )
        upper_name_entry.pack(side=tk.LEFT, padx=2)
    
    def _setup_cash_flow_config(self):
        """Set up configuration options for cash flow area chart."""
        # Category filter
        filter_frame = tk.Frame(self.config_frame)
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(filter_frame, text="Category Filter:").pack(side=tk.LEFT)
        category_entry = tk.Entry(filter_frame, width=20)
        category_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(filter_frame, text="(leave empty to show all)").pack(side=tk.LEFT)
    
    def display_chart(self, chart_data):
        """Display a chart based on the provided data."""
        try:
            if chart_data is None:
                messagebox.showerror("Chart Error", "No valid chart data to display.")
                return
            
            # Store the current dataset
            self.current_dataset = chart_data
            
            # Clear existing chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Create figure and canvas if they don't exist
            if self.figure is None:
                self.figure = plt.Figure(figsize=(8, 5), dpi=100)
                self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
                self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Clear figure for new chart
            self.figure.clear()
            
            # Get chart type from dataset if available, otherwise use selected chart type
            chart_type = None
            if isinstance(chart_data, dict) and 'chart_type' in chart_data:
                chart_type = chart_data.get('chart_type')
            
            if chart_type is None:
                chart_type = self.chart_type.get()
            
            # Display the appropriate chart
            if chart_type == "stacked_bar":
                self._display_stacked_bar_chart(chart_data)
            elif chart_type == "daily_cash":
                self._display_daily_cash_chart(chart_data)
            elif chart_type == "cash_flow":
                self._display_cash_flow_chart(chart_data)
            else:
                messagebox.showerror("Chart Error", f"Unknown chart type: {chart_type}")
            
        except Exception as e:
            messagebox.showerror("Chart Error", f"Error displaying chart: {e}")
            print(f"Error displaying chart: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error in the chart area
            if self.figure is not None:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.set_title("Error Displaying Chart")
                ax.text(
                    0.5, 0.5, 
                    f"An error occurred while displaying the chart:\n{str(e)}",
                    ha='center', va='center',
                    transform=ax.transAxes
                )
                if self.canvas is not None:
                    self.canvas.draw()
    
    def _display_stacked_bar_chart(self, chart_data):
        """Display a stacked bar chart."""
        # Create the chart
        chart = StackedBarIncomeChart()
        
        # Handle non-dictionary inputs
        if not isinstance(chart_data, dict):
            ax = self.figure.add_subplot(111)
            ax.set_title("Stacked Bar Chart - Invalid Data")
            ax.text(
                0.5, 0.5, 
                "The data format is not compatible with this chart type.\nExpected a dictionary but got a different type.",
                ha='center', va='center',
                transform=ax.transAxes
            )
            self.canvas.draw()
            return
        
        # Check if we have valid data structure
        if 'months' not in chart_data or 'income_values' not in chart_data or 'expense_data' not in chart_data:
            ax = self.figure.add_subplot(111)
            ax.set_title("Stacked Bar Chart - Invalid Data")
            ax.text(
                0.5, 0.5, 
                "The data format is not compatible with this chart type.\nPlease check the input data format.",
                ha='center', va='center',
                transform=ax.transAxes
            )
            self.canvas.draw()
            return
        
        # Draw on our figure (instead of creating a new one)
        chart.fig = self.figure
        chart.ax = self.figure.add_subplot(111)
        
        try:
            # Plot the chart
            chart.plot(chart_data)
            
            # Draw the canvas
            self.canvas.draw()
        except Exception as e:
            print(f"Error displaying stacked bar chart: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error message in the chart
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_title("Error Displaying Chart")
            ax.text(
                0.5, 0.5, 
                f"An error occurred while displaying the chart:\n{str(e)}",
                ha='center', va='center',
                transform=ax.transAxes
            )
            self.canvas.draw()
    
    def _display_daily_cash_chart(self, chart_data):
        """Display a daily cash balance chart."""
        # Create the chart
        chart = DailyCashBalanceChart()
        
        # Handle non-dictionary inputs
        if not isinstance(chart_data, dict):
            ax = self.figure.add_subplot(111)
            ax.set_title("Daily Cash Balance Chart - Invalid Data")
            ax.text(
                0.5, 0.5, 
                "The data format is not compatible with this chart type.\nExpected a dictionary but got a different type.",
                ha='center', va='center',
                transform=ax.transAxes
            )
            self.canvas.draw()
            return
        
        # Check if we have valid data structure
        if 'dates' not in chart_data or 'account_data' not in chart_data:
            ax = self.figure.add_subplot(111)
            ax.set_title("Daily Cash Balance Chart - Invalid Data")
            ax.text(
                0.5, 0.5, 
                "The data format is not compatible with this chart type.\nPlease check the input data format.",
                ha='center', va='center',
                transform=ax.transAxes
            )
            self.canvas.draw()
            return
        
        # Apply threshold settings
        if self.use_lower_threshold.get():
            try:
                lower_value = float(self.lower_threshold_value.get())
                chart_data['lower_threshold'] = {
                    'value': lower_value,
                    'label': self.lower_threshold_name.get()
                }
            except ValueError:
                print("Invalid lower threshold value")
        
        if self.use_upper_threshold.get():
            try:
                upper_value = float(self.upper_threshold_value.get())
                chart_data['upper_threshold'] = {
                    'value': upper_value,
                    'label': self.upper_threshold_name.get()
                }
            except ValueError:
                print("Invalid upper threshold value")
        
        # Draw on our figure (instead of creating a new one)
        chart.fig = self.figure
        chart.ax = self.figure.add_subplot(111)
        
        try:
            # Plot the chart
            chart.plot(chart_data)
            
            # Draw the canvas
            self.canvas.draw()
        except Exception as e:
            print(f"Error displaying daily cash chart: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error message in the chart
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_title("Error Displaying Chart")
            ax.text(
                0.5, 0.5, 
                f"An error occurred while displaying the chart:\n{str(e)}",
                ha='center', va='center',
                transform=ax.transAxes
            )
            self.canvas.draw()
    
    def _display_cash_flow_chart(self, chart_data):
        """Display a cash flow area chart."""
        # Handle non-dictionary inputs
        if not isinstance(chart_data, dict):
            ax = self.figure.add_subplot(111)
            ax.set_title("Cash Flow Area Chart - Invalid Data")
            ax.text(
                0.5, 0.5, 
                "The data format is not compatible with this chart type.\nExpected a dictionary but got a different type.",
                ha='center', va='center',
                transform=ax.transAxes
            )
            self.canvas.draw()
            return
        
        # Check if we have valid data structure
        required_fields = ['dates', 'amounts', 'running_balance']
        missing_fields = [field for field in required_fields if field not in chart_data]
        
        if missing_fields:
            # For now, just show a placeholder with the data
            ax = self.figure.add_subplot(111)
            ax.set_title("Cash Flow Area Chart - Invalid Data")
            ax.text(
                0.5, 0.5, 
                f"The data format is missing required fields: {', '.join(missing_fields)}.\n" +
                "Please check the input data format.",
                ha='center', va='center',
                transform=ax.transAxes
            )
            self.canvas.draw()
            return
        
        # TODO: Implement cash flow chart display once the chart is created
        
        # For now, just show a placeholder with the data
        ax = self.figure.add_subplot(111)
        ax.set_title("Cash Flow Area Chart")
        ax.text(
            0.5, 0.5, 
            "Cash Flow Area Chart will be implemented soon.",
            ha='center', va='center',
            transform=ax.transAxes
        )
        
        # Draw the canvas
        self.canvas.draw()
    
    def save_chart(self):
        """Save the current chart to a file."""
        if self.figure is None or self.current_dataset is None:
            messagebox.showwarning("No Chart", "No chart has been generated yet.")
            return
            
        try:
            # Get client name and dataset name for the filename
            client_name = self.data_manager.clients[self.client_id]['name']
            
            # Handle different dataset types
            if isinstance(self.current_dataset, dict):
                dataset_name = self.current_dataset.get('name', 'chart')
                chart_type = self.current_dataset.get('chart_type', self.chart_type.get())
            elif isinstance(self.current_dataset, list):
                dataset_name = "dataset"
                chart_type = self.chart_type.get()
            else:
                dataset_name = "chart"
                chart_type = self.chart_type.get()
            
            # Create a default filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"{client_name}_{chart_type}_{timestamp}.png"
            default_filename = default_filename.replace(' ', '_').lower()
            
            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=default_filename,
                initialdir="output"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Save the figure
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Success", f"Chart saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving chart: {e}")
            import traceback
            traceback.print_exc()
    
    def update_dataset_list(self):
        """Update the dataset dropdown with available datasets for the client."""
        try:
            # Safety check for client_id
            if not self.client_id:
                print(f"Warning: No client ID available for dataset list update")
                self.dataset_dropdown['values'] = []
                return
            
            # Make sure the client exists
            if self.client_id not in self.data_manager.clients:
                print(f"Warning: Client ID {self.client_id} not found")
                self.dataset_dropdown['values'] = []
                return
            
            # Make sure the client has a datasets field
            client_data = self.data_manager.clients[self.client_id]
            if 'datasets' not in client_data:
                print(f"Warning: Client has no datasets field, creating empty one")
                self.data_manager.clients[self.client_id]['datasets'] = {}
                self.data_manager.save_data()
                self.dataset_dropdown['values'] = []
                return
            
            # Get list of datasets for the client
            try:
                datasets = list(self.data_manager.clients[self.client_id]['datasets'].keys())
            except Exception as e:
                print(f"Error getting dataset list: {e}")
                datasets = []
            
            # Update dropdown values
            self.dataset_dropdown['values'] = datasets
            
            # Select first dataset if available
            if datasets:
                self.dataset_var.set(datasets[0])
            else:
                self.dataset_var.set("")
            
        except Exception as e:
            print(f"Error updating dataset list: {e}")
            import traceback
            traceback.print_exc()
            # Set empty values as fallback
            try:
                self.dataset_dropdown['values'] = []
                self.dataset_var.set("")
            except:
                pass
    
    def load_selected_dataset(self):
        """Load and display the selected dataset."""
        dataset_name = self.dataset_var.get()
        if not dataset_name:
            messagebox.showinfo("No Dataset", "Please select a dataset to load.")
            return
        
        try:
            # Get the dataset
            dataset = self.data_manager.get_dataset(dataset_name, self.client_id)
            
            if dataset is None:
                messagebox.showerror("Error", f"Could not find dataset '{dataset_name}'.")
                return
            
            # Update chart type to match dataset if it has a chart_type
            if isinstance(dataset, dict) and 'chart_type' in dataset:
                self.chart_type.set(dataset['chart_type'])
                self.update_config_frame()
            
            # Display the chart
            self.display_chart(dataset)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading dataset: {e}")
            print(f"Error loading dataset: {e}")
            import traceback
            traceback.print_exc()
            
            # Display an empty chart with an error message
            if self.figure is not None:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.set_title("Error Loading Dataset")
                ax.text(
                    0.5, 0.5, 
                    f"An error occurred while loading dataset '{dataset_name}':\n{str(e)}",
                    ha='center', va='center',
                    transform=ax.transAxes
                )
                if self.canvas is not None:
                    self.canvas.draw() 