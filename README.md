# 🌟 Monthly Income vs. Expense Chart Generator (Baba Style)

Hi there, friend! 👋 Welcome to this cozy little Python project. It helps you make a beautiful chart that shows how much money came in 💚, how much went out 💸, and what's left each month ➕ ➖ = ❤️.

---

## 🎯 What This Project Does

This project creates colorful financial charts showing:

✅ Green bars for **income** (money in)
✅ Stacked bars for **expenses** by type (like payroll, materials, etc.)
✅ A dotted red line showing **net income** (income - expenses)
✅ Bonus! It highlights the last month with category labels ✨
✅ Daily cash balance visualization with multiple account lines
✅ Support for future balance projections with dotted lines

It also saves the chart as a picture file (PNG 📸) so you can use it anywhere.

## 💰 Daily Cash Balance Chart

This project also includes a daily cash balance visualization tool that:
- Shows multiple account balances over time
- Displays a total balance line across all accounts
- Supports future projections with a dotted line
- Can display threshold levels for monitoring

Input format for cash balance data:

---

## 🛠️ How to Set It Up (Just Once)

Open your terminal (PowerShell or Command Prompt), and type:

```bash
python -m venv .venv  # makes a sandbox for your project 🏖️
.venv\Scripts\activate  # step into the sandbox 🧼
pip install -r requirements.txt  # grab the tools you need 🎨
```

---

## ▶️ How to Run the Chart (Every Time)

There are two ways to use this tool:

### Option 1: Use the original template script
```bash
.venv\Scripts\activate  # activate your cozy coding space 🧘
python monthly_chart_template.py  # go make that chart! 🎉
```

Or you can double-click the `run_chart.bat` file if you're using Windows (it does all that for you 🤖).

### Option 2: Use the clipboard tool (Recommended)
```bash
.venv\Scripts\activate  # activate your cozy coding space 🧘
python clipboard_tool.py  # launch the friendly UI! 🪟
```

With the clipboard tool, you can:
- Paste data from Excel/Google Sheets
- Import data from CSV files
- Add Type rows to properly classify your columns
- Generate charts with less hassle

---

## 📊 Data Format (Important!)

For best results, your data should include:
1. A header row with column names (first column should be "Month")
2. A "Type" row that identifies column types:
   - "Income" for income columns
   - "Expense" for expense columns
   - "NET INCOME" for net income columns
3. Your actual data rows with numbers

Example:

Month    Income    OPEX      PAYROLL   MATERIALS   NET INCOME
Type     Income    Expense   Expense   Expense     NET INCOME
Jan'24   1000      200       300       150         350
Feb'24   1100      210       320       160         410
```

Don't worry if you don't include NET INCOME - it will be calculated automatically!

---

## 💾 Where's My Chart?

After you run it, look in your folder! You'll find:

```
📄 output/[dataset_name].png ✅
```

You can share it, print it, or send it to your biz team 📈💌

---

## 🧙 How to Change the Numbers

Two easy ways:
1. Edit the spreadsheet where your data lives, then copy & paste into the clipboard tool
2. Open the `monthly_chart_template.py` file and update the data arrays directly

---

## 🧠 Want to Go Further?
This project is just getting started. We've got big dreams! ✨

Check out `DEVELOPMENT_STATE.md` to see our progress and future plans:
- ✅ Reading from CSV files (done!)
- ✅ Accepting data via clipboard (done!)
- ✅ Auto-calculating net income (done!)
- 📄 Reading directly from Excel or Google Sheets
- 🖱️ Making it interactive like a dashboard
- 💼 Generating reports for clients

Made with heart, color, and clarity 💗

Keep coding with joy! 🧸✨

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

### Phase 1: Data Layer (Current phase)
- ✅ Create data loading module
- ✅ Set up a simple data structure to store client information and financial data
- ❌ Add basic file-based persistence so data doesn't need to be re-entered (Not fully implemented - save_data() not called)
- ✅ Support for clipboard data import
- ✅ CSV file import capability
- ✅ Type row for identifying column purposes
- ✅ Fix NET INCOME display as line graph, not stacked bar
- ✅ Automatic NET INCOME calculation

### Phase 1.5: Daily Cash Balance Chart (Current Priority)
- [ ] Create daily cash balance line chart module
  - [ ] Set up DailyCashBalanceChart class extending BaseChart
  - [ ] Implement multi-line visualization for multiple accounts
  - [ ] Add total balance calculation and display
  - [ ] Implement date axis formatting
  - [ ] Add support for future projections (dotted line)
  - [ ] Add threshold line functionality
- [ ] Add data processing for daily cash balances
  - [ ] Create CSV import function for daily cash data
  - [ ] Implement date parsing and handling
  - [ ] Set up account-based data transformation
- [ ] Create basic UI for cash balance charts
  - [ ] Build file upload interface
  - [ ] Add chart configuration options
  - [ ] Implement chart rendering and saving

Estimated time: 3-5 hours

### Phase 2: UI Enhancements (Next)
- [ ] Improved UI layout and design
- [ ] Direct Excel file import
- [ ] Save/load configuration
- [ ] Theme customization

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
- [ ] 💰 **Create daily cash balance visualization** (Current priority)

---

## 🐞 Known Glitches
- Some versions of Cursor might not auto-detect `.venv` until you select it manually (use `Python: Select Interpreter`)
- If you add too many expense categories, labels on bars may overlap 🤹
- ~~Net Income showing as an expense category in stacked bars instead of as a line~~ Fixed! ✅
- Client data is not being saved to disk. The data structure works in memory but `save_data()` method is not being called after chart generation. This needs to be fixed for true data persistence.

---

## 🤗 Final Thought
This isn't just code. It's a **practice in clarity, intention, and joy**. 
Thanks for being part of this — future-you is gonna love you for keeping it tidy ✨💜

## ⚠️ Known Issues

- **Client Data Persistence**: Currently, client data is stored in memory but not automatically saved to disk. Data will be lost when the application is closed. This will be fixed in an upcoming update.
