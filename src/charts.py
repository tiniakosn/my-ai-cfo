import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_sunburst(df):
    """
    Sunburst Chart: Κατηγορία -> Υποκατηγορία
    """
    expenses = df[
        (df['Amount'] < 0) & 
        (df['Category'] != '💰 Αποταμίευση')
    ].copy()
    expenses['Abs_Amount'] = expenses['Amount'].abs()

    if expenses.empty: return None

    fig = px.sunburst(
        expenses, 
        path=['Category', 'Subcategory'], 
        values='Abs_Amount',
        color='Category',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hover_data={'Abs_Amount': ':.2f'}
    )
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=400)
    return fig

def plot_spend_trend(df):
    """
    Area Chart: Cumulative Spend Trend
    """
    expenses = df[
        (df['Amount'] < 0) & 
        (df['Category'] != '💰 Αποταμίευση')
    ].copy()
    
    if expenses.empty: return None

    expenses['Abs_Amount'] = expenses['Amount'].abs()
    daily_spend = expenses.groupby('Date')['Abs_Amount'].sum().reset_index().sort_values('Date')
    daily_spend['Cumulative'] = daily_spend['Abs_Amount'].cumsum()
    
    fig = px.area(
        daily_spend, 
        x='Date', y='Cumulative',
        title="💸 Ταχύτητα Εξόδων",
        labels={'Cumulative': 'Έξοδα (€)', 'Date': ''},
        color_discrete_sequence=['#ff4b4b']
    )
    fig.update_layout(
        height=350, margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_gridcolor='rgba(200, 200, 200, 0.2)'
    )
    return fig

def plot_sankey(df, income):
    """
    Modern 'Monochromatic' Sankey (Blue/Cyan Theme).
    """
    # 1. Prepare Data
    expenses = df[(df['Amount'] < 0) & (df['Category'] != '💰 Αποταμίευση')].copy()
    expenses['Abs_Amount'] = expenses['Amount'].abs()
    
    expenses_by_cat = expenses.groupby('Category')['Abs_Amount'].sum().reset_index()
    expenses_by_cat = expenses_by_cat.sort_values('Abs_Amount', ascending=False)
    
    total_expenses = expenses_by_cat['Abs_Amount'].sum()
    savings = max(0, income - total_expenses)
    
    # 2. Force English Labels
    def clean_translate(name):
        name = str(name).split('>')[0].strip()
        mapping = {
            "Σπίτι & Πάγια": "Home & Bills", "Supermarket": "Groceries",
            "Lifestyle & Έξοδοι": "Lifestyle", "Shopping": "Shopping",
            "Μετακίνηση": "Transport", "FinTech": "FinTech",
            "Διάφορα": "Misc", "Αποταμίευση": "Savings",
            "Μισθός": "Salary", "Income": "Income"
        }
        for greek_key, english_val in mapping.items():
            if greek_key in name: return english_val
        return name

    labels = ["Income"] 
    for cat in expenses_by_cat['Category']:
        labels.append(clean_translate(cat))
    if savings > 0: labels.append("Savings")
    
    # 3. COLOR PALETTE: Cool Financial Spectrum
    node_colors = ["rgba(255, 255, 255, 0.9)"] * len(labels)
    node_colors[0] = "#a5b4fc" # Soft Indigo for Income

    # Links: Blue shades
    link_colors_palette = [
        "rgba(56, 189, 248, 0.45)",   # Sky Blue
        "rgba(96, 165, 250, 0.45)",   # Blue
        "rgba(129, 140, 248, 0.45)",  # Indigo
        "rgba(167, 139, 250, 0.45)",  # Violet
        "rgba(45, 212, 191, 0.45)",   # Teal
        "rgba(148, 163, 184, 0.45)"   # Slate
    ]
    
    link_colors = [link_colors_palette[i % len(link_colors_palette)] for i in range(len(expenses_by_cat))]
    if savings > 0: link_colors.append("rgba(6, 182, 212, 0.6)") # Cyan for Savings

    # 4. Flow Logic
    source = [0] * len(expenses_by_cat)
    target = list(range(1, len(expenses_by_cat) + 1))
    value = expenses_by_cat['Abs_Amount'].tolist()
    
    if savings > 0:
        source.append(0)
        target.append(len(labels) - 1)
        value.append(savings)

    # 5. Build Figure
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=40, thickness=10, line=dict(color="white", width=0.5),
            label=labels, color=node_colors, hoverinfo='all'
        ),
        link=dict(
            source=source, target=target, value=value, color=link_colors
        ),
        textfont=dict(size=14, color="#334155", family="Inter", weight="bold") 
    )])
    
    fig.update_layout(
        font=dict(size=14, family="Inter"),
        height=550, margin=dict(l=20, r=100, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def get_bucket_html(current, target, name):
    """
    Uniform 'Liquid' Vials (Blue Theme).
    FIXED: No indentation in HTML string to prevent rendering errors.
    """
    if target <= 0: target = 1
    percent = (current / target) * 100
    if percent > 100: percent = 100

    # Ocean Gradient
    c1, c2 = "#0ea5e9", "#6366f1"

    # ПРОСОΧΗ: Το HTML string είναι κολλημένο αριστερά!
    html = f"""
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 15px;">
<div style="width: 70px; height: 140px; background: rgba(255, 255, 255, 0.3); border: 1px solid rgba(255, 255, 255, 0.6); border-radius: 50px; position: relative; overflow: hidden; box-shadow: 0 10px 25px rgba(14, 165, 233, 0.1); backdrop-filter: blur(8px);">
<div style="width: 100%; height: {percent}%; background: linear-gradient(180deg, {c1} 0%, {c2} 100%); position: absolute; bottom: 0; left: 0; transition: height 1.2s cubic-bezier(0.4, 0, 0.2, 1); opacity: 0.9; box-shadow: 0 0 25px {c1};"></div>
<div class="sparkle-effect"></div>
<div style="position: absolute; top: 15px; left: 50%; transform: translateX(-50%); font-weight: 800; font-size: 14px; color: #fff; text-shadow: 0 1px 3px rgba(0,0,0,0.2); z-index: 10;">{percent:.0f}%</div>
</div>
<div style="text-align: center; margin-top: 10px;">
<div style="font-weight: 700; font-size: 13px; color: #334155; margin-bottom: 2px;">{name}</div>
<div style="font-size: 11px; font-weight: 600; color: #94a3b8;">{current:,.0f} / {target:,.0f}€</div>
</div>
</div>
"""
    return html