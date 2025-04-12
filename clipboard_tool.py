# clipboard_tool.py
# A simple tool to test the clipboard data loading functionality

import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from data_loader import FinancialDataManager
from charts.stacked_bar import StackedBarIncomeChart
import re
import csv

class ClipboardToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Chart - Clipboard Tool")
        self.root.geometry("600x500")
        
        self.data_mgr = FinancialDataManager()
        self.data_mgr.add_client("clipboard_client", "Clipboard Data")
        
        # Create widgets
        self.create_widgets()
    
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
    
    def process_data(self):
        """Process the clipboard data and generate a chart."""
        clipboard_text = self.text_area.get("1.0", tk.END)
        
        if len(clipboard_text.strip()) < 10:  # Arbitrary minimum length
            messagebox.showerror("Error", "Please paste some data first!")
            return
        
        # Update client name if changed
        client_name = self.client_entry.get()
        if client_name != self.data_mgr.clients.get("clipboard_client", {}).get("name"):
            self.data_mgr.clients["clipboard_client"]["name"] = client_name
        
        # Process the data
        dataset_name = self.dataset_entry.get() or "clipboard_data"
        dataset = self.data_mgr.load_clipboard_data(clipboard_text, dataset_name)
        
        if not dataset:
            messagebox.showerror("Error", "Could not process the data. Check the format.")
            return
        
        # Add client name to dataset
        dataset['client_name'] = client_name
        
        # Debug before creating chart
        print(f"Dataset for chart:")
        print(f"Months: {dataset['months']}")
        print(f"Income values: {dataset['income_values']}")
        print(f"Net income values: {dataset['net_income_values']}")
        print(f"Client name: {dataset['client_name']}")
        
        # Generate and show the chart with improved net income handling
        chart = StackedBarIncomeChart(client_name=client_name)
        chart.plot(dataset)
        chart.save_chart(f"output/{dataset_name}.png")
        chart.show_chart()
        
        messagebox.showinfo("Success", 
                           f"Chart generated successfully and saved to 'output/{dataset_name}.png'")
    
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
                    income = float(values[income_idx].replace(',', ''))
                    income_values.append(income)
                except (ValueError, IndexError):
                    print(f"Income value error in line: {line}")
                    income_values.append(0.0)
                
                for idx, header in expense_columns:
                    try:
                        if idx < len(values) and values[idx].strip():
                            value = float(values[idx].replace(',', ''))
                            expense_data[header].append(value)
                        else:
                            expense_data[header].append(0.0)
                    except (ValueError, IndexError):
                        print(f"Error parsing expense {header} in line: {line}")
                        expense_data[header].append(0.0)
                
                if net_income_idx is not None and net_income_idx < len(values):
                    try:
                        value = values[net_income_idx].strip()
                        if value:
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
            
            client_name = self.client_entry.get() or "Clipboard Client"
            dataset_name = self.dataset_entry.get() or "clipboard_data"
            
            print(f"\nFinal data prepared for charting:")
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
            
            self.data_mgr.clients["clipboard_client"]["name"] = client_name
            self.data_mgr.clients["clipboard_client"]["datasets"][dataset_name] = dataset
            
            chart = StackedBarIncomeChart(client_name=client_name)
            chart.plot(dataset)
            chart.save_chart(f"output/{dataset_name}.png")
            chart.show_chart()
            
            messagebox.showinfo("Success", 
                               f"Chart generated successfully and saved to 'output/{dataset_name}.png'")
        except Exception as e:
            messagebox.showerror("Error", f"Error processing data: {str(e)}\n\nPlease check the data format.")
            raise

    def _is_likely_month(self, text):
        """Check if text is likely a month."""
        month_patterns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return any(pattern in text for pattern in month_patterns)

    def upload_csv(self):
        """Upload and process data from a CSV file."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        
        try:
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                
                # Read header row
                headers = next(reader)
                
                # Check if the next row is a type row
                has_type_row = False
                types = None
                row_check = next(reader, None)
                
                if row_check and any(cell.lower() == 'type' for cell in row_check):
                    has_type_row = True
                    types = row_check
                    first_data_row = next(reader, None)  # Get the first actual data row
                else:
                    first_data_row = row_check  # The row we read is actually the first data row
                
                if has_type_row:
                    # Create mapping of column types
                    column_types = {}
                    for i, header in enumerate(headers):
                        if i < len(types):
                            column_types[header] = types[i].upper()
                    
                    # Find columns by type
                    income_idx = None
                    expense_columns = []
                    net_income_idx = None
                    
                    for i, header in enumerate(headers):
                        if i < len(types):
                            column_type = types[i].upper()
                            if column_type == "INCOME":
                                income_idx = i
                            elif column_type == "EXPENSE":
                                expense_columns.append((i, header))
                            elif "NET" in column_type and "INCOME" in column_type:
                                net_income_idx = i
                else:
                    # Use default assumptions as before
                    income_idx = headers.index('Income') if 'Income' in headers else 1
                    net_income_idx = headers.index('Net Income') if 'Net Income' in headers else None
                    expense_columns = [(i, header) for i, header in enumerate(headers) 
                                      if header not in ['Month', 'Income', 'Net Income']]
                
                # Initialize data storage
                months = []
                income_values = []
                expense_data = {headers[idx]: [] for idx, _ in expense_columns}
                net_income_values = []
                
                # Process the first data row if we have it
                if first_data_row:
                    months.append(first_data_row[0])
                    
                    try:
                        income_values.append(float(first_data_row[income_idx].replace(',', '')))
                    except (ValueError, IndexError):
                        income_values.append(0.0)
                    
                    for idx, header in expense_columns:
                        try:
                            if idx < len(first_data_row) and first_data_row[idx].strip():
                                expense_data[header].append(float(first_data_row[idx].replace(',', '')))
                            else:
                                expense_data[header].append(0.0)
                        except (ValueError, IndexError):
                            expense_data[header].append(0.0)
                    
                    if net_income_idx is not None and net_income_idx < len(first_data_row):
                        try:
                            value = first_data_row[net_income_idx].strip()
                            if value:
                                net_income_values.append(float(value.replace(',', '')))
                            else:
                                # Calculate net income
                                total_expenses = sum(expense_data[cat][-1] for cat in expense_data)
                                net_income = income_values[-1] - total_expenses
                                net_income_values.append(net_income)
                        except (ValueError, IndexError):
                            # Calculate net income on error
                            total_expenses = sum(expense_data[cat][-1] for cat in expense_data)
                            net_income = income_values[-1] - total_expenses
                            net_income_values.append(net_income)
                
                # Process the rest of the rows
                for row in reader:
                    if not row or not row[0].strip():
                        continue
                    
                    months.append(row[0])
                    
                    try:
                        income_values.append(float(row[income_idx].replace(',', '')))
                    except (ValueError, IndexError):
                        income_values.append(0.0)
                    
                    for idx, header in expense_columns:
                        try:
                            if idx < len(row) and row[idx].strip():
                                expense_data[header].append(float(row[idx].replace(',', '')))
                            else:
                                expense_data[header].append(0.0)
                        except (ValueError, IndexError):
                            expense_data[header].append(0.0)
                    
                    if net_income_idx is not None and net_income_idx < len(row):
                        try:
                            value = row[net_income_idx].strip()
                            if value:
                                net_income_values.append(float(value.replace(',', '')))
                            else:
                                # Calculate net income
                                total_expenses = sum(expense_data[cat][-1] for cat in expense_data)
                                net_income = income_values[-1] - total_expenses
                                net_income_values.append(net_income)
                        except (ValueError, IndexError):
                            # Calculate net income on error
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

            dataset = {
                'months': months,
                'income_values': income_values,
                'expense_data': expense_data,
                'expense_colors': expense_colors,
                'net_income_values': net_income_values,
                'client_name': self.client_entry.get() or "Clipboard Client"
            }

            self.data_mgr.clients["clipboard_client"]["datasets"][self.dataset_entry.get() or "clipboard_data"] = dataset
            
            chart = StackedBarIncomeChart(client_name=dataset['client_name'])
            chart.plot(dataset)
            chart.save_chart(f"output/{self.dataset_entry.get() or 'clipboard_data'}.png")
            chart.show_chart()
            
            messagebox.showinfo("Success", "Chart generated successfully from CSV.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process CSV: {str(e)}")

def main():
    root = tk.Tk()
    app = ClipboardToolApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 