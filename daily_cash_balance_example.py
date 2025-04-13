# daily_cash_balance_example.py
# Example script to generate a daily cash balance chart with sample data

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from data_loader import FinancialDataManager
from charts.daily_cash_line import DailyCashBalanceChart

def ensure_directories():
    """Make sure required directories exist."""
    os.makedirs("client_data", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("data", exist_ok=True)

def generate_sample_data():
    """
    Generate sample daily cash balance data for multiple accounts.
    
    Returns:
    - DataFrame with columns [Date, Account, Balance]
    """
    # Generate dates for the past year
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Define accounts
    accounts = ['Checking', 'Savings', 'Investment', 'Emergency Fund', 'Tax Reserve', 'Business Account']
    
    # Initial balances for each account
    initial_balances = {
        'Checking': 5000,
        'Savings': 15000,
        'Investment': 25000,
        'Emergency Fund': 10000,
        'Tax Reserve': 7500,
        'Business Account': 12000
    }
    
    # Create an empty list to store data
    data_records = []
    
    # Generate data for each account
    for account in accounts:
        # Set initial balance
        balance = initial_balances[account]
        
        # Set volatility parameters for each account type
        if account == 'Checking':
            # High volatility - everyday expenses and income
            daily_change_mean = 0
            daily_change_std = 200
            large_change_prob = 0.2  # Probability of large deposits/withdrawals
            large_change_mean = 1500
            large_change_std = 1000
        elif account == 'Savings':
            # Medium volatility - occasional deposits/withdrawals
            daily_change_mean = 5  # Small interest
            daily_change_std = 50
            large_change_prob = 0.05
            large_change_mean = 1000
            large_change_std = 500
        elif account == 'Investment':
            # High volatility - market fluctuations
            daily_change_mean = 50  # Expected growth
            daily_change_std = 500
            large_change_prob = 0.03
            large_change_mean = 2000
            large_change_std = 1500
        elif account == 'Emergency Fund':
            # Low volatility - rarely used
            daily_change_mean = 3  # Small interest
            daily_change_std = 20
            large_change_prob = 0.01  # Rare withdrawals
            large_change_mean = -2000  # Usually withdrawals
            large_change_std = 1000
        elif account == 'Tax Reserve':
            # Medium volatility - regular additions, quarterly payments
            daily_change_mean = 10
            daily_change_std = 30
            large_change_prob = 0.08
            large_change_mean = 0  # Both deposits and withdrawals
            large_change_std = 2000
        else:  # Business Account
            # High volatility - business transactions
            daily_change_mean = 100
            daily_change_std = 300
            large_change_prob = 0.3
            large_change_mean = 1000
            large_change_std = 3000
            
        # Generate daily balances for this account
        for date in dates:
            # Simulate daily change
            daily_change = np.random.normal(daily_change_mean, daily_change_std)
            
            # Simulate large deposits/withdrawals occasionally
            if np.random.random() < large_change_prob:
                daily_change += np.random.normal(large_change_mean, large_change_std)
                
            # Update balance
            balance += daily_change
            
            # Ensure balance doesn't go negative for certain accounts
            if account in ['Emergency Fund', 'Tax Reserve'] and balance < 0:
                balance = 0
                
            # Add record
            data_records.append({
                'Date': date,
                'Account': account,
                'Balance': round(balance, 2)
            })
    
    # Create DataFrame
    df = pd.DataFrame(data_records)
    
    # Save to CSV for future use
    df.to_csv("data/sample_daily_cash_balance.csv", index=False)
    
    return df

def main():
    """Main program entry point."""
    ensure_directories()
    
    # Generate or load sample data
    sample_file = "data/sample_daily_cash_balance.csv"
    if os.path.exists(sample_file):
        print(f"Loading sample data from {sample_file}")
        data = pd.read_csv(sample_file)
    else:
        print("Generating new sample data...")
        data = generate_sample_data()
    
    # Initialize data manager and add a client
    data_mgr = FinancialDataManager()
    data_mgr.add_client("sample_client", "Sample Financial, Inc.")
    
    # Load daily cash balance data
    dataset = data_mgr.load_daily_cash_balance_data(data, "daily_cash_balance")
    
    # Create and show the chart
    chart = DailyCashBalanceChart()
    chart.plot(dataset)
    
    # Save the chart to a file
    output_file = "output/daily_cash_balance_chart.png"
    chart.save_chart(output_file)
    print(f"Chart saved to {output_file}")
    
    # Display the chart
    chart.show_chart()

if __name__ == "__main__":
    main() 