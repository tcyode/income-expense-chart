import pandas as pd
import numpy as np
import io
import re
from datetime import datetime, timedelta

def parse_clipboard_data(text, chart_type="stacked_bar"):
    """Parse clipboard data based on the chart type.
    
    Args:
        text (str): Text data copied from clipboard
        chart_type (str): Type of chart to parse data for
        
    Returns:
        dict: Processed data suitable for the specified chart type
    """
    if chart_type == "stacked_bar":
        return parse_stacked_bar_data(text)
    elif chart_type == "daily_cash":
        return parse_daily_cash_data(text)
    elif chart_type == "cash_flow":
        return parse_cash_flow_data(text)
    else:
        raise ValueError(f"Unknown chart type: {chart_type}")

def detect_delimiter(text):
    """Detect the delimiter used in the data."""
    # Count potential delimiters
    tab_count = text.count('\t')
    comma_count = text.count(',')
    pipe_count = text.count('|')
    semicolon_count = text.count(';')
    
    # Find the most common delimiter
    delimiters = {
        '\t': tab_count,
        ',': comma_count,
        '|': pipe_count,
        ';': semicolon_count
    }
    
    # Return the most common delimiter, default to tab if none found
    most_common = max(delimiters.items(), key=lambda x: x[1])
    if most_common[1] > 0:
        return most_common[0]
    return '\t'  # Default to tab if no clear delimiter is found

def parse_stacked_bar_data(text):
    """Parse clipboard data for stacked bar chart.
    
    Expected format:
    Month    Income    OPEX    Payroll    ...
    Jan'24   1000      500     200        ...
    Feb'24   1200      550     220        ...
    """
    # Detect the delimiter
    delimiter = detect_delimiter(text)
    
    try:
        # Convert clipboard text to a dataframe
        df = pd.read_csv(io.StringIO(text), sep=delimiter)
        
        # Check if we have a header row that might contain "Type" labels
        has_type_row = False
        type_row_index = None
        
        # Look for a row with "Type" or similar in the first column
        for idx, row in df.iterrows():
            first_col = str(row.iloc[0]).strip().upper()
            if first_col in ['TYPE', 'CATEGORY', 'CATEGORIES']:
                has_type_row = True
                type_row_index = idx
                break
        
        # If we found a type row, use it to identify columns
        if has_type_row:
            type_row = df.iloc[type_row_index]
            # Remove the type row from the dataframe
            df = df.drop(type_row_index)
            
            # Get column types from the type row
            col_types = {}
            for col_idx, col_type in enumerate(type_row):
                col_type = str(col_type).strip().upper()
                if col_type in ['INCOME', 'REVENUE', 'TOTAL INCOME']:
                    col_types[df.columns[col_idx]] = 'income'
                elif col_type in ['NET INCOME', 'NET', 'PROFIT']:
                    col_types[df.columns[col_idx]] = 'net_income'
                elif col_type not in ['', 'NAN', 'TYPE', 'CATEGORY', 'MONTH']:
                    col_types[df.columns[col_idx]] = 'expense'
        
        # Reset index after removing rows
        df = df.reset_index(drop=True)
        
        # Identify columns if we didn't have a type row
        if not has_type_row:
            # Assume first column is month, second is income, rest are expenses
            # unless we find columns with specific names
            col_types = {}
            
            for col_idx, col in enumerate(df.columns):
                col_upper = col.upper()
                if col_upper in ['MONTH', 'DATE', 'PERIOD']:
                    col_types[col] = 'month'
                elif col_upper in ['INCOME', 'REVENUE', 'TOTAL INCOME']:
                    col_types[col] = 'income'
                elif col_upper in ['NET INCOME', 'NET', 'PROFIT']:
                    col_types[col] = 'net_income'
                elif col_idx > 0:  # Skip first column as it's likely the month
                    col_types[col] = 'expense'
        
        # Extract months
        month_col = df.columns[0]  # Assume first column is months
        months = df[month_col].tolist()
        
        # Extract income values
        income_col = next((col for col, type_ in col_types.items() if type_ == 'income'), None)
        if income_col:
            income_values = df[income_col].tolist()
            # Convert to float
            income_values = [float(str(v).replace(',', '')) if str(v).strip() not in ['', 'nan'] else 0.0 
                            for v in income_values]
        else:
            # If no income column found, use zeros
            income_values = [0.0] * len(months)
        
        # Extract net income values if available
        net_income_col = next((col for col, type_ in col_types.items() if type_ == 'net_income'), None)
        if net_income_col:
            net_income_values = df[net_income_col].tolist()
            # Convert to float
            net_income_values = [float(str(v).replace(',', '')) if str(v).strip() not in ['', 'nan'] else 0.0 
                                for v in net_income_values]
        else:
            # Will calculate later
            net_income_values = None
        
        # Extract expense data and colors
        expense_data = {}
        expense_colors = {}
        
        # Standard color palette for expenses
        color_palette = [
            '#4169E1', '#40E0D0', '#BA55D3', '#FF69B4', '#FBBC04', 
            '#FF00FF', '#FF8000', '#32CD32', '#9370DB', '#008080'
        ]
        
        # Get expense columns
        expense_cols = [col for col, type_ in col_types.items() if type_ == 'expense']
        
        for i, col in enumerate(expense_cols):
            category = col
            values = df[col].tolist()
            # Convert to float
            values = [float(str(v).replace(',', '')) if str(v).strip() not in ['', 'nan'] else 0.0 
                     for v in values]
            
            # Add to the expense data dictionary
            expense_data[category] = values
            
            # Assign a color from the palette (wrapping around if needed)
            color_index = i % len(color_palette)
            expense_colors[category] = color_palette[color_index]
        
        # Calculate net income if not provided
        if net_income_values is None:
            net_income_values = []
            for i, income in enumerate(income_values):
                total_expense = sum(expense_data[category][i] for category in expense_data)
                net_income_values.append(income - total_expense)
        
        # Assemble the result
        result = {
            'months': months,
            'income_values': income_values,
            'expense_data': expense_data,
            'expense_colors': expense_colors,
            'net_income_values': net_income_values
        }
        
        return result
    
    except Exception as e:
        raise ValueError(f"Error parsing stacked bar data: {e}")

def parse_daily_cash_data(text):
    """Parse clipboard data for daily cash balance chart.
    
    Handles two formats:
    
    Format 1 (one account per row):
    Date         Account    Balance
    2024-01-01   Checking   5000
    2024-01-02   Checking   4800
    
    Format 2 (multiple account columns):
    Date         Account1   Account2   Account3   ...
    2024-01-01   5000       1000       200        ...
    2024-01-02   4800       1200       250        ...
    """
    # Detect the delimiter
    delimiter = detect_delimiter(text)
    
    try:
        # Convert clipboard text to a dataframe
        df = pd.read_csv(io.StringIO(text), sep=delimiter)
        
        # Check if we have a multiple-column format (each column is an account)
        # or the standard format (account and balance columns)
        date_col = None
        first_data_col = None
        
        # First identify date column
        for col in df.columns:
            col_upper = str(col).upper()
            if col_upper in ['DATE', 'DAY', 'PERIOD']:
                date_col = col
                break
                
        # If no date column found, assume first column is date
        if date_col is None:
            date_col = df.columns[0]
        
        # Get the first non-date column
        for col in df.columns:
            if col != date_col:
                first_data_col = col
                break
        
        # Determine if we're dealing with wide format (each column is an account)
        # or long format (account and balance columns)
        format_type = "wide"  # Assume wide format initially
        account_col = None
        balance_col = None
        
        # Check if column names match account/balance pattern
        for col in df.columns:
            col_upper = str(col).upper()
            if col_upper in ['ACCOUNT', 'ACCOUNTS', 'SOURCE', 'CATEGORY']:
                account_col = col
                format_type = "long"
            elif col_upper in ['BALANCE', 'AMOUNT', 'VALUE']:
                balance_col = col
                format_type = "long"
        
        # Process date column regardless of format
        dates = []
        for date_str in df[date_col]:
            # Try different date formats
            date_str = str(date_str).strip()
            try:
                if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                    # ISO format YYYY-MM-DD
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                elif re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
                    # MM/DD/YYYY
                    date = datetime.strptime(date_str, '%m/%d/%Y')
                elif re.match(r'\d{1,2}/\d{1,2}/\d{2}', date_str):
                    # MM/DD/YY
                    date = datetime.strptime(date_str, '%m/%d/%y')
                elif re.match(r'\d{1,2}-\d{1,2}-\d{4}', date_str):
                    # MM-DD-YYYY
                    date = datetime.strptime(date_str, '%m-%d-%Y')
                elif re.match(r'\d{1,2}-\d{1,2}-\d{2}', date_str):
                    # MM-DD-YY
                    date = datetime.strptime(date_str, '%m-%d-%y')
                else:
                    # Try a flexible parser
                    date = pd.to_datetime(date_str).to_pydatetime()
                
                # Convert to ISO format string
                dates.append(date.strftime('%Y-%m-%d'))
            except Exception:
                # If date parsing fails, use the original string
                dates.append(date_str)
        
        # Color palette for accounts
        color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        
        # Create account data dictionary and colors
        account_data = {}
        account_colors = {}
        
        if format_type == "wide":
            # Process wide format (each column is an account)
            account_columns = [col for col in df.columns if col != date_col]
            
            for i, account_name in enumerate(account_columns):
                account_balances = []
                
                for balance in df[account_name]:
                    try:
                        # Remove currency symbols, commas, etc.
                        balance_str = str(balance).strip().replace('$', '').replace(',', '')
                        account_balances.append(float(balance_str))
                    except Exception:
                        # Use 0 if conversion fails
                        account_balances.append(0.0)
                
                # Add to account data dictionary
                account_data[account_name] = {
                    'dates': dates.copy(),  # All accounts have same dates
                    'balances': account_balances
                }
                
                # Assign color
                color_index = i % len(color_palette)
                account_colors[account_name] = color_palette[color_index]
        else:
            # Process long format (account and balance columns)
            if account_col is None:
                # If no account column identified, assume second column
                if len(df.columns) > 1:
                    account_col = df.columns[1]
                else:
                    # Fall back to a default account
                    accounts = ["Default Account"] * len(dates)
                    account_col = "Account"
                    df[account_col] = accounts
            
            if balance_col is None:
                # If no balance column identified, assume third column or second non-date column
                remaining_cols = [col for col in df.columns if col != date_col and col != account_col]
                if remaining_cols:
                    balance_col = remaining_cols[0]
                else:
                    raise ValueError("Could not identify balance column")
            
            # Extract accounts and balances
            accounts = [str(account).strip() for account in df[account_col]]
            balances = []
            
            for balance in df[balance_col]:
                try:
                    balance_str = str(balance).strip().replace('$', '').replace(',', '')
                    balances.append(float(balance_str))
                except Exception:
                    balances.append(0.0)
            
            # Process data for each unique account
            unique_accounts = sorted(set(accounts))
            
            for i, account in enumerate(unique_accounts):
                # Extract data points for this account
                account_dates = []
                account_balances = []
                
                for j in range(len(dates)):
                    if accounts[j] == account:
                        account_dates.append(dates[j])
                        account_balances.append(balances[j])
                
                # Sort by date
                date_balance_pairs = sorted(zip(account_dates, account_balances))
                account_dates = [pair[0] for pair in date_balance_pairs]
                account_balances = [pair[1] for pair in date_balance_pairs]
                
                # Add to account data
                account_data[account] = {
                    'dates': account_dates,
                    'balances': account_balances
                }
                
                # Assign color
                color_index = i % len(color_palette)
                account_colors[account] = color_palette[color_index]
        
        # Calculate total balances for each date
        all_dates = sorted(set(dates))
        total_balances = []
        
        for date in all_dates:
            total = 0.0
            for account_name, account_info in account_data.items():
                if date in account_info['dates']:
                    idx = account_info['dates'].index(date)
                    total += account_info['balances'][idx]
            total_balances.append(total)
        
        # Assemble the result
        result = {
            'dates': all_dates,
            'account_data': account_data,
            'account_colors': account_colors,
            'total_balances': total_balances
        }
        
        return result
    
    except Exception as e:
        raise ValueError(f"Error parsing daily cash balance data: {e}")
        import traceback
        traceback.print_exc()

def parse_cash_flow_data(text):
    """Parse clipboard data for cash flow area chart.
    
    Expected format:
    Date         Description              Amount    Category
    2024-01-01   Initial Balance          5000      Balance
    2024-01-02   Rent Payment            -1500      Housing
    """
    # Detect the delimiter
    delimiter = detect_delimiter(text)
    
    try:
        # Convert clipboard text to a dataframe
        df = pd.read_csv(io.StringIO(text), sep=delimiter)
        
        # Identify required columns
        date_col = None
        desc_col = None
        amount_col = None
        category_col = None
        
        # Try to identify columns by name
        for col in df.columns:
            col_upper = col.upper()
            if col_upper in ['DATE', 'DAY', 'PERIOD']:
                date_col = col
            elif col_upper in ['DESCRIPTION', 'DESC', 'MEMO', 'NOTES']:
                desc_col = col
            elif col_upper in ['AMOUNT', 'VALUE', 'TRANSACTION']:
                amount_col = col
            elif col_upper in ['CATEGORY', 'TYPE', 'GROUP']:
                category_col = col
        
        # If columns weren't identified by name, assume positions
        if date_col is None:
            date_col = df.columns[0]
        if desc_col is None and len(df.columns) > 1:
            desc_col = df.columns[1]
        if amount_col is None and len(df.columns) > 2:
            amount_col = df.columns[2]
        if category_col is None and len(df.columns) > 3:
            category_col = df.columns[3]
        
        # Process date column
        dates = []
        for date_str in df[date_col]:
            # Try different date formats
            date_str = str(date_str).strip()
            try:
                if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                    # ISO format YYYY-MM-DD
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                elif re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
                    # MM/DD/YYYY
                    date = datetime.strptime(date_str, '%m/%d/%Y')
                elif re.match(r'\d{1,2}/\d{1,2}/\d{2}', date_str):
                    # MM/DD/YY
                    date = datetime.strptime(date_str, '%m/%d/%y')
                elif re.match(r'\d{1,2}-\d{1,2}-\d{4}', date_str):
                    # MM-DD-YYYY
                    date = datetime.strptime(date_str, '%m-%d-%Y')
                elif re.match(r'\d{1,2}-\d{1,2}-\d{2}', date_str):
                    # MM-DD-YY
                    date = datetime.strptime(date_str, '%m-%d-%y')
                else:
                    # Try a flexible parser
                    date = pd.to_datetime(date_str).to_pydatetime()
                
                # Convert to ISO format string
                dates.append(date.strftime('%Y-%m-%d'))
            except Exception:
                # If date parsing fails, use the original string
                dates.append(date_str)
        
        # Get descriptions
        descriptions = []
        if desc_col:
            descriptions = [str(desc).strip() for desc in df[desc_col]]
        else:
            # Use default description if no description column
            descriptions = ["Transaction"] * len(dates)
        
        # Get amounts
        amounts = []
        for amount in df[amount_col]:
            # Convert to float
            try:
                # Remove currency symbols, commas, etc.
                amount_str = str(amount).strip().replace('$', '').replace(',', '')
                amounts.append(float(amount_str))
            except Exception:
                # Use 0 if conversion fails
                amounts.append(0.0)
        
        # Get categories
        categories = []
        if category_col:
            categories = [str(cat).strip() for cat in df[category_col]]
        else:
            # Use default category if no category column
            categories = ["Uncategorized"] * len(dates)
        
        # Create unique category list and color mapping
        unique_categories = sorted(set(categories))
        category_colors = {}
        
        # Color palette for categories
        color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        
        for i, category in enumerate(unique_categories):
            color_index = i % len(color_palette)
            category_colors[category] = color_palette[color_index]
        
        # Sort data by date
        sorted_data = sorted(zip(dates, descriptions, amounts, categories))
        
        # Create lists from sorted data
        sorted_dates = [item[0] for item in sorted_data]
        sorted_descriptions = [item[1] for item in sorted_data]
        sorted_amounts = [item[2] for item in sorted_data]
        sorted_categories = [item[3] for item in sorted_data]
        
        # Calculate running balance
        running_balance = []
        balance = 0.0
        
        for amount in sorted_amounts:
            balance += amount
            running_balance.append(balance)
        
        # Group transactions by category
        category_data = {}
        
        for category in unique_categories:
            category_dates = []
            category_amounts = []
            category_descriptions = []
            
            for i, cat in enumerate(sorted_categories):
                if cat == category:
                    category_dates.append(sorted_dates[i])
                    category_amounts.append(sorted_amounts[i])
                    category_descriptions.append(sorted_descriptions[i])
            
            category_data[category] = {
                'dates': category_dates,
                'amounts': category_amounts,
                'descriptions': category_descriptions
            }
        
        # Assemble the result
        result = {
            'dates': sorted_dates,
            'descriptions': sorted_descriptions,
            'amounts': sorted_amounts,
            'categories': sorted_categories,
            'running_balance': running_balance,
            'category_data': category_data,
            'category_colors': category_colors
        }
        
        return result
        
    except Exception as e:
        raise ValueError(f"Error parsing cash flow data: {e}")

def is_likely_month(text):
    """Check if a string is likely to be a month."""
    month_patterns = [
        r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\'?\d{2}$',
        r'^(January|February|March|April|May|June|July|August|September|October|November|December)\'?\d{2}$',
        r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s\-\.\_]?\d{4}$',
        r'^(January|February|March|April|May|June|July|August|September|October|November|December)[\s\-\.\_]?\d{4}$',
        r'^\d{1,2}[\-\/]\d{4}$',  # MM-YYYY or MM/YYYY
        r'^\d{4}[\-\/]\d{1,2}$',  # YYYY-MM or YYYY/MM
    ]
    
    for pattern in month_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return True
    return False 