# charts/daily_cash_line.py
# Daily Cash Balance Visualization - Line chart showing daily cash balances for multiple accounts

from charts.base import BaseChart
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

class DailyCashBalanceChart(BaseChart):
    """
    Creates a line chart showing daily cash balances for multiple accounts
    with a total balance line.
    """
    
    def __init__(self, title="Daily Cash Balance", 
                 xlabel="Date", ylabel="Balance ($)",
                 figsize=(15, 8), client_name=None):
        """Initialize the daily cash balance line chart."""
        # Add client name to title if provided
        if client_name:
            title = f"{client_name}: {title}"
        super().__init__(title, xlabel, ylabel, figsize)
        self.client_name = client_name
        
    def process_data(self, data):
        """
        Process raw data into a format suitable for plotting.
        
        Expected input format:
        - data: DataFrame with columns [Date, Account, Balance]
        
        Returns:
        - Dictionary with processed data ready for plotting
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame")
            
        # Ensure required columns exist
        required_cols = ['Date', 'Account', 'Balance']
        for col in required_cols:
            if col not in data.columns:
                raise ValueError(f"Input data must contain '{col}' column")
        
        # Convert dates to datetime if they aren't already
        if not pd.api.types.is_datetime64_any_dtype(data['Date']):
            data['Date'] = pd.to_datetime(data['Date'])
            
        # Ensure Balance is numeric
        data['Balance'] = pd.to_numeric(data['Balance'], errors='coerce')
        
        # Sort by date
        data = data.sort_values('Date')
        
        # Get unique dates and accounts
        dates = data['Date'].unique()
        accounts = data['Account'].unique()
        
        # Group by date and account to handle multiple entries for the same account on the same day
        # This ensures we only have one data point per account per day
        grouped_data = data.groupby(['Date', 'Account']).agg({'Balance': 'last'}).reset_index()
        
        # Create a pivot table: dates as index, accounts as columns
        pivot_data = grouped_data.pivot_table(
            index='Date', 
            columns='Account', 
            values='Balance',
            aggfunc='last'  # Use the last value for each day
        ).reset_index()
        
        # Fill any missing values with the previous day's value
        pivot_data = pivot_data.fillna(method='ffill')
        
        # Calculate total balance across all accounts for each date
        pivot_data['Total'] = pivot_data.iloc[:, 1:].sum(axis=1)
        
        return {
            'dates': pivot_data['Date'],
            'accounts': accounts,
            'account_data': {account: pivot_data[account].values for account in accounts},
            'total_balance': pivot_data['Total'].values
        }
        
    def plot(self, data):
        """
        Generate the daily cash balance line chart.
        
        Parameters:
        - data: Can be either:
            1. A pandas DataFrame with columns [Date, Account, Balance]
            2. A dictionary with processed data (output from process_data)
        """
        # Process data if it's a DataFrame
        if isinstance(data, pd.DataFrame):
            dataset = self.process_data(data)
        else:
            dataset = data
            
        # Extract data from the dataset
        dates = dataset['dates']
        accounts = dataset['accounts']
        account_data = dataset['account_data']
        total_balance = dataset['total_balance']
        
        # If client name is in dataset and we didn't already set it in constructor
        if 'client_name' in dataset and dataset['client_name'] and not self.client_name:
            client_name = dataset['client_name']
            self.title = f"{client_name}: Daily Cash Balance"
        
        # Create the figure with extra space for labels
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        
        # Set the updated title
        self.ax.set_title(self.title, fontsize=14, pad=20)
        
        # Color palette for different accounts
        colors = plt.cm.tab10.colors  # Using a colormap for consistent colors
        
        # Plot line for each account
        for i, account in enumerate(accounts):
            values = account_data[account]
            self.ax.plot(dates, values, linestyle='-', marker='', 
                        color=colors[i % len(colors)], linewidth=1.5, 
                        label=account, alpha=0.7)
        
        # Plot total balance with thicker line
        self.ax.plot(dates, total_balance, linestyle='-', marker='', 
                    color='black', linewidth=2.5, 
                    label='Total Balance')
        
        # Format x-axis with dates - improve date formatting
        date_format = mdates.DateFormatter('%b %d')  # Format as 'Jan 01'
        self.ax.xaxis.set_major_formatter(date_format)
        
        # Set appropriate date locator based on date range
        date_range = (dates.max() - dates.min()).days
        if date_range > 180:  # More than 6 months
            self.ax.xaxis.set_major_locator(mdates.MonthLocator())
            self.ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
        elif date_range > 30:  # More than a month
            self.ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))  # Every Monday
        else:  # Less than a month
            self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Every day
        
        # Rotate date labels for better readability
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add lower threshold line if provided (red dashed line)
        if 'lower_threshold' in dataset:
            threshold = dataset['lower_threshold']
            threshold_name = dataset.get('lower_threshold_name', f'Minimum (${threshold:,.2f})')
            self.ax.axhline(y=threshold, color='red', linestyle='--', alpha=0.7, 
                           label=threshold_name)
        
        # Add upper threshold line if provided (green dashed line)
        if 'upper_threshold' in dataset:
            threshold = dataset['upper_threshold']
            threshold_name = dataset.get('upper_threshold_name', f'Target (${threshold:,.2f})')
            self.ax.axhline(y=threshold, color='green', linestyle='--', alpha=0.7, 
                           label=threshold_name)
        
        # Backward compatibility for older datasets with just 'threshold'
        elif 'threshold' in dataset:
            threshold = dataset['threshold']
            self.ax.axhline(y=threshold, color='red', linestyle='--', alpha=0.7, 
                           label=f'Threshold (${threshold:,.2f})')
        
        # Add styling
        self.add_styling()
        
        # Add legend to the right outside the plot area
        self.ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5), frameon=True, 
                       fancybox=True, shadow=True)
        
        # Add grid for better readability
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Format y-axis with dollar signs and commas
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.2f}'))
        
        # Add more padding to avoid cutoff
        self.fig.subplots_adjust(bottom=0.15, right=0.8)
        
        # Adjust layout
        self.fig.tight_layout()
        
        return self.fig, self.ax
    
    def load_from_csv(self, csv_path):
        """
        Load data from a CSV file.
        
        Expected CSV format:
        Date,Account,Balance
        2023-01-01,Checking,5000.00
        2023-01-01,Savings,10000.00
        ...
        
        Returns:
        - DataFrame with the loaded data
        """
        try:
            data = pd.read_csv(csv_path)
            return data
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {e}") 