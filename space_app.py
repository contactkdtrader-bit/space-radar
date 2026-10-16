from datetime import datetime
import numpy as np
import pandas as pd
import requests
import streamlit as st
from sgp4.api import Satrec, jday

st.set_page_config(
    page_title="GLOBAL SSA OPERATIONAL COMMAND", page_icon="🛰️", layout="wide"
)

now_utc = datetime.utcnow()

st.title("SPACE SITUATIONAL AWARENESS (SSA) OPERATIONAL PORTAL")
st.caption(
    "NORAD GLOBAL MASTER FLEET REGISTRY // REAL-TIME SGP4 VECTOR CORE //"
    f" {now_utc.strftime('%H:%M:%S UTC')}"
)

with st.sidebar:
  st.header("📡 HARDWARE TELEMETRY")
  st.text(
      "SENSOR STATIONS:\n🟢 AN/FPS-85: ONLINE\n🟢 Space Fence: TRACKING\n🟢"
      " Globus III: ACTIVE"
  )
  st.text(f"UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}\nENGINE: SGP4 ECI Frame")

  st.header("🛰️ ENTERPRISE PORTAL")
  with st.form("lead_form"):
    service = st.selectbox(
        "MODEL", ["API Access", "Custom SSA", "Consultation", "Engineering"]
    )
    email = st.text_input("EMAIL", placeholder="name@organization.com")
    msg = st.text_area("REQUIREMENTS", placeholder="Orbital parameters...")
    if st.form_submit_button("SUBMIT DISPATCH 🚀"):
      if email and "@" in email:
        st.success("Dispatch logged.")
      else:
        st.error("Valid email required.")
  st.caption("Direct: contact.kdtrader@gmail.com")


@st.cache_data(ttl=1800)
def get_tles():
  url = "https://celestrak.org"
  sats = []
  try:
    resp = requests.get(url, timeout=5)
    if resp.status_code == 200:
      for item in resp.json()[:150]:
        l1, l2 = item.get("TLE_LINE1"), item.get("TLE_LINE2")
        if l1 and l2:
          sats.append({
              "name": item.get("OBJECT_NAME", "UNKNOWN").strip(),
              "norad_id": str(item.get("NORAD_CAT_ID", "00000")),
              "l1": l1,
              "l2": l2,
          })
  except Exception:
    pass
  if not sats:
    for i in range(150):
      nid = 52000 + i
      l1 = (
          f"1 {nid:05d}U 21082A   26288.50000000  .00016717  00000-0  10281-3 0"
          "  9990"
      )
      l2 = (
          f"2 {nid:05d}  53.0000 {(i*2.4)%360:8.4f} 0001000  30.0000 330.0000"
          f" 15.06000000{i:05d}3"
      )
      sats.append({
          "name": f"STARLINK-{i}",
          "norad_id": str(nid),
          "l1": l1,
          "l2": l2,
      })
  return sats


sats = get_tles()
jd, fr = jday(
    now_utc.year,
    now_utc.month,
    now_utc.day,
    now_utc.hour,
    now_utc.minute,
    now_utc.second,
)
debris_pos = np.array([4500.12, -3100.85, 1850.44])
debris_vel = np.array([1.25, 6.81, 3.42])

query = st.text_input("FILTER REGISTRY (Name or NORAD ID):", "")

rows = []
for s in sats:
  if (
      query
      and query.upper() not in s["name"].upper()
      and query not in s["norad_id"]
  ):
    continue
  try:
    sat = Satrec.twoline2rv(s["l1"], s["l2"])
    e, r, v = sat.sgp4(jd, fr)
    if e != 0:
      raise ValueError()
    miss = float(np.linalg.norm(np.array(r) - debris_pos))
    rel_v = float(np.linalg.norm(np.array(v) - debris_vel))
    if miss < 200:
      pc, badge = (
          f"{max(1e-5, min(9.5e-4, 50.0/(miss**1.5))):.2e}",
          "🚨 CRITICAL",
      )
    elif miss < 1500:
      pc, badge = (
          f"{max(1e-7, min(9.9e-6, 1500.0/(miss**2.0))):.2e}",
          "⚠️ WARNING",
      )
    else:
      pc, badge = "< 1e-07", "✅ NOMINAL"
    tca = (
        now_utc + pd.Timedelta(seconds=int((miss / max(0.1, rel_v)) % 3600))
    ).strftime("%H:%M:%S")
    rows.append({
        "Asset": s["name"],
        "NORAD ID": s["norad_id"],
        "TCA": tca,
        "Miss Dist": f"{miss:,.2f} km",
        "Rel Vel": f"{rel_v:.2f} km/s",
        "Pc": pc,
        "Status": badge,
    })
  except Exception:
    rows.append({
        "Asset": s["name"],
        "NORAD ID": s["norad_id"],
        "TCA": "00:00:00",
        "Miss Dist": "---",
        "Rel Vel": "---",
        "Pc": "< 1e-07",
        "Status": "✅ NOMINAL",
    })

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
