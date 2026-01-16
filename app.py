import streamlit as st
import pandas as pd
import os
import json 
from src.etl import load_data
from src.analytics import generate_advice, check_budget, get_top_expenses
from src.ai_advisor import get_financial_advice
from src.forecast import project_goal_date
from src.charts import plot_sankey, get_bucket_html
from src.history import load_history, plot_monthly_overview, plot_category_trends
from src.styles import apply_pro_style, render_hero_section, display_dashboard_card

# --- 1. CONFIG ---
st.set_page_config(page_title="AI CFO", page_icon="💳", layout="wide")
apply_pro_style()

# --- 0. DATA & SETTINGS ---
os.makedirs("config", exist_ok=True)
BUDGET_FILE = "config/budget_limits.json"
GOALS_FILE = "config/savings_goals_v2.json"

# 🔒 PRIVACY UPDATE: Όλα τα ποσά είναι στο 0 για να μην φαίνονται προσωπικά δεδομένα
DEFAULT_BUDGETS = {
    "🏠 Home & Utilities": 0, 
    "🛒 Supermarket": 0, 
    "🍿 Lifestyle & Fun": 0,   
    "🛍️ Shopping": 0, 
    "🚗 Transport": 0, 
    "💳 FinTech": 0, 
    "💸 Misc": 0
}

# 🔒 PRIVACY UPDATE: Ένα κενό παράδειγμα στόχου
DEFAULT_GOALS = [
    {"name": "🎯 My First Goal", "target": 1000, "saved": 0}
]

if 'budget_limits' not in st.session_state:
    # Αν υπάρχει αρχείο (τοπικά), φόρτωσέ το. Αλλιώς βάλε τα μηδενικά.
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r", encoding='utf-8') as f: st.session_state.budget_limits = json.load(f)
    else: st.session_state.budget_limits = DEFAULT_BUDGETS.copy()

if 'goals_config' not in st.session_state:
    if os.path.exists(GOALS_FILE):
        with open(GOALS_FILE, "r", encoding='utf-8') as f: st.session_state.goals_config = json.load(f)
    else: st.session_state.goals_config = DEFAULT_GOALS.copy()

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8992/8992203.png", width=90)
    st.markdown("### Control Center")
    uploaded_file = st.file_uploader("Upload Statement (CSV/TXT)", type=['txt', 'csv'])
    
    if uploaded_file:
        save_path = "data/raw/bank_export.txt"
        os.makedirs("data/raw", exist_ok=True)
        with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
        st.success("File Processed!", icon="✅")
        # Καθαρίζουμε τη μνήμη για να φορτώσει το νέο αρχείο
        if 'raw_data' in st.session_state: del st.session_state.raw_data
    
    st.markdown("---")
    
    # Οι ρυθμίσεις εμφανίζονται, αλλά θα έχουν 0 ως τιμές αρχικά
    with st.expander("⚙️ Budget Limits"):
        new_limits = {}
        b_changed = False
        for cat, limit in st.session_state.budget_limits.items():
            val = st.number_input(f"{cat}", value=int(limit), step=10, key=f"b_{cat}")
            new_limits[cat] = val
            if val != st.session_state.budget_limits[cat]: b_changed = True
        if b_changed and st.button("Save Budgets"):
            st.session_state.budget_limits = new_limits
            # Σημείωση: Στο Cloud το αρχείο δεν σώζεται μόνιμα, αλλά κρατιέται όσο είναι ανοιχτό το site
            with open(BUDGET_FILE, "w", encoding='utf-8') as f: json.dump(new_limits, f, ensure_ascii=False)
            st.rerun()

    with st.expander("🎯 Savings Goals"):
        goals_df = pd.DataFrame(st.session_state.goals_config)
        ed_goals = st.data_editor(goals_df, num_rows="dynamic", use_container_width=True, key="goals_ed")
        if st.button("Save Goals"):
            st.session_state.goals_config = ed_goals.to_dict('records')
            with open(GOALS_FILE, "w", encoding='utf-8') as f: json.dump(st.session_state.goals_config, f, ensure_ascii=False)
            st.rerun()

# ==============================================================================
# MAIN AREA
# ==============================================================================
render_hero_section()

# Εδώ ελέγχουμε αν υπάρχει αρχείο. Αν όχι, σταματάμε και δεν δείχνουμε τίποτα.
try:
    if 'raw_data' not in st.session_state: st.session_state.raw_data = load_data()
    df = st.session_state.raw_data
except:
    # Μήνυμα υποδοχής χωρίς προσωπικά δεδομένα
    st.info("👋 **Welcome to your private AI CFO!**\n\nTo see your dashboard, please upload your bank statement from the sidebar.")
    st.markdown("---")
    st.caption("🔒 *Privacy Note: Your data is processed in memory and is wiped when you close this tab.*")
    st.stop() # Σταματάει εδώ η εκτέλεση μέχρι να ανέβει αρχείο

# Month Selection
col_sel, _ = st.columns([1, 3])
with col_sel:
    all_months = sorted(df['Month'].unique(), reverse=True)
    selected_month = st.selectbox("📅 Select Period", all_months)

os.makedirs("data/processed", exist_ok=True)
proc_path = f"data/processed/corrected_{selected_month}.csv"
if not os.path.exists(proc_path):
    df[df['Month'] == selected_month].to_csv(proc_path, index=False)
month_df = pd.read_csv(proc_path) if os.path.exists(proc_path) else df[df['Month'] == selected_month]
month_df['Date'] = pd.to_datetime(month_df['Date'])

# ==============================================================================
# TABS INTERFACE
# ==============================================================================
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "✍️ Editor", "📅 History"])

# --- TAB 1: DASHBOARD ---
with tab1:
    income = month_df[month_df['Amount'] > 0]['Amount'].sum()
    real_expenses = abs(month_df[(month_df['Amount'] < 0) & (month_df['Category'] != '💰 Αποταμίευση')]['Amount'].sum())
    savings = income - real_expenses
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    with c1: display_dashboard_card("Total Income", f"{income:,.0f} €", "#4f46e5", "#818cf8", "💸", "Inflow")
    with c2: display_dashboard_card("Expenses", f"{real_expenses:,.0f} €", "#ef4444", "#f87171", "🛒", "Outflow")
    with c3: display_dashboard_card("Net Savings", f"{savings:,.0f} €", "#10b981", "#34d399", "🐷", "Retained")

    if st.button("✨ Get AI Insights", type="primary"):
        with st.spinner("Analyzing..."):
            st.info(get_financial_advice(month_df, income, real_expenses, savings))

    st.markdown("---")
    
    col_main, col_side = st.columns([1.8, 1.2], gap="large")
    
    with col_main:
        st.subheader("Monthly Budget Tracker")
        budget_df = check_budget(month_df, custom_limits=st.session_state.budget_limits)
        if not budget_df.empty:
            budget_df['Status'] = budget_df['Status'].str.replace('✅ ', '').str.replace('⚠️ ', '')
            st.dataframe(
                budget_df, 
                column_config={
                    "Category": st.column_config.TextColumn("Category"),
                    "Actual (€)": st.column_config.NumberColumn("Spent", format="%.0f €"),
                    "Limit (€)": st.column_config.NumberColumn("Limit", format="%.0f €"),
                    "Progress": st.column_config.ProgressColumn("Usage", format="%.0f%%", min_value=0, max_value=1),
                }, hide_index=True, use_container_width=True
            )
        
        st.markdown("##### 🌊 Cash Flow")
        st.plotly_chart(plot_sankey(month_df, income), use_container_width=True)

    with col_side:
        st.subheader("Savings Vials")
        goals_list = st.session_state.goals_config
        if goals_list and goals_list[0]['target'] > 0: # Δείξε μόνο αν υπάρχει στόχος > 0
            for goal in goals_list:
                st.markdown(get_bucket_html(goal['saved'], goal['target'], goal['name']), unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("**Simulator**")
            sel_g = st.selectbox("Select Goal:", [g["name"] for g in goals_list])
            act_g = next((g for g in goals_list if g["name"] == sel_g), goals_list[0])
            val = st.slider(f"Add monthly:", 0, 2000, 200, 50)
            msg, _ = project_goal_date(act_g['saved'], act_g['target'], val)
            if val>0: st.caption(f"🗓️ Target Date: **{msg}**")
        else:
            st.info("ℹ️ Set your Savings Goals in the Sidebar to activate the Vials.")

    st.markdown("---")
    st.subheader("Top Transactions")
    st.dataframe(get_top_expenses(month_df, 10), hide_index=True, use_container_width=True)

# --- TAB 2: EDITOR ---
with tab2:
    st.subheader("Transaction Editor")
    TAXONOMY = {
        "🍿 Lifestyle & Fun": ["Delivery", "Dining Out", "Entertainment", "Weekend Trip"],
        "🛍️ Shopping": ["Tech & Home", "Clothes", "Health & Beauty", "Misc Shopping"],
        "🛒 Supermarket": ["Groceries"],
        "🏠 Home & Utilities": ["Rent", "Bills", "Common Exp"],
        "🚗 Transport": ["Public Transport", "Fuel", "Service"],
        "💳 FinTech": ["Revolut", "Bank Fees"],
        "💸 Misc": ["IRIS/Friends", "Uncategorized"],
        "💰 Savings": ["Transfer to Self"],
        "Salary": ["Payroll"],
        "Deposit/Gift": ["Deposits"]
    }
    COMBO_OPTIONS = [f"{c} > {s}" for c, subs in TAXONOMY.items() for s in subs]
    
    edit_prep = month_df.copy()
    edit_prep['Category'] = edit_prep['Category'] + " > " + edit_prep['Subcategory']
    
    edited = st.data_editor(
        edit_prep,
        column_order=["Date", "Transaction Description", "Amount", "Category"],
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY", disabled=True),
            "Transaction Description": st.column_config.TextColumn("Description", disabled=True),
            "Amount": st.column_config.NumberColumn("Amount", format="%.2f €", disabled=True),
            "Category": st.column_config.SelectboxColumn("Categorize", options=COMBO_OPTIONS, width="large", required=True)
        },
        hide_index=True, use_container_width=True, height=600, key="editor_main"
    )
    
    if st.button("💾 Save Changes", type="primary", use_container_width=True):
        split = edited['Category'].str.split(' > ', n=1, expand=True)
        to_save = edited.copy()
        to_save['Category'] = split[0]
        to_save['Subcategory'] = split[1]
        to_save.to_csv(proc_path, index=False)
        st.success("Data Saved!")

# --- TAB 3: HISTORY ---
with tab3:
    st.subheader("Yearly Overview")
    history_df = load_history()
    if not history_df.empty:
         st.info("Charts coming soon...")
    else:
        st.info("No history yet.")