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
# --- NEW UI IMPORTS ---
from src.styles import apply_pro_style, render_hero_section, display_dashboard_card

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="AI CFO", page_icon="💳", layout="wide")
apply_pro_style() # Εφαρμογή του νέου CSS

# --- 0. DATA & SETTINGS MANAGEMENT ---
os.makedirs("config", exist_ok=True)
BUDGET_FILE = "config/budget_limits.json"
GOALS_FILE = "config/savings_goals_v2.json"

DEFAULT_BUDGETS = {
    "🏠 Σπίτι & Πάγια": 600, "🛒 Supermarket": 300, "🍿 Lifestyle & Έξοδοι": 200,   
    "🛍️ Shopping": 150, "🚗 Μετακίνηση": 100, "💳 FinTech": 20, "💸 Διάφορα": 50
}
DEFAULT_GOALS = [
    {"name": "🚗 Car Fund", "target": 15000, "saved": 2000},
    {"name": "✈️ Copenhagen Trip", "target": 2000, "saved": 500}
]

if 'budget_limits' not in st.session_state:
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
    # Στο αρχείο app.py, μέσα στο "with st.sidebar:"
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=80)
    st.markdown("### Control Center")
    uploaded_file = st.file_uploader("Upload Bank Statement", type=['txt', 'csv'])
    
    if uploaded_file:
        save_path = "data/raw/bank_export.txt"
        os.makedirs("data/raw", exist_ok=True)
        with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
        st.success("Analysis Ready!", icon="✅")
        if 'raw_data' in st.session_state: del st.session_state.raw_data
    
    st.markdown("---")
    
    # Settings Accordions
    with st.expander("⚙️ Budget Limits"):
        new_limits = {}
        b_changed = False
        for cat, limit in st.session_state.budget_limits.items():
            val = st.number_input(f"{cat}", value=int(limit), step=10, key=f"b_{cat}")
            new_limits[cat] = val
            if val != st.session_state.budget_limits[cat]: b_changed = True
        if b_changed and st.button("Update Budgets"):
            st.session_state.budget_limits = new_limits
            with open(BUDGET_FILE, "w", encoding='utf-8') as f: json.dump(new_limits, f, ensure_ascii=False)
            st.rerun()

    with st.expander("🎯 Savings Goals"):
        goals_df = pd.DataFrame(st.session_state.goals_config)
        ed_goals = st.data_editor(goals_df, num_rows="dynamic", use_container_width=True, key="goals_ed")
        if st.button("Update Goals"):
            st.session_state.goals_config = ed_goals.to_dict('records')
            with open(GOALS_FILE, "w", encoding='utf-8') as f: json.dump(st.session_state.goals_config, f, ensure_ascii=False)
            st.rerun()

# ==============================================================================
# MAIN AREA
# ==============================================================================
render_hero_section() # ΝΕΟΣ ΤΙΤΛΟΣ

# Load Data
try:
    if 'raw_data' not in st.session_state: st.session_state.raw_data = load_data()
    df = st.session_state.raw_data
except:
    st.warning("👋 Welcome! Please upload your bank statement to begin.")
    st.stop()

# Month Selection
col_sel, _ = st.columns([1, 3])
with col_sel:
    all_months = sorted(df['Month'].unique(), reverse=True)
    selected_month = st.selectbox("📅 Select Period", all_months)

# Process Data Logic (Auto-Save/Load)
os.makedirs("data/processed", exist_ok=True)
proc_path = f"data/processed/corrected_{selected_month}.csv"
if not os.path.exists(proc_path):
    df[df['Month'] == selected_month].to_csv(proc_path, index=False)
month_df = pd.read_csv(proc_path) if os.path.exists(proc_path) else df[df['Month'] == selected_month]
month_df['Date'] = pd.to_datetime(month_df['Date'])

# ==============================================================================
# TABS INTERFACE
# ==============================================================================
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "✍️ Transactions", "📅 History"])

# --- TAB 1: DASHBOARD ---
with tab1:
    # Calc Metrics
    income = month_df[month_df['Amount'] > 0]['Amount'].sum()
    real_expenses = abs(month_df[(month_df['Amount'] < 0) & (month_df['Category'] != '💰 Αποταμίευση')]['Amount'].sum())
    savings = income - real_expenses
    
    # 🌟 NEW: PRO CARDS INSTEAD OF METRICS 🌟
    c1, c2, c3 = st.columns(3)
    with c1:
        display_dashboard_card("Total Income", f"{income:,.0f} €", "#10b981", "#34d399", "💸", "Monthly Inflow")
    with c2:
        display_dashboard_card("Total Expenses", f"{real_expenses:,.0f} €", "#ef4444", "#f87171", "🛒", "Monthly Outflow")
    with c3:
        display_dashboard_card("Net Savings", f"{savings:,.0f} €", "#3b82f6", "#60a5fa", "🐷", "Remaining Cash")

    # AI Insight Button
    if st.button("✨ Ask AI CFO for Advice", type="primary"):
        with st.spinner("Analyzing spending patterns..."):
            st.info(get_financial_advice(month_df, income, real_expenses, savings))

    st.markdown("---")
    
    # Layout: Budget Left, Goals Right
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
                },
                hide_index=True, use_container_width=True
            )
        else: st.info("No spending data yet.")
        
        st.markdown("##### 🌊 Money Flow (Sankey)")
        st.plotly_chart(plot_sankey(month_df, income), use_container_width=True)

    with col_side:
        st.subheader("Savings Buckets")
        goals_list = st.session_state.goals_config
        if goals_list:
            for goal in goals_list:
                st.markdown(get_bucket_html(goal['saved'], goal['target'], goal['name']), unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("**Simulator**")
            sel_g = st.selectbox("Goal:", [g["name"] for g in goals_list])
            act_g = next((g for g in goals_list if g["name"] == sel_g), goals_list[0])
            val = st.slider(f"Add monthly:", 0, 2000, 200, 50)
            msg, _ = project_goal_date(act_g['saved'], act_g['target'], val)
            if val>0: st.caption(f"🗓️ Completion: **{msg}**")
        else:
            st.warning("Add goals in sidebar!")

    st.markdown("---")
    st.subheader("Top Expenses")
    st.dataframe(get_top_expenses(month_df, 10), hide_index=True, use_container_width=True)

# --- TAB 2: EDITOR ---
with tab2:
    st.subheader("Transaction Editor")
    TAXONOMY = {
        "🍿 Lifestyle & Έξοδοι": ["Delivery", "Εστίαση & Καφές", "Θέαμα & Συνδρομές", "Weekend Outing"],
        "🛍️ Shopping": ["Tech & Σπίτι", "Ρούχα & Μόδα", "Υγεία & Ομορφιά", "Διάφορα Ψώνια"],
        "🛒 Supermarket": ["Ψώνια Σπιτιού"],
        "🏠 Σπίτι & Πάγια": ["Ενοίκιο", "Λογαριασμοί", "Κοινόχρηστα"],
        "🚗 Μετακίνηση": ["Μεταφορικά", "Καύσιμα", "Σέρβις"],
        "💳 FinTech": ["Revolut", "Τραπεζικά Έξοδα"],
        "💸 Διάφορα": ["IRIS/Φίλοι", "Uncategorized"],
        "💰 Αποταμίευση": ["Μεταφορές σε εμένα"],
        "Salary": ["Μισθός"],
        "Deposit/Gift": ["Καταθέσεις"]
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
            "Category": st.column_config.SelectboxColumn("Edit Category", options=COMBO_OPTIONS, width="large", required=True)
        },
        hide_index=True, use_container_width=True, height=600, key="editor_main"
    )
    
    if st.button("💾 Save Changes", type="primary", use_container_width=True):
        split = edited['Category'].str.split(' > ', n=1, expand=True)
        to_save = edited.copy()
        to_save['Category'] = split[0]
        to_save['Subcategory'] = split[1]
        to_save.to_csv(proc_path, index=False)
        st.success("Saved successfully!")
        st.toast("Data updated!", icon="💾")

# --- TAB 3: HISTORY ---
with tab3:
    st.subheader("Financial Timeline")
    history_df = load_history()
    if not history_df.empty:
        if history_df['Date'].dt.to_period('M').nunique() < 2:
            st.warning("⚠️ Need more data for trend analysis.")
        
        st.plotly_chart(plot_monthly_overview(history_df), use_container_width=True)
        st.markdown("---")
        st.plotly_chart(plot_category_trends(history_df), use_container_width=True)
        
        # Yearly Totals
        inc = history_df[history_df['Amount'] > 0]['Amount'].sum()
        exp = abs(history_df[(history_df['Amount'] < 0) & (history_df['Category'] != '💰 Αποταμίευση')]['Amount'].sum())
        sav = inc - exp
        
        st.markdown("### Year at a Glance")
        cc1, cc2, cc3 = st.columns(3)
        with cc1: display_dashboard_card("Total Income", f"{inc:,.0f} €", "#64748b", "#94a3b8", "📅", "Yearly")
        with cc2: display_dashboard_card("Total Saved", f"{sav:,.0f} €", "#64748b", "#94a3b8", "🏦", "Yearly")
        with cc3: display_dashboard_card("Saving Rate", f"{(sav/inc)*100:.1f}%", "#64748b", "#94a3b8", "📈", "Average")
    else:
        st.info("No historical data found.")