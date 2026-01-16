import pandas as pd
import numpy as np

def get_top_expenses(df, n=10):
    """
    Επιστρέφει τα n μεγαλύτερα έξοδα του μήνα.
    """
    expenses = df[
        (df['Amount'] < 0) & 
        (df['Category'] != '💰 Αποταμίευση')
    ].copy()
    
    top_expenses = expenses.sort_values(by='Amount', ascending=True).head(n)
    return top_expenses[['Date', 'Subcategory', 'Comments', 'Amount']]

def generate_advice(df, savings_rate):
    advice_list = []
    if savings_rate < 0:
        advice_list.append("⚠️ **Critical:** Ξοδεύεις παραπάνω από το εισόδημα. Έλεγξε τα 'Shopping' και 'Lifestyle'.")
    elif savings_rate < 300:
        advice_list.append("ℹ️ **Tip:** Καλή προσπάθεια. Μπορούμε να αυξήσουμε την αποταμίευση;")
    else:
        advice_list.append("✅ **Μπράβο!** Εξαιρετική οικονομική υγεία.")
    return advice_list

def check_budget(df, custom_limits=None):
    """
    Ελέγχει τον προϋπολογισμό βάσει των ορίων που θέτει ο χρήστης.
    """
    DEFAULT_LIMITS = {
        "🏠 Σπίτι & Πάγια": 650, "🛒 Supermarket": 250, "🍿 Lifestyle & Έξοδοι": 200,   
        "🛍️ Shopping": 250, "🚗 Μετακίνηση": 100, "💳 FinTech": 50, "💸 Διάφορα": 50
    }
    limits = custom_limits if custom_limits else DEFAULT_LIMITS

    expenses = df[
        (df['Amount'] < 0) & 
        (df['Category'] != '💰 Αποταμίευση')
    ].copy()
    
    actual_spend = expenses.groupby('Category')['Amount'].sum().abs().round(2)
    budget_data = []
    
    all_categories = set(actual_spend.index) | set(limits.keys())

    for category in all_categories:
        if category == '💰 Αποταμίευση': continue
        amount = actual_spend.get(category, 0.0)
        limit = limits.get(category, 0.0)

        if limit > 0:
            percent = min(amount / limit, 1.0)
            status = "⚠️" if amount > limit else "✅"
        else:
            percent = 0.0
            status = "ℹ️" if amount > 0 else "-"

        if amount > 0 or limit > 0:
            budget_data.append({
                "Category": category,
                "Actual (€)": amount,
                "Limit (€)": limit,
                "Progress": percent,
                "Status": status,
                "Left (€)": limit - amount
            })
    
    df_budget = pd.DataFrame(budget_data)
    if not df_budget.empty:
        df_budget = df_budget.sort_values(by='Actual (€)', ascending=False)

    return df_budget

