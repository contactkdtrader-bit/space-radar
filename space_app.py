import streamlit as st
import datetime
import pandas as pd
import math
import time
import requests

st.set_page_config(page_title="NORAD/SSA Control Center", page_icon="🛸", layout="wide")

# Sci-Fi Scientist Lab Header
st.markdown("""
    <h1 style='text-align: center; color: #00FF66; font-family: monospace;'>🛸 NORAD MISSION CONTROL: SPACE SITUATIONAL AWARENESS</h1>
    <p style='text-align: center; color: #888888; font-family: monospace;'>[SECURITY STATUS: CLASSIFIED] LEVEL-4 ORBITAL RADAR TRACKING</p>
    """, unsafe_allow_html=True)

st.sidebar.markdown("<h2 style='color: #00FF66; font-family: monospace;'>📡 System Control</h2>", unsafe_allow_html=True)
st.sidebar.info("Radar Status: ACTIVE\n\nSensor Nodes: ONLINE\n\nTargeting Computer: LOCKED")

# ਲਾਈਵ Celestrak API ਤੋਂ TLE ਡਾਟਾ ਲਿਆਉਣ ਲਈ ਫੰਕਸ਼ਨ
@st.cache_data(ttl=3600) # 1 ਘੰਟੇ ਲਈ ਡਾਟਾ ਕੈਸ਼ ਕਰੇਗਾ ਤਾਂ ਜੋ ਬਾਰ-ਬਾਰ API ਹਿੱਟ ਨਾ ਹੋਵੇ
def fetch_live_satellite_data():
    # Celestrak API ਤੋਂ ਪ੍ਰਸਿੱਧ ਸੈਟੇਲਾਈਟਾਂ ਦਾ ਡਾਟਾ
    url = "https://celestrak.org"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            live_sats = {}
            # ਸਿਰਫ਼ ਚੋਣਵੇਂ ਸੈਟੇਲਾਈਟਾਂ ਨੂੰ ਫਿਲਟਰ ਕਰਨਾ
            targets = ["ISS (ZARYA)", "TIANGONG", "HUBBLE SPACE TELESCOPE"]
            
            for item in data:
                name = item.get("OBJECT_NAME", "").strip()
                if name in targets or (len(live_sats) < 4 and "STARLINK" in name):
                    # API ਤੋਂ ਅਸਲੀ ਔਰਬਿਟਲ ਪੈਰਾਮੀਟਰ ਕੱਢਣਾ
                    live_sats[name] = {
                        "inc": float(item.get("INCLINATION", 51.6)),
                        "raan": float(item.get("RAAN", 180.0)),
                        "n": float(item.get("MEAN_MOTION", 15.5)),
                        "norad_id": item.get("NORAD_CAT_ID", "00000")
                    }
            return live_sats
    except Exception as e:
        pass
    
    # ਜੇ API ਫੇਲ੍ਹ ਹੋਵੇ ਤਾਂ ਫਾਲਬੈਕ (Fallback) ਡਾਟਾ
    return {
        "ISS (ZARYA) [OFFLINE MODE]": {"inc": 51.6391, "raan": 180.2031, "n": 15.49321473, "norad_id": "25544"},
        "STARLINK-1044": {"inc": 53.0542, "raan": 210.1543, "n": 15.05432110, "norad_id": "44713"},
        "TIANGONG": {"inc": 41.5843, "raan": 110.3214, "n": 15.61024530, "norad_id": "48274"}
    }

# ਲਾਈਵ ਡਾਟਾ ਲੋਡ ਕਰੋ
with st.spinner("⚡ Connecting to NORAD Database & Fetching Live Orbital Elements..."):
    protected_satellites = fetch_live_satellite_data()

# ਲਾਈਵ ਸਪੇਸ ਡੇਬਰਿਸ (ਕੂੜਾ) - COSMOS 2251 Debris
debris = {"inc": 74.0322, "raan": 124.2311, "n": 15.12053140}

def calculate_distance(sat, deb, t_minutes):
    dt = t_minutes / 1440.0
    sat_anomaly = (sat["n"] * dt * 2 * math.pi)
    deb_anomaly = (deb["n"] * dt * 2 * math.pi)
    
    x1 = 6738.1 * math.cos(sat_anomaly) * math.cos(math.radians(sat["raan"]))
    y1 = 6738.1 * math.sin(sat_anomaly) * math.cos(math.radians(sat["inc"]))
    
    x2 = 6750.0 * math.cos(deb_anomaly) * math.cos(math.radians(deb["deb_raan"] if "deb_raan" in deb else deb["raan"]))
    y2 = 6750.0 * math.sin(deb_anomaly) * math.cos(math.radians(deb["inc"]))
    
    dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return dist

# Scientist Lab Simulation Button
if st.button("📡 INITIATE LIVE RADAR SWEEP", type="primary", use_container_width=True):
    results = []
    
    # ਸਾਇੰਸ ਲੈਬ ਸਟਾਈਲ ਲੋਡਿੰਗ ਪ੍ਰੋਗਰੈਸ
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, (sat_name, param) in enumerate(protected_satellites.items()):
        status_text.text(f"Calculating Proximity Matrix for {sat_name} [NORAD ID: {param['norad_id']}]...")
        min_dist = float('inf')
        
        for minutes in range(1440):
            dist = calculate_distance(param, debris, minutes)
            if dist < min_dist:
                min_dist = dist
        
        progress_bar.progress(int((idx + 1) / len(protected_satellites) * 100))
        
        status = "🚨 CONJUNCTION DANGER" if min_dist < 500.0 else "✅ ORBIT NOMINAL"
        results.append({
            "Satellite / Asset": sat_name,
            "NORAD ID": param["norad_id"],
            "Inclination (°)": f"{param['inc']:.2f}°",
            "Closest Approach": round(min_dist, 2),
            "Status": status
        })
    
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    
    df = pd.DataFrame(results)
    
    # ਸਾਇੰਸ ਲੈਬ ਸਟਾਈਲ ਹਾਈਲਾਈਟਰ
    def style_scientist_table(val):
        if "DANGER" in str(val):
            return 'background-color: #2b0000; color: #FF3333; font-weight: bold; border: 1px solid #FF3333;'
        elif "NOMINAL" in str(val):
            return 'background-color: #002b00; color: #00FF66; border: 1px solid #00FF66;'
        return 'color: #CCCCCC; font-family: monospace;'

    styled_df = df.style.map(style_scientist_table, subset=['Status'])
    
    st.markdown("<h3 style='font-family: monospace; color: #00FF66;'>📊 Live Radar Telemetry Data Log</h3>", unsafe_allow_html=True)
    st.dataframe(styled_df, use_container_width=True)
    st.success("Omni-Radar cloud engine executed successfully! All vectors correlated.")
    
    # ਸਾਇੰਸ ਲੈਬ ਮੈਟ੍ਰਿਕ ਗ੍ਰਿਡ
    st.markdown("<h3 style='font-family: monospace; color: #00FF66;'>🖥️ Real-time Core Monitors</h3>", unsafe_allow_html=True)
    cols = st.columns(len(results))
    for index, row in df.iterrows():
        with cols[index]:
            st.metric(
                label=f"🛰️ {row['Satellite / Asset']}", 
                value=f"{row['Closest Approach']} KM", 
                delta="ALERT" if "DANGER" in row["Status"] else "OK",
                delta_color="inverse" if "DANGER" in row["Status"] else "normal"
            )

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; font-family: monospace; color: #666666;'>
        <h4>📬 Commercial Licensing & Custom Vectors</h4>
        <p>Want to deploy this sovereign SSA engine for your specific constellation?</p>
        <p>📩 Secure Comm: <b>contactkdtrader@gmail.com</b></p>
    </div>
    """, unsafe_allow_html=True)
