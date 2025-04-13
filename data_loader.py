# data_loader.py
# Loads and formats financial data for chart visualization

import pandas as pd
import json
import os
import io
import csv
import numpy as np

class FinancialDataManager:
    """Manages financial data for multiple clients and time periods."""
    
    def __init__(self):
        """Initialize the data manager."""
        self.clients = {}
        self.current_client = None
        
        # Try to load any existing clients from saved files
        self.load_existing_clients()
    
    def load_existing_clients(self):
        """Load any existing client data files from the client_data directory."""
        client_dir = "client_data"
        if os.path.exists(client_dir):
            for filename in os.listdir(client_dir):
                if filename.endswith(".json"):
                    client_id = filename[:-5]  # Remove .json extension
                    try:
                        file_path = os.path.join(client_dir, filename)
                        with open(file_path, 'r') as f:
                            client_data = json.load(f)
                            self.clients[client_id] = client_data
                            print(f"Loaded client data from {file_path}")
                    except Exception as e:
                        print(f"Error loading client data from {filename}: {e}")
    
    def add_client(self, client_id, client_name=None):
        """Add a new client to the system."""
        if client_id not in self.clients:
            self.clients[client_id] = {
                'name': client_name or client_id,
                'datasets': {}
            }
            self.current_client = client_id
            return True
        return False
    
    def load_manual_data(self, dataset_name, months, income_values, expense_data, 
                         expense_colors, net_income_values=None):
        """Load data that's manually entered (like your current hardcoded data)."""
        if self.current_client is None:
            raise ValueError("No client selected. Add a client first.")
            
        # Calculate net income if not provided
        if net_income_values is None:
            net_income_values = []
            for i, income in enumerate(income_values):
                total_expense = sum(expense_data[category][i] for category in expense_data)
                net_income_values.append(income - total_expense)
        
        dataset = {
            'months': months,
            'income_values': income_values,
            'expense_data': expense_data,
            'expense_colors': expense_colors,
            'net_income_values': net_income_values
        }
        
        self.clients[self.current_client]['datasets'][dataset_name] = dataset
        return dataset
    
    def load_excel_data(self, file_path, sheet_name=0, dataset_name=None):
        """Import data from Excel file."""
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            return self._process_dataframe(df, dataset_name or os.path.basename(file_path))
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return False
    
    def load_csv_data(self, file_path, dataset_name=None):
        """Import data from CSV file."""
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            return self._process_dataframe(df, dataset_name or os.path.basename(file_path))
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return False
    
    def load_clipboard_data(self, clipboard_text, dataset_name="clipboard_data"):
        """
        Parse data that's copied from a spreadsheet and pasted as text.
        
        Expected format:
        Month   Income  OPEX    Payroll  ...
        Jan'24  1000    500     200      ...
        Feb'24  1200    550     220      ...
        ...
        """
        try:
            # Convert clipboard text to a dataframe
            # First, read the pasted text as CSV using StringIO
            df = pd.read_csv(io.StringIO(clipboard_text), sep='\t')
            return self._process_dataframe(df, dataset_name)
        except Exception as e:
            # Try another common delimiter (comma) if tab didn't work
            try:
                df = pd.read_csv(io.StringIO(clipboard_text), sep=',')
                return self._process_dataframe(df, dataset_name)
            except Exception as e2:
                print(f"Error parsing clipboard data: {e}\nThen: {e2}")
                return False
    
    def load_transposed_clipboard_data(self, clipboard_text, dataset_name="transposed_data"):
        """
        Load data where categories are in rows and months are in columns
        (the natural spreadsheet export format).
        
        Format expected:
        | Category      | Jan'24 | Feb'24 | Mar'24 | ...  | TOTAL |
        |---------------|--------|--------|--------|------|-------|
        | Total Income  | 1000   | 1200   | 1300   | ...  | 3500  |
        | OPEX          | 200    | 250    | 300    | ...  | 750   |
        | PAYROLL       | 300    | 350    | 400    | ...  | 1050  |
        | ...           | ...    | ...    | ...    | ...  | ...   |
        | NET INCOME    | 500    | 600    | 600    | ...  | 1700  |
        """
        if self.current_client is None:
            raise ValueError("No client selected. Add a client first.")
        
        try:
            # Read the pasted text as CSV
            import io
            import pandas as pd
            import numpy as np
            
            # Try to find the delimiter
            delimiter = self._detect_delimiter(clipboard_text)
            if not delimiter:
                raise ValueError("Could not detect delimiter in data")
            
            # Parse the table
            df = pd.read_csv(io.StringIO(clipboard_text), sep=delimiter)
            
            # Clean up column names - the first column might have no header
            if df.columns[0] == 'Unnamed: 0' or df.columns[0].strip() == '':
                df = df.rename(columns={df.columns[0]: 'Category'})
            
            # Extract the months (column headers, excluding first and last if TOTAL)
            months = list(df.columns[1:])
            if months[-1].upper() in ['TOTAL', 'SUM', 'TOTALS']:
                months = months[:-1]  # Remove the TOTAL column
            
            # Find the rows for income, expense categories, and net income
            income_row = None
            net_income_row = None
            expense_rows = []
            
            for idx, row in df.iterrows():
                category = str(row.iloc[0]).strip().upper()
                if 'INCOME' in category and 'NET' not in category:
                    income_row = row
                elif 'NET' in category and 'INCOME' in category:
                    net_income_row = row
                elif category not in ['', 'TOTAL', 'TOTAL EXPENSES']:
                    # Check if this is not a section header (usually has empty values)
                    values = row.iloc[1:len(months)+1]
                    if not values.isna().all() and not (values == '').all():
                        expense_rows.append(row)
            
            # Extract the data
            income_values = []
            if income_row is not None:
                income_values = income_row.iloc[1:len(months)+1].tolist()
                income_values = [float(str(v).replace(',', '')) if str(v).strip() not in ['', 'nan'] else 0.0 
                                for v in income_values]
            
            # Extract expense data
            expense_data = {}
            expense_colors = {}
            
            # Standard color palette for expenses
            color_palette = [
                '#4169E1', '#40E0D0', '#BA55D3', '#FF69B4', '#FBBC04', 
                '#FF00FF', '#FF8000', '#32CD32', '#9370DB', '#008080'
            ]
            
            for i, row in enumerate(expense_rows):
                category = str(row.iloc[0]).strip()
                values = row.iloc[1:len(months)+1].tolist()
                # Convert to float, replace empty/nan with 0
                values = [float(str(v).replace(',', '')) if str(v).strip() not in ['', 'nan'] else 0.0 
                          for v in values]
                
                # Add to the expense data dictionary
                expense_data[category] = values
                
                # Assign a color from the palette
                color_idx = i % len(color_palette)
                expense_colors[category] = color_palette[color_idx]
            
            # Extract net income values
            net_income_values = []
            if net_income_row is not None:
                net_income_values = net_income_row.iloc[1:len(months)+1].tolist()
                net_income_values = [float(str(v).replace(',', '')) if str(v).strip() not in ['', 'nan'] else 0.0 
                                    for v in net_income_values]
            else:
                # Calculate net income if not provided
                net_income_values = []
                for i in range(len(months)):
                    income = income_values[i] if i < len(income_values) else 0
                    expenses = sum(expense_data[cat][i] for cat in expense_data)
                    net_income_values.append(income - expenses)
            
            # Create the dataset
            dataset = {
                'months': months,
                'income_values': income_values,
                'expense_data': expense_data,
                'expense_colors': expense_colors,
                'net_income_values': net_income_values
            }
            
            self.clients[self.current_client]['datasets'][dataset_name] = dataset
            return dataset
        
        except Exception as e:
            print(f"Error processing transposed data: {e}")
            return None
    
    def _process_dataframe(self, df, dataset_name):
        """Process a dataframe into our dataset format."""
        if self.current_client is None:
            raise ValueError("No client selected. Add a client first.")
        
        # Check if we have enough data
        if len(df.columns) < 3:  # Need at least month, income, and one expense
            print("Not enough columns in data source. Need at least month, income and one expense.")
            return False
        
        try:
            # First column should be months
            months = df.iloc[:, 0].tolist()
            
            # Second column is usually income
            income_values = df.iloc[:, 1].tolist()
            
            # Remaining columns are expense categories
            expense_data = {}
            expense_colors = {}
            
            # Default colors palette (can be customized later)
            colors = ['#4169E1', '#40E0D0', '#BA55D3', '#FF69B4', 
                      '#FBBC04', '#FF00FF', '#FF8000', '#32CD32', 
                      '#9370DB', '#20B2AA', '#DA70D6', '#FF6347']
            
            # Process each expense category
            for i, col in enumerate(df.columns[2:]):
                category = col.strip()
                expense_data[category] = df.iloc[:, i+2].tolist()
                expense_colors[category] = colors[i % len(colors)]  # Cycle through colors
            
            # Calculate net income
            net_income_values = []
            for i, income in enumerate(income_values):
                total_expense = sum(expense_data[category][i] for category in expense_data)
                net_income_values.append(income - total_expense)
            
            # Create the dataset
            dataset = {
                'months': months,
                'income_values': income_values,
                'expense_data': expense_data,
                'expense_colors': expense_colors,
                'net_income_values': net_income_values
            }
            
            self.clients[self.current_client]['datasets'][dataset_name] = dataset
            print(f"Successfully processed data into dataset: {dataset_name}")
            return dataset
            
        except Exception as e:
            print(f"Error processing dataframe: {e}")
            return False
    
    def parse_clipboard_format(self, text):
        """
        Helper function to determine the format of clipboard text.
        Returns the delimiter used.
        """
        # Count potential delimiters
        tabs = text.count('\t')
        commas = text.count(',')
        semicolons = text.count(';')
        
        # Find the most common delimiter
        delimiters = {'\t': tabs, ',': commas, ';': semicolons}
        most_common = max(delimiters, key=delimiters.get)
        
        return most_common if delimiters[most_common] > 0 else None
    
    def save_data(self, directory="client_data"):
        """Save client data to JSON files."""
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created {directory} directory")
        
        # Add JSON serialization for pandas objects
        class PandasJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                import pandas as pd
                import numpy as np
                
                # Handle pandas Series
                if isinstance(obj, pd.Series):
                    return obj.tolist()
                
                # Handle pandas Timestamp
                if isinstance(obj, pd.Timestamp):
                    return obj.isoformat()
                    
                # Handle numpy arrays
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                    
                # Handle numpy numeric types
                if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
                    return int(obj)
                if isinstance(obj, (np.float64, np.float32, np.float16)):
                    return float(obj)
                    
                # Let the base class handle other types or raise TypeError
                return super().default(obj)
        
        print(f"Attempting to save data for {len(self.clients)} clients to {directory}")
        
        for client, client_data in self.clients.items():
            try:
                print(f"Processing client {client} with {len(client_data.get('datasets', {}))} datasets")
                
                # Analyze each dataset
                for dataset_name, dataset in client_data.get('datasets', {}).items():
                    if 'months' in dataset:
                        # This is a stacked bar chart dataset
                        months = dataset.get('months', [])
                        print(f"  Dataset {dataset_name} contains {len(months)} months of data")
                        if months:
                            print(f"    First month: {months[0]}")
                            income_values = dataset.get('income_values', [])
                            if income_values:
                                print(f"    First income value: {income_values[0]}")
                            expense_data = dataset.get('expense_data', {})
                            print(f"    Expense categories: {list(expense_data.keys())}")
                    elif 'dates' in dataset:
                        # This is a daily cash balance dataset
                        dates = dataset.get('dates', [])
                        print(f"  Dataset {dataset_name} contains {len(dates)} days of data")
                        if len(dates) > 0:
                            print(f"    First date: {dates[0]}")
                            accounts = dataset.get('accounts', [])
                            print(f"    Accounts: {list(accounts)}")
                
                # Save the client data
                file_path = os.path.join(directory, f"{client}.json")
                with open(file_path, 'w') as f:
                    json.dump(client_data, f, indent=4, cls=PandasJSONEncoder)
                print(f"Data saved for client {client} to {file_path}")
            except Exception as e:
                print(f"Error saving data: {e}")
                # Print the full stack trace for debugging
                import traceback
                traceback.print_exc()
                
                # Try to save just the basic client info
                try:
                    basic_client_data = {
                        "name": client_data.get("name", client),
                        "datasets": {}
                    }
                    file_path = os.path.join(directory, f"{client}.json")
                    with open(file_path, 'w') as f:
                        json.dump(basic_client_data, f, indent=4)
                    print(f"Saved basic client data for {client}")
                except Exception as basic_error:
                    print(f"Could not even save basic client data: {basic_error}")
    
    def load_saved_data(self, client_id, directory="client_data"):
        """Load client data from a saved JSON file."""
        file_path = os.path.join(directory, f"{client_id}.json")
        try:
            with open(file_path, 'r') as f:
                client_data = json.load(f)
                self.clients[client_id] = client_data
                self.current_client = client_id
            return True
        except Exception as e:
            print(f"Error loading client data: {e}")
            return False
    
    def get_dataset(self, dataset_name, client_id=None):
        """Retrieve a specific dataset for charting."""
        client = client_id or self.current_client
        if client is None:
            raise ValueError("No client specified")
            
        if client not in self.clients or dataset_name not in self.clients[client]['datasets']:
            return None
            
        return self.clients[client]['datasets'][dataset_name]
    
    def load_daily_cash_balance_data(self, data_source, dataset_name="daily_cash_balance", 
                                     date_col="Date", account_col="Account", balance_col="Balance"):
        """
        Load daily cash balance data from a file or clipboard text.
        
        Parameters:
        - data_source: Either a file path (str) or DataFrame with columns [Date, Account, Balance]
        - dataset_name: Name to give the dataset
        - date_col: Name of the date column (default: "Date")
        - account_col: Name of the account column (default: "Account")
        - balance_col: Name of the balance column (default: "Balance")
        
        Expected data format (as CSV):
        Date,Account,Balance
        2023-01-01,Checking,5000.00
        2023-01-01,Savings,10000.00
        ...
        
        Returns:
        - The processed dataset
        """
        if self.current_client is None:
            raise ValueError("No client selected. Add a client first.")
            
        # Load the data based on the source type
        if isinstance(data_source, str):
            # Check if it's a file path or clipboard text
            if os.path.exists(data_source):
                # It's a file path
                if data_source.lower().endswith('.csv'):
                    df = pd.read_csv(data_source)
                elif data_source.lower().endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(data_source)
                else:
                    raise ValueError("Unsupported file type. Only CSV and Excel files are supported.")
            else:
                # Assume it's clipboard text
                try:
                    df = pd.read_csv(io.StringIO(data_source), sep='\t')
                except:
                    # Try with comma separator
                    df = pd.read_csv(io.StringIO(data_source), sep=',')
        elif isinstance(data_source, pd.DataFrame):
            # It's already a DataFrame
            df = data_source
        else:
            raise ValueError("data_source must be a file path, clipboard text, or DataFrame")
            
        # Standardize column names
        if date_col != "Date" and date_col in df.columns:
            df = df.rename(columns={date_col: "Date"})
        if account_col != "Account" and account_col in df.columns:
            df = df.rename(columns={account_col: "Account"})
        if balance_col != "Balance" and balance_col in df.columns:
            df = df.rename(columns={balance_col: "Balance"})
            
        # Validate required columns
        required_cols = ["Date", "Account", "Balance"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Data must contain '{col}' column")
        
        # Convert dates to datetime
        df["Date"] = pd.to_datetime(df["Date"])
        
        # Ensure Balance is numeric
        df["Balance"] = pd.to_numeric(df["Balance"], errors='coerce')
        
        # Sort by date
        df = df.sort_values("Date")
        
        # Store the raw data
        if 'raw_data' not in self.clients[self.current_client]:
            self.clients[self.current_client]['raw_data'] = {}
        
        self.clients[self.current_client]['raw_data'][dataset_name] = df.to_dict(orient='records')
        
        # Process the data for visualization
        # Get unique dates and accounts
        dates = df["Date"].unique()
        accounts = df["Account"].unique()
        
        # Create a pivot table: dates as index, accounts as columns
        pivot_data = df.pivot_table(
            index='Date', 
            columns='Account', 
            values='Balance',
            aggfunc='sum'  # In case there are multiple entries for the same account on the same day
        ).reset_index()
        
        # Calculate total balance across all accounts for each date
        pivot_data['Total'] = pivot_data.iloc[:, 1:].sum(axis=1)
        
        # Create the dataset for the chart
        dataset = {
            'dates': pivot_data['Date'],
            'accounts': accounts,
            'account_data': {account: pivot_data[account].values for account in accounts},
            'total_balance': pivot_data['Total'].values,
            'client_name': self.clients[self.current_client]['name']
        }
        
        # Store the processed dataset
        self.clients[self.current_client]['datasets'][dataset_name] = dataset
        
        return dataset

# Example of how to use this class with your existing data
def load_example_data():
    """Load the example data from monthly_chart_template.py"""
    data_mgr = FinancialDataManager()
    data_mgr.add_client("example_client", "Example Business")
    
    # This matches your current hardcoded data
    months = ["Sept'24", "Oct'24", "Nov'24", "Dec'24", "Jan'25", "Feb'25", "Mar'25"]
    
    income_vals = [0, 22792.50, 23070.00, 23560.00, 22724.15, 22725.15, 24075.55]
    
    expense_data = {
        'OPEX (minus payroll)': [2090.0, 5084.83, 5051.76, 4681.96, 3651.93, 4718.19, 3742.52],
        'Payroll': [0, 0.00, 2020.09, 1516.50, 1507.51, 2932.50, 2535.11],
        'Royalties': [0, 0, 6479.25, 5356.22, 4770.91, 5051.68, 5237.46],
        'Owners Draw': [0, 0, 0, 3000, 3500, 4000, 5000],
        'Business Loan': [0, 2500, 2000, 2000, 2000, 1434.62, 2000],
        'Profit Payout': [0, 0, 0, 0, 0, 8870.63, 0],
        'Loan from Pervez': [0, 0, 12200, 0, 0, 0, 0],
    }
    
    expense_colors = {
        'OPEX (minus payroll)': '#4169E1',
        'Payroll': '#40E0D0',
        'Royalties': '#BA55D3',
        'Owners Draw': '#FF69B4',
        'Business Loan': '#FBBC04',
        'Profit Payout': '#FF00FF',
        'Loan from Pervez': '#FF8000'
    }
    
    net_income_vals = [-2090.00, 15551.90, -8336.87, 6349.55, 7138.03, -4503.62, 6904.69]
    
    data_mgr.load_manual_data(
        "2024_2025_monthly", 
        months, 
        income_vals, 
        expense_data, 
        expense_colors, 
        net_income_vals
    )
    
    return data_mgr

# Example of using clipboard data
def example_clipboard_usage():
    """Example of how to use clipboard data."""
    # This is data you might copy from Excel or Google Sheets
    clipboard_text = """Month	Income	OPEX	Payroll	Royalties	Owners Draw
Jan'24	20000	5000	2000	6000	3000
Feb'24	22000	5200	2100	6200	3500
Mar'24	21000	4800	2200	6100	3500"""

    data_mgr = FinancialDataManager()
    data_mgr.add_client("new_client", "Business From Clipboard")
    data_mgr.load_clipboard_data(clipboard_text, "Q1_2024")
    
    # You could now create a chart with this data
    dataset = data_mgr.get_dataset("Q1_2024")
    return data_mgr, dataset

if __name__ == "__main__":
    # Test the data manager
    data_mgr = load_example_data()
    data_mgr.save_data()
    print("Example data loaded and saved successfully!")
    
    # Test clipboard functionality
    clipboard_mgr, clipboard_data = example_clipboard_usage()
    if clipboard_data:
        print("Clipboard data processed successfully:")
        print(f"Months: {clipboard_data['months']}")
        print(f"Income: {clipboard_data['income_values']}")
        print(f"Expense categories: {list(clipboard_data['expense_data'].keys())}")
