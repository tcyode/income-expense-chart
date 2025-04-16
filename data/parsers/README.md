# Data Parsers

This directory contains parsers for different data formats and chart types.

## Parsers

- `clipboard.py` - Parses data from clipboard text for different chart types
- `csv.py` (to be implemented) - Parses data from CSV files
- `excel.py` (to be implemented) - Parses data from Excel files

## Supported Formats

### Stacked Bar Chart
```
Month    Income    OPEX    Payroll    ...
Jan'24   1000      500     200        ...
Feb'24   1200      550     220        ...
```

### Daily Cash Balance Chart
```
Date         Account    Balance
2024-01-01   Checking   5000
2024-01-02   Checking   4800
```

### Cash Flow Area Chart
```
Date         Description              Amount    Category
2024-01-01   Initial Balance          5000      Balance
2024-01-02   Rent Payment            -1500      Housing
```

## Guidelines for Adding New Parsers

1. Create a new parser file for each data source type
2. Follow the pattern of returning a standardized data structure
3. Handle error cases gracefully
4. Add thorough documentation of expected formats 