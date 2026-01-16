import streamlit as st

def apply_pro_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #1e293b;
        }

        /* --- CLEAN BACKGROUND --- */
        /* Πολύ πιο απαλό και επαγγελματικό */
        .stApp {
            background-color: #f8fafc; /* Slate 50 */
            background-image: 
                radial-gradient(at 0% 0%, rgba(224, 242, 254, 0.5) 0px, transparent 50%), /* Light Sky */
                radial-gradient(at 100% 100%, rgba(224, 231, 255, 0.5) 0px, transparent 50%); /* Light Indigo */
            background-attachment: fixed;
        }

        /* --- GLASS CHART CONTAINER --- */
        [data-testid="stPlotlyChart"] {
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 10px 30px rgba(148, 163, 184, 0.1); /* Grey shadow, not colored */
            padding: 10px;
            position: relative;
            overflow: hidden;
        }

        /* --- SUBTLE SHIMMER --- */
        [data-testid="stPlotlyChart"]::after {
            content: "";
            position: absolute; top: 0; left: -150%; width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
            transform: skewX(-20deg);
            animation: chart-shimmer 6s infinite;
            pointer-events: none;
        }

        @keyframes chart-shimmer {
            0% { left: -150%; }
            20% { left: 150%; }
            100% { left: 150%; }
        }

        /* --- DATAFRAME & SIDEBAR --- */
        [data-testid="stDataFrame"], section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(16px);
            border-radius: 16px;
            border: 1px solid white;
        }

        /* --- TABS --- */
        .stTabs [data-baseweb="tab-list"] {
            background: white; padding: 4px; border-radius: 50px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.02);
            display: inline-flex; gap: 5px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 40px; padding: 6px 20px; border: none; background: transparent; 
            font-weight: 600; font-size: 13px; color: #64748b;
        }
        .stTabs [aria-selected="true"] {
            background: #0f172a; color: white !important; /* Dark Slate Button */
        }

        /* --- VIAL ANIMATION --- */
        @keyframes shimmer {
            0% { transform: translateX(-150%) skewX(-20deg); }
            100% { transform: translateX(200%) skewX(-20deg); }
        }
        .sparkle-effect {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0) 100%);
            animation: shimmer 3s infinite; pointer-events: none;
        }
        </style>
    """, unsafe_allow_html=True)

def display_dashboard_card(title, value, color_start, color_end, icon="💰", subtext=""):
    html_code = f"""
<div style="background: rgba(255,255,255,0.7); backdrop-filter: blur(12px); border: 1px solid white; border-radius: 20px; padding: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); position: relative; overflow: hidden; transition: transform 0.2s;">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
        <div style="width: 40px; height: 40px; background: linear-gradient(135deg, {color_start}, {color_end}); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 18px; color: white;">{icon}</div>
        <span style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">{title}</span>
    </div>
    <div style="font-size: 30px; font-weight: 800; color: #0f172a; letter-spacing: -1px;">{value}</div>
    <div style="font-size: 12px; color: #64748b; font-weight: 500; margin-top: 4px;">{subtext}</div>
</div>
"""
    st.markdown(html_code, unsafe_allow_html=True)

def render_hero_section():
    html_code = """
<div style="margin-bottom: 40px;">
    <h1 style="font-size: 42px; font-weight: 900; color: #0f172a; letter-spacing: -1.5px; margin-bottom: 5px;">
        AI Personal <span style="background: linear-gradient(to right, #3b82f6, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">CFO</span>
    </h1>
    <p style="font-size: 15px; color: #64748b; font-weight: 500;">
        Intelligent Finance & Analytics <span style="background: #f1f5f9; color: #475569; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; margin-left: 8px; vertical-align: middle;">V5.0</span>
    </p>
</div>
"""
    st.markdown(html_code, unsafe_allow_html=True)