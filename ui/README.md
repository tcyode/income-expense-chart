# UI Components

This directory contains the UI components for the Financial Charts application.

## Components

- `app.py` - Main application window with client tabs
- `input_panel.py` - Panel for data input via clipboard or file upload
- `chart_panel.py` - Panel for chart selection, configuration, and display

## Structure

The UI follows a modular approach:

1. App (main window)
   - Contains client tabs
   - Manages overall application state

2. Input Panel (per client tab)
   - Handles data input methods
   - Processes data input

3. Chart Panel (per client tab)
   - Manages chart selection
   - Provides chart-specific configuration
   - Displays and saves charts

## Future Improvements

- Detachable tabs for side-by-side comparison
- Comparison tab for multi-client/multi-chart view
- Enhanced data editor for each chart type
- Direct Excel import
- Theme customization 