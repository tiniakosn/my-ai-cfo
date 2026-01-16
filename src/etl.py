import pandas as pd
import numpy as np

def clean_amount(amount_str):
    if pd.isna(amount_str): return 0.0
    clean_str = str(amount_str).replace(' EUR', '').strip().replace('.', '').replace(',', '.')
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

def assign_category_data(row):
    """
    V16.0 - Merged Dining & Coffee into one subcategory.
    """
    raw_text = (str(row['Transaction Description']) + " " + str(row['Comments'])).upper()
    full_text = raw_text.replace('Ά', 'Α').replace('Έ', 'Ε').replace('Ή', 'Η').replace('Ί', 'Ι').replace('Ό', 'Ο').replace('Ύ', 'Υ').replace('Ώ', 'Ω')
    
    amount = row['Amount']
    day_name = row.get('Day_Name', '')

    # 1. ΑΠΟΤΑΜΙΕΥΣΗ
    if amount < 0 and ('TINIAKOS' in full_text or 'ΤΗΝΙΑΚΟΣ' in full_text): return '💰 Αποταμίευση', 'Μεταφορές σε εμένα'
    if 'ΜΙΣΘΟΔΟΣΙΑ' in full_text: return 'Salary', 'Μισθός'
    if 'ΚΑΤΑΘΕΣΗ' in full_text and amount > 0: return 'Deposit/Gift', 'Καταθέσεις'

    # 2. ΣΠΙΤΙ & ΠΑΓΙΑ
    if 'ΕΝΟΙΚ' in full_text or 'ENOIK' in full_text: return '🏠 Σπίτι & Πάγια', 'Ενοίκιο'
    if any(kw in full_text for kw in ['COSMOTE', 'VODAFONE', 'NOVA', 'WIND', 'DEI', 'PROTERGIA', 'EYDAP', 'VOLTON', 'KOINOXR']): return '🏠 Σπίτι & Πάγια', 'Λογαριασμοί'

    # 3. SUPERMARKET
    if any(kw in full_text for kw in ['SKLAVENITIS', 'LIDL', 'MARKET IN', 'AB VASSILOPOULOS', 'MY MARKET', 'KRITIKOS', 'MASOUTIS', 'BAZAAR', 'GALAXIAS', 'AV SHOP', 'PAPAGIA', 'KOUOLITY', 'QUALITY FOODS']): 
        return '🛒 Supermarket', 'Ψώνια Σπιτιού'
    
    # 4. LIFESTYLE (ΕΔΩ ΕΓΙΝΕ Η ΑΛΛΑΓΗ)
    
    # A. Delivery (Το κρατάμε ξεχωριστά γιατί είναι "κακή συνήθεια" σπιτιού)
    if any(kw in full_text for kw in ['WOLT', 'WOΛT', 'WΟΛΤ', 'E-FOOD', 'EFOOD', 'BOX', 'PIZZA', 'BURGER', 'SOUVLAKI']): 
        return '🍿 Lifestyle & Έξοδοι', 'Delivery'
    
    # B. Εστίαση & Καφές (Ενωμένα όλα τα "έξω": Καφέδες, Εστιατόρια, Ποτά, Κυλικεία)
    dining_keywords = [
        'CAFE', 'COFFEE', 'GREGORYS', 'GRIGORIS', 'EVEREST', 'FOURNOS', 'KYLIKEIO', 'MAMA JAY', 'RUDU', 'DILIEN', 'GEFSINUS', 'KARADIMAS', # Καφέδες
        'RESTAURANT', 'TAVERNA', 'BAR', 'CLUB', 'ESTIATORIA', 'HOLY GINGER', 'PINAKAS' # Φαγητό έξω
    ]
    if any(kw in full_text for kw in dining_keywords): 
        return '🍿 Lifestyle & Έξοδοι', 'Εστίαση & Καφές'
    
    # C. Διασκέδαση & Συνδρομές
    if any(kw in full_text for kw in ['NETFLIX', 'SPOTIFY', 'YOUTUBE', 'CINEMA', 'THEATER', 'TICKET', 'VIVA', 'MORE.GR']): 
        return '🍿 Lifestyle & Έξοδοι', 'Θέαμα & Συνδρομές'

    # 5. SHOPPING
    if any(kw in full_text for kw in ['PUBLIC', 'PLAISIO', 'ISTORM', 'GERMANOS', 'KOTSOVOLOS', 'APPLE STORE', 'APPLE.COM', 'ELECTRONICS', 'IKEA', 'LEROY', 'JUMBO', 'PRACTIKER', 'E-SHOP']): 
        return '🛍️ Shopping', 'Tech & Σπίτι'
    if any(kw in full_text for kw in ['ZARA', 'H&M', 'HM ', 'BSB', 'ATTICA', 'MAZARAKI', 'MICHALIK', 'VANIKIOTI', 'ACCESSORIES', 'CLOTHES', 'SHOES', 'INTERSPORT', 'ELLE', 'ARTOPOIIMATA']): 
        return '🛍️ Shopping', 'Ρούχα & Μόδα'
    if any(kw in full_text for kw in ['HONDOS', 'SEPHORA', 'BEAUTY', 'HAIR', 'BARBER', 'PHARMACY', 'FARMAKEIO', 'DOCTOR', 'HOSPITAL', 'IATROS']): 
        return '🛍️ Shopping', 'Υγεία & Ομορφιά'
    if 'IQOS' in full_text: return '🛍️ Shopping', 'Διάφορα Ψώνια'

    # 6. IRIS & ΜΕΤΑΦΟΡΕΣ
    if 'IRIS' in full_text or 'YPER' in full_text or 'ΥΠΕΡ' in full_text: 
        return '💸 Διάφορα', 'IRIS/Φίλοι'

    # 7. ΥΠΟΛΟΙΠΑ
    if any(kw in full_text for kw in ['UBER', 'BOLT', 'BEAT', 'FREENOW', 'OASA', 'SHELL', 'EKO', 'AVIN', 'AEGEAN']): return '🚗 Μετακίνηση', 'Μεταφορικά'
    if any(kw in full_text for kw in ['REVOLUT', 'PAYPAL', 'TOP UP']): return '💳 FinTech', 'Revolut'

    # Weekend Trap -> Πάει στο Εστίαση & Καφές
    if day_name in ['Saturday', 'Sunday'] and amount < 0:
        return '🍿 Lifestyle & Έξοδοι', 'Εστίαση & Καφές'

    # Fallback
    bank_cat = str(row['Bank Category']).upper()
    if 'ΕΣΤΙΑΤΟΡΙΑ' in bank_cat: return '🍿 Lifestyle & Έξοδοι', 'Εστίαση & Καφές' # Ενωμένο και εδώ
    if 'SUPERMARKET' in bank_cat: return '🛒 Supermarket', 'Ψώνια Σπιτιού'
    if 'ΡΟΥΧΙΣΜΟΣ' in bank_cat or 'ΑΞΕΣΟΥΑΡ' in bank_cat: return '🛍️ Shopping', 'Ρούχα (Bank)'
    if 'ΥΓΕΙΑ' in bank_cat: return '🛍️ Shopping', 'Υγεία (Bank)'
    if 'ΤΕΧΝΟΛΟΓΙΑ' in bank_cat: return '💸 Διάφορα', 'Uncategorized Tech'
    
    return '💸 Διάφορα', 'Uncategorized'

def load_data():
    file_path = "data/raw/bank_export.txt"
    start_row = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f: lines = f.readlines()
    except:
        with open(file_path, 'r', encoding='cp1253') as f: lines = f.readlines()

    for i, line in enumerate(lines):
        if 'Κατηγορία' in line and 'Ποσό' in line:
            start_row = i
            break
            
    try:
        df = pd.read_csv(file_path, sep='\t', skiprows=start_row)
    except:
        df = pd.read_csv(file_path, sep=';', skiprows=start_row)

    col_map = {
        'Ημ/νία Συναλλαγής': 'Date',
        'Περιγραφή Συναλλαγής': 'Transaction Description',
        'Σχόλια / Κωδικός Αναφοράς': 'Comments',
        'Ποσό': 'Amount',
        'Κατηγορία': 'Bank Category'
    }
    cols_to_keep = [c for c in col_map.keys() if c in df.columns]
    df = df[cols_to_keep].rename(columns=col_map)

    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Month'] = df['Date'].dt.strftime('%Y-%m')
    df['Day_Name'] = df['Date'].dt.day_name()
    df['Amount'] = df['Amount'].apply(clean_amount)
    
    df[['Category', 'Subcategory']] = df.apply(lambda x: pd.Series(assign_category_data(x)), axis=1)

    return df