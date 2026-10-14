import streamlit as st
import ephem
import datetime
import pandas as pd

# ਵੈੱਬ ਪੇਜ ਦੀ ਸੈਟਿੰਗ
st.set_page_config(page_title="24/7 Space Radar", page_icon="🚀", layout="wide")

st.title("🛸 Live 24/7 Space Situational Awareness (SSA) Radar")
st.write("This dashboard monitors orbital assets against space debris in real-time.")

# ਸੈਟੇਲਾਈਟ ਡਾਟਾ
protected_satellites = {
    "ISS (ZARYA)": {"inc": 51.6391, "raan": 180.2031, "e": 0.0005123, "ap": 88.1632, "M": 272.0423, "n": 15.49321473, "epoch": '2026/10/14 21:24:51'},
    "STARLINK-1044": {"inc": 53.0542, "raan": 210.1543, "e": 0.0001421, "ap": 120.4321, "M": 145.9102, "n": 15.05432110, "epoch": '2026/10/14 21:24:51'},
    "STARLINK-2311": {"inc": 53.0551, "raan": 95.4321, "e": 0.0001150, "ap": 45.1204, "M": 312.4501, "n": 15.06124530, "epoch": '2026/10/14 21:24:51'},
    "STARLINK-5490": {"inc": 70.0123, "raan": 15.3214, "e": 0.0002100, "ap": 210.9432, "M": 89.1243, "n": 14.89543210, "epoch": '2026/10/14 21:24:51'}
}

# Debris
debris_obj = ephem.EarthSatellite()
debris_obj._inc, debris_obj._raan, debris_obj._e, debris_obj._ap, debris_obj._M, debris_obj._n, debris_obj._epoch = 74.0322, 124.2311, 0.0018765, 85.4321, 274.9102, 15.12053140, ephem.Date('2026/10/14 21:24:51')

if st.button("🔄 Refresh Radar Scan"):
    start_time = datetime.datetime.utcnow()
    results = []
    
    for sat_name, param in protected_satellites.items():
        sat = ephem.EarthSatellite()
        sat._inc, sat._raan, sat._e, sat._ap, sat._M, sat._n, sat._epoch = param["inc"], param["raan"], param["e"], param["ap"], param["M"], param["n"], ephem.Date(param["epoch"])
        
        min_dist = float('inf')
        for minutes in range(1440):
            check_time = start_time + datetime.timedelta(minutes=minutes)
            sat.compute(check_time)
            debris_obj.compute(check_time)
            dist = ephem.separation(sat, debris_obj) * 6378.1
            if dist < min_dist:
                min_dist = dist
        
        status = "🚨 DANGER" if min_dist < 10.0 else "✅ SAFE"
        results.append({"Satellite Name": sat_name, "Closest Approach (KM)": f"{min_dist:.2f} km", "Status": status})
    
    # ਟੇਬਲ ਦੇ ਰੂਪ ਵਿੱਚ ਵੈੱਬਸਾਈਟ 'ਤੇ ਦਿਖਾਓ
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
    st.success("Radar scan completed successfully!")
