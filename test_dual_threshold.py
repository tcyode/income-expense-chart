# test_dual_threshold.py
# Test script demonstrating dual threshold lines (upper and lower)

import pandas as pd
import matplotlib.pyplot as plt
from data_loader import FinancialDataManager
from charts.daily_cash_line import DailyCashBalanceChart
import os

def ensure_directories():
    """Make sure required directories exist."""
    os.makedirs("client_data", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("data", exist_ok=True)

def create_sample_data():
    """Create a sample dataset to demonstrate dual thresholds."""
    data = [
        # Date, Account, Balance
        ["2023-01-01", "Checking", 5000.00],
        ["2023-01-01", "Savings", 15000.00],
        ["2023-01-01", "Investment", 25000.00],
        ["2023-01-01", "Credit Card", -2500.00],
        
        ["2023-01-02", "Checking", 5250.75],
        ["2023-01-02", "Savings", 15015.00],
        ["2023-01-02", "Investment", 24875.50],
        ["2023-01-02", "Credit Card", -3200.50],
        
        ["2023-01-03", "Checking", 4975.25],
        ["2023-01-03", "Savings", 15025.75],
        ["2023-01-03", "Investment", 25125.00],
        ["2023-01-03", "Credit Card", -3500.00],
        
        ["2023-01-04", "Checking", 4850.00],
        ["2023-01-04", "Savings", 15035.50],
        ["2023-01-04", "Investment", 25350.25],
        ["2023-01-04", "Credit Card", -3800.50],
        
        ["2023-01-05", "Checking", 4725.50],
        ["2023-01-05", "Savings", 15045.25],
        ["2023-01-05", "Investment", 25425.75],
        ["2023-01-05", "Credit Card", -4200.75],
        
        ["2023-01-06", "Checking", 7500.00],
        ["2023-01-06", "Savings", 20045.25],
        ["2023-01-06", "Investment", 30425.75],
        ["2023-01-06", "Credit Card", -4500.00],
        
        ["2023-01-07", "Checking", 7200.00],
        ["2023-01-07", "Savings", 20045.25],
        ["2023-01-07", "Investment", 31425.75],
        ["2023-01-07", "Credit Card", -5000.00],
        
        ["2023-01-08", "Checking", 6950.00],
        ["2023-01-08", "Savings", 19045.25],
        ["2023-01-08", "Investment", 30425.75],
        ["2023-01-08", "Credit Card", -5200.50],
        
        ["2023-01-09", "Checking", 6700.00],
        ["2023-01-09", "Savings", 18045.25],
        ["2023-01-09", "Investment", 29425.75],
        ["2023-01-09", "Credit Card", -5500.00],
        
        ["2023-01-10", "Checking", 6450.00],
        ["2023-01-10", "Savings", 16045.25],
        ["2023-01-10", "Investment", 28425.75],
        ["2023-01-10", "Credit Card", -5800.50],
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=["Date", "Account", "Balance"])
    
    # Save as CSV for reference
    df.to_csv("data/dual_threshold_sample.csv", index=False)
    
    return df

def main():
    """Main test function."""
    ensure_directories()
    
    # Create sample data
    df = create_sample_data()
    print(f"Created sample data with {len(df)} rows")
    
    # Initialize data manager
    data_mgr = FinancialDataManager()
    
    # Add a test client
    client_name = "Dual Threshold Test"
    data_mgr.add_client("dual_threshold_test", client_name)
    
    # Load the data
    dataset = data_mgr.load_daily_cash_balance_data(df, "dual_threshold")
    
    # Add threshold lines
    lower_threshold = 40000
    upper_threshold = 55000
    
    dataset['lower_threshold'] = lower_threshold
    dataset['lower_threshold_name'] = "Critical Balance"
    
    dataset['upper_threshold'] = upper_threshold
    dataset['upper_threshold_name'] = "Target Reserve"
    
    # Create and display the chart
    print("Creating chart...")
    chart = DailyCashBalanceChart(client_name=client_name)
    chart.plot(dataset)
    
    # Save the chart
    output_file = "output/dual_threshold_chart.png"
    chart.save_chart(output_file)
    print(f"Chart saved to {output_file}")
    
    # Try to save the data
    try:
        data_mgr.save_data()
        print("Data saved successfully")
    except Exception as e:
        print(f"Error saving data: {e}")
    
    # Show the chart
    print("Displaying chart...")
    chart.show_chart()

if __name__ == "__main__":
    main() 