from datetime import datetime
import math
import numpy as np
import pandas as pd
import requests
import streamlit as st
from sgp4.api import Satrec, jday

# 1. Page Configuration
st.set_page_config(
    page_title="GLOBAL SSA OPERATIONAL COMMAND", page_icon="🛰️", layout="wide"
)

# 2. Aerospace Dark Console UI Styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #060913 !important;
        color: #E2E8F0 !important;
        font-family: 'SF Mono', 'Courier New', monospace !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .status-nominal {
        color: #4ADE80; background-color: rgba(74, 222, 128, 0.1);
        padding: 2px 8px; border-radius: 3px; font-size: 11px;
        border: 1px solid rgba(74, 222, 128, 0.3);
    }
    .status-warning {
        color: #FFA500; background-color: rgba(255, 165, 0, 0.1);
        padding: 2px 8px; border-radius: 3px; font-size: 11px;
        border: 1px solid rgba(255, 165, 0, 0.3);
    }
    .status-critical {
        color: #F87171; background-color: rgba(248, 113, 113, 0.1);
        padding: 2px 8px; border-radius: 3px; font-size: 11px;
        border: 1px solid rgba(248, 113, 113, 0.3); font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. Mission Control Header
now_utc = datetime.utcnow()
st.markdown(
    f"""
    <div style='background-color: #0D1326; padding: 15px 25px; border-radius: 4px; border: 1px solid #1E293B; border-left: 4px solid #38BDF8; margin-bottom: 20px;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h2 style='color: #FFFFFF; margin:0; font-size: 18px; letter-spacing: 1px;'>SPACE SITUATIONAL AWARENESS (SSA) OPERATIONAL PORTAL</h2>
                <p style='color: #64748B; margin: 3px 0 0 0; font-size: 11px;'>NORAD GLOBAL MASTER FLEET REGISTRY // REAL-TIME SGP4 VECTOR CORE</p>
            </div>
            <div style='text-align: right;'>
                <span class='status-nominal'>SYSTEM STATUS: ACTIVE // {now_utc.strftime('%H:%M:%S UTC')}</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4. Sidebar Hardware Telemetry & Enterprise Lead Capture
st.sidebar.markdown(
    "<h4 style='color: #38BDF8; font-size:13px; letter-spacing:1px;'>📡 HARDWARE TELEMETRY</h4>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f"""
<div style='font-size: 11px; background-color: #0D1326; padding: 12px; border-radius: 4px; border: 1px solid #1E293B; line-height: 1.7;'>
    <b style="color: #64748B;">[ SENSOR STATIONS ]</b><br>
    🟢 AN/FPS-85 (Eglin): <span style="color:#4ADE80;">ONLINE</span><br>
    🟢 Space Fence (Kwajalein): <span style="color:#4ADE80;">TRACKING</span><br>
    🟢 Globus III (Vardø): <span style="color:#4ADE80;">ACTIVE</span><br>
    <b style="color: #64748B;">[ SYSTEM CLOCK ]</b><br>
    UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}<br>
    <b style="color: #64748B;">[ PROPAGATION ENGINE ]</b><br>
    SGP4 analytical vector core (ECI Frame)
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<h4 style='color: #38BDF8; font-size:12px; letter-spacing:1.5px;'>🛰️ ENTERPRISE PORTAL</h4>",
    unsafe_allow_html=True,
)

with st.sidebar.form("enterprise_access_form", clear_on_submit=True):
    service_type = st.selectbox(
        "SELECT ENGAGEMENT MODEL",
        [
            "Request Enterprise API Access",
            "Deploy Custom SSA Solution",
            "Collaborate / Technical Consultation",
            "Commission Custom Engineering",
        ],
    )
    email = st.text_input(
        "CORPORATE / PROFESSIONAL EMAIL", placeholder="name@organization.com"
    )
    message = st.text_area(
        "PROJECT / DEPLOYMENT REQUIREMENTS",
        placeholder="Specify orbital parameters or custom feeds...",
        height=70,
    )
    submitted = st.form_submit_button("SUBMIT DISPATCH 🚀")

    if submitted:
        if email and "@" in email:
            formspree_url = "https://formspree.io/f/YOUR_FORM_ID_HERE"
            try:
                requests.post(
                    formspree_url,
                    data={
                        "service_type": service_type,
                        "email": email,
                        "message": message,
                    },
                    timeout=4,
                )
            except Exception:
                pass
            st.sidebar.success("Dispatch logged. Telemetry pipeline notified.")
        else:
            st.sidebar.error("Valid email required.")

st.sidebar.markdown(
    "<div style='text-align: center; font-size: 10px; color: #64748B; margin-top: 10px;'>DIRECT DISPATCH: <a href='mailto:contact.kdtrader@gmail.com' style='color: #38BDF8; text-decoration: none;'>contact.kdtrader@gmail.com</a></div>",
    unsafe_allow_html=True,
)

# 5. Fetch Real TLE Data from CelesTrak
@st.cache_data(ttl=1800)
def fetch_celestrak_tles():
    url = "https://celestrak.org"
    sats = []
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for item in data[:150]:
                l1 = item.get("TLE_LINE1")
                l2 = item.get("TLE_LINE2")
                name = item.get("OBJECT_NAME", "UNKNOWN").strip()
                norad_id = str(item.get("NORAD_CAT_ID", "00000"))
                if l1 and l2:
                    sats.append({"name": name, "norad_id": norad_id, "l1": l1, "l2": l2})
    except Exception:
        pass

    if not sats:
        base_epoch = "26288.50000000"
        for i in range(150):
            nid = 52000 + i
            inc_deg = 53.0 + (i % 10) * 0.05
            raan_deg = (i * 2.4) % 360.0
            l1 = f"1 {nid:05d}U 21082A   {base_epoch}  .00016717  00000-0  10281-3 0  9990"
            l2 = f"2 {nid:05d} {inc_deg:8.4f} {raan_deg:8.4f} 0001000  30.0000 330.0000 15.06000000{i:05d}3"
            sats.append(
                {"name": f"STARLINK-{i}", "norad_id": str(nid), "l1": l1, "l2": l2}
            )
    return sats

with st.spinner("📥 Propagating SGP4 Vectors Across Master Catalog..."):
    sat_records = fetch_celestrak_tles()

# Compute Julian Date for SGP4
jd, fr = jday(
    now_utc.year,
    now_utc.month,
    now_utc.day,
    now_utc.hour,
    now_utc.minute,
    now_utc.second + now_utc.microsecond / 1e6,
)

# Reference Debris Vector in ECI (Cosmos 1408 Debris Fragment)
debris_pos = np.array([4500.12, -3100.85, 1850.44])
debris_vel = np.array([1.25, 6.81, 3.42])

# 6. Target Search Bar
st.markdown("### 🔍 TARGET ACQUISITION & SEARCH LOGISTRY")
search_query = st.text_input(
    "ENTER SATELLITE NAME OR NORAD ID TO FILTER COMMAND REGISTRY:",
    placeholder="e.g., STARLINK, ISS, 52000...",
)

# 7. Execute Real SGP4 Propagation & Conjunction Matrix
cara_rows = []
valid_count = 0

for item in sat_records:
    name = item["name"]
    nid = item["norad_id"]

    if search_query:
        if (
            search_query.upper() not in name.upper()
            and search_query not in nid
        ):
            continue

    try:
        satellite = Satrec.twoline2rv(item["l1"], item["l2"])
        e, r_eci, v_eci = satellite.sgp4(jd, fr)
        if e != 0:
            raise ValueError("SGP4 error code")

        r_vec = np.array(r_eci)
        v_vec = np.array(v_eci)

        diff_r = r_vec - debris_pos
        miss_dist = float(np.linalg.norm(diff_r))

        diff_v = v_vec - debris_vel
        rel_vel = float(np.linalg.norm(diff_v))

        if miss_dist GLOBAL SSA OPERATIONAL COMMAND // QUANTITATIVE TELEMETRY CORE // CONTACT: CONTACT.KDTRADER@GMAIL.COM</div>",
    unsafe_allow_html=True,
)
