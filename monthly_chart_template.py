# monthly_chart_template.py
# Description: Template for generating a monthly stacked bar chart with net income line and category labels on the final month (Mar'25)

import matplotlib.pyplot as plt

# === CONFIGURABLE DATA INPUT ===
months = ["Sept'24", "Oct'24", "Nov'24", "Dec'24", "Jan'25", "Feb'25", "Mar'25"]
x = range(len(months))

income_vals = [0, 22792.50, 23070.00, 23560.00, 22724.15, 22725.15, 24075.55]
net_income_vals = [-2090.00, 15551.90, -8336.87, 6349.55, 7138.03, -4503.62, 6904.69]

expense_data = {
    'OPEX (minus payroll)': [2090.0, 5084.83, 5051.76, 4681.96, 3651.93, 4718.19, 3742.52],
    'Payroll': [0, 0.00, 2020.09, 1516.50, 1507.51, 2932.50, 2535.11],
    'Royalties': [0, 0, 6479.25, 5356.22, 4770.91, 5051.68, 5237.46],
    'Owners Draw': [0, 0, 0, 3000, 3500, 4000, 5000],
    'Business Loan': [0, 2500, 2000, 2000, 2000, 1434.62, 2000],
    'Profit Payout': [0, 0, 0, 0, 0, 8870.63, 0],
    'Loan from Pervez': [0, 0, 12200, 0, 0, 0, 0],
}

expense_colors = {
    'OPEX (minus payroll)': '#4169E1',
    'Payroll': '#40E0D0',
    'Royalties': '#BA55D3',
    'Owners Draw': '#FF69B4',
    'Business Loan': '#FBBC04',
    'Profit Payout': '#FF00FF',
    'Loan from Pervez': '#FF8000'
}

# === PLOT SETUP ===
plt.figure(figsize=(15, 8))
bar_width = 0.35

# Plot income bars
plt.bar([i - bar_width/2 for i in x], income_vals, width=bar_width, label='Income', color='#90EE90')

# Plot stacked expenses with Mar'25 labels
bottoms = [0] * len(months)
mar_index = months.index("Mar'25")
for category, color in expense_colors.items():
    values = expense_data[category]
    plt.bar([i + bar_width/2 for i in x], values, width=bar_width, label=category, bottom=bottoms, color=color)
    if values[mar_index] > 0:
        height = bottoms[mar_index] + values[mar_index] / 2
        plt.text(mar_index + bar_width/2 + 0.05, height, category, va='center', fontsize=13)
    bottoms = [bottoms[j] + values[j] for j in range(len(values))]

# Plot net income dotted red line
plt.plot(x, net_income_vals, linestyle='dotted', marker='o', color='red', linewidth=2, label='Net Income')

# Styling
plt.xticks(x, months)
plt.xlabel("Month")
plt.ylabel("Amount ($)")
plt.title("Income vs. Stacked Expenses with Net Income (Mar'25 Labels)")
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Save or Show
plt.savefig("monthly_income_expense_chart.png", dpi=300, bbox_inches='tight')
plt.show()
