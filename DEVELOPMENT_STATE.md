# 🛠️ Development Notes & Roadmap (Baba Style)

Hey developer soul 👩‍💻👨‍💻 — welcome to the inside scoop! ✨ This doc keeps track of everything we've done, what's cooking, and where this little chart friend could grow next. Think of it as your cozy dev diary 📓💡

---

## ✅ What We Built
- A Python program that turns income + expenses into a **stacked bar chart**
- **Green bars** for income 💚, stacked colors for expense categories 🌈
- A **red dotted line** for net income ❤️📉📈
- Sweet little **labels for March 2025** categories for clarity 🏷️
- Export to PNG with high quality
- Clipboard tool UI for easy data pasting
- Type row support to accurately identify Income, Expense, and Net Income columns
- CSV file import option for structured data
- Automatic net income calculation when not provided in the data
- Daily cash balance visualization with multiple account lines
- Upper (green) and lower (red) threshold lines with custom labels
- Data editor for fixing date and value errors

---

## 🧱 Tools We Used
- Python 3 🐍
- Matplotlib (for the pretty pictures 🎨)
- Tkinter (for the friendly UI 💻)
- Virtual Environment (`.venv`) to keep things neat 🧼
- A `requirements.txt` file to remember which tools we need
- A `.bat` file for one-click magic on Windows 🧙‍♂️

---

## 📍 What's Working Great
- Chart renders beautifully and opens in a window
- Easy to edit data inside `monthly_chart_template.py`
- Clipboard tool for quick data import from Excel/Google Sheets
- Support for spreadsheet-like "Type" row to identify column purposes
- Automatic calculation of Net Income if not provided
- Saves the chart automatically
- Virtual env setup and clean folder structure

---

## 🌿 Development Phases

### Phase 0: Prototype
- ✅ Basic script with hardcoded data
- ✅ Generate static PNG image
- ✅ Simple stacked bar chart with income and expenses

### Phase 1: Data Layer
- ✅ Create data loading module
- ✅ Set up a simple data structure to store client information and financial data
- ✅ Add basic file-based persistence so data doesn't need to be re-entered
- ✅ Support for clipboard data import
- ✅ CSV file import capability
- ✅ Type row for identifying column purposes
- ✅ Fix NET INCOME display as line graph, not stacked bar
- ✅ Automatic NET INCOME calculation

### Phase 1.5: Daily Cash Balance Chart (Needs Bug Fixes) ⚠️
- ✅ Create daily cash balance line chart module
  - ✅ Set up DailyCashBalanceChart class extending BaseChart
  - ✅ Implement multi-line visualization for multiple accounts
  - ✅ Add total balance calculation and display
  - ✅ Implement date axis formatting
  - ✅ Add support for future projections with dotted lines
  - ✅ Add threshold line functionality with customizable labels
- ✅ Add data processing for daily cash balances
  - ✅ Create CSV import function for daily cash data
  - ✅ Implement date parsing and handling
  - ✅ Set up account-based data transformation
  - ✅ Support for negative balance values
- ✅ Create enhanced UI for cash balance charts
  - ✅ Build file upload interface and clipboard input
  - ✅ Add chart configuration options with threshold controls
  - ✅ Implement chart rendering and saving
  - ✅ Add data editor for fixing dates and values
- 🔄 Bug Fixes & Refactoring (Current Focus)
  - [ ] Fix date handling in `daily_cash_line.py` - calling `.max()` on string dates
  - [ ] Improve data parsing for different input formats
  - [ ] Create debug functionality for data format issues
  - [ ] Implement consistent data structure using pandas DataFrames
  - [ ] Fix loading existing datasets into the input panel
  - [ ] Standardize error handling and user feedback

### Phase 1.6: Cash Flow Area Chart (After Bug Fixes)
- [ ] Create cash flow area chart module
  - [ ] Set up CashFlowAreaChart class extending BaseChart
  - [ ] Implement flowing area visualization for cash movements
  - [ ] Support for multiple transactions in the same day
  - [ ] Handle running balance calculations
  - [ ] Add shaded areas for positive and negative flow regions
- [ ] Add data processing for cash flow data
  - [ ] Create data loader for transactions-based format
  - [ ] Implement date grouping and sorting
  - [ ] Support running balance verification
  - [ ] Add transaction categorization
- [ ] Create UI for cash flow area charts
  - [ ] Build specialized upload interface
  - [ ] Add filtering capabilities by category
  - [ ] Implement zooming to specific date ranges
  - [ ] Support transaction annotations

Estimated time: 5-7 hours

### Phase 2: UI Enhancements (Next)
- ✅ Create a simple GUI interface with Tkinter
- 🔄 Refactor codebase for improved modularity (Current Focus):
  - [ ] Convert data handling to pandas DataFrames throughout codebase
  - [ ] Split large files into focused components
  - [ ] Create centralized data management system
  - [ ] Implement consistent chart interface pattern
- [ ] Improve the UI to allow:
  - [ ] Client-based tab organization
  - [ ] Select data files with dialog
  - [ ] Choose chart types from dropdown within client tab
  - [ ] Select time periods with filters
  - [ ] Choose clients from a dropdown
  - [ ] Detachable tabs for side-by-side comparison
  - [ ] Comparison tab for multi-client/multi-chart view
- [ ] Direct Excel file import
- [ ] Save/load configuration
- [ ] Theme customization

Estimated time: 8-10 hours

### Phase 3: Advanced Features
- [ ] Interactive dashboard
- [ ] Trend analysis
- [ ] Multiple chart types
- [ ] Comparison views
- [ ] Data filtering options

### Phase 4: Distribution & Production
- [ ] Standalone executable
- [ ] Client management system
- [ ] Scheduled reports
- [ ] Cloud sync option

---

## 🔮 What's Next (Future Dev Options)
Here are some magical seeds we can plant later 🌱:

- [x] 📄 **Read data from CSV files** ✅
- [x] 🧮 Auto-calculate **net income from income - expenses** ✅
- [x] 📋 **Accept data from clipboard** to make it easy to use ✅
- [ ] 📄 **Read data directly from Excel or Google Sheets**
- [ ] 🧑‍💼 **Add dropdowns or filters** using Streamlit
- [ ] 📆 Add support for any month range (not just Sept–Mar)
- [ ] 🌐 Build a web dashboard with interactivity (hover like QuickBooks)
- [ ] 📊 Use Plotly for dynamic charting
- [ ] 🧾 Export to PDF or full report package
- [ ] ✨ Add animations or transitions for visual flair

---

## 🐞 Known Glitches
- Some versions of Cursor might not auto-detect `.venv` until you select it manually (use `Python: Select Interpreter`)
- If you add too many expense categories, labels on bars may overlap 🤹
- ~~Net Income showing as an expense category in stacked bars instead of as a line~~ Fixed! ✅
- There's an error when adding a lower threshold and clicking "Process & Generate Chart" in some scenarios - investigating this issue
- Sometimes data with year-end transitions (Dec-Jan) may show anomalies in date formatting
- JSON serialization can fail with certain pandas objects (added workaround with custom encoder)
- **Daily Cash Chart bug**: Error when trying to call `.max()` on a list of string dates in `daily_cash_line.py` - dates need to be converted to datetime objects
- **Loading existing datasets**: Not properly loading dataset content into the input panel
- **Data format inconsistencies**: Input parsing is not handling some formats correctly, needs more robust delimiter detection
- **Data structure**: Current mix of lists, dictionaries, and sometimes pandas objects leads to inconsistencies and bugs

## 📋 Data Structure Refactoring Plan
We're planning to refactor our data handling to use pandas DataFrames consistently:

1. **Consistent Data Types**:
   - Store dates as proper datetime objects
   - Maintain numeric types for amounts/balances
   - Keep categorical data (account names, etc.) as typed categories

2. **Central Data Management**:
   - Use DataFrame as the primary data structure
   - Convert to specialized formats only when needed for visualization
   - Implement standardized validation and cleaning

3. **Implementation Strategy**:
   - Fix critical bugs first for minimum working functionality
   - Refactor the data parsing layer to use pandas throughout
   - Update chart generation to work with the new data structure
   - Maintain backward compatibility for existing datasets

---

## 🔮 Final Thought
This isn't just code. It's a **practice in clarity, intention, and joy**. 
Thanks for being part of this — future-you is gonna love you for keeping it tidy ✨💜

Don't worry if you don't include NET INCOME - it will be calculated automatically!

---

## 💾 Where's My Chart?

After you run it, look in your folder! You'll find:

📄 output/[dataset_name].png ✅

You can share it, print it, or send it to your biz team 📈💌

---

## 🧙 How to Change the Numbers

Two easy ways:
1. Edit the spreadsheet where your data lives, then copy & paste into the clipboard tool
2. Open the `monthly_chart_template.py` file and update the data arrays directly

---

## 🧠 Want to Go Further?
This project is just getting started. We've got big dreams! ✨

Check out `DEVELOPMENT_STATE.md` to see our progress and future plans.

Made with heart, color, and clarity 💗

Keep coding with joy! 🧸✨
