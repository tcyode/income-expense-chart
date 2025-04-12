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
- ✅ Add basic file-based persistence so data doesn't need to be re-entered
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
- ✅ Create a simple GUI interface with Tkinter
- [ ] Improve the UI to allow:
  - [ ] Select data files with dialog
  - [ ] Choose chart types (add more chart options)
  - [ ] Select time periods with filters
  - [ ] Choose clients from a dropdown
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

---

## 🐞 Known Glitches
- Some versions of Cursor might not auto-detect `.venv` until you select it manually (use `Python: Select Interpreter`)
- If you add too many expense categories, labels on bars may overlap 🤹
- ~~Net Income showing as an expense category in stacked bars instead of as a line~~ Fixed! ✅

---

## 🤗 Final Thought
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
