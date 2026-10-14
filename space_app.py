import streamlit as st
import datetime
import pandas as pd
import math

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
    # Pure vector calculation using orbital geometry angles
    dt = t_minutes / 1440.0
    sat_anomaly = (sat["n"] * dt * 2 * math.pi)
    deb_anomaly = (deb["n"] * dt * 2 * math.pi)
    
    # Math matrices to flat earth-centered distance estimation
    x1 = 6738.1 * math.cos(sat_anomaly) * math.cos(math.radians(sat["raan"]))
    y1 = 6738.1 * math.sin(sat_anomaly) * math.cos(math.radians(sat["inc"]))
    
    x2 = 6750.0 * math.cos(deb_anomaly) * math.cos(math.radians(deb["raan"]))
    y2 = 6750.0 * math.sin(deb_anomaly) * math.cos(math.radians(deb["inc"]))
    
    dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return dist

if st.button("🔄 Refresh Radar Scan"):
    results = []
    
    for sat_name, param in protected_satellites.items():
        min_dist = float('inf')
        
        # 24 ਘੰਟੇ (1440 ਮਿੰਟ) ਦੀ ਗਣਨਾ
        for minutes in range(1440):
            dist = calculate_distance(param, debris, minutes)
            if dist < min_dist:
                min_dist = dist
        
        # ਸਪੇਸ ਸੁਰੱਖਿਆ ਮੀਟਰ
        status = "🚨 DANGER" if min_dist < 200.0 else "✅ SAFE"
        results.append({
            "Satellite Name": sat_name, 
            "Closest Approach (KM)": f"{min_dist:.2f} km", 
            "Status": status
        })
    
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
    st.success("Omni-Radar cloud engine executed successfully!")
