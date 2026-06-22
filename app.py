import streamlit as st
import os
import sys
import asyncio
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.utils.generate_data import generate_crop_data, generate_mandi_data
from src.utils.weather_api import get_weather_forecast
from src.utils.crop_model import predict_crop
from src.utils.mandi_query import get_mandi_price_data
from src.agents.coordinator import run_krishi_saarthi_pipeline

data_dir = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(os.path.join(data_dir, "crop_recommendation.csv")):
    generate_crop_data()
if not os.path.exists(os.path.join(data_dir, "mandi_prices.csv")):
    generate_mandi_data()

@st.cache_data(ttl=600, show_spinner=False)
def get_cached_weather(location: str, days: int = 7) -> dict:
    return get_weather_forecast(location, days)

def inject_weather_icons(text: str) -> str:
    import re
    # Beautiful Lucide SVG weather icons styled to fit the dashboard theme
    sun_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" '
        'stroke="#FFB000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; margin-right: 4px; display: inline-block;"><circle cx="12" cy="12" r="4"></circle>'
        '<path d="M12 2v2"></path><path d="M12 20v2"></path><path d="M4.93 4.93l1.41 1.41"></path>'
        '<path d="M17.66 17.66l1.41 1.41"></path><path d="M2 12h2"></path><path d="M20 12h2"></path>'
        '<path d="M6.34 17.66l-1.41 1.41"></path><path d="M19.07 4.93l-1.41 1.41"></path></svg>'
    )
    rain_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" '
        'stroke="#1A73E8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; margin-right: 4px; display: inline-block;"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"></path>'
        '<path d="M16 14v6"></path><path d="M8 14v6"></path><path d="M12 16v6"></path></svg>'
    )
    
    # Replace "Sunny / Dry" or "Sunny/Dry" or "Sunny / Clear"
    text = re.sub(
        r'(?<!StyledLinkIconContainer">)(?<!svg>)(Sunny\s*/\s*Dry|Sunny\s*/\s*Clear)',
        f'{sun_svg}\\1',
        text,
        flags=re.IGNORECASE
    )
    
    # Replace "Rain (X.Ymm)" or "Rain: X.Ymm (Z% chance)"
    def rain_repl(match):
        return f"{rain_svg}{match.group(0)}"
        
    text = re.sub(
        r'(?<!StyledLinkIconContainer">)(?<!svg>)(Rain\s*\(\d+\.?\d*mm\)|Rain:\s*\d+\.?\d*mm\s*\(\d+%\s*chance\))',
        rain_repl,
        text,
        flags=re.IGNORECASE
    )
    
    return text


st.set_page_config(
    page_title="KrishiSaarthi - Farm Planner",
    page_icon="logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #FBF9F6;
    color: #2C3E2E;
}

[data-testid="stSidebar"] {
    background-color: #F4EFEA !important;
    border-right: 1px solid #E3DBD2;
}

/* Fix sidebar text color targeting to prevent unreadable input contents/placeholders */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] summary {
    color: #2C3E2E !important;
}

/* Style expander container to have a clean card appearance */
[data-testid="stSidebar"] details {
    border: 1px solid #E3DBD2 !important;
    background-color: #FDFBFA !important;
    border-radius: 8px !important;
    padding: 5px 10px !important;
    margin-top: 10px;
}

/* Target only the primary button in the sidebar for white text color */
[data-testid="stSidebar"] button[kind="primary"], 
[data-testid="stSidebar"] button[kind="primary"] * {
    color: #FFFFFF !important;
}

/* Explicitly style Streamlit tabs for high contrast and readability */
button[data-baseweb="tab"] p {
    color: #6E7C6E !important;
    font-weight: 500 !important;
}
button[data-baseweb="tab"][aria-selected="true"] p {
    color: #1E4620 !important;
    font-weight: 700 !important;
}

/* Style inputs to prevent invisible text in dark-mode browser environments */
input {
    color: #2C3E2E !important;
    background-color: #FFFFFF !important;
}

/* Force password toggle visibility icons to be dark green */
div[data-testid="stTextInput"] button,
div[data-testid="stTextInput"] button * {
    color: #2C3E2E !important;
}

/* Hide "Press Enter to apply" instructional labels under inputs */
div[data-testid="InputInstructions"] {
    display: none !important;
}

/* Force selectbox elements and dropdown menu options to show a pointer/hand cursor */
[data-baseweb="select"], [data-baseweb="select"] *, div[role="listbox"] li, ul[role="listbox"] li {
    cursor: pointer !important;
}

/* Hide Streamlit's default heading hover anchor link icons */
div[data-testid="StyledLinkIconContainer"] {
    display: none !important;
}

.metric-card {
    background: #FFFFFF;
    border: 1px solid #E3DBD2;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 4px 6px rgba(141, 90, 54, 0.02);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: #C0D8C0;
    box-shadow: 0 8px 16px rgba(30, 70, 32, 0.05);
}

.metric-title {
    font-size: 0.85rem;
    color: #6E7C6E;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-val {
    font-size: 1.8rem;
    color: #1E4620;
    font-weight: 700;
    line-height: 1.15;
}

.metric-sub {
    font-size: 0.8rem;
    color: #8D5A36;
    margin-top: 2px;
    font-weight: 500;
}

.main-title {
    color: #1E4620;
    font-weight: 800;
    font-size: clamp(2.2rem, 5vw, 3.5rem);
    line-height: 1.08;
    margin-bottom: 2px;
}

.subtitle {
    font-size: 1.1rem;
    color: #6E7C6E;
    margin-bottom: 20px;
}

.badge-agri {
    font-size: 1rem;
    font-weight: 600;
    background-color: #E8F0E8;
    color: #1E4620;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid #C0D8C0;
    margin-left: 10px;
    vertical-align: middle;
}

.mode-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 20px;
    background-color: #F5EFEB;
    color: #8D5A36;
    border: 1px solid #E3DBD2;
}

.report-container {
    background: #FFFFFF;
    border: 1px solid #E3DBD2;
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 8px 16px rgba(30, 70, 32, 0.02);
    transition: all 0.3s ease;
}

.report-container:hover {
    box-shadow: 0 12px 24px rgba(30, 70, 32, 0.04);
}

.agent-card-active {
    background: #FFFFFF;
    border: 1px solid #C0D8C0;
    border-radius: 8px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(30, 70, 32, 0.03);
    transition: all 0.3s ease;
}

.agent-card-active:hover {
    transform: translateY(-2px);
    border-color: #1E4620;
    box-shadow: 0 6px 12px rgba(30, 70, 32, 0.05);
}

.agent-card-idle {
    background: #FFFFFF;
    border: 1px solid #E3DBD2;
    border-radius: 8px;
    padding: 12px;
    text-align: center;
    opacity: 0.65;
    transition: all 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

if "agent_trace" not in st.session_state:
    st.session_state["agent_trace"] = {
        "weather": "Idle",
        "crop": "Idle",
        "market": "Idle",
        "safety": "Idle",
        "report": "Idle"
    }

if "results" not in st.session_state:
    st.session_state["results"] = None

st.sidebar.markdown("## KrishiSaarthi Settings")

run_mode = st.sidebar.selectbox(
    "Run Mode",
    ["Offline demo", "Gemini", "OpenRouter fallback"],
    index=0,
    help="Select execution mode."
)

if run_mode == "Gemini":
    if not os.environ.get("GEMINI_API_KEY"):
        st.sidebar.error("GEMINI_API_KEY missing. Please enter your API key in the 'Technical Settings' section below.")
elif run_mode == "OpenRouter fallback":
    if not os.environ.get("OPENROUTER_API_KEY"):
        st.sidebar.error("OPENROUTER_API_KEY missing. Please enter your API key in the 'Technical Settings' section below.")

st.sidebar.markdown("---")
st.sidebar.markdown("### Soil inputs")
n_soil = st.sidebar.slider("Nitrogen (N) - kg/ha", 0, 140, 90)
p_soil = st.sidebar.slider("Phosphorus (P) - kg/ha", 5, 140, 45)
k_soil = st.sidebar.slider("Potassium (K) - kg/ha", 5, 200, 45)
ph_soil = st.sidebar.slider("Soil pH Level", 3.5, 9.0, 6.2, step=0.1)

st.sidebar.markdown("---")
st.sidebar.markdown("### Location and crop inputs")
loc_city = st.sidebar.text_input("Farm Location (City/Town)", "Amritsar")
loc_state = st.sidebar.text_input("State", "Punjab")
loc_district = st.sidebar.text_input("District", "Amritsar")
commodity_interest = st.sidebar.text_input("Primary Crop of Interest", "rice")

st.sidebar.markdown("---")
run_pipeline = st.sidebar.button("Generate Plan", type="primary", use_container_width=True)

if run_mode != "Offline demo":
    st.sidebar.markdown("---")
    with st.sidebar.expander("Technical Settings", expanded=False):
        if run_mode == "Gemini":
            override_gemini = st.text_input("Temporary Gemini Key", type="password")
            if override_gemini:
                os.environ["GEMINI_API_KEY"] = override_gemini
        elif run_mode == "OpenRouter fallback":
            override_or = st.text_input("Temporary OpenRouter Key", type="password")
            if override_or:
                os.environ["OPENROUTER_API_KEY"] = override_or

st.markdown("""
<div style="display: flex; align-items: center; gap: 14px; margin-bottom: 2px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#1E4620" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 3.5 1 8a7 7 0 0 1-9 10z"></path><path d="M19 2c-2.26 4.33-5.27 7.14-8 8"></path></svg>
    <span class="main-title" style="margin: 0; line-height: 1;">KrishiSaarthi</span>
</div>
""", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Farm risk and market planning dashboard</p>', unsafe_allow_html=True)

weather_card_val = "Pending plan"
crop_card_val = "Pending plan"
market_card_val = "Pending plan"
safety_card_val = "Pending plan"

if st.session_state["results"]:
    res = st.session_state["results"]
    if "rain" in res["weather_advice"].lower():
        weather_card_val = "Rain expected"
    else:
        weather_card_val = "Dry / Clear"
    
    crop_card_val = commodity_interest.capitalize()
    
    import re
    prices = re.findall(r"₹\d+", res["market_advice"])
    if prices:
        market_card_val = f"Modal: {prices[0]}"
    else:
        market_card_val = "Data queried"
        
    if "approved" in res["safety_advice"].lower():
        safety_card_val = "Low risk"
    else:
        safety_card_val = "Advisories active"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span class="metric-title">Weather Risk</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8D5A36" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 13a5 5 0 0 0-9.9-1A4.75 4.75 0 0 0 8 21h8a5 5 0 0 0 0-10z"></path><line x1="8" y1="13" x2="8" y2="15"></line><line x1="16" y1="13" x2="16" y2="15"></line><line x1="12" y1="15" x2="12" y2="23"></line></svg>
        </div>
        <div class="metric-val">{weather_card_val}</div>
        <div class="metric-sub">7-day forecast check</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span class="metric-title">Crop Suitability</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1E4620" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 3.5 1 8a7 7 0 0 1-9 10z"></path><path d="M19 2c-2.26 4.33-5.27 7.14-8 8"></path></svg>
        </div>
        <div class="metric-val">{crop_card_val}</div>
        <div class="metric-sub">Based on NPK + pH</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span class="metric-title">Market Insight</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8D5A36" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
        </div>
        <div class="metric-val">{market_card_val}</div>
        <div class="metric-sub">Local mandi price / quintal</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span class="metric-title">Safety Check</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1E4620" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        </div>
        <div class="metric-val">{safety_card_val}</div>
        <div class="metric-sub">Basic sustainability review</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### Planning Process Status")

agents_status = st.session_state["agent_trace"]

def get_step_status_html(status, text):
    if status == "Completed":
        return f"<div style='color: #1E4620; font-weight: 500; font-size: 0.95rem; margin-bottom: 8px;'>✓ {text} completed</div>"
    elif status == "Running...":
        return f"<div style='color: #8D5A36; font-weight: 500; font-size: 0.95rem; margin-bottom: 8px;'>» {text} running...</div>"
    else:
        return f"<div style='color: #9A958F; font-size: 0.95rem; margin-bottom: 8px; opacity: 0.65;'>• {text} pending</div>"

st.markdown(f"""
<div style='background-color: #FFFFFF; border: 1px solid #E3DBD2; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(141, 90, 54, 0.02);'>
    {get_step_status_html(agents_status['weather'], 'Weather analysis')}
    {get_step_status_html(agents_status['crop'], 'Crop suitability check')}
    {get_step_status_html(agents_status['market'], 'Market data query')}
    {get_step_status_html(agents_status['safety'], 'Safety review')}
    {get_step_status_html(agents_status['report'], 'Weekly plan compilation')}
</div>
""", unsafe_allow_html=True)

if run_pipeline:
    with st.spinner("Fetching coordinates and weather forecast..."):
        forecast = get_cached_weather(loc_city, days=7)
        
    avg_temp = sum(d["temp_max"] + d["temp_min"] for d in forecast["days"]) / (2 * len(forecast["days"]))
    total_rain = sum(d["rain"] for d in forecast["days"])
    avg_hum = 75.0
    
    inputs = {
        "N": float(n_soil),
        "P": float(p_soil),
        "K": float(k_soil),
        "ph": float(ph_soil),
        "temperature": round(avg_temp, 2),
        "humidity": avg_hum,
        "rainfall": round(total_rain, 2),
        "location": loc_city,
        "state": loc_state,
        "district": loc_district,
        "commodity": commodity_interest.lower().strip()
    }
    
    status_box = st.info("Initializing planner...")
    
    mode_map = {
        "Gemini": "gemini",
        "OpenRouter fallback": "openrouter",
        "Offline demo": "offline"
    }
    selected_provider = mode_map[run_mode]
    
    async def run_agents_with_fallback(inputs, provider):
        if provider == "gemini":
            if not os.environ.get("GEMINI_API_KEY"):
                st.warning("Gemini API key is missing. Attempting OpenRouter fallback...")
                return await run_agents_with_fallback(inputs, "openrouter")
            try:
                status_box.info("Executing plan using Gemini...")
                res = await run_krishi_saarthi_pipeline(inputs, provider="gemini")
                st.session_state["agent_trace"] = {
                    "weather": "Completed", "crop": "Completed", "market": "Completed", "safety": "Completed", "report": "Completed"
                }
                return res
            except Exception as e:
                err_msg = str(e).upper()
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "QUOTA" in err_msg or "LIMIT" in err_msg:
                    st.warning("Gemini limit reached. Attempting OpenRouter fallback...")
                    return await run_agents_with_fallback(inputs, "openrouter")
                else:
                    raise e
        elif provider == "openrouter":
            if not os.environ.get("OPENROUTER_API_KEY"):
                st.warning("OpenRouter API key is missing. Switching to offline mode.")
                return await run_agents_with_fallback(inputs, "offline")
            try:
                status_box.info("Executing plan using OpenRouter fallback...")
                res = await run_krishi_saarthi_pipeline(inputs, provider="openrouter")
                st.session_state["agent_trace"] = {
                    "weather": "Completed", "crop": "Completed", "market": "Completed", "safety": "Completed", "report": "Completed"
                }
                return res
            except Exception as e:
                st.warning(f"OpenRouter connection failed: {e}. Switching to offline mode.")
                return await run_agents_with_fallback(inputs, "offline")
        else:
            status_box.info("Executing offline simulation...")
            res = await run_krishi_saarthi_pipeline(inputs, provider="offline")
            st.session_state["agent_trace"] = {
                "weather": "Completed", "crop": "Completed", "market": "Completed", "safety": "Completed", "report": "Completed"
            }
            return res
            
    try:
        results = asyncio.run(run_agents_with_fallback(inputs, selected_provider))
        st.session_state["results"] = results
        st.rerun()
    except Exception as e:
        status_box.error(f"Analysis Error: {e}")
        st.exception(e)

if st.session_state["results"]:
    results = st.session_state["results"]
    
    st.success("Analysis completed successfully!")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Weekly Farm Plan", 
        "Weather Risk", 
        "Crop Suitability", 
        "Market Note", 
        "Safety Note"
    ])
    
    with tab1:
        st.markdown(f'<div class="report-container">\n\n{inject_weather_icons(results["final_report"])}\n\n</div>', unsafe_allow_html=True)
        
        st.markdown(
            "<div style='margin-top: 15px; padding: 12px; background-color: #FDF8E2; border-left: 4px solid #F5C653; border-radius: 4px; font-size: 0.9rem; color: #856404;'>"
            "<strong>Notice:</strong> This is decision-support guidance, not professional financial or agricultural advice."
            "</div>",
            unsafe_allow_html=True
        )
        
    with tab2:
        st.markdown(f'<div class="report-container">\n\n{inject_weather_icons(results["weather_advice"])}\n\n</div>', unsafe_allow_html=True)
        
    with tab3:
        st.markdown(f'<div class="report-container">\n\n{results["crop_advice"]}\n\n</div>', unsafe_allow_html=True)
        
    with tab4:
        st.markdown(f'<div class="report-container">\n\n{results["market_advice"]}\n\n</div>', unsafe_allow_html=True)
        
    with tab5:
        st.markdown(f'<div class="report-container">\n\n{results["safety_advice"]}\n\n</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6E7C6E; font-size: 0.85rem;'>"
    "KrishiSaarthi • Farm planning dashboard"
    "</div>",
    unsafe_allow_html=True
)
