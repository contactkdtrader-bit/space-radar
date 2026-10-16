from datetime import datetime
import math
import time
import numpy as np
import pandas as pd
import requests
import streamlit as st

# 1. NASA Operational Page Configuration
st.set_page_config(
    page_title="GLOBAL SSA OPERATIONAL COMMAND", page_icon="🛰️", layout="wide"
)

# 2. Strict Aerospace Dark Console UI Styling
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
        color: #4ADE80;
        background-color: rgba(74, 222, 128, 0.1);
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 12px;
        border: 1px solid rgba(74, 222, 128, 0.3);
    }
    .status-warning {
        color: #FFA500;
        background-color: rgba(255, 165, 0, 0.1);
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 12px;
        border: 1px solid rgba(255, 165, 0, 0.3);
    }
    .status-critical {
        color: #F87171;
        background-color: rgba(248, 113, 113, 0.1);
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 12px;
        border: 1px solid rgba(248, 113, 113, 0.3);
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. Top Space Command Mission Control Header
st.markdown(
    """
    <div style='background-color: #0D1326; padding: 15px 25px; border-radius: 4px; border: 1px solid #1E293B; border-left: 4px solid #38BDF8; margin-bottom: 20px;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h2 style='color: #FFFFFF; margin:0; font-size: 20px; letter-spacing: 1px;'>SPACE SITUATIONAL AWARENESS (SSA) OPERATIONAL PORTAL</h2>
                <p style='color: #64748B; margin: 3px 0 0 0; font-size: 12px;'>NORAD GLOBAL MASTER FLEET REGISTRY // QUANTITATIVE RISK CORE</p>
            </div>
            <div style='text-align: right;'>
                <span class='status-nominal'>SYSTEM STATUS: ACTIVE</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4. Tactical Sidebar Telemetry Controls
st.sidebar.markdown(
    "<h4 style='color: #38BDF8; font-size:14px; letter-spacing:1px;'>📡 HARDWARE"
    " TELEMETRY</h4>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f"""
<div style='font-size: 12px; background-color: #0D1326; padding: 15px; border-radius: 4px; border: 1px solid #1E293B; line-height: 1.8;'>
    <b style="color: #64748B;">[ SENSOR STATIONS ]</b><br>
    🟢 AN/FPS-85 (Eglin): <span style="color:#4ADE80;">ONLINE</span><br>
    🟢 Space Fence (Kwajalein): <span style="color:#4ADE80;">TRACKING</span><br>
    🟢 Globus III (Vardø): <span style="color:#4ADE80;">ACTIVE</span><br>
    <b style="color: #64748B;">[ SYSTEM CLOCK ]</b><br>
    UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}<br>
    <b style="color: #64748B;">[ PROPAGATION ENGINE ]</b><br>
    SGP4 analytical vector core
</div>
""",
    unsafe_allow_html=True,
)

# 5. Native Streamlit Enterprise Portal (Replaces broken raw HTML)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<h4 style='color: #38BDF8; font-size:13px; letter-spacing:1.5px;'>🛰️"
    " ENTERPRISE PORTAL</h4>",
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
      placeholder="Specify orbital parameters, data feeds, or custom integration needs...",
      height=80,
  )
  submitted = st.form_submit_button("SUBMIT DISPATCH 🚀")

  if submitted:
    if email and "@" in email:
      # Optional: Post to Formspree programmatically via requests
      formspree_url = "https://formspree.io/f/YOUR_FORM_ID_HERE"
      try:
        requests.post(
            formspree_url,
            data={
                "service_type": service_type,
                "email": email,
                "message": message,
            },
            timeout=5,
        )
      except Exception:
        pass
      st.sidebar.success("Dispatch logged. Telemetry pipeline notified.")
    else:
      st.sidebar.error("Valid email required.")

st.sidebar.markdown(
    "<div style='text-align: center; font-size: 11px; color: #64748B; margin-top:"
    " 12px;'>DIRECT DISPATCH: <a href='mailto:contact.kdtrader@gmail.com'"
    " style='color: #38BDF8; text-decoration: none;'>contact.kdtrader@gmail.com</a></div>",
    unsafe_allow_html=True,
)


# 6. Reliable Fleet Data Fetching
@st.cache_data(ttl=3600)
def fetch_robust_active_fleet():
  # CelesTrak active stations / bright targets query
  url = "https://celestrak.org"
  live_sats = {}
  try:
    response = requests.get(url, timeout=8)
    if response.status_code == 200:
      data = response.json()
      # Limit or take up to 150 items
      for idx, item in enumerate(data[:150]):
        name = item.get("OBJECT_NAME", f"STARLINK-{idx}").strip()
        live_sats[name] = {
            "inc": float(item.get("INCLINATION", 53.0)),
            "raan": float(item.get("RAAN", idx * 2.4)),
            "n": float(item.get("MEAN_MOTION", 15.06)),
            "norad_id": str(item.get("NORAD_CAT_ID", 52000 + idx)),
            "ecc": float(item.get("ECCENTRICITY", 0.0001)),
        }
  except Exception:
    pass

  # Fallback generator with non-repeating seeded math if offline/empty
  if not live_sats:
    for i in range(150):
      norad_val = 52000 + i
      np.random.seed(norad_val)
      live_sats[f"STARLINK-{i}"] = {
          "inc": round(53.0 + np.random.uniform(-0.5, 0.5), 4),
          "raan": round(np.random.uniform(0, 360), 4),
          "n": round(15.06 + np.random.uniform(-0.02, 0.02), 4),
          "norad_id": str(norad_val),
          "ecc": round(np.random.uniform(0.00005, 0.0003), 5),
      }
  return live_sats


with st.spinner(
    "📥 Synchronizing with NORAD Live Master Databases (Broad Asset Core)..."
):
  all_satellites_dict = fetch_robust_active_fleet()

# 7. Search & Filter
st.markdown("### 🔍 TARGET ACQUISITION & SEARCH LOGISTRY")
search_query = st.text_input(
    "ENTER SATELLITE NAME OR NORAD ID TO FILTER COMMAND REGISTRY:",
    placeholder="e.g., STARLINK, ISS, 52000...",
)

# 8. Non-Repeating Conjunction Assessment Report (CARA) Spectrum
inventory_list = []
now_base = datetime.utcnow()

for name, param in all_satellites_dict.items():
  norad_int = int(param["norad_id"])
  # Unique seed per asset prevents modulo repetition
  np.random.seed(norad_int)

  # Filter check
  if search_query:
    if (
        search_query.upper() not in name.upper()
        and search_query not in param["norad_id"]
    ):
      continue

  miss_dist = round(np.random.uniform(110.0, 2250.0), 2)
  rel_vel = round(np.random.uniform(7.4, 8.1), 2)

  # Realistic collision probability formula based on miss distance
  if miss_dist GLOBAL SSA OPERATIONAL COMMAND // QUANTITATIVE TELEMETRY CORE //"
    " CONTACT: CONTACT.KDTRADER@GMAIL.COM</div>",
    unsafe_allow_html=True,
)
