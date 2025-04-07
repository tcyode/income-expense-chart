<<<<<<< HEAD
# 🌟 Monthly Income vs. Expense Chart Generator (Baba Style)

Hi there, friend! 👋 Welcome to this cozy little Python project. It helps you make a beautiful chart that shows how much money came in 💚, how much went out 💸, and what's left each month ➕ ➖ = ❤️.

---

## 🎯 What This Project Does

This script creates a colorful chart from **September 2024 to March 2025**, showing:

✅ Green bars for **income** (money in)
✅ Stacked bars for **expenses** by type (like payroll, royalties, etc.)
✅ A dotted red line showing **net income** (income - expenses)
✅ Bonus! It highlights March 2025 with cute labels ✨

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

After you’ve set it up once:

```bash
.venv\Scripts\activate  # activate your cozy coding space 🧘
python monthly_chart_template.py  # go make that chart! 🎉
```

Or you can double-click the `run_chart.bat` file if you're using Windows (it does all that for you 🤖).

---

## 💾 Where’s My Chart?

After you run it, look in your folder! You’ll find:

```
📄 monthly_income_expense_chart.png ✅
```

You can share it, print it, or send it to your biz team 📈💌

---

## 🧙 How to Change the Numbers

Want to show a different month or new data?
Open the `monthly_chart_template.py` file and look for these parts:

- `months` → change the months
- `income_vals` → update money-in for each month
- `expense_data` → update each category's expenses
- `net_income_vals` → update the red dotted line (net 💖)

---

## 🧠 Want to Go Further?
This project is just getting started. We’ve got big dreams! ✨

Check out `DEVELOPMENT_STATE.md` to see future plans like:
- Reading from Excel or Google Sheets 📄
- Making it interactive like a dashboard 🖱️
- Generating reports for clients 💼

Made with heart, color, and clarity 💗

Keep coding with joy! 🧸✨
======
