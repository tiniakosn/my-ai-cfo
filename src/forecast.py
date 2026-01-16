import pandas as pd
from datetime import datetime, timedelta

def project_goal_date(current_saved, goal_amount, monthly_savings_rate):
    """
    Υπολογίζει πότε θα πιάσεις τον στόχο με βάση τον τωρινό ρυθμό σου.
    """
    # 1. Έλεγχοι Ασφαλείας
    if current_saved >= goal_amount:
        return "🎉 Ο στόχος επιτεύχθηκε!", pd.DataFrame()
    
    if monthly_savings_rate <= 0:
        return "⚠️ Με αρνητική/μηδενική αποταμίευση, δεν θα φτάσεις ποτέ...", pd.DataFrame()

    # 2. Μαθηματικά Πρόβλεψης
    remaining_amount = goal_amount - current_saved
    months_needed = remaining_amount / monthly_savings_rate
    days_needed = int(months_needed * 30) # Μετατροπή σε μέρες κατά προσέγγιση
    
    # 3. Εύρεση Ημερομηνίας
    today = datetime.now()
    target_date = today + timedelta(days=days_needed)
    formatted_date = target_date.strftime("%d/%m/%Y") # π.χ. 15/08/2026
    
    # 4. Δημιουργία Δεδομένων για Γράφημα (Projection Chart)
    # Θέλουμε να φτιάξουμε μια γραμμή που ξεκινάει από ΣΗΜΕΡΑ και πάει μέχρι τον ΣΤΟΧΟ
    projection_data = []
    
    # Σημείο 0: Σήμερα
    projection_data.append({
        "Date": today,
        "Balance": current_saved,
        "Type": "Current"
    })
    
    # Σημείο 1: Κάθε μήνα μέχρι τον στόχο
    running_balance = current_saved
    current_sim_date = today
    
    for i in range(int(months_needed) + 2): # +2 για να είμαστε σίγουροι ότι θα περάσει τη γραμμή
        current_sim_date += timedelta(days=30)
        running_balance += monthly_savings_rate
        
        projection_data.append({
            "Date": current_sim_date,
            "Balance": running_balance,
            "Type": "Projected"
        })
        
        # Αν περάσαμε τον στόχο, σταματάμε
        if running_balance >= goal_amount * 1.1: # Λίγο παραπάνω για εφέ
            break
            
    df_project = pd.DataFrame(projection_data)
    
    return f"📅 Εκτιμώμενη Ημερομηνία: **{formatted_date}** (σε {months_needed:.1f} μήνες)", df_project