# charts/stacked_bar.py
# Stacked bar chart with net income line - refactored from monthly_chart_template.py

from charts.base import BaseChart
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.messagebox as messagebox

class StackedBarIncomeChart(BaseChart):
    """
    Creates a stacked bar chart with income, expenses, and net income line.
    Highlights the final month with category labels.
    """
    
    def __init__(self, title="Income vs. Stacked Expenses with Net Income", 
                 xlabel="Month", ylabel="Amount ($)",
                 figsize=(15, 8), highlight_last_month=True, client_name=None):
        """Initialize the stacked bar chart."""
        # Add client name to title if provided
        if client_name:
            title = f"{client_name}: {title}"
        super().__init__(title, xlabel, ylabel, figsize)
        self.highlight_last_month = highlight_last_month
        self.bar_width = 0.35
        self.client_name = client_name
    
    def plot(self, dataset):
        """Generate the stacked bar chart based on the dataset."""
        # Extract data from the dataset
        months = dataset['months']
        income_vals = dataset['income_values']
        expense_data = dataset['expense_data']
        expense_colors = dataset['expense_colors']
        net_income_vals = dataset['net_income_values']
        
        # If client name is in dataset and we didn't already set it in constructor
        if 'client_name' in dataset and dataset['client_name'] and not self.client_name:
            client_name = dataset['client_name']
            self.title = f"{client_name}: Income vs. Stacked Expenses with Net Income"
        
        # Create the figure
        self.create_figure()
        
        # Set the updated title
        self.ax.set_title(self.title)
        
        # Define x locations for the bars
        x = range(len(months))
        
        # Plot income bars
        self.ax.bar([i - self.bar_width/2 for i in x], income_vals, 
                   width=self.bar_width, label='Income', color='#90EE90')
        
        # Plot stacked expenses with labels on the last month if requested
        bottoms = [0] * len(months)
        last_month_index = len(months) - 1 if self.highlight_last_month else None
        
        # This part is from your original code - maintaining the stacked bars functionality
        for category, color in expense_colors.items():
            values = expense_data[category]
            self.ax.bar([i + self.bar_width/2 for i in x], values, 
                       width=self.bar_width, label=category, 
                       bottom=bottoms, color=color)
            
            # Add labels for the last month if values are positive
            if last_month_index is not None and values[last_month_index] > 0:
                height = bottoms[last_month_index] + values[last_month_index] / 2
                self.ax.text(last_month_index + self.bar_width/2 + 0.05, 
                            height, category, va='center', fontsize=10)
            
            # Update bottoms for next category
            bottoms = [bottoms[j] + values[j] for j in range(len(values))]
        
        # Plot net income dotted line
        self.ax.plot(x, net_income_vals, linestyle='dotted', marker='o', 
                    color='red', linewidth=2, label='Net Income')
        
        # Set x-axis labels with more space for rotation
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(months, rotation=45, ha='right')
        
        # Add styling
        self.add_styling()
        self.ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        
        # Adjust layout to prevent cut-off month labels
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)
        
        return self.fig, self.ax

    def process_with_fixed_format(self, text):
        """Process data with explicitly fixed format for this specific data"""
        try:
            lines = text.strip().split('\n')
            if not lines:
                messagebox.showerror("Error", "No data found")
                return
            
            # First, let's analyze and show what we're working with
            debug_info = []  # We'll collect debug info to show the user
            
            # First line contains month names
            header_line = lines[0]
            # Split by tabs or multiple spaces
            import re
            columns = re.split(r'\t+|\s{2,}', header_line.strip())
            debug_info.append(f"Found columns: {columns}")
            
            # Detect if data is in inverted format (months as columns)
            is_inverted = any(month in header_line.lower() for month in 
                             ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                              'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])
            
            debug_info.append(f"Data format detected: {'Inverted' if is_inverted else 'Standard'}")
            
            if is_inverted:
                # Get months from column headers (skip first column which is category names)
                months = columns[1:]  # Skip the first column header
                debug_info.append(f"Months detected: {months}")
                
                # Process each row to find income and expenses
                income_values = []
                expense_data = {}
                net_income_values = []
                
                # Process each line
                for line in lines[1:]:  # Skip header row
                    if not line.strip():  # Skip empty lines
                        continue
                        
                    # Split the line into parts
                    parts = re.split(r'\t+|\s{2,}', line.strip())
                    
                    # Get category name (first column)
                    category = parts[0]
                    # Handle multi-word categories
                    i = 1
                    while i < len(parts) and not self._is_likely_number(parts[i]):
                        category += " " + parts[i]
                        i += 1
                    
                    # Convert remaining parts to numbers
                    values = []
                    for val in parts[i:]:
                        try:
                            # Handle commas in numbers
                            num_val = float(val.replace(',', '')) if val.strip() else 0.0
                            values.append(num_val)
                        except ValueError:
                            values.append(0.0)
                    
                    # Categorize the row
                    category = category.strip().upper()
                    if "TOTAL INCOME" in category:
                        income_values = values
                        debug_info.append(f"Found income values: {values}")
                    elif "NET INCOME" in category:
                        net_income_values = values
                        debug_info.append(f"Found net income values: {values}")
                    elif not any(x in category for x in ["TOTAL", "NET INCOME"]):
                        expense_data[category] = values
                        debug_info.append(f"Found expense category {category}: {values}")
                
                # Verify we have all necessary data
                if not income_values:
                    raise ValueError("No income values found")
                if not expense_data:
                    raise ValueError("No expense categories found")
                
                # Create color scheme for expenses
                expense_colors = {}
                color_palette = [
                    '#4169E1', '#40E0D0', '#BA55D3', '#FF69B4', '#FBBC04', 
                    '#FF00FF', '#FF8000', '#32CD32', '#9370DB', '#008080'
                ]
                
                for i, category in enumerate(expense_data.keys()):
                    expense_colors[category] = color_palette[i % len(color_palette)]
                
                # If net income wasn't found, calculate it
                if not net_income_values:
                    net_income_values = []
                    for i in range(len(months)):
                        income = income_values[i] if i < len(income_values) else 0
                        total_expense = sum(expense_data[cat][i] for cat in expense_data)
                        net_income_values.append(income - total_expense)
                
                # Create the dataset
                dataset = {
                    'months': months,
                    'income_values': income_values,
                    'expense_data': expense_data,
                    'expense_colors': expense_colors,
                    'net_income_values': net_income_values
                }
                
                # Show debug information
                debug_window = tk.Toplevel(self.root)
                debug_window.title("Processing Results")
                debug_window.geometry("600x400")
                
                text_widget = tk.Text(debug_window, wrap=tk.WORD)
                text_widget.pack(fill=tk.BOTH, expand=True)
                
                for info in debug_info:
                    text_widget.insert(tk.END, info + "\n")
                
                # Create and show the chart
                try:
                    chart = StackedBarIncomeChart()
                    chart.plot(dataset)
                    chart.save_chart(f"output/chart_{self.dataset_entry.get() or 'default'}.png")
                    chart.show_chart()
                    messagebox.showinfo("Success", "Chart generated successfully!")
                except Exception as e:
                    messagebox.showerror("Chart Error", f"Error creating chart: {str(e)}")
                    raise
                
            else:
                messagebox.showerror("Error", "Data format not recognized as inverted format")
                return
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing data: {str(e)}\n\nPlease check the data format.")
            raise  # This will print the full error trace to the console
