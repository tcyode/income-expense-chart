# test_negative_balances.py
# Test script for daily cash balance chart with negative account balances

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

def create_sample_data_with_negatives():
    """Create a sample dataset with some negative account balances."""
    data = [
        # Date, Account, Balance
        ["2023-01-01", "Checking", 5000.00],
        ["2023-01-01", "Savings", 15000.00],
        ["2023-01-01", "Credit Card", -2500.00],
        ["2023-01-01", "Investment", 25000.00],
        
        ["2023-01-02", "Checking", 5250.75],
        ["2023-01-02", "Savings", 15015.00],
        ["2023-01-02", "Credit Card", -3200.50],
        ["2023-01-02", "Investment", 24875.50],
        
        ["2023-01-03", "Checking", -1500.25],  # Checking goes negative
        ["2023-01-03", "Savings", 15025.75],
        ["2023-01-03", "Credit Card", -3500.00],
        ["2023-01-03", "Investment", 25125.00],
        
        ["2023-01-04", "Checking", -2100.00],  # More negative
        ["2023-01-04", "Savings", 15035.50],
        ["2023-01-04", "Credit Card", -3800.50],
        ["2023-01-04", "Investment", 25350.25],
        
        ["2023-01-05", "Checking", 1200.50],   # Back to positive
        ["2023-01-05", "Savings", 15045.25],
        ["2023-01-05", "Credit Card", -4200.75],
        ["2023-01-05", "Investment", 25425.75],
        
        ["2023-01-06", "Checking", 2500.00],
        ["2023-01-06", "Savings", 10045.25],   # Savings drops
        ["2023-01-06", "Credit Card", -4500.00],
        ["2023-01-06", "Investment", 20425.75], # Investment drops
        
        ["2023-01-07", "Checking", 3200.00],
        ["2023-01-07", "Savings", 8045.25],    # Continues dropping
        ["2023-01-07", "Credit Card", -5000.00], # More debt
        ["2023-01-07", "Investment", 18425.75],
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=["Date", "Account", "Balance"])
    
    # Save as CSV for reference
    df.to_csv("data/negative_balances_sample.csv", index=False)
    
    return df

def main():
    """Main test function."""
    ensure_directories()
    
    # Create sample data with negative balances
    df = create_sample_data_with_negatives()
    print(f"Created sample data with {len(df)} rows, including negative balances")
    
    # Initialize data manager
    data_mgr = FinancialDataManager()
    
    # Add a test client
    client_name = "Negative Balance Test"
    client_id = "negative_test"
    data_mgr.add_client(client_id, client_name)
    
    # Set as current client
    data_mgr.current_client = client_id
    
    # Load the data
    dataset = data_mgr.load_daily_cash_balance_data(df, "negative_balances")
    
    # Add a threshold line
    dataset['threshold'] = 20000  # Add a threshold line at $20,000
    
    # Create and display the chart
    print("Creating chart...")
    chart = DailyCashBalanceChart(client_name=client_name)
    chart.plot(dataset)
    
    # Save the chart
    output_file = "output/negative_balances_chart.png"
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