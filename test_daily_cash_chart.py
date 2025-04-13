# test_daily_cash_chart.py
# Simple test script for the daily cash balance chart

import pandas as pd
import matplotlib.pyplot as plt
from data_loader import FinancialDataManager
from charts.daily_cash_line import DailyCashBalanceChart
import os

def ensure_directories():
    """Make sure required directories exist."""
    os.makedirs("client_data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

def create_sample_data():
    """Create a small sample dataset for testing."""
    data = [
        # Date, Account, Balance
        ["2023-01-01", "Checking", 5000.00],
        ["2023-01-01", "Savings", 15000.00],
        ["2023-01-01", "Investment", 25000.00],
        ["2023-01-01", "Emergency Fund", 10000.00],
        
        ["2023-01-02", "Checking", 5250.75],
        ["2023-01-02", "Savings", 15015.00],
        ["2023-01-02", "Investment", 24875.50],
        ["2023-01-02", "Emergency Fund", 10005.25],
        
        ["2023-01-03", "Checking", 5975.25],
        ["2023-01-03", "Savings", 15025.75],
        ["2023-01-03", "Investment", 25125.00],
        ["2023-01-03", "Emergency Fund", 10010.50],
        
        ["2023-01-04", "Checking", 6250.00],
        ["2023-01-04", "Savings", 15035.50],
        ["2023-01-04", "Investment", 25350.25],
        ["2023-01-04", "Emergency Fund", 10015.75],
        
        ["2023-01-05", "Checking", 6125.50],
        ["2023-01-05", "Savings", 15045.25],
        ["2023-01-05", "Investment", 25425.75],
        ["2023-01-05", "Emergency Fund", 10021.00]
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=["Date", "Account", "Balance"])
    
    # Save as CSV for reference
    df.to_csv("data/test_daily_cash_sample.csv", index=False)
    
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
    client_name = "Test Client"
    data_mgr.add_client("test_client", client_name)
    
    # Load the data
    dataset = data_mgr.load_daily_cash_balance_data(df, "test_daily_cash")
    
    # Create and display the chart
    print("Creating chart...")
    chart = DailyCashBalanceChart(client_name=client_name)
    chart.plot(dataset)
    
    # Save the chart
    output_file = "output/test_daily_cash_chart.png"
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