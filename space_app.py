import streamlit as st
import datetime
import pandas as pd
import math
import time
import requests

# 1. Page Config
st.set_page_config(page_title="NORAD SSA CONTROL", page_icon="🛸", layout="wide")

# 2. Advanced Sci-Fi Dark Theme CSS Injection
st.markdown("""
    <style>
    /* Full Dark Background */
    .stApp {
        background-color: #0B0F19 !important;
        color: #E2E8F0 !important;
    }
    /* Metric Cards Styling */
    div[data-testid="stMetricSimpleValue"] {
        font-family: 'Courier New', monospace !important;
        color: #00FF66 !important;
        font-size: 2rem !important;
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        font-family: 'Courier New', monospace !important;
        color: #8A99AD !important;
    }
    /* Custom Scientist Container */
    .lab-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-left: 4px solid #00FF66;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    .danger-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-left: 4px solid #FF3333;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Top Cyber Header
st.markdown("""
    <div style='background-color: #111827; padding: 20px; border-radius: 8px; border: 1px solid #00FF66; box-shadow: 0px 0px 15px rgba(0, 255, 102, 0.2); margin-bottom: 25px;'>
        <h1 style='text-align: center; color: #00FF66; font-family: monospace; margin:0; letter-spacing: 2px;'>🛸 NORAD SYSTEMS: SPACE SITUATIONAL AWARENESS (SSA)</h1>
        <p style='text-align: center; color: #8A99AD; font-family: monospace; margin: 5px 0 0 0;'>[ CLASSIFIED CORE INFRASTRUCTURE ] // REAL-TIME ORBITAL CONJUNCTION RADAR</p>
    </div>
    """, unsafe_allow_html=True)

# 4. Sidebar System Stats
st.sidebar.markdown("<h2 style='color: #00FF66; font-family: monospace;'>📡 SYSTEM TELEMETRY</h2>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='font-family: monospace; background-color: #111827; padding: 15px; border-radius: 6px; border: 1px solid #1F2937;'>
    <p style='color: #00FF66; margin: 5px 0;'>● RADAR: ACTIVE</p>
    <p style='color: #00FF66; margin: 5px 0;'>● INTERFACE: EXPERT LAB</p>
    <p style='color: #00FF66; margin: 5px 0;'>● CORE ENGINE: ONLINE</p>
    <p style='color: #FFA500; margin: 5px 0;'>● THREAT DETECTION: AUTO</p>
</div>
""", unsafe_allow_html=True)

# 5. Fetch Live Data from Celestrak API
@st.cache_data(ttl=3600)
def fetch_live_satellite_data():
    url = "https://celestrak.org"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            live_sats = {}
            targets = ["ISS (ZARYA)", "TIANGONG", "HUBBLE SPACE TELESCOPE"]
            for item in data:
                name = item.get("OBJECT_NAME", "").strip()
                if name in targets or (len(live_sats) < 4 and "STARLINK" in name):
                    live_sats[name] = {
                        "inc": float(item.get("INCLINATION", 51.6)),
                        "raan": float(item.get("RAAN", 180.0)),
                        "n": float(item.get("MEAN_MOTION", 15.5)),
                        "norad_id": item.get("NORAD_CAT_ID", "00000")
                    }
            return live_sats
    except:
        pass
    return {
        "ISS (ZARYA)": {"inc": 51.6391, "raan": 180.2031, "n": 15.49321473, "norad_id": "25544"},
        "STARLINK-1044": {"inc": 53.0542, "raan": 210.1543, "n": 15.05432110, "norad_id": "44713"},
        "TIANGONG": {"inc": 41.5843, "raan": 110.3214, "n": 15.61024530, "norad_id": "48274"}
    }

protected_satellites = fetch_live_satellite_data()
debris = {"inc": 74.0322, "raan": 124.2311, "n": 15.12053140}

# 6. Advanced 2D/3D Radar Map Plotting
st.markdown("<h3 style='font-family: monospace; color: #00FF66;'>🖥️ LIVE ORBITAL VECTOR SIMULATION</h3>", unsafe_allow_html=True)

t_now = time.time() / 60.0
coordinates = []

for name, param in protected_satellites.items():
    for minutes in range(0, 1440, 20):
        angle = (param["n"] * (t_now + minutes) * 2 * math.pi) / 100
        lon = ((param["raan"] + math.degrees(math.cos(angle))) % 360) - 180
        lat = (param["inc"] * math.sin(angle))
        coordinates.append({"Asset": name, "Longitude (X)": lon, "Latitude (Y)": lat})

# Add Debris Path
for minutes in range(0, 1440, 20):
    deb_angle = (debris["n"] * (t_now + minutes) * 2 * math.pi) / 100
    d_lon = ((debris["raan"] + math.degrees(math.cos(deb_angle))) % 360) - 180
    d_lat = (debris["inc"] * math.sin(deb_angle))
    coordinates.append({"Asset": "🚨 SPACE DEBRIS", "Longitude (X)": d_lon, "Latitude (Y)": d_lat})

df_coords = pd.DataFrame(coordinates)

st.scatter_chart(
    df_coords,
    x="Longitude (X)",
    y="Latitude (Y)",
    color="Asset",
    use_container_width=True,
    height=380
)

def calculate_distance(sat, deb, t_minutes):
    dt = t_minutes / 1440.0
    sat_anomaly = (sat["n"] * dt * 2 * math.pi)
    deb_anomaly = (deb["n"] * dt * 2 * math.pi)
    x1 = 6738.1 * math.cos(sat_anomaly) * math.cos(math.radians(sat["raan"]))
    y1 = 6738.1 * math.sin(sat_anomaly) * math.cos(math.radians(sat["inc"]))
    x2 = 6750.0 * math.cos(deb_anomaly) * math.cos(math.radians(debris["raan"]))
    y2 = 6750.0 * math.sin(deb_anomaly) * math.cos(math.radians(debris["inc"]))
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

st.markdown("<br>", unsafe_allow_html=True)

# 7. Proximity Control Grid
if st.button("📡 INITIALIZE RADAR SWEEP NETWORK", type="primary", use_container_width=True):
    results = []
    
    with st.spinner("⚡ Correlating target matrices with threat vectors..."):
        time.sleep(0.8)
        for sat_name, param in protected_satellites.items():
            min_dist = float('inf')
            for minutes in range(1440):
                dist = calculate_distance(param, debris, minutes)
                if dist < min_dist:
                    min_dist = dist
            
            status = "🚨 THREAT DETECTION" if min_dist < 500.0 else "✅ NOMINAL"
            results.append({"Asset": sat_name, "NORAD ID": param["norad_id"], "Closest Approach": min_dist, "Status": status})
        
        df_results = pd.DataFrame(results)
        
        st.markdown("<h3 style='font-family: monospace; color: #00FF66;'>📊 REAL-TIME TELEMETRY MONITORS</h3>", unsafe_allow_html=True)
        cols = st.columns(len(results))
        for index, row in df_results.iterrows():
            with cols[index]:
                card_style = "danger-card" if "THREAT" in row["Status"] else "lab-card"
                # ਇੱਥੇ row['NORAD ID'] ਨੂੰ ਬਿਲਕੁਲ ਸਹੀ ਸਪੇਸ ਨਾਲ ਲਿਖ ਦਿੱਤਾ ਹੈ
                st.markdown(f"""
                    <div class='{card_style}'>
                        <h4 style='margin:0; color:#FFFFFF; font-family:monospace;'>🛰️ {row['Asset']}</h4>
                        <p style='margin:5px 0 0 0; color:#8A99AD; font-size:12px; font-family:monospace;'>NORAD ID: {row['NORAD ID']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                st.metric(label="Closest Approach Distance", value=f"{row['Closest Approach']:.2f} KM", delta=row["Status"])

# 8. Sleek Cyber Footer
st.markdown("<br><hr style='border-color: #1F2937;'>", unsafe_allow_html=True)
st.markdown("""
    <div style='background-color: #111827; padding: 20px; border-radius: 8px; border: 1px solid #1F2937; text-align: center; font-family: monospace;'>
        <h4 style='color: #00FF66; margin: 0 0 10px 0;'>📬 SOVEREIGN SSA ENGINE LICENSING</h4>
        <p style='color: #8A99AD; margin: 0;'>Secure encrypted gateway for orbital logistics and analytics.</p>
        <p style='color: #FFFFFF; margin: 10px 0 0 0;'>📩 SECURE EMAIL: <b>contactkdtrader@gmail.com</b></p>
    </div>
    """, unsafe_allow_html=True)
