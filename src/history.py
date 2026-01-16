import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def load_history():
    """
    Φορτώνει όλα τα CSV από το data/processed και τα ενώνει.
    """
    folder = "data/processed"
    if not os.path.exists(folder):
        return pd.DataFrame()

    all_files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    if not all_files:
        return pd.DataFrame()

    df_list = []
    for filename in all_files:
        path = os.path.join(folder, filename)
        try:
            temp_df = pd.read_csv(path)
            temp_df['Date'] = pd.to_datetime(temp_df['Date'])
            df_list.append(temp_df)
        except Exception as e:
            print(f"Error loading {filename}: {e}")

    if df_list:
        full_history = pd.concat(df_list, ignore_index=True)
        return full_history.sort_values(by='Date')
    else:
        return pd.DataFrame()

def plot_monthly_overview(df):
    """
    Bar Chart: Income vs Expenses (Διορθωμένο Math & Axis)
    """
    # 1. Grouping ανά Μήνα
    df['Period'] = df['Date'].dt.to_period('M').astype(str)
    
    # 2. Υπολογισμός (Σωστά Μαθηματικά)
    # Income: Όλα τα θετικά
    # Expenses: Όλα τα αρνητικά ΕΚΤΟΣ Αποταμίευσης
    # Savings: Income - Expenses (Θεωρητική Αποταμίευση, όχι υπόλοιπο τράπεζας)
    
    monthly = df.groupby('Period').apply(
        lambda x: pd.Series({
            'Income': x[x['Amount'] > 0]['Amount'].sum(),
            'Expenses': abs(x[(x['Amount'] < 0) & (x['Category'] != '💰 Αποταμίευση')]['Amount'].sum()),
        })
    ).reset_index()

    # Υπολογίζουμε την καθαρή αποταμίευση βάσει της εξίσωσης
    monthly['Savings'] = monthly['Income'] - monthly['Expenses']

    fig = go.Figure()

    # Μπάρες
    fig.add_trace(go.Bar(x=monthly['Period'], y=monthly['Income'], name='Έσοδα', marker_color='#198754'))
    fig.add_trace(go.Bar(x=monthly['Period'], y=monthly['Expenses'], name='Έξοδα', marker_color='#dc3545'))

    # Γραμμή (Trend)
    fig.add_trace(go.Scatter(
        x=monthly['Period'], y=monthly['Savings'], name='Net Savings',
        mode='lines+markers+text', text=monthly['Savings'].apply(lambda x: f"{x:.0f}€"),
        textposition="top center",
        line=dict(color='#0dcaf0', width=3)
    ))

    # Layout (Fix Axis Type to Category)
    fig.update_layout(
        title="📊 Έσοδα vs Έξοδα (Σύγκριση Μηνών)",
        barmode='group',
        height=450,
        xaxis=dict(type='category'), # <-- ΑΥΤΟ ΦΤΙΑΧΝΕΙ ΤΟ ΓΡΑΦΗΜΑ ΝΑ ΜΗΝ ΕΧΕΙ ΚΕΝΑ
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_category_trends(df):
    """
    Line Chart: Τάσεις Κατηγοριών
    """
    expenses = df[(df['Amount'] < 0) & (df['Category'] != '💰 Αποταμίευση')].copy()
    expenses['Period'] = expenses['Date'].dt.to_period('M').astype(str)
    expenses['Abs_Amount'] = expenses['Amount'].abs()
    
    trends = expenses.groupby(['Period', 'Category'])['Abs_Amount'].sum().reset_index()
    
    fig = px.line(
        trends, x='Period', y='Abs_Amount', color='Category', markers=True,
        title="📈 Πού αυξάνονται τα έξοδα;"
    )
    
    fig.update_layout(
        height=400,
        xaxis=dict(type='category'), # <-- ΚΑΙ ΕΔΩ CATEGORY
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig