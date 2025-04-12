# 🌟 Monthly Income vs. Expense Chart Generator (Baba Style)

Hi there, friend! 👋 Welcome to this cozy little Python project. It helps you make a beautiful chart that shows how much money came in 💚, how much went out 💸, and what's left each month ➕ ➖ = ❤️.

---

## 🎯 What This Project Does

This project creates colorful financial charts showing:

✅ Green bars for **income** (money in)
✅ Stacked bars for **expenses** by type (like payroll, materials, etc.)
✅ A dotted red line showing **net income** (income - expenses)
✅ Bonus! It highlights the last month with category labels ✨

It also saves the chart as a picture file (PNG 📸) so you can use it anywhere.

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
