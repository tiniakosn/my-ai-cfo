import pandas as pd

def get_financial_advice(df, income, expenses, savings):
    """
    V2.0 Smart CFO: Διαχωρίζει τα Δώρα/Bonus από τον Μισθό
    για να δίνει ρεαλιστικές προβλέψεις και όχι φούσκες.
    """
    
    # --- 1. DETECT BONUS / ΔΩΡΟ ---
    # Ψάχνουμε για έκτακτα εισοδήματα μέσα στις περιγραφές
    income_rows = df[df['Amount'] > 0].copy()
    bonus_keywords = ['ΔΩΡΟ', 'DORO', 'BONUS', 'XRISTOUGENNON', 'XMAS', 'CHRISTMAS', 'PASXA', 'EASTER', 'ΔΩΡΟΧΡ', 'DOROXRIST']
    
    bonus_amount = 0.0
    for index, row in income_rows.iterrows():
        text = (str(row['Transaction Description']) + " " + str(row['Comments'])).upper()
        if any(kw in text for kw in bonus_keywords):
            bonus_amount += row['Amount']

    # --- 2. ΥΠΟΛΟΓΙΣΜΟΣ "ΚΑΘΑΡΗΣ" ΑΠΟΤΑΜΙΕΥΣΗΣ ---
    # Πόσα αποταμίευσες ΜΟΝΟ από τον μισθό σου (χωρίς το δώρο)
    sustainable_savings = savings - bonus_amount
    
    # Ρυθμός αποταμίευσης (επί του κανονικού εισοδήματος)
    regular_income = income - bonus_amount
    if regular_income > 0:
        real_savings_rate = (sustainable_savings / regular_income) * 100
    else:
        real_savings_rate = 0

    # --- 3. ΔΗΜΙΟΥΡΓΙΑ REPORT ---
    report = []

    # A. REALITY CHECK (Δώρο vs Μισθός)
    if bonus_amount > 0:
        report.append(f"🎄 **Εντοπίστηκε Δώρο/Bonus:** {bonus_amount:.2f}€")
        
        if sustainable_savings <= 0:
            # Περίπτωση που περιγράφεις: Έφαγες τον μισθό και πείραξες και το δώρο
            deficit = abs(sustainable_savings)
            report.append(f"⚠️ **Προσοχή:** Η αποταμίευσή σου φαίνεται θετική ({savings:.2f}€) μόνο λόγω του Δώρου.")
            report.append(f"   👉 Στην πραγματικότητα, από τον μισθό σου **μπήκες μέσα κατά {deficit:.2f}€**.")
        else:
            # Περίπτωση που αποταμίευσες και από τον μισθό
            report.append(f"✅ **Good Job:** Αποταμίευσες ολόκληρο το Δώρο ΚΑΙ {sustainable_savings:.2f}€ από τον μισθό σου!")
    else:
        # Κλασικός μήνας
        if savings < 0:
            report.append(f"🔴 **Deficit:** Ξόδεψες {abs(savings):.2f}€ παραπάνω από όσα έβγαλες.")
        elif real_savings_rate < 10:
            report.append(f"🟠 **Low Savings:** Αποταμιεύεις μόνο το {real_savings_rate:.1f}% του μισθού.")
        else:
            report.append(f"✅ **Healthy:** Αποταμιεύεις το {real_savings_rate:.1f}% του μισθού.")

    report.append("\n") 

    # B. ΕΞΥΠΝΗ ΠΡΟΒΛΕΨΗ (FORECAST)
    # Προβάλουμε μόνο την "βιώσιμη" αποταμίευση x 12
    projected_yearly = (sustainable_savings * 12) + bonus_amount # (Το δώρο το μετράμε μια φορά)
    
    if projected_yearly > 0:
        report.append(f"🔮 **Ρεαλιστική Πρόβλεψη:** Με τον τρέχοντα ρυθμό εξόδων (χωρίς να υπολογίζουμε έξτρα δώρα), σε 1 χρόνο θα έχεις μαζέψει περίπου **{projected_yearly:,.0f}€**.")
    else:
        report.append("🔮 **Πρόβλεψη:** Αν συνεχίσεις έτσι, θα τρως από τα έτοιμα. Πρέπει να μειώσεις τα έξοδα του μήνα.")

    report.append("\n")

    # C. TOP EXPENSE (Η Μαύρη Τρύπα)
    elastic_expenses = df[
        (df['Amount'] < 0) & 
        (~df['Category'].isin(['🏠 Σπίτι & Πάγια', '💰 Αποταμίευση']))
    ]
    if not elastic_expenses.empty:
        top_category = elastic_expenses.groupby('Category')['Amount'].sum().abs().idxmax()
        top_cat_amount = elastic_expenses.groupby('Category')['Amount'].sum().abs().max()
        report.append(f"📉 **Μεγαλύτερο Έξοδο:** {top_category} ({top_cat_amount:.2f}€).")

    return "\n".join(report)