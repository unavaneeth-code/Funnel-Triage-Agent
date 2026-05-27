import streamlit as st
import pandas as pd
from agent import analyze_deals

st.set_page_config(page_title="Funnel Triage Agent", page_icon="F", layout="wide")

# API Key from secrets
api_key = st.secrets["GROQ_API_KEY"]

# Custom CSS for vibrant UI
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
    .main-header { 
        font-size: 2.5rem; font-weight: 800; 
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-color: transparent;
        background-clip: text; color: transparent;
        text-align: center; margin-top: 1rem;
    }
    .sub-header { color: #b8b8d4; font-size: 1.1rem; text-align: center; margin-bottom: 2rem; }
    .upload-zone {
        background: linear-gradient(135deg, #1a1a3e, #2d2b55);
        border: 2px dashed #667eea;
        border-radius: 16px; padding: 3rem; text-align: center;
        margin: 2rem auto; max-width: 600px;
        transition: all 0.3s ease;
    }
    .upload-zone:hover { border-color: #764ba2; box-shadow: 0 0 30px rgba(102, 126, 234, 0.2); }
    .upload-text { color: #a8a8cc; font-size: 1.1rem; margin-top: 1rem; }
    .upload-highlight { color: #667eea; font-weight: 600; }
    .metric-card {
        background: linear-gradient(135deg, #1e1e3f, #2a2a5a);
        border-radius: 12px; padding: 1.5rem; text-align: center;
        border: 1px solid #3a3a6a; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-value { font-size: 2rem; font-weight: 800; color: #fff; }
    .metric-label { font-size: 0.75rem; color: #8888aa; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.3rem; }
    .section-title { color: #e0e0ff; font-size: 1.4rem; font-weight: 700; margin: 2rem 0 1rem; }
    .deal-card {
        background: linear-gradient(135deg, #1a1a3e, #252550);
        border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
        border-left: 5px solid #ddd;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
    }
    .deal-card:hover { transform: translateX(4px); box-shadow: 0 6px 25px rgba(0,0,0,0.4); }
    .deal-card.critical { border-left-color: #ff4757; }
    .deal-card.high { border-left-color: #ffa502; }
    .deal-card.medium { border-left-color: #ffdd59; }
    .deal-card.low { border-left-color: #2ed573; }
    .deal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; }
    .deal-name { font-size: 1.1rem; font-weight: 700; color: #fff; }
    .deal-score { 
        font-size: 1.3rem; font-weight: 800; 
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-color: transparent;
        background-clip: text; color: transparent;
    }
    .tier-badge { 
        display: inline-block; padding: 3px 12px; border-radius: 20px; 
        font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
    }
    .tier-critical { background: rgba(255,71,87,0.2); color: #ff4757; border: 1px solid #ff4757; }
    .tier-high { background: rgba(255,165,2,0.2); color: #ffa502; border: 1px solid #ffa502; }
    .tier-medium { background: rgba(255,221,89,0.2); color: #ffdd59; border: 1px solid #ffdd59; }
    .tier-low { background: rgba(46,213,115,0.2); color: #2ed573; border: 1px solid #2ed573; }
    .deal-meta { display: flex; gap: 1.5rem; color: #8888aa; font-size: 0.85rem; flex-wrap: wrap; margin-bottom: 0.6rem; }
    .deal-meta strong { color: #b8b8d4; }
    .risk-tag { 
        background: rgba(255,71,87,0.15); color: #ff6b7a; 
        padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; 
        margin-right: 6px; display: inline-block; margin-bottom: 4px;
        border: 1px solid rgba(255,71,87,0.3);
    }
    .reasoning { color: #9999bb; font-size: 0.9rem; margin: 0.6rem 0; line-height: 1.5; }
    .action-box { 
        background: linear-gradient(135deg, rgba(46,213,115,0.1), rgba(102,126,234,0.1));
        border-radius: 8px; padding: 0.8rem 1rem; margin-top: 0.8rem;
        border: 1px solid rgba(46,213,115,0.3);
    }
    .action-box strong { color: #2ed573; }
    .action-box span { color: #ccc; }
    .top-risk { 
        background: linear-gradient(135deg, #1e1e3f, #2a2a5a);
        border-radius: 8px; padding: 0.8rem 1.2rem; 
        border: 1px solid #3a3a6a; color: #b8b8d4;
        margin-top: 1rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        color: white !important; border: none !important;
        padding: 0.7rem 2rem !important; border-radius: 8px !important;
        font-weight: 600 !important; font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover { transform: scale(1.02) !important; box-shadow: 0 4px 15px rgba(102,126,234,0.4) !important; }
    [data-testid="stFileUploader"] { 
        max-width: 600px; margin: 0 auto;
    }
    [data-testid="stFileUploader"] > div { 
        background: linear-gradient(135deg, #1a1a3e, #2d2b55) !important;
        border: 2px dashed #667eea !important; border-radius: 16px !important;
        padding: 2rem !important;
    }
    [data-testid="stFileUploader"] label { color: #b8b8d4 !important; text-align: center !important; }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    [data-testid="stExpander"] { background: #1a1a3e; border-radius: 8px; border: 1px solid #3a3a6a; }
    .stSpinner > div { color: #667eea !important; }
    div[data-testid="stInfo"] { background: linear-gradient(135deg, #1a1a3e, #2d2b55); border: 1px solid #3a3a6a; color: #b8b8d4; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">Funnel Triage Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered deal prioritization for sales managers — upload, analyze, act</div>', unsafe_allow_html=True)

# Centered file upload
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader("Drag and drop your pipeline CSV here", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Validate required columns
    REQUIRED_COLUMNS = [
        "Opportunity Name", "Close Date", "Opportunity Owner", "Stage",
        "Potential Risk Identified", "Status", "Decision Maker Involved",
        "ACV", "Last Activity Date", "ICP Or Not", "Intent Timing",
        "Our Current Product Addresses Their Pain Point Or Not",
        "Opportunity Risk Reason", "Pain Point"
    ]
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2a1a1a, #3d2020); border: 1px solid #ff4757; 
                    border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
            <p style="color: #ff6b7a; font-weight: 700; font-size: 1.1rem; margin-bottom: 1rem;">
                CSV is missing required columns
            </p>
            <p style="color: #ccc; margin-bottom: 1rem;">
                Your file is missing the following fields needed for triage analysis:
            </p>
            <div style="margin-bottom: 1.2rem;">
        """ + "".join([f'<span style="background: rgba(255,71,87,0.15); color: #ff6b7a; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; margin: 3px 4px; display: inline-block; border: 1px solid rgba(255,71,87,0.3);">{col}</span>' for col in missing]) + """
            </div>
            <p style="color: #8888aa; font-size: 0.85rem; margin-bottom: 0.8rem;">
                <strong style="color: #b8b8d4;">Required columns and their purpose:</strong>
            </p>
            <table style="width: 100%; color: #9999bb; font-size: 0.82rem; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Opportunity Name</strong></td><td>Deal identifier</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Close Date</strong></td><td>Expected close date (proximity scoring)</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Stage</strong></td><td>Deal stage: Discovery / Qualification / Demo Scheduled / Demo Completed / Proposal / Negotiation</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">ACV</strong></td><td>Annual contract value in USD</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Decision Maker Involved</strong></td><td>Yes / Partial / No</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Intent Timing</strong></td><td>Immediate / Q3 / Q4 / Q4+</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Our Current Product Addresses Their Pain Point Or Not</strong></td><td>Yes / Partial / No</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Last Activity Date</strong></td><td>Date of most recent engagement</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">ICP Or Not</strong></td><td>Yes / No — fits ideal customer profile</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Status</strong></td><td>Active / Stalled</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Potential Risk Identified</strong></td><td>Known risk factors for the deal</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Opportunity Risk Reason</strong></td><td>Why the deal is at risk</td></tr>
                <tr style="border-bottom: 1px solid #3a3a6a;"><td style="padding: 6px 0;"><strong style="color:#ccc;">Opportunity Owner</strong></td><td>Sales rep assigned to the deal</td></tr>
                <tr><td style="padding: 6px 0;"><strong style="color:#ccc;">Pain Point</strong></td><td>Customer's core problem</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<p style='text-align:center; color:#b8b8d4;'><strong>{len(df)} deals</strong> loaded successfully</p>", unsafe_allow_html=True)
    
    with st.expander("Preview raw data"):
        st.dataframe(df, use_container_width=True, height=200)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run = st.button("Run Triage Analysis", type="primary", use_container_width=True)

    if run:
        with st.spinner("Analyzing pipeline..."):
            try:
                result = analyze_deals(df, api_key)
                st.session_state["triage_result"] = result
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.stop()

    if "triage_result" in st.session_state:
        result = st.session_state["triage_result"]

        # Summary metrics
        s = result["summary"]
        st.markdown('<div class="section-title">Pipeline Overview</div>', unsafe_allow_html=True)
        cols = st.columns(5)
        metrics = [
            ("Total Deals", s["total_deals"], "#667eea"),
            ("Active", s["active_deals"], "#2ed573"),
            ("Stalled", s["stalled_deals"], "#ff4757"),
            ("Pipeline Value", f"${s['total_pipeline_value']:,}", "#ffa502"),
            ("Actions Needed", s["immediate_actions_needed"], "#764ba2"),
        ]
        for col, (label, value, color) in zip(cols, metrics):
            col.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {color};">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f'<div class="top-risk"><strong>Top risk pattern:</strong> {s["top_risk"]}</div>', unsafe_allow_html=True)

        # Prioritized deals
        st.markdown('<div class="section-title">Prioritized Deals</div>', unsafe_allow_html=True)
        
        # Filter tabs
        tiers = ["All"] + list(dict.fromkeys([d["priority_tier"] for d in result["deals"]]))
        selected_tier = st.radio("Filter by tier", tiers, horizontal=True, label_visibility="collapsed")
        
        filtered_deals = result["deals"] if selected_tier == "All" else [d for d in result["deals"] if d["priority_tier"] == selected_tier]

        for deal in filtered_deals:
            tier = deal["priority_tier"].lower()
            risk_html = "".join([f'<span class="risk-tag">{r}</span>' for r in deal["risk_flags"]]) if deal["risk_flags"] else ""

            st.markdown(f"""
            <div class="deal-card {tier}">
                <div class="deal-header">
                    <div>
                        <span class="deal-name">#{deal['rank']}. {deal['opportunity_name']}</span>
                        <span class="tier-badge tier-{tier}" style="margin-left: 10px;">{deal['priority_tier']}</span>
                    </div>
                    <span class="deal-score">{deal['score']}/100</span>
                </div>
                <div class="deal-meta">
                    <span><strong>Stage:</strong> {deal['stage']}</span>
                    <span><strong>ACV:</strong> ${deal['acv']:,}</span>
                    <span><strong>Close:</strong> {deal['close_date']}</span>
                    <span><strong>Owner:</strong> {deal['owner']}</span>
                    <span><strong>Status:</strong> {deal['status']}</span>
                </div>
                {f'<div style="margin-bottom: 0.5rem;">{risk_html}</div>' if risk_html else ''}
                <div class="reasoning">{deal['reasoning']}</div>
                <div class="action-box"><strong>Next action: </strong><span>{deal['suggested_next_action']}</span></div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align: center; color: #8888aa; margin-top: 2rem;">
        <p>Upload a CSV file with your pipeline data to get started.</p>
        <p style="font-size: 0.85rem;">A sample <code>mock_opportunities.csv</code> is included in this project.</p>
    </div>
    """, unsafe_allow_html=True)
