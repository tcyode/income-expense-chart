# main.py
# Main entry point for the financial chart generator

from data_loader import FinancialDataManager, load_example_data
from charts.stacked_bar import StackedBarIncomeChart
import os

def ensure_directories():
    """Make sure required directories exist."""
    os.makedirs("client_data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

def main():
    """Main program entry point."""
    ensure_directories()
    
    # Load data from the example
    data_mgr = load_example_data()
    
    # Get the dataset for creating a chart
    dataset = data_mgr.get_dataset("2024_2025_monthly")
    
    # Add client name to the dataset
    client_name = data_mgr.clients[data_mgr.current_client]['name']
    dataset['client_name'] = client_name
    
    # Create and show the chart
    chart = StackedBarIncomeChart()
    chart.plot(dataset)
    
    # Save the chart to a file
    chart.save_chart("output/monthly_income_expense_chart.png")
    
    # Display the chart
    chart.show_chart()
    
    print("Chart generated successfully! Check the output directory.")

if __name__ == "__main__":
    main() 