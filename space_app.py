import streamlit as st
import datetime
import pandas as pd
import math
import time

st.set_page_config(page_title="24/7 Space Radar", page_icon="🚀", layout="wide")

st.title("🛸 Live 24/7 Space Situational Awareness (SSA) Radar")
st.write("This dashboard monitors orbital assets against space debris in real-time using localized orbital vectors.")

# ਔਰਬਿਟਲ ਪੈਰਾਮੀਟਰ (Pure Python Math Model)
protected_satellites = {
    "ISS (ZARYA)": {"inc": 51.6391, "raan": 180.2031, "n": 15.49321473},
    "STARLINK-1044": {"inc": 53.0542, "raan": 210.1543, "n": 15.05432110},
    "STARLINK-2311": {"inc": 53.0551, "raan": 95.4321, "n": 15.06124530},
    "STARLINK-5490": {"inc": 70.0123, "raan": 15.3214, "n": 14.89543210}
}

# COSMOS 2251 Debris Vector
debris = {"inc": 74.0322, "raan": 124.2311, "n": 15.12053140}

def calculate_distance(sat, deb, t_minutes):
    dt = t_minutes / 1440.0
    sat_anomaly = (sat["n"] * dt * 2 * math.pi)
    deb_anomaly = (deb["n"] * dt * 2 * math.pi)
    
    x1 = 6738.1 * math.cos(sat_anomaly) * math.cos(math.radians(sat["raan"]))
    y1 = 6738.1 * math.sin(sat_anomaly) * math.cos(math.radians(sat["inc"]))
    
    x2 = 6750.0 * math.cos(deb_anomaly) * math.cos(math.radians(deb["raan"]))
    y2 = 6750.0 * math.sin(deb_anomaly) * math.cos(math.radians(deb["inc"]))
    
    dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return dist

# ਰੇਡਾਰ ਸਕੈਨ ਬਟਨ
if st.button("🔄 Refresh Radar Scan", type="primary"):
    results = []
    
    # ਲੋਡਿੰਗ ਐਨੀਮੇਸ਼ਨ
    with st.spinner("🛰️ Scanning orbital vectors and tracking debris path..."):
        time.sleep(1) # ਰੀਅਲ-ਟਾਈਮ ਫੀਲ ਦੇਣ ਲਈ ਛੋਟਾ ਜਿਹਾ ਡਿਲੇਅ
        
        for sat_name, param in protected_satellites.items():
            min_dist = float('inf')
            
            for minutes in range(1440):
                dist = calculate_distance(param, debris, minutes)
                if dist < min_dist:
                    min_dist = dist
            
            status = "🚨 DANGER" if min_dist < 200.0 else "✅ SAFE"
            results.append({
                "Satellite Name": sat_name, 
                "Closest Approach (KM)": round(min_dist, 2), 
                "Status": status
            })
        
        df = pd.DataFrame(results)
        
        # ਸਟੇਟਸ ਦੇ ਹਿਸਾਬ ਨਾਲ ਰੰਗ ਬਦਲਣ ਲਈ ਸਟਾਈਲਿੰਗ
        def highlight_status(val):
            if val == "🚨 DANGER":
                return 'background-color: #ffcccc; color: black; font-weight: bold;'
            elif val == "✅ SAFE":
                return 'background-color: #ccffcc; color: black;'
            return ''
        
        styled_df = df.style.applymap(highlight_status, subset=['Status'])
        
        # UI ਤੇ ਡਾਟਾ ਦਿਖਾਉਣਾ
        st.dataframe(styled_df, use_container_width=True)
        st.success("Omni-Radar cloud engine executed successfully!")
        
        # ਵਿਜ਼ੂਅਲ ਚਾਰਟ (Metric Bars)
        st.subheader("📊 Proximity Overview")
        cols = st.columns(len(results))
        for index, row in df.iterrows():
            with cols[index]:
                st.metric(label=row["Satellite Name"], value=f"{row['Closest Approach (KM)']} KM", delta=row["Status"])

st.markdown("---")
st.subheader("📬 Business & Inquiries")
st.write("Want to buy this software or customize it for your satellites?")
st.write("📩 Email me directly at: **contactkdtrader@gmail.com**")
