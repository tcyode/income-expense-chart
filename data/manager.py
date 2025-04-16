import json
import os
import pandas as pd
import numpy as np
from data.parsers.clipboard import parse_clipboard_data

class DataManager:
    """Central data management system for financial chart application."""
    
    def __init__(self):
        """Initialize the data manager."""
        self.clients = {}
        self.current_client = None
        
        # Ensure directories exist
        if not os.path.exists("client_data"):
            os.makedirs("client_data")
            print("Created client_data directory")
        if not os.path.exists("output"):
            os.makedirs("output")
            print("Created output directory")
            
        # Load any existing clients
        self.load_existing_clients()
    
    def load_existing_clients(self):
        """Load any existing client data files from the client_data directory."""
        client_dir = "client_data"
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
    
    def delete_client(self, client_id):
        """Delete a client and its data."""
        if client_id not in self.clients:
            return False
            
        # Remove from memory
        del self.clients[client_id]
        
        # Remove from disk
        file_path = os.path.join("client_data", f"{client_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted client file: {file_path}")
        except Exception as e:
            print(f"Error deleting client file {file_path}: {e}")
            
        # Reset current client if it was the deleted one
        if self.current_client == client_id:
            self.current_client = next(iter(self.clients)) if self.clients else None
            
        return True
    
    def get_client_list(self):
        """Get a list of all clients."""
        return [(client_id, data['name']) for client_id, data in self.clients.items()]
    
    def set_current_client(self, client_id):
        """Set the current active client."""
        if client_id in self.clients:
            self.current_client = client_id
            return True
        return False
    
    def save_data(self):
        """Save all client data to disk."""
        client_dir = "client_data"
        if not os.path.exists(client_dir):
            os.makedirs(client_dir)
            
        for client_id, client_data in self.clients.items():
            try:
                file_path = os.path.join(client_dir, f"{client_id}.json")
                with open(file_path, 'w') as f:
                    # Handle pandas objects that aren't JSON serializable
                    json.dump(client_data, f, indent=4, cls=PandasJSONEncoder)
                print(f"Saved client data to {file_path}")
            except Exception as e:
                print(f"Error saving client data for {client_id}: {e}")
                import traceback
                traceback.print_exc()
    
    def get_dataset(self, dataset_name, client_id=None):
        """Get a specific dataset for a client.
        
        Returns:
            dict: The dataset as a dictionary, or a valid empty dataset if not found
        """
        client_id = client_id or self.current_client
        if not client_id:
            raise ValueError("No client selected")
            
        result = None
        
        try:
            # Get the dataset
            if client_id in self.clients and dataset_name in self.clients[client_id]['datasets']:
                raw_dataset = self.clients[client_id]['datasets'][dataset_name]
                
                # Make sure it's a dictionary
                if isinstance(raw_dataset, dict):
                    result = raw_dataset
                else:
                    # Convert list or other types to a valid dictionary
                    print(f"Warning: Dataset '{dataset_name}' is not a dictionary. Converting to a valid format.")
                    result = {
                        'chart_type': 'unknown',
                        'data': raw_dataset,
                        'client_name': self.clients[client_id]['name']
                    }
                    # Save the converted version for future use
                    self.clients[client_id]['datasets'][dataset_name] = result
                    self.save_data()
        except Exception as e:
            print(f"Error getting dataset: {e}")
            import traceback
            traceback.print_exc()
        
        # If no valid dataset was found or an error occurred, return an empty valid dataset
        if result is None:
            result = {
                'chart_type': 'unknown',
                'client_name': self.clients[client_id]['name'] if client_id in self.clients else 'Unknown',
                'error': f"Dataset '{dataset_name}' not found or could not be loaded."
            }
        
        return result
    
    def get_datasets_for_client(self, client_id=None):
        """Get all datasets for a client."""
        client_id = client_id or self.current_client
        if not client_id:
            raise ValueError("No client selected")
            
        if client_id in self.clients:
            return list(self.clients[client_id]['datasets'].keys())
        return []
    
    def process_data(self, data_text, dataset_name, client_id=None, chart_type="stacked_bar"):
        """Process data for a specific chart type and save it to the client's dataset."""
        client_id = client_id or self.current_client
        if not client_id:
            raise ValueError("No client selected")
            
        # Call the appropriate parser based on chart type
        if chart_type == "stacked_bar":
            return self._process_stacked_bar_data(data_text, dataset_name, client_id)
        elif chart_type == "daily_cash":
            return self._process_daily_cash_data(data_text, dataset_name, client_id)
        elif chart_type == "cash_flow":
            return self._process_cash_flow_data(data_text, dataset_name, client_id)
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
    
    def _process_stacked_bar_data(self, data_text, dataset_name, client_id):
        """Process data for stacked bar chart."""
        try:
            # Parse the clipboard data
            result = parse_clipboard_data(data_text, "stacked_bar")
            
            # Add to client's datasets
            self.clients[client_id]['datasets'][dataset_name] = result
            
            # Add client name for reference
            result['client_name'] = self.clients[client_id]['name']
            result['chart_type'] = 'stacked_bar'
            
            return result
        except Exception as e:
            print(f"Error processing stacked bar data: {e}")
            raise
    
    def _process_daily_cash_data(self, data_text, dataset_name, client_id):
        """Process data for daily cash balance chart."""
        try:
            # Parse the clipboard data
            result = parse_clipboard_data(data_text, "daily_cash")
            
            # Add to client's datasets
            self.clients[client_id]['datasets'][dataset_name] = result
            
            # Add client name for reference
            result['client_name'] = self.clients[client_id]['name']
            result['chart_type'] = 'daily_cash'
            
            return result
        except Exception as e:
            print(f"Error processing daily cash data: {e}")
            raise
    
    def _process_cash_flow_data(self, data_text, dataset_name, client_id):
        """Process data for cash flow area chart."""
        try:
            # Parse the clipboard data
            result = parse_clipboard_data(data_text, "cash_flow")
            
            # Add to client's datasets
            self.clients[client_id]['datasets'][dataset_name] = result
            
            # Add client name for reference
            result['client_name'] = self.clients[client_id]['name']
            result['chart_type'] = 'cash_flow'
            
            return result
        except Exception as e:
            print(f"Error processing cash flow data: {e}")
            raise

    def validate_client_data(self, client_id):
        """Validate client data structure and correct any issues."""
        if client_id not in self.clients:
            return False
        
        client_data = self.clients[client_id]
        made_changes = False
        
        # Ensure all required fields exist
        if 'name' not in client_data:
            client_data['name'] = client_id
            made_changes = True
        
        if 'datasets' not in client_data:
            client_data['datasets'] = {}
            made_changes = True
        
        # Validate each dataset
        for dataset_name, dataset in list(client_data['datasets'].items()):
            # Skip if not a dictionary (e.g., it's a list)
            if not isinstance(dataset, dict):
                print(f"Warning: Dataset '{dataset_name}' is not a dictionary, skipping validation.")
                # Convert it to a minimal valid dictionary
                client_data['datasets'][dataset_name] = {
                    'chart_type': 'unknown',
                    'data': dataset  # Store original data for reference
                }
                made_changes = True
                continue
            
            # Add chart_type if missing
            if 'chart_type' not in dataset:
                # Try to infer chart type from data structure
                if 'months' in dataset and 'income_values' in dataset:
                    dataset['chart_type'] = 'stacked_bar'
                    made_changes = True
                elif 'dates' in dataset and ('account_data' in dataset or 'accounts' in dataset):
                    dataset['chart_type'] = 'daily_cash'
                    made_changes = True
                elif 'dates' in dataset and 'amounts' in dataset and 'running_balance' in dataset:
                    dataset['chart_type'] = 'cash_flow'
                    made_changes = True
                else:
                    dataset['chart_type'] = 'unknown'
                    made_changes = True
            
            # Normalize data structure based on chart type
            chart_type = dataset.get('chart_type')
            
            if chart_type == 'stacked_bar':
                # Ensure required fields exist for stacked bar chart
                required_fields = ['months', 'income_values', 'expense_data', 'expense_colors', 'net_income_values']
                for field in required_fields:
                    if field not in dataset:
                        if field == 'expense_data':
                            dataset[field] = {}
                        elif field == 'expense_colors':
                            dataset[field] = {}
                        elif field == 'net_income_values':
                            # Calculate if we have income and expense data
                            if 'income_values' in dataset and 'expense_data' in dataset:
                                income = dataset['income_values']
                                net_income = []
                                for i, inc in enumerate(income):
                                    total_expense = sum(dataset['expense_data'].get(cat, [0]*len(income))[i] 
                                                       for cat in dataset['expense_data'])
                                    net_income.append(inc - total_expense)
                                dataset[field] = net_income
                            else:
                                dataset[field] = [0]
                        else:
                            dataset[field] = []
                        made_changes = True
                        
            elif chart_type == 'daily_cash':
                # Handle legacy format - convert 'accounts' to 'account_data' if needed
                if 'accounts' in dataset and 'account_data' not in dataset:
                    account_data = {}
                    for account in dataset.get('accounts', []):
                        # Skip if account is not a dictionary
                        if not isinstance(account, dict):
                            continue
                        
                        account_name = account.get('name', 'Unknown')
                        account_data[account_name] = {
                            'dates': account.get('dates', []),
                            'balances': account.get('balances', [])
                        }
                    dataset['account_data'] = account_data
                    made_changes = True
                    
                # Ensure required fields exist for daily cash chart
                required_fields = ['dates', 'account_data', 'account_colors', 'total_balances']
                for field in required_fields:
                    if field not in dataset:
                        if field == 'account_data':
                            dataset[field] = {}
                        elif field == 'account_colors':
                            # Create colors for existing accounts
                            colors = {}
                            color_palette = [
                                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
                            ]
                            for i, account in enumerate(dataset.get('account_data', {}).keys()):
                                colors[account] = color_palette[i % len(color_palette)]
                            dataset[field] = colors
                        elif field == 'total_balances':
                            # Calculate total balances from account data
                            all_dates = []
                            for account_info in dataset.get('account_data', {}).values():
                                all_dates.extend(account_info.get('dates', []))
                            all_dates = sorted(set(all_dates))
                            
                            total_balances = []
                            for date in all_dates:
                                total = 0
                                for account, info in dataset.get('account_data', {}).items():
                                    if date in info.get('dates', []):
                                        idx = info.get('dates', []).index(date)
                                        total += info.get('balances', [])[idx] if idx < len(info.get('balances', [])) else 0
                                total_balances.append(total)
                            
                            dataset[field] = total_balances
                            dataset['dates'] = all_dates
                        else:
                            dataset[field] = []
                        made_changes = True
                        
            elif chart_type == 'cash_flow':
                # Ensure required fields exist for cash flow chart
                required_fields = ['dates', 'descriptions', 'amounts', 'categories', 'running_balance', 'category_data', 'category_colors']
                for field in required_fields:
                    if field not in dataset:
                        if field in ['category_data', 'category_colors']:
                            dataset[field] = {}
                        else:
                            dataset[field] = []
                        made_changes = True
        
        # Save changes if any were made
        if made_changes:
            self.save_data()
        
        return True

class PandasJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle pandas objects."""
    
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        if isinstance(obj, pd.Series):
            return obj.to_dict()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super().default(obj) 