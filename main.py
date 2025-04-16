# main.py
# Entry point for the Financial Charts application

import tkinter as tk
import os
import sys
from ui.app import ChartApplication

def ensure_directories():
    """Ensure necessary directories exist."""
    directories = ["client_data", "output", "ui", "data", "data/parsers"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    """Start the Financial Charts application."""
    # Make sure all necessary directories exist
    ensure_directories()
    
    # Check if running as executable or script
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        application_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Change working directory to application path
    os.chdir(application_path)
    
    # Create the main application
    app = ChartApplication()
    
    # Start the application
    app.run()

if __name__ == "__main__":
    main() 