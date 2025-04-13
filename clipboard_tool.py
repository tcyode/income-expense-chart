# clipboard_tool.py
# A simple tool to test the clipboard data loading functionality

import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from data_loader import FinancialDataManager
from charts.stacked_bar import StackedBarIncomeChart
from charts.daily_cash_line import DailyCashBalanceChart
import re
import csv
import os
import json

class ClipboardToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Chart - Clipboard Tool")
        self.root.geometry("600x500")
        
        # Ensure directories exist
        if not os.path.exists("client_data"):
            os.makedirs("client_data")
            print("Created client_data directory")
        if not os.path.exists("output"):
            os.makedirs("output")
            print("Created output directory")
        
        # Test direct file creation to ensure permissions are correct
        test_file = os.path.join("client_data", "test_file.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("This is a test file to verify write permissions.")
            print(f"Successfully created test file: {test_file}")
        except Exception as e:
            print(f"ERROR: Cannot write to client_data directory: {e}")
        
        # Initialize the data manager (but don't create default client)
        self.data_mgr = FinancialDataManager()
        
        # Migrate any legacy data
        self.migrate_legacy_data()
        
        # Initialize chart type
        self.chart_type = tk.StringVar(value="stacked_bar")
        
        # Initialize threshold values
        self.use_lower_threshold = tk.BooleanVar(value=False)
        self.lower_threshold_value = tk.StringVar(value="0")
        self.lower_threshold_name = tk.StringVar(value="Minimum Balance")
        
        self.use_upper_threshold = tk.BooleanVar(value=False)
        self.upper_threshold_value = tk.StringVar(value="0")
        self.upper_threshold_name = tk.StringVar(value="Target Balance")
        
        # Track the current dataset for editing
        self.current_dataset = None
        self.current_df = None
        
        # Create widgets
        self.create_widgets()
    
    def migrate_legacy_data(self):
        """Migrate data from legacy clipboard_client.json if it exists."""
        legacy_file = os.path.join("client_data", "clipboard_client.json")
        if os.path.exists(legacy_file):
            try:
                # Load the legacy data
                with open(legacy_file, 'r') as f:
                    legacy_data = json.load(f)
                
                # Get the client name from the file
                client_name = legacy_data.get("name", "Migrated Client")
                
                # Create a proper client ID
                client_id = client_name.lower().replace(' ', '_').replace('-', '_')
                
                # Check if we already have this client
                if client_id not in self.data_mgr.clients:
                    # Create the new client with the proper ID
                    self.data_mgr.add_client(client_id, client_name)
                    
                    # Copy all datasets
                    self.data_mgr.clients[client_id]["datasets"] = legacy_data.get("datasets", {})
                    
                    # Save the new client data
                    self.data_mgr.save_data()
                    print(f"Migrated legacy data to new client: {client_id}")
                    
                    # Rename the old file so it doesn't get loaded again
                    try:
                        backup_file = os.path.join("client_data", "clipboard_client.json.bak")
                        if os.path.exists(backup_file):
                            os.remove(backup_file)  # Remove existing backup if it exists
                        os.rename(legacy_file, backup_file)
                        print("Renamed legacy file to clipboard_client.json.bak")
                    except Exception as rename_err:
                        print(f"Error renaming legacy file: {rename_err}, trying to remove it")
                        try:
                            os.remove(legacy_file)
                            print("Removed legacy file instead of renaming")
                        except Exception as remove_err:
                            print(f"Error removing legacy file: {remove_err}")
            except Exception as e:
                print(f"Error migrating legacy data: {e}")
                import traceback
                traceback.print_exc()
                
                # If we can't properly migrate, try to rename or remove the file
                try:
                    os.rename(legacy_file, os.path.join("client_data", "clipboard_client.json.error"))
                    print("Renamed problematic legacy file to clipboard_client.json.error")
                except Exception:
                    try:
                        os.remove(legacy_file)
                        print("Removed problematic legacy file")
                    except Exception as remove_err:
                        print(f"Cannot remove problematic legacy file: {remove_err}")
    
    def create_widgets(self):
        # Instructions label
        instructions = """Copy data from Excel/Google Sheets and paste below.
        
Format should be:
Month    Income    Expense1    Expense2    ...
Jan'24   1000      200         300         ...
Feb'24   1100      250         320         ...
        
First column = months, second = income, rest = expense categories"""
        
        label = tk.Label(self.root, text=instructions, justify=tk.LEFT, padx=10, pady=10)
        label.pack(fill=tk.X)
        
        # Text area for pasting data
        self.text_area = tk.Text(self.root, height=10, width=80)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Client name entry
        client_frame = tk.Frame(self.root)
        client_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(client_frame, text="Client Name:").pack(side=tk.LEFT)
        self.client_entry = tk.Entry(client_frame, width=30)
        self.client_entry.pack(side=tk.LEFT, padx=5)
        self.client_entry.insert(0, "Clipboard Client")
        
        # Dataset name entry
        dataset_frame = tk.Frame(self.root)
        dataset_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(dataset_frame, text="Dataset Name:").pack(side=tk.LEFT)
        self.dataset_entry = tk.Entry(dataset_frame, width=30)
        self.dataset_entry.pack(side=tk.LEFT, padx=5)
        self.dataset_entry.insert(0, "clipboard_data")
        
        # Chart type selection
        chart_type_frame = tk.Frame(self.root)
        chart_type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(chart_type_frame, text="Chart Type:").pack(side=tk.LEFT)
        
        stacked_bar_radio = tk.Radiobutton(chart_type_frame, text="Income/Expense Bar Chart", 
                                          variable=self.chart_type, value="stacked_bar",
                                          command=self.update_ui)
        stacked_bar_radio.pack(side=tk.LEFT, padx=5)
        
        cash_balance_radio = tk.Radiobutton(chart_type_frame, text="Daily Cash Balance Line Chart", 
                                           variable=self.chart_type, value="daily_cash",
                                           command=self.update_ui)
        cash_balance_radio.pack(side=tk.LEFT, padx=5)
        
        # Threshold options frame (will be shown/hidden based on chart type)
        self.threshold_frame = tk.LabelFrame(self.root, text="Threshold Lines", padx=10, pady=5)
        
        # Lower threshold (red line)
        lower_threshold_frame = tk.Frame(self.threshold_frame)
        lower_threshold_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.lower_threshold_check = tk.Checkbutton(lower_threshold_frame, text="Lower Threshold (Red)",
                                                   variable=self.use_lower_threshold)
        self.lower_threshold_check.pack(side=tk.LEFT)
        
        tk.Label(lower_threshold_frame, text="Value:").pack(side=tk.LEFT, padx=(10, 2))
        lower_threshold_entry = tk.Entry(lower_threshold_frame, width=10, 
                                        textvariable=self.lower_threshold_value)
        lower_threshold_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(lower_threshold_frame, text="Label:").pack(side=tk.LEFT, padx=(10, 2))
        lower_threshold_name_entry = tk.Entry(lower_threshold_frame, width=15, 
                                             textvariable=self.lower_threshold_name)
        lower_threshold_name_entry.pack(side=tk.LEFT, padx=2)
        
        # Upper threshold (green line)
        upper_threshold_frame = tk.Frame(self.threshold_frame)
        upper_threshold_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.upper_threshold_check = tk.Checkbutton(upper_threshold_frame, text="Upper Threshold (Green)",
                                                   variable=self.use_upper_threshold)
        self.upper_threshold_check.pack(side=tk.LEFT)
        
        tk.Label(upper_threshold_frame, text="Value:").pack(side=tk.LEFT, padx=(10, 2))
        upper_threshold_entry = tk.Entry(upper_threshold_frame, width=10, 
                                        textvariable=self.upper_threshold_value)
        upper_threshold_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(upper_threshold_frame, text="Label:").pack(side=tk.LEFT, padx=(10, 2))
        upper_threshold_name_entry = tk.Entry(upper_threshold_frame, width=15, 
                                             textvariable=self.upper_threshold_name)
        upper_threshold_name_entry.pack(side=tk.LEFT, padx=2)
        
        # Instructions label with default stacked bar instructions
        self.instructions_text = tk.StringVar()
        self.update_instructions()  # Set initial instructions
        
        self.instruction_label = tk.Label(self.root, textvariable=self.instructions_text, 
                                        justify=tk.LEFT, padx=10, pady=10)
        self.instruction_label.pack(fill=tk.X)
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.process_btn = tk.Button(button_frame, text="Process & Generate Chart", 
                                    command=self.process_data)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_text)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Add debug button
        self.debug_btn = tk.Button(button_frame, text="Analyze Data", 
                                  command=self.debug_clipboard_data)
        self.debug_btn.pack(side=tk.LEFT, padx=5)
        
        # Add CSV upload button
        self.upload_btn = tk.Button(button_frame, text="Upload CSV", command=self.upload_csv)
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        # Add Edit Data button
        self.edit_data_btn = tk.Button(button_frame, text="Edit Data", 
                                     command=self.open_data_editor,
                                     state=tk.DISABLED)  # Initially disabled
        self.edit_data_btn.pack(side=tk.LEFT, padx=5)
        
        # Add Save Data button
        self.save_btn = tk.Button(button_frame, text="Save Data", 
                                 command=self.save_current_data,
                                 bg="#e6ffe6",  # Light green background
                                 font=("Arial", 10, "bold"))
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Initial UI update
        self.update_ui()
    
    def update_ui(self):
        """Update UI elements based on selected chart type."""
        chart_type = self.chart_type.get()
        
        # Show/hide threshold options based on chart type
        if chart_type == "daily_cash":
            self.threshold_frame.pack(fill=tk.X, padx=10, pady=5, after=self.instruction_label)
        else:
            self.threshold_frame.pack_forget()
        
        # Update instructions
        self.update_instructions()
    
    def update_instructions(self):
        """Update the instructions based on the selected chart type."""
        if self.chart_type.get() == "stacked_bar":
            instructions = """Copy data from Excel/Google Sheets and paste below.
            
Format should be:
Month    Income    Expense1    Expense2    ...
Jan'24   1000      200         300         ...
Feb'24   1100      250         320         ...
            
First column = months, second = income, rest = expense categories"""
        else:  # daily_cash
            instructions = """Copy data from Excel/Google Sheets and paste below.
            
Format should be:
Date,Account,Balance
2023-01-01,Checking,5000.00
2023-01-01,Savings,15000.00
2023-01-02,Checking,5250.75
            
CSV format with headers: Date, Account, Balance"""
        
        self.instructions_text.set(instructions)
    
    def process_data(self):
        """Process the clipboard data and generate a chart."""
        clipboard_text = self.text_area.get("1.0", tk.END)
        
        if len(clipboard_text.strip()) < 10:  # Arbitrary minimum length
            messagebox.showerror("Error", "Please paste some data first!")
            return
        
        # Get client name and generate a safe client ID
        client_name = self.client_entry.get()
        # Create a safe client ID from the name (lowercase, replace spaces with underscores)
        client_id = client_name.lower().replace(' ', '_').replace('-', '_')
        
        # Check if this is a new client
        if client_id not in self.data_mgr.clients:
            print(f"Creating new client: {client_name} with ID: {client_id}")
            self.data_mgr.add_client(client_id, client_name)
        else:
            # Update existing client name if changed
            if client_name != self.data_mgr.clients[client_id].get("name"):
                self.data_mgr.clients[client_id]["name"] = client_name
                print(f"Updated client name for {client_id} to {client_name}")
        
        # Set as current client
        self.data_mgr.current_client = client_id
        
        # Process the data based on chart type
        dataset_name = self.dataset_entry.get() or "clipboard_data"
        
        if self.chart_type.get() == "stacked_bar":
            # Process as stacked bar chart data
            dataset = self.data_mgr.load_clipboard_data(clipboard_text, dataset_name)
            
            if not dataset:
                messagebox.showerror("Error", "Could not process the data. Check the format.")
                return
            
            # Add client name to dataset
            dataset['client_name'] = client_name
            
            # Create and save the chart
            chart = StackedBarIncomeChart()
            chart.plot(dataset)
            
            # Save with client name in the filename
            safe_filename = dataset_name.replace(' ', '_').lower()
            output_path = f"output/{client_id}_{safe_filename}.png"
            chart.save_chart(output_path)
            
            # Show success message with file path
            messagebox.showinfo("Success", f"Chart saved to {output_path}")
            
            # Display the chart
            chart.show_chart()
        
        else:  # daily_cash
            try:
                # For daily cash data, process it as CSV
                import io
                import pandas as pd
                
                # Try to parse the clipboard text as CSV
                try:
                    # First try comma separator
                    df = pd.read_csv(io.StringIO(clipboard_text))
                except:
                    # If that fails, try tab separator
                    try:
                        df = pd.read_csv(io.StringIO(clipboard_text), sep='\t')
                    except:
                        # If that also fails, show error
                        messagebox.showerror("Error", "Could not parse the data as CSV. Please check the format.")
                        return
                
                # Process daily cash balance data
                dataset = self.data_mgr.load_daily_cash_balance_data(df, dataset_name)
                
                # Store the current dataset and DataFrame for editing
                self.current_dataset = dataset
                self.current_df = df
                self.edit_data_btn.config(state=tk.NORMAL)  # Enable the edit button
                
                # Add threshold lines if enabled
                if self.use_lower_threshold.get():
                    try:
                        value = float(self.lower_threshold_value.get())
                        dataset['lower_threshold'] = value
                        dataset['lower_threshold_name'] = self.lower_threshold_name.get()
                    except ValueError:
                        print("Invalid lower threshold value, ignoring")
                
                if self.use_upper_threshold.get():
                    try:
                        value = float(self.upper_threshold_value.get())
                        dataset['upper_threshold'] = value
                        dataset['upper_threshold_name'] = self.upper_threshold_name.get()
                    except ValueError:
                        print("Invalid upper threshold value, ignoring")
                
                # Import the chart if not already imported
                from charts.daily_cash_line import DailyCashBalanceChart
                
                # Create and save the chart
                chart = DailyCashBalanceChart(client_name=client_name)
                chart.plot(dataset)
                
                # Save with client name in the filename
                safe_filename = dataset_name.replace(' ', '_').lower()
                output_path = f"output/{client_id}_{safe_filename}.png"
                chart.save_chart(output_path)
                
                # Show success message with file path
                messagebox.showinfo("Success", f"Daily cash balance chart saved to {output_path}")
                
                # Display the chart
                chart.show_chart()
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Error processing daily cash balance data: {str(e)}")
                return
    
    def clear_text(self):
        """Clear the text area."""
        self.text_area.delete("1.0", tk.END)

    def debug_clipboard_data(self):
        """Analyze and show debug info about the pasted data"""
        clipboard_text = self.text_area.get("1.0", tk.END)
        if len(clipboard_text.strip()) < 10:
            messagebox.showerror("Error", "Please paste some data first!")
            return
        
        # Show a debug window with data analysis
        debug_window = tk.Toplevel(self.root)
        debug_window.title("Data Analysis")
        debug_window.geometry("700x600")
        debug_window.minsize(600, 400)
        
        # Use grid layout for better control
        debug_window.grid_columnconfigure(0, weight=1)
        debug_window.grid_rowconfigure(0, weight=1)
        debug_window.grid_rowconfigure(1, weight=0)
        
        # Create frame for text area
        text_frame = tk.Frame(debug_window)
        text_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # Configure grid for text frame
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Create text area for showing debug info
        debug_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        debug_text.grid(row=0, column=0, sticky='nsew')
        scrollbar.config(command=debug_text.yview)
        
        # Analyze the data
        lines = clipboard_text.strip().split('\n')
        debug_text.insert(tk.END, f"Number of lines: {len(lines)}\n\n")
        
        if lines:
            debug_text.insert(tk.END, f"First line: {lines[0]}\n")
            debug_text.insert(tk.END, f"Contains tabs: {'\\t' in lines[0]}\n")
            debug_text.insert(tk.END, f"Contains pipes: {'|' in lines[0]}\n")
            debug_text.insert(tk.END, f"Split by spaces: {len(lines[0].split())}\n\n")
            
            # Try to identify column headers
            headers = re.split(r'\t+|\s{2,}', lines[0].strip())
            debug_text.insert(tk.END, f"Possible columns: {headers}\n\n")
            
            # Try to identify rows
            if len(lines) > 1:
                debug_text.insert(tk.END, f"First data row: {lines[1]}\n")
                row_items = lines[1].split('\t') if '\t' in lines[1] else lines[1].split()
                debug_text.insert(tk.END, f"Items in first row: {row_items}\n\n")
        
        # Add a separator line
        separator = tk.Frame(debug_window, height=2, bd=1, relief=tk.SUNKEN)
        separator.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        
        # Create separate frame for buttons
        button_frame = tk.Frame(debug_window)
        button_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        
        # Configure button frame columns
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Add a "Try Fixed Format" button
        fix_button = tk.Button(
            button_frame, 
            text="Try With Fixed Format", 
            command=lambda: self.process_with_fixed_format(clipboard_text),
            height=2,
            bg="#e6f2ff",
            font=("Arial", 10, "bold")
        )
        fix_button.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # Add close button too
        close_button = tk.Button(
            button_frame, 
            text="Close", 
            command=debug_window.destroy,
            height=2
        )
        close_button.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Make sure window is drawn and buttons are visible
        debug_window.update_idletasks()

    def process_with_fixed_format(self, text):
        """Process data with explicitly fixed format for this specific data"""
        try:
            lines = text.strip().split('\n')
            if not lines:
                messagebox.showerror("Error", "No data found")
                return
            
            # Get client name and generate a safe client ID
            client_name = self.client_entry.get()
            # Create a safe client ID from the name (lowercase, replace spaces with underscores)
            client_id = client_name.lower().replace(' ', '_').replace('-', '_')
            
            # Check if this is a new client
            if client_id not in self.data_mgr.clients:
                print(f"Creating new client: {client_name} with ID: {client_id}")
                self.data_mgr.add_client(client_id, client_name)
            else:
                # Update existing client name if changed
                if client_name != self.data_mgr.clients[client_id].get("name"):
                    self.data_mgr.clients[client_id]["name"] = client_name
                    print(f"Updated client name for {client_id} to {client_name}")
            
            # Set as current client
            self.data_mgr.current_client = client_id
            
            # Force save client data to ensure it exists even before processing
            try:
                self.data_mgr.save_data()
                print(f"Saved initial client data for {client_id}")
            except Exception as e:
                print(f"Error saving initial client data: {e}")
            
            # Debugging: Print the raw lines
            print("Raw lines:", lines)
            
            # First line contains headers
            header_line = lines[0]  
            headers = re.split(r'\t+|\s{2,}', header_line.strip())
            print(f"Detected headers: {headers}")
            
            # Check if we have a type row
            has_type_row = False
            if len(lines) > 1 and "type" in lines[1].lower():
                has_type_row = True
                print("Type row detected")
                
                # Second line contains types
                type_line = lines[1]
                types = re.split(r'\t+|\s{2,}', type_line.strip())
                print(f"Detected types: {types}")
                
                # Map headers to their types
                column_types = {}
                for i, header in enumerate(headers):
                    if i < len(types):
                        column_types[header] = types[i].upper()
                
                # Find columns by type
                income_idx = None
                expense_columns = []
                net_income_idx = None
                
                for i, header in enumerate(headers):
                    column_type = column_types.get(header, "").upper()
                    if column_type == "INCOME":
                        income_idx = i
                        print(f"Found Income column at index {i}")
                    elif column_type == "EXPENSE":
                        expense_columns.append((i, header))
                        print(f"Found Expense column {header} at index {i}")
                    elif "NET" in column_type and "INCOME" in column_type:
                        net_income_idx = i
                        print(f"Found Net Income column at index {i}")
                
                # Start processing from line 3 (index 2)
                data_start_line = 2
            else:
                # No type row, use default assumptions
                print("No type row found, using default assumptions")
                income_idx = 1  # Default is second column
                net_income_idx = None
                expense_columns = []
                
                # Check headers for identifiable columns
                for i, header in enumerate(headers):
                    header_upper = header.upper()
                    if i > 1 and "NET" in header_upper and "INCOME" in header_upper:
                        net_income_idx = i
                    elif i > 1:  # All other columns after Income are expenses
                        expense_columns.append((i, header))
                
                # Start processing from line 2 (index 1)
                data_start_line = 1
            
            # Initialize expense data
            expense_data = {}
            for idx, header in expense_columns:
                expense_data[header] = []
            
            print(f"Expense categories: {list(expense_data.keys())}")
            
            # Process data rows
            months = []
            income_values = []
            net_income_values = []
            
            for line in lines[data_start_line:]:
                if not line.strip():
                    continue
                
                values = re.split(r'\t+|\s{2,}', line.strip())
                print(f"Parsed values: {values}")
                
                if len(values) < 3:
                    print(f"Skipping invalid line: {line}")
                    continue
                
                months.append(values[0])
                
                try:
                    income_str = values[income_idx].replace(',', '')
                    income = float(income_str)
                    income_values.append(income)
                except (ValueError, IndexError) as e:
                    print(f"Income value error in line: {line}, error: {e}")
                    income_values.append(0.0)
                
                for idx, header in expense_columns:
                    try:
                        if idx < len(values) and values[idx].strip():
                            # Ensure we're converting a string to float
                            expense_str = str(values[idx]).replace(',', '')
                            value = float(expense_str)
                            expense_data[header].append(value)
                        else:
                            expense_data[header].append(0.0)
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing expense {header} in line: {line}, error: {e}")
                        expense_data[header].append(0.0)
                
                if net_income_idx is not None and net_income_idx < len(values):
                    try:
                        value = str(values[net_income_idx]).strip()
                        if value and value.lower() != 'nan':
                            net_income = float(value.replace(',', ''))
                            net_income_values.append(net_income)
                            print(f"Parsed net income: {net_income}")
                        else:
                            total_expenses = sum(expense_data[cat][-1] for cat in expense_data)
                            net_income = income_values[-1] - total_expenses
                            net_income_values.append(net_income)
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing net income in line: {line} - {e}")
                        total_expenses = sum(expense_data[cat][-1] for cat in expense_data)
                        net_income = income_values[-1] - total_expenses
                        net_income_values.append(net_income)
            
            # Check if net income values are empty, calculate them if needed
            if not net_income_values:
                print("Net income values missing, calculating automatically")
                for i in range(len(months)):
                    total_expenses = sum(expense_data[cat][i] for cat in expense_data)
                    net_income = income_values[i] - total_expenses
                    net_income_values.append(net_income)
                    print(f"Calculated net income for {months[i]}: {net_income}")
            
            # Create color palette
            color_palette = [
                '#4169E1', '#40E0D0', '#BA55D3', '#FF69B4', '#FBBC04', 
                '#FF00FF', '#FF8000', '#32CD32', '#9370DB', '#008080'
            ]
            
            expense_colors = {}
            for i, category in enumerate(expense_data.keys()):
                expense_colors[category] = color_palette[i % len(color_palette)]
            
            dataset_name = self.dataset_entry.get() or "clipboard_data"
            
            print(f"\nFinal data prepared for charting:")
            print(f"Client: {client_name} (ID: {client_id})")
            print(f"Months: {months}")
            print(f"Income values: {income_values}")
            for cat, vals in expense_data.items():
                print(f"{cat}: {vals}")
            print(f"Net income values: {net_income_values}")
            
            dataset = {
                'months': months,
                'income_values': income_values,
                'expense_data': expense_data,
                'expense_colors': expense_colors,
                'net_income_values': net_income_values,
                'client_name': client_name
            }
            
            # Explicitly assign the dataset to the client's datasets dictionary
            self.data_mgr.clients[client_id]["datasets"][dataset_name] = dataset
            
            # Verify the dataset was added and print contents for debugging
            print(f"Dataset '{dataset_name}' added to client '{client_id}' with {len(dataset['months'])} months of data")
            print(f"Client now has {len(self.data_mgr.clients[client_id]['datasets'])} datasets")
            
            # Create output directory if it doesn't exist
            if not os.path.exists("output"):
                os.makedirs("output")
                print("Created output directory")
            
            chart = StackedBarIncomeChart(client_name=client_name)
            chart.plot(dataset)
            chart.save_chart(f"output/{client_id}_{dataset_name}.png")
            chart.show_chart()
            
            # Save data to file for persistence
            try:
                print(f"Saving data to disk for client {client_id} with datasets: {list(self.data_mgr.clients[client_id]['datasets'].keys())}")
                self.data_mgr.save_data()
                print("Data saved successfully")
            except Exception as save_error:
                print(f"Error saving data: {save_error}")
                messagebox.showwarning("Warning", 
                                     f"Chart was generated but data could not be saved: {save_error}")
            
            messagebox.showinfo("Success", 
                               f"Chart generated successfully and saved to 'output/{client_id}_{dataset_name}.png'")
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error processing data: {str(e)}\n\nPlease check the data format.")
            return False

    def _is_likely_month(self, text):
        """Check if text is likely a month."""
        month_patterns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return any(pattern in text for pattern in month_patterns)

    def upload_csv(self):
        """Upload and process a CSV file."""
        # Ask user to select a CSV file
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Get client name and generate a safe client ID
            client_name = self.client_entry.get()
            # Create a safe client ID from the name (lowercase, replace spaces with underscores)
            client_id = client_name.lower().replace(' ', '_').replace('-', '_')
            
            # Check if this is a new client
            if client_id not in self.data_mgr.clients:
                print(f"Creating new client: {client_name} with ID: {client_id}")
                self.data_mgr.add_client(client_id, client_name)
            else:
                # Update existing client name if changed
                if client_name != self.data_mgr.clients[client_id].get("name"):
                    self.data_mgr.clients[client_id]["name"] = client_name
                    print(f"Updated client name for {client_id} to {client_name}")
            
            # Set as current client
            self.data_mgr.current_client = client_id
            
            # Get dataset name
            dataset_name = self.dataset_entry.get() or os.path.basename(file_path).replace(".csv", "")
            
            # Process based on chart type
            if self.chart_type.get() == "stacked_bar":
                # Load as stacked bar chart data
                dataset = self.data_mgr.load_csv_data(file_path, dataset_name)
                
                if not dataset:
                    messagebox.showerror("Error", "Could not process the CSV file. Check the format.")
                    return
                
                # Add client name to dataset
                dataset['client_name'] = client_name
                
                # Create and save the chart
                chart = StackedBarIncomeChart()
                chart.plot(dataset)
                
                # Save with client name in the filename
                safe_filename = dataset_name.replace(' ', '_').lower()
                output_path = f"output/{client_id}_{safe_filename}.png"
                chart.save_chart(output_path)
                
                # Show success message with file path
                messagebox.showinfo("Success", f"Chart saved to {output_path}")
                
                # Display the chart
                chart.show_chart()
                
            else:  # daily_cash
                # Import pandas to read the CSV
                import pandas as pd
                
                # Read the CSV file
                df = pd.read_csv(file_path)
                
                # Load into the text area for review
                header = ",".join(df.columns)
                sample_rows = "\n".join([",".join(map(str, row)) for row in df.values[:10]])
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", f"{header}\n{sample_rows}\n...\n({len(df)} rows total)")
                
                # Process daily cash balance data
                dataset = self.data_mgr.load_daily_cash_balance_data(file_path, dataset_name)
                
                # Store the current dataset and DataFrame for editing
                self.current_dataset = dataset
                self.current_df = df
                self.edit_data_btn.config(state=tk.NORMAL)  # Enable the edit button
                
                # Add threshold lines if enabled
                if self.use_lower_threshold.get():
                    try:
                        value = float(self.lower_threshold_value.get())
                        dataset['lower_threshold'] = value
                        dataset['lower_threshold_name'] = self.lower_threshold_name.get()
                    except ValueError:
                        print("Invalid lower threshold value, ignoring")
                
                if self.use_upper_threshold.get():
                    try:
                        value = float(self.upper_threshold_value.get())
                        dataset['upper_threshold'] = value
                        dataset['upper_threshold_name'] = self.upper_threshold_name.get()
                    except ValueError:
                        print("Invalid upper threshold value, ignoring")
                
                # Import the chart if not already imported
                from charts.daily_cash_line import DailyCashBalanceChart
                
                # Create and save the chart
                chart = DailyCashBalanceChart(client_name=client_name)
                chart.plot(dataset)
                
                # Save with client name in the filename
                safe_filename = dataset_name.replace(' ', '_').lower()
                output_path = f"output/{client_id}_{safe_filename}.png"
                chart.save_chart(output_path)
                
                # Show success message with file path
                messagebox.showinfo("Success", f"Daily cash balance chart saved to {output_path}")
                
                # Display the chart
                chart.show_chart()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error processing CSV file: {str(e)}")

    def save_current_data(self):
        """Manually save the current data."""
        try:
            # Get client name and generate a safe client ID
            client_name = self.client_entry.get()
            client_id = client_name.lower().replace(' ', '_').replace('-', '_')
            
            # Get the dataset name
            dataset_name = self.dataset_entry.get() or "clipboard_data"
            
            # Check if we have this client
            if client_id not in self.data_mgr.clients:
                # Create the client if it doesn't exist
                self.data_mgr.add_client(client_id, client_name)
                print(f"Created new client {client_name} with ID {client_id}")
            
            # Check if we have data in the text area that hasn't been processed
            clipboard_text = self.text_area.get("1.0", tk.END).strip()
            if len(clipboard_text) > 10:
                # Try to process the data in the text area if it hasn't been processed yet
                print("Found data in the text area. Attempting to process it.")
                try:
                    self.process_with_fixed_format(clipboard_text)
                    # Return after processing since it will also save
                    return
                except Exception as e:
                    print(f"Error processing text data: {e}")
            
            # If client has no datasets, show a warning
            if not self.data_mgr.clients[client_id].get("datasets"):
                print(f"Warning: Client {client_name} has no datasets to save.")
                messagebox.showwarning("No Data", 
                                     f"Client {client_name} has no datasets to save.\n\nPlease paste data and process it first.")
                return
            
            # Print information about what we're saving
            print(f"Saving client {client_id} with datasets: {list(self.data_mgr.clients[client_id]['datasets'].keys())}")
            for ds_name, dataset in self.data_mgr.clients[client_id]['datasets'].items():
                if 'months' in dataset:
                    print(f"  Dataset {ds_name}: {len(dataset['months'])} months of data")
            
            # Save the data to disk
            success = self.data_mgr.save_data()
            
            if success:
                messagebox.showinfo("Success", f"Data saved successfully for client: {client_name}")
            else:
                messagebox.showwarning("Warning", "Data may not have saved correctly. Check the console for details.")
        except Exception as e:
            print(f"Error saving data: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to save data: {e}")

    def open_data_editor(self):
        """Open a data editor window for editing the current dataset."""
        if self.current_df is None:
            messagebox.showinfo("No Data", "Please process data first before editing.")
            return
        
        # Create a new window for data editing
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Data Editor")
        editor_window.geometry("800x600")
        
        # Create a frame for the table
        table_frame = tk.Frame(editor_window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollbars
        y_scrollbar = tk.Scrollbar(table_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create a Text widget for displaying and editing data
        self.edit_text = tk.Text(table_frame, wrap=tk.NONE, 
                                yscrollcommand=y_scrollbar.set,
                                xscrollcommand=x_scrollbar.set)
        self.edit_text.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.edit_text.yview)
        x_scrollbar.config(command=self.edit_text.xview)
        
        # Format the DataFrame as CSV and insert into the Text widget
        csv_data = self.current_df.to_csv(index=False)
        self.edit_text.insert(tk.END, csv_data)
        
        # Add control buttons at the bottom
        buttons_frame = tk.Frame(editor_window)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Validate and save button
        save_button = tk.Button(buttons_frame, text="Apply Changes", 
                               command=lambda: self.apply_data_changes(self.edit_text.get("1.0", tk.END)))
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_button = tk.Button(buttons_frame, text="Cancel", command=editor_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Add helper text
        help_text = tk.Label(editor_window, text="Edit the CSV data directly. Make sure to keep the header row intact.", 
                            justify=tk.LEFT, padx=10, pady=5)
        help_text.pack(side=tk.BOTTOM, fill=tk.X)
    
    def apply_data_changes(self, text_data):
        """Apply changes made in the data editor."""
        try:
            import io
            import pandas as pd
            
            # Parse the modified CSV text
            new_df = pd.read_csv(io.StringIO(text_data))
            
            # Store the updated DataFrame
            self.current_df = new_df
            
            # Re-process the data
            client_id = self.data_mgr.current_client
            dataset_name = self.dataset_entry.get() or "clipboard_data"
            
            # Process the updated data
            dataset = self.data_mgr.load_daily_cash_balance_data(new_df, dataset_name)
            
            # Add threshold lines if enabled
            if self.use_lower_threshold.get():
                try:
                    value = float(self.lower_threshold_value.get())
                    dataset['lower_threshold'] = value
                    dataset['lower_threshold_name'] = self.lower_threshold_name.get()
                except ValueError:
                    print("Invalid lower threshold value, ignoring")
            
            if self.use_upper_threshold.get():
                try:
                    value = float(self.upper_threshold_value.get())
                    dataset['upper_threshold'] = value
                    dataset['upper_threshold_name'] = self.upper_threshold_name.get()
                except ValueError:
                    print("Invalid upper threshold value, ignoring")
            
            # Update the current dataset
            self.current_dataset = dataset
            
            # Create and save the chart
            client_name = self.client_entry.get()
            chart = DailyCashBalanceChart(client_name=client_name)
            chart.plot(dataset)
            
            # Save with client name in the filename
            safe_filename = dataset_name.replace(' ', '_').lower()
            output_path = f"output/{client_id}_{safe_filename}.png"
            chart.save_chart(output_path)
            
            # Show success message with file path
            messagebox.showinfo("Success", "Data updated and chart regenerated.\n" +
                               f"Chart saved to {output_path}")
            
            # Display the chart
            chart.show_chart()
            
            # Close the editor window
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel) and widget.title() == "Data Editor":
                    widget.destroy()
                    break
                    
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error applying changes: {str(e)}")

def main():
    root = tk.Tk()
    app = ClipboardToolApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 