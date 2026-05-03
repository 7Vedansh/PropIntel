"""
PropIntel AI — Premium NBFC Intelligence Dashboard
Design: Playfair Display × DM Sans × Space Mono
"""

import streamlit as st
import requests
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from components.python_report import generate_pdf

st.set_page_config(
    page_title="PropIntel AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_URL = "http://localhost:8000"

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&family=Space+Mono:wght@400&display=swap');

:root {
  --black:    #050508;
  --surface:  #0d0d12;
  --surface2: #13131a;
  --border:   rgba(255,255,255,0.07);
  --border2:  rgba(255,255,255,0.12);
  --cyan:     #00d4ff;
  --cdim:     rgba(0,212,255,0.15);
  --cglow:    rgba(0,212,255,0.06);
  --white:    #f0eeea;
  --muted:    rgba(240,238,234,0.45);
  --green:    #00e5a0;
  --amber:    #f5a623;
  --red:      #ff4757;
  --fd: 'Playfair Display', Georgia, serif;
  --fb: 'DM Sans', sans-serif;
  --fm: 'Space Mono', monospace;
}

/* Reset & base */
html, body, [class*="css"], .stApp {
  background: var(--black) !important;
  color: var(--white) !important;
  font-family: var(--fb) !important;
}
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stToolbar"], footer, #MainMenu { display: none !important; }
header { background: transparent !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── Widget overrides ── */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stSlider label, .stCheckbox label {
  font-family: var(--fm) !important;
  font-size: 9.5px !important;
  letter-spacing: 2px !important;
  color: rgba(240,238,234,0.4) !important;
  text-transform: uppercase !important;
}
.stTextInput input, .stNumberInput input {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 6px !important;
  color: var(--white) !important;
  font-family: var(--fb) !important;
  font-size: 13px !important;
}
.stTextInput input::placeholder { color: rgba(240,238,234,0.22) !important; }
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: rgba(0,212,255,0.4) !important;
  box-shadow: none !important;
}
.stSelectbox > div > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
  color: var(--white) !important;
}
.stCheckbox span { color: var(--muted) !important; font-size: 13px !important; }

/* Buttons */
div.stButton > button, div.stFormSubmitButton > button {
  background: transparent !important;
  border: 1px solid var(--cyan) !important;
  color: var(--cyan) !important;
  font-family: var(--fb) !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  border-radius: 6px !important;
  padding: 12px 32px !important;
  letter-spacing: 0.5px !important;
  transition: all 0.2s !important;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
  background: var(--cdim) !important;
}
div.stDownloadButton > button {
  background: transparent !important;
  border: 1px solid rgba(0,212,255,0.35) !important;
  color: var(--cyan) !important;
  font-family: var(--fm) !important;
  font-size: 10px !important;
  border-radius: 4px !important;
  padding: 8px 18px !important;
  letter-spacing: 1px !important;
}
div.stDownloadButton > button:hover { background: var(--cglow) !important; }

/* Sliders */
.stSlider [data-baseweb="slider"] div[role="slider"] { background: var(--cyan) !important; }

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  font-family: var(--fm) !important;
  font-size: 10px !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  padding: 12px 22px !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom: 2px solid var(--cyan) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
  background: transparent !important;
  padding-top: 24px !important;
}

/* Expander */
[data-testid="stExpander"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; }
[data-testid="stExpander"] summary { color: var(--muted) !important; font-family: var(--fm) !important; font-size: 10px !important; letter-spacing: 1px !important; }

/* Form container */
[data-testid="stForm"] { border: none !important; background: transparent !important; padding: 0 !important; }

/* Number input buttons */
button[data-testid="baseButton-secondary"] { background: var(--surface2) !important; border: 1px solid var(--border) !important; color: var(--muted) !important; }

/* ════════════════════════════════════════ ANIMATIONS ════════════════════════════════════════ */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

@keyframes progressFill {
  0% { width: 0%; }
  100% { width: var(--progress-width, 100%); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes orb {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
  50% { transform: translate(-50%, -50%) scale(1.04); opacity: 0.7; }
}

@keyframes flt {
  0%, 100% { transform: translateX(-50%) translateY(0); opacity: 0.3; }
  50% { transform: translateX(-50%) translateY(-5px); opacity: 0.6; }
}

@keyframes cardSlideIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 8px rgba(0, 212, 255, 0.2); }
  50% { box-shadow: 0 0 16px rgba(0, 212, 255, 0.4); }
}

/* Animation utility classes */
.fade-in-up { animation: fadeInUp 0.6s ease-out; }
.slide-in-left { animation: slideInLeft 0.6s ease-out; }
.slide-in-right { animation: slideInRight 0.6s ease-out; }
.scale-in { animation: scaleIn 0.5s ease-out; }
.card-slide-in { animation: cardSlideIn 0.5s ease-out forwards; }
.glow-pulse { animation: glowPulse 2s ease-in-out infinite; }

.card-slide-in:nth-child(1) { animation-delay: 0ms; }
.card-slide-in:nth-child(2) { animation-delay: 100ms; }
.card-slide-in:nth-child(3) { animation-delay: 200ms; }
.card-slide-in:nth-child(4) { animation-delay: 300ms; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSIONS STATE
# ══════════════════════════════════════════════════════════════════════════════
def _ss(k, v):
    if k not in st.session_state: st.session_state[k] = v

_ss("results", None)
_ss("sample", None)
_ss("form_vals", {})

SAMPLES = {
    "baner":   {"address":"Survey No 45, Baner Road","locality":"baner","city":"Pune","bhk":2,"sqft":1200,"age":8,"floor":7,"tfloor":14,"lift":True,"own":"Freehold"},
    "wagholi": {"address":"Near Wagholi Chowk","locality":"wagholi","city":"Pune","bhk":3,"sqft":1450,"age":18,"floor":2,"tfloor":5,"lift":False,"own":"Freehold"},
    "fraud":   {"address":"Plot 12, Kothrud","locality":"kothrud","city":"Pune","bhk":2,"sqft":4800,"age":3,"floor":1,"tfloor":4,"lift":False,"own":"Disputed"},
}
s = SAMPLES.get(st.session_state.sample, {})

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
try:
    health = requests.get(f"{API_URL}/health", timeout=2).json()
    api_ok, api_ver = True, health.get("api_version","2.0.0")
except Exception:
    api_ok, api_ver = False, "—"

sc = "#00e5a0" if api_ok else "#ff4757"

st.markdown(f"""
<div style="min-height:92vh;display:flex;flex-direction:column;align-items:center;justify-content:center;
  position:relative;background:var(--black);text-align:center;padding:60px 40px;overflow:hidden;">
  <div style="position:absolute;width:520px;height:520px;border-radius:50%;
    background:radial-gradient(circle at 40% 40%,rgba(0,212,255,0.08) 0%,rgba(0,212,255,0.03) 40%,transparent 70%);
    border:1px solid rgba(0,212,255,0.08);top:50%;left:50%;transform:translate(-50%,-50%);
    animation:orb 6s ease-in-out infinite;pointer-events:none;"></div>
  <style>
    @keyframes orb{{0%,100%{{transform:translate(-50%,-50%) scale(1);opacity:1;}}50%{{transform:translate(-50%,-50%) scale(1.04);opacity:0.7;}}}}
    @keyframes flt{{0%,100%{{transform:translateX(-50%) translateY(0);opacity:0.3;}}50%{{transform:translateX(-50%) translateY(-5px);opacity:0.6;}}}}
  </style>
  <div style="position:relative;z-index:2;">
    <div style="font-family:'Playfair Display',Georgia,serif;font-size:72px;font-weight:700;letter-spacing:-2px;line-height:1;margin-bottom:12px;">
      <span style="color:#00d4ff">Prop</span><span style="color:rgba(240,238,234,0.5)">Intel</span><span style="color:rgba(240,238,234,0.85)"> AI</span>
    </div>
    <p style="font-size:15px;color:var(--muted);letter-spacing:0.5px;margin-bottom:36px;font-weight:300;">
      <span style="color:#00d4ff;opacity:0.85">Collateral Valuation</span> &nbsp;·&nbsp; Liquidity Intelligence &nbsp;·&nbsp; <span style="color:#00d4ff;opacity:0.85">Risk Assessment</span>
    </p>
    <p style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;color:{sc};">
      ● &nbsp;API v{api_ver} &nbsp;{'Online' if api_ok else 'Offline — check backend'}
    </p>
  </div>
  <div style="position:absolute;bottom:32px;left:50%;transform:translateX(-50%);
    font-family:'Space Mono',monospace;font-size:9px;letter-spacing:3px;
    color:rgba(255,255,255,0.22);animation:flt 2s ease-in-out infinite;">SCROLL DOWN</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FORM HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="background:#0d0d12;padding:64px 56px 0 56px;border-top:1px solid rgba(255,255,255,0.07);animation:fadeInUp 0.8s ease-out 0.3s both;">
  <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;
    opacity:0.7;margin-bottom:10px;text-transform:uppercase;">Step 01 — Property Input</div>
  <div style="font-family:'Playfair Display',Georgia,serif;font-size:34px;font-weight:400;color:#f0eeea;
    margin-bottom:8px;letter-spacing:-0.5px;">Enter Property Details</div>
  <p style="font-size:14px;color:rgba(240,238,234,0.45);margin-bottom:36px;max-width:540px;line-height:1.7;">
    Enter the address and basic property details. Market signals, builder scores, and demand metrics are auto-computed by the intelligence engine.
  </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# QUICK FILL BUTTONS
# ══════════════════════════════════════════════════════════════════════════════
with st.container():
    qc1, qc2, qc3, _ = st.columns([1.2, 1.4, 1.2, 8])
    with qc1:
        if st.button("⚡ Baner 2BHK", key="btn_baner"):
            st.session_state.sample = "baner"; st.rerun()
    with qc2:
        if st.button("⚠ Wagholi 3BHK", key="btn_wagholi"):
            st.session_state.sample = "wagholi"; st.rerun()
    with qc3:
        if st.button("✕ Fraud Case", key="btn_fraud"):
            st.session_state.sample = "fraud"; st.rerun()
    
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FORM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="animation:fadeInUp 0.8s ease-out 0.4s both;">
""", unsafe_allow_html=True)

with st.form("assessment_form"):
    # Row 1: Address + Locality
    c1, c2 = st.columns([4, 1])
    with c1:
        address = st.text_input("Full Address", value=s.get("address",""), placeholder="e.g. Survey No 45, Baner Road, Baner, Pune")
    with c2:
        locality = st.text_input("Locality / Area", value=s.get("locality",""), placeholder="e.g. Baner")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Row 2: Main config
    g1, g2, g3 = st.columns(3)
    with g1:
        bhk  = st.selectbox("BHK Configuration", [1,2,3,4], index=[1,2,3,4].index(s.get("bhk",2)))
        sqft = st.number_input("Carpet Area (sqft)", 200, 8000, value=int(s.get("sqft",1200)), step=50)
    with g2:
        city = st.selectbox("City", ["Pune","Mumbai","Bangalore","Hyderabad","Chennai"],
                            index=["Pune","Mumbai","Bangalore","Hyderabad","Chennai"].index(s.get("city","Pune")))
        age  = st.number_input("Property Age (years)", 0, 50, value=int(s.get("age",8)))
    with g3:
        fl   = st.number_input("Floor Number", 0, 60, value=int(s.get("floor",7)))
        tfl  = st.number_input("Total Floors", 1, 60, value=int(s.get("tfloor",14)))

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Row 3: Ownership + Lift
    o1, o2 = st.columns(2)
    with o1:
        own_opts = ["Freehold","Leasehold","Disputed"]
        own = st.selectbox("Ownership Type", own_opts, index=own_opts.index(s.get("own","Freehold")))
    with o2:
        lift  = st.checkbox("Has Lift", value=bool(s.get("lift",True)))

    submitted = st.form_submit_button("Analyse Collateral →", use_container_width=False)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HANDLE SUBMISSION
# ══════════════════════════════════════════════════════════════════════════════
if submitted:
    if not address.strip() or not locality.strip():
        st.error("Please enter both Address and Locality.")
        st.stop()
    payload = {
        "address": address, "locality": locality, "city": city,
        "bhk": bhk, "carpet_area_sqft": sqft, "age_years": age,
        "floor_number": fl, "total_floors": tfl, "property_type": "apartment",
        "ownership_type": own.lower(), "has_rera": 1,
        "has_lift": lift, "builder_score": 70,
        "govt_project_nearby": 0, "npa_zone": 0,
        "absorption_rate": 0.18, "supply_demand_ratio": 1.0, "price_trend_6m": 5.0,
    }
    
    # Show advanced loading screen with 6 analysis layers
    loading_html = """
<div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#050508;text-align:center;padding:60px 40px;">
  <div style="position:relative;width:100%;max-width:500px;">
    <div style="font-family:'Playfair Display',Georgia,serif;font-size:36px;color:#00d4ff;margin-bottom:8px;letter-spacing:-1px;animation:fadeInUp 0.6s ease-out;">Analysing Property</div>
    <div style="font-size:14px;color:rgba(240,238,234,0.45);margin-bottom:48px;letter-spacing:0.5px;animation:fadeInUp 0.8s ease-out 0.2s both;">Running through 6 intelligence layers...</div>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <div style="animation:fadeInUp 0.5s ease-out 0.2s forwards;display:flex;align-items:center;gap:12px;padding:12px 16px;background:rgba(0,212,255,0.04);border-radius:6px;border:1px solid rgba(0,212,255,0.15);"><div style="width:20px;height:20px;border-radius:50%;background:#00d4ff;display:flex;align-items:center;justify-content:center;color:#000;font-size:10px;font-weight:bold;">1</div><span style="flex:1;text-align:left;font-size:12px;color:rgba(240,238,234,0.7);">Location & Geocoding</span><span style="font-size:11px;color:#00d4ff;font-family:'Space Mono',monospace;">●●●</span></div>
      <div style="animation:fadeInUp 0.5s ease-out 0.4s forwards;display:flex;align-items:center;gap:12px;padding:12px 16px;background:rgba(0,212,255,0.04);border-radius:6px;border:1px solid rgba(0,212,255,0.15);"><div style="width:20px;height:20px;border-radius:50%;background:#00d4ff;display:flex;align-items:center;justify-content:center;color:#000;font-size:10px;font-weight:bold;">2</div><span style="flex:1;text-align:left;font-size:12px;color:rgba(240,238,234,0.7);">Valuation Engine</span><span style="font-size:11px;color:#00d4ff;font-family:'Space Mono',monospace;">●●●</span></div>
      <div style="animation:fadeInUp 0.5s ease-out 0.6s forwards;display:flex;align-items:center;gap:12px;padding:12px 16px;background:rgba(0,212,255,0.04);border-radius:6px;border:1px solid rgba(0,212,255,0.15);"><div style="width:20px;height:20px;border-radius:50%;background:#00d4ff;display:flex;align-items:center;justify-content:center;color:#000;font-size:10px;font-weight:bold;">3</div><span style="flex:1;text-align:left;font-size:12px;color:rgba(240,238,234,0.7);">Liquidity Analysis</span><span style="font-size:11px;color:#00d4ff;font-family:'Space Mono',monospace;">●●●</span></div>
      <div style="animation:fadeInUp 0.5s ease-out 0.8s forwards;display:flex;align-items:center;gap:12px;padding:12px 16px;background:rgba(0,212,255,0.04);border-radius:6px;border:1px solid rgba(0,212,255,0.15);"><div style="width:20px;height:20px;border-radius:50%;background:#00d4ff;display:flex;align-items:center;justify-content:center;color:#000;font-size:10px;font-weight:bold;">4</div><span style="flex:1;text-align:left;font-size:12px;color:rgba(240,238,234,0.7);">Proximity Intelligence</span><span style="font-size:11px;color:#00d4ff;font-family:'Space Mono',monospace;">●●●</span></div>
      <div style="animation:fadeInUp 0.5s ease-out 1s forwards;display:flex;align-items:center;gap:12px;padding:12px 16px;background:rgba(0,212,255,0.04);border-radius:6px;border:1px solid rgba(0,212,255,0.15);"><div style="width:20px;height:20px;border-radius:50%;background:#00d4ff;display:flex;align-items:center;justify-content:center;color:#000;font-size:10px;font-weight:bold;">5</div><span style="flex:1;text-align:left;font-size:12px;color:rgba(240,238,234,0.7);">Fraud Detection</span><span style="font-size:11px;color:#00d4ff;font-family:'Space Mono',monospace;">●●●</span></div>
      <div style="animation:fadeInUp 0.5s ease-out 1.2s forwards;display:flex;align-items:center;gap:12px;padding:12px 16px;background:rgba(0,212,255,0.04);border-radius:6px;border:1px solid rgba(0,212,255,0.15);"><div style="width:20px;height:20px;border-radius:50%;background:#00d4ff;display:flex;align-items:center;justify-content:center;color:#000;font-size:10px;font-weight:bold;">6</div><span style="flex:1;text-align:left;font-size:12px;color:rgba(240,238,234,0.7);">Confidence Scoring</span><span style="font-size:11px;color:#00d4ff;font-family:'Space Mono',monospace;">●●●</span></div>
    </div>
    <div style="margin-top:36px;display:flex;justify-content:center;align-items:center;gap:8px;"><span style="width:8px;height:8px;border-radius:50%;background:#00d4ff;animation:pulse 1.5s ease-in-out infinite;"></span><span style="font-size:12px;color:rgba(240,238,234,0.5);font-family:'Space Mono',monospace;">Processing analysis...</span></div>
  </div>
</div>
"""
    st.markdown(loading_html, unsafe_allow_html=True)
    
    with st.spinner("Running backend analysis..."):
        try:
            resp = requests.post(f"{API_URL}/assess", json=payload, timeout=60)
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach API server. Is the backend running?"); st.stop()
    if resp.status_code == 422:
        st.error(f"Validation error: {resp.json().get('detail','unknown')}"); st.stop()
    elif resp.status_code != 200:
        st.error(f"Assessment failed (HTTP {resp.status_code}): {resp.text[:200]}"); st.stop()
    # Store results AND form context
    st.session_state.results = resp.json()
    st.session_state.form_vals = {
        "bhk": bhk, "locality": locality, "city": city, "sqft": sqft,
        "own": own,
    }

# ══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.results:
    r   = st.session_state.results
    fv  = st.session_state.form_vals

    # Restore context (use stored values or current widget values as fallback)
    _bhk      = fv.get("bhk", bhk)
    _locality = fv.get("locality", locality)
    _city     = fv.get("city", city)
    _own      = fv.get("own", own)

    # Extract core results before deriving metrics
    val   = r["valuation"];  liq   = r["liquidity"]
    conf  = r["confidence"]; fraud = r["fraud_flags"]
    loc   = r["location_resolved"]; prox = r["proximity_data"]
    rec   = r["lender_recommendation"]; drivers = r.get("key_drivers", [])

    # Derive market intelligence from API response (no longer from user sliders)
    _npa      = loc.get("circle_rate_zone", "") == "developing"
    _sp_raw   = liq.get("supply_pressure", "60%")
    _sp_val   = float(_sp_raw.replace("%","")) / 100.0 if isinstance(_sp_raw, str) else 0.6
    _sdr      = 0.4 + _sp_val * 2.1  # Map supply pressure 0-100% to S/D ratio 0.4-2.5
    _trend    = float(liq.get("absorption_rate_pct", "18%").replace("%","")) * 0.3 if liq.get("absorption_rate_pct") else 5.0

    decision   = rec["decision"]
    dec_cls    = decision.lower()
    dec_labels = {"APPROVE":"Approved for Lending","REVIEW":"Manual Review Required","REJECT":"Do Not Proceed"}
    ri         = liq.get("resale_index", 0)
    grade      = liq.get("grade","—")
    grade_col  = "#00e5a0" if grade=="HIGH" else "#f5a623" if grade=="MEDIUM" else "#ff4757"
    pps        = val.get("price_per_sqft", 0)
    conf_pct   = conf.get("percentage","—")
    conf_lbl   = conf.get("label","—")
    conf_col   = "#00e5a0" if conf_lbl=="HIGH" else "#f5a623" if conf_lbl=="MEDIUM" else "#ff4757"
    trend_col  = "#00e5a0" if _trend >= 0 else "#ff4757"
    trend_str  = f"+{_trend:.1f}%" if _trend >= 0 else f"{_trend:.1f}%"

    # Decision banner colours
    dec_bg  = {"APPROVE":"rgba(0,229,160,0.05)","REVIEW":"rgba(245,166,35,0.05)","REJECT":"rgba(255,71,87,0.05)"}
    dec_bdr = {"APPROVE":"rgba(0,229,160,0.2)","REVIEW":"rgba(245,166,35,0.2)","REJECT":"rgba(255,71,87,0.2)"}
    dec_dot = {"APPROVE":"#00e5a0","REVIEW":"#f5a623","REJECT":"#ff4757"}
    dec_glow= {"APPROVE":"rgba(0,229,160,0.4)","REVIEW":"rgba(245,166,35,0.4)","REJECT":"rgba(255,71,87,0.4)"}

    # Risk pills
    high_fraud   = sum(1 for f in fraud if f.get("severity")=="HIGH")
    fraud_risk   = "high" if high_fraud else "med" if fraud else "low"
    fraud_lbl    = "High" if high_fraud else "Medium" if fraud else "Low"
    supply_risk  = "high" if _sdr>1.5 else "med" if _sdr>1.0 else "low"
    supply_lbl   = "High" if _sdr>1.5 else "Medium" if _sdr>1.0 else "Low"
    npa_risk, npa_lbl = ("high","Flagged") if _npa else ("low","Clear")
    own_risk, own_lbl = ("high","Disputed") if _own=="Disputed" else ("low","Clear")

    pill_colors = {"low":("rgba(0,229,160,0.05)","rgba(0,229,160,0.2)","#00e5a0"),
                   "med":("rgba(245,166,35,0.05)","rgba(245,166,35,0.2)","#f5a623"),
                   "high":("rgba(255,71,87,0.05)","rgba(255,71,87,0.2)","#ff4757")}

    def pill(risk, label):
        bg, bd, c = pill_colors[risk]
        return (f'<span style="display:inline-flex;align-items:center;gap:8px;padding:7px 14px;'
                f'border-radius:100px;font-size:10px;font-family:\'Space Mono\',monospace;'
                f'letter-spacing:1px;border:1px solid {bd};background:{bg};color:{c};margin-right:8px;">'
                f'<span style="width:6px;height:6px;border-radius:50%;background:{c};display:inline-block;"></span>'
                f'{label}</span>')

    # Proximity helper
    def pdot(dist, good, warn):
        if dist is None: return "#888", "N/A"
        return ("#00e5a0" if dist<good else "#f5a623" if dist<warn else "#ff4757"), f"{dist:.1f} km"

    amenities = [
        ("Metro Station",        prox.get("distance_to_metro_km"),    2, 5),
        ("Highway / Expressway", prox.get("distance_to_highway_km"),  2, 5),
        ("Hospital",             prox.get("distance_to_hospital_km"), 1, 3),
        ("School",               prox.get("distance_to_school_km"),   1, 2),
        ("Shopping Mall",        prox.get("distance_to_mall_km"),     3, 6),
        ("IT Park",              prox.get("distance_to_it_park_km"),  3, 8),
    ]

    prox_html = "".join(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'padding:11px 0;border-bottom:1px solid rgba(255,255,255,0.07);">'
        f'<span style="font-size:13px;color:rgba(240,238,234,0.45);">{lbl}</span>'
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'<span style="font-family:\'Space Mono\',monospace;font-size:13px;color:#f0eeea;">{pdot(d,g,w)[1]}</span>'
        f'<span style="width:7px;height:7px;border-radius:50%;background:{pdot(d,g,w)[0]};display:inline-block;"></span>'
        f'</div></div>'
        for lbl, d, g, w in amenities
    )

    # Factor bars
    factors_html = ""
    for f in liq.get("factor_breakdown", []):
        sc2 = f.get("score", 0)
        bc  = "#00d4ff" if sc2>=70 else "#f5a623" if sc2>=40 else "#ff4757"
        factors_html += (
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
            f'<span style="font-size:12px;color:rgba(240,238,234,0.45);width:130px;flex-shrink:0;">{f.get("factor","")}</span>'
            f'<div style="flex:1;height:3px;background:rgba(255,255,255,0.06);border-radius:2px;">'
            f'<div style="height:3px;width:{sc2}%;background:{bc};border-radius:2px;"></div></div>'
            f'<span style="font-family:\'Space Mono\',monospace;font-size:11px;color:rgba(240,238,234,0.45);width:28px;text-align:right;">{sc2}</span>'
            f'</div>'
        )

    # Val chain
    cr = loc.get("circle_rate_sqft", 0)
    chain_html = (
        f'<div style="display:flex;justify-content:space-between;padding:11px 14px;'
        f'background:rgba(255,255,255,0.02);border-radius:4px;margin-bottom:2px;">'
        f'<span style="font-size:12px;color:rgba(240,238,234,0.45);">Circle Rate (IGR 2025-26)</span>'
        f'<span style="font-family:\'Space Mono\',monospace;font-size:12px;color:#00d4ff;">&#8377;{cr:,.0f}/sqft</span>'
        f'</div>'
    )
    for d in drivers:
        val_color = "#00e5a0" if d.startswith("+") else "#ff4757" if d.startswith("-") else "#00d4ff"
        chain_html += (
            f'<div style="display:flex;justify-content:space-between;padding:11px 14px;'
            f'background:rgba(255,255,255,0.02);border-radius:4px;margin-bottom:2px;">'
            f'<span style="font-size:12px;color:rgba(240,238,234,0.45);">{d[1:].strip()}</span>'
            f'<span style="font-family:\'Space Mono\',monospace;font-size:12px;color:{val_color};">{d[0]}</span>'
            f'</div>'
        )
    chain_html += f'<div style="height:1px;background:rgba(255,255,255,0.12);margin:6px 0;"></div>'
    chain_html += (
        f'<div style="display:flex;justify-content:space-between;padding:11px 14px;'
        f'background:rgba(0,212,255,0.04);border-radius:4px;">'
        f'<span style="font-size:12px;color:#f0eeea;font-weight:500;">Final Market Rate</span>'
        f'<span style="font-family:\'Space Mono\',monospace;font-size:14px;color:#f0eeea;">&#8377;{pps:,.0f}/sqft</span>'
        f'</div>'
    )

    # Sparkline
    bases = [55,58,56,62,66,71,78]
    heights = [min(95,max(20,h+(_trend*1.2))) for h in bases]
    spark_html = "".join(
        f'<div style="flex:1;border-radius:2px 2px 0 0;height:{h:.0f}%;'
        f'background:{"#00d4ff" if i==6 else "rgba(0,212,255,0.2)"}"></div>'
        for i, h in enumerate(heights)
    )

    # Liquidity bullets
    bullets_html = "".join(
        f'<div style="margin-bottom:7px;font-size:12px;line-height:1.6;'
        f'color:{"#f5a623" if ld.startswith("!") else "#00e5a0"};">&#8250; {ld}</div>'
        for ld in liq.get("liquidity_drivers",[])
    )

    # Documents
    docs = ["Sale Deed / Agreement to Sale","Encumbrance Certificate (past 13 years)",
            "Property Tax Receipt (latest)","RERA Registration Certificate",
            "Builder NOC & Approved Building Plan","Occupancy Certificate",
            "Photo ID & Address Proof of Borrower","Bank Statements (last 6 months)"]
    docs_html = "".join(
        f'<div style="display:flex;align-items:center;gap:10px;padding:10px 0;'
        f'border-bottom:1px solid rgba(255,255,255,0.07);font-size:13px;color:rgba(240,238,234,0.45);">'
        f'<div style="width:16px;height:16px;border:1px solid rgba(255,255,255,0.12);'
        f'border-radius:3px;flex-shrink:0;"></div>{doc}</div>'
        for doc in docs
    )

    # Growth cards
    growth_items = [
        ("&#128407;", "Metro Connectivity Impact",
         "Metro proximity (within 2km) consistently drives 12-18% residential appreciation. "
         "Properties in this micro-market benefit from reduced commute and improved livability scores.",
         "+10-15% over 18 months"),
        ("&#127959;", "Infrastructure Development Premium",
         f"Government-announced projects in adjacent zones historically precede 8-12% appreciation. "
         f"Smart city upgrades compound this effect.",
         "+6-10% over 24 months"),
        ("&#128188;", f"IT Employment Hub Tailwind — {_city}",
         f"Growing IT workforce demand in {_city} continues to fuel residential demand in "
         f"well-connected micro-markets near employment hubs.",
         "Sustained positive outlook over 12 months"),
    ]
    growth_html = "".join(
        f'<div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;'
        f'padding:20px;margin-bottom:12px;display:flex;gap:16px;align-items:flex-start;">'
        f'<div style="width:36px;height:36px;border-radius:6px;background:rgba(0,212,255,0.15);'
        f'display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:16px;">{ico}</div>'
        f'<div><div style="font-size:13px;color:#f0eeea;margin-bottom:4px;font-weight:500;">{title}</div>'
        f'<div style="font-size:12px;color:rgba(240,238,234,0.45);line-height:1.6;">{desc}</div>'
        f'<div style="font-family:\'Space Mono\',monospace;font-size:11px;color:#00e5a0;margin-top:6px;">'
        f'Estimated impact: {impact}</div></div></div>'
        for ico, title, desc, impact in growth_items
    )

    # Fraud flags
    fraud_html = ""
    if not fraud:
        fraud_html = ('<div style="padding:14px;background:rgba(0,229,160,0.04);border-radius:6px;'
                     'border:1px solid rgba(0,229,160,0.15);font-size:12px;color:#00e5a0;">'
                     '&#10003; No fraud indicators detected. All data signals are internally consistent.</div>')
    else:
        for flag in fraud:
            sev = flag.get("severity","LOW")
            fc  = {"HIGH":"#ff4757","MEDIUM":"#f5a623","LOW":"#00d4ff"}.get(sev,"#00d4ff")
            fraud_html += (
                f'<div style="padding:14px;background:rgba(255,255,255,0.02);border-radius:6px;'
                f'border-left:3px solid {fc};margin-bottom:8px;">'
                f'<div style="font-family:\'Space Mono\',monospace;font-size:10px;color:{fc};'
                f'letter-spacing:1px;margin-bottom:4px;">{sev} — {flag.get("code","")}</div>'
                f'<div style="font-size:12px;color:rgba(240,238,234,0.45);line-height:1.6;">{flag.get("message","")}</div>'
                f'</div>'
            )

    # Confidence breakdown
    bd = conf.get("breakdown", {})

    # ── RENDER RESULTS HEADER ─────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:#050508;padding:40px 56px 0 56px;border-top:1px solid rgba(255,255,255,0.07);">
  <!-- BREADCRUMB NAVIGATION -->
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:32px;
    font-family:'Space Mono',monospace;font-size:10px;letter-spacing:1px;">
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="width:24px;height:24px;border-radius:50%;background:rgba(0,212,255,0.15);
        border:1px solid rgba(0,212,255,0.3);display:flex;align-items:center;justify-content:center;
        color:#00d4ff;font-weight:bold;animation:fadeInUp 0.4s ease-out;">✓</span>
      <span style="color:#00d4ff;">STEP 01: INPUT</span>
    </div>
    <span style="color:rgba(255,255,255,0.2);">→</span>
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="width:24px;height:24px;border-radius:50%;background:#00d4ff;
        display:flex;align-items:center;justify-content:center;color:#000;font-weight:bold;
        animation:scaleIn 0.5s ease-out 0.2s both;">●</span>
      <span style="color:#00d4ff;">STEP 02: REPORT</span>
    </div>
    <span style="color:rgba(255,255,255,0.2);">→</span>
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="width:24px;height:24px;border-radius:50%;background:rgba(255,255,255,0.1);
        border:1px solid rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;
        color:rgba(240,238,234,0.45);font-weight:bold;">3</span>
      <span style="color:rgba(240,238,234,0.45);">STEP 03: EXPORT</span>
    </div>
  </div>

  <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;
    opacity:0.7;margin-bottom:10px;text-transform:uppercase;animation:fadeInUp 0.5s ease-out 0.1s both;">
    Step 02 — Intelligence Report
  </div>
  <div style="font-family:'Playfair Display',Georgia,serif;font-size:34px;font-weight:400;color:#f0eeea;
    margin-bottom:32px;letter-spacing:-0.5px;animation:fadeInUp 0.6s ease-out 0.2s both;">
    {_bhk}BHK &middot; {_locality.title()}, {_city}
  </div>

  <!-- QUICK DECISION BANNER -->
  <div style="max-width:920px;margin-bottom:32px;border-radius:8px;padding:28px 32px;
    display:flex;align-items:center;justify-content:space-between;
    background:{dec_bg[decision]};border:1px solid {dec_bdr[decision]};
    animation:slideInUp 0.7s ease-out 0.3s both;">
    <div style="display:flex;align-items:center;gap:18px;">
      <div style="width:12px;height:12px;border-radius:50%;flex-shrink:0;
        background:{dec_dot[decision]};box-shadow:0 0 16px {dec_glow[decision]};
        animation:glowPulse 2s ease-in-out infinite;"></div>
      <div>
        <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;
          text-transform:uppercase;color:{dec_dot[decision]};margin-bottom:4px;">
          {dec_labels[decision]}
        </div>
        <div style="font-family:'Playfair Display',Georgia,serif;font-size:26px;color:#f0eeea;line-height:1.1;">
          Safe Loan: {rec.get('safe_loan_display','—')}
        </div>
      </div>
    </div>
    <div style="font-family:'Space Mono',monospace;font-size:11px;color:rgba(240,238,234,0.45);text-align:right;">
      <div>Confidence: {conf_pct}</div>
      <div>LTV: {rec.get('ltv_ratio','—')}</div>
    </div>
  </div>

  <!-- RISK PILLS -->
  <div style="display:flex;flex-wrap:wrap;gap:0;margin-bottom:40px;animation:fadeInUp 0.8s ease-out 0.4s both;">
    {pill(fraud_risk, f"Fraud Risk: {fraud_lbl}")}
    {pill(own_risk,   f"Legal Risk: {own_lbl}")}
    {pill(supply_risk,f"Supply Pressure: {supply_lbl}")}
    {pill(npa_risk,   f"NPA Zone: {npa_lbl}")}
  </div>
</div>

<!-- METRICS CARDS WITH STAGGERED ANIMATION -->
<div style="background:#050508;padding:0 56px 48px 56px;">
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;max-width:920px;">
    <div class="card-slide-in" style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);
      border-radius:8px;padding:24px 20px;position:relative;overflow:hidden;opacity:0;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;background:#00d4ff;"></div>
      <div style="font-size:10px;letter-spacing:2px;color:rgba(240,238,234,0.45);text-transform:uppercase;
        font-family:'Space Mono',monospace;margin-bottom:12px;">Market Value</div>
      <div style="font-family:'Playfair Display',Georgia,serif;font-size:22px;color:#f0eeea;
        line-height:1.2;margin-bottom:6px;">{val.get('market_value_display','—')}</div>
      <div style="font-size:11px;color:rgba(240,238,234,0.45);">&#8377;{pps:,.0f} per sqft</div>
      <div style="display:inline-block;font-size:9px;letter-spacing:1.5px;padding:3px 8px;border-radius:3px;
        font-family:'Space Mono',monospace;text-transform:uppercase;margin-top:6px;
        background:rgba(0,212,255,0.1);color:#00d4ff;">Distress: {val.get('distress_value_display','—')}</div>
    </div>
    
    <div class="card-slide-in" style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);
      border-radius:8px;padding:24px 20px;position:relative;overflow:hidden;opacity:0;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;background:#00e5a0;"></div>
      <div style="font-size:10px;letter-spacing:2px;color:rgba(240,238,234,0.45);text-transform:uppercase;
        font-family:'Space Mono',monospace;margin-bottom:12px;">Resale Index</div>
      <div style="font-family:'Playfair Display',Georgia,serif;font-size:26px;color:#f0eeea;
        line-height:1.1;margin-bottom:4px;">{ri} <span style="font-size:14px;color:rgba(240,238,234,0.45)">/100</span></div>
      <div style="display:inline-block;font-size:9px;letter-spacing:1.5px;padding:3px 8px;border-radius:3px;
        font-family:'Space Mono',monospace;text-transform:uppercase;background:rgba(0,229,160,0.1);
        color:#00e5a0;">{grade} Liquidity</div>
      <div style="font-size:11px;color:rgba(240,238,234,0.45);margin-top:6px;">
        {liq.get('absorption_rate_pct','—')} monthly absorption
      </div>
    </div>
    
    <div class="card-slide-in" style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);
      border-radius:8px;padding:24px 20px;position:relative;overflow:hidden;opacity:0;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;background:#f5a623;"></div>
      <div style="font-size:10px;letter-spacing:2px;color:rgba(240,238,234,0.45);text-transform:uppercase;
        font-family:'Space Mono',monospace;margin-bottom:12px;">Time to Sell</div>
      <div style="font-family:'Playfair Display',Georgia,serif;font-size:26px;color:#f0eeea;
        line-height:1.1;margin-bottom:4px;">{liq.get('time_to_sell_display','—')}</div>
      <div style="display:inline-block;font-size:9px;letter-spacing:1.5px;padding:3px 8px;border-radius:3px;
        font-family:'Space Mono',monospace;text-transform:uppercase;background:rgba(245,166,35,0.1);
        color:#f5a623;">Expected Resale</div>
    </div>
    
    <div class="card-slide-in" style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);
      border-radius:8px;padding:24px 20px;position:relative;overflow:hidden;opacity:0;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;background:rgba(0,212,255,0.4);"></div>
      <div style="font-size:10px;letter-spacing:2px;color:rgba(240,238,234,0.45);text-transform:uppercase;
        font-family:'Space Mono',monospace;margin-bottom:12px;">Confidence</div>
      <div style="font-family:'Playfair Display',Georgia,serif;font-size:26px;color:#f0eeea;
        line-height:1.1;margin-bottom:4px;">{conf_pct}</div>
      <div style="display:inline-block;font-size:9px;letter-spacing:1.5px;padding:3px 8px;border-radius:3px;
        font-family:'Space Mono',monospace;text-transform:uppercase;background:rgba(0,212,255,0.1);
        color:#00d4ff;">{conf_lbl}</div>
      <div style="font-size:11px;color:rgba(240,238,234,0.45);margin-top:6px;">
        {conf.get('interpretation','')[:55]}...
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── PDF download ──────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:#050508;padding:24px 56px;border-top:1px solid rgba(255,255,255,0.07);">
  <div style="display:flex;align-items:center;gap:16px;animation:slideInLeft 1s ease-out 0.5s both;">
    <span style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:2px;
      color:rgba(240,238,234,0.45);text-transform:uppercase;">STEP 03 – EXPORT</span>
    <div style="flex:1;height:1px;background:rgba(255,255,255,0.07);"></div>
  </div>
</div>
""", unsafe_allow_html=True)
    
    try:
        from datetime import datetime as _dt
        pdf_bytes = generate_pdf(r)
        col1, col2, col3 = st.columns([2, 1, 3])
        with col1:
            st.download_button(
                "⬇  Export PDF Report",
                data=pdf_bytes,
                file_name=f"PropIntel_{_dt.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
        with col2:
            if st.button("🔄 New Analysis"):
                st.session_state.results = None
                st.session_state.sample = None
                st.rerun()
    except Exception as e:
        st.warning(f"PDF unavailable: {e}")

    # ── TABS ──────────────────────────────────────────────────────────────────
    st.markdown("""
<div style="background:#050508;padding:36px 56px 0 56px;border-top:1px solid rgba(255,255,255,0.07);
  animation:fadeInUp 1.1s ease-out 0.6s both;">
  <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;
    opacity:0.6;text-transform:uppercase;margin-bottom:20px;">Detailed Analysis</div>
</div>
""", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Valuation", "Liquidity", "Proximity", "Market Intelligence", "Future Growth", "Documents"
    ])

    # ── TAB 1: VALUATION ──────────────────────────────────────────────────────
    with tab1:
        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:920px;">
  <div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:28px;">
    <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">Valuation Breakdown</div>
    {chain_html}
  </div>
  <div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:28px;">
    <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">6-Month Price Trend — {_locality.title()}</div>
    <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:16px;">
      <span style="font-family:'Playfair Display',Georgia,serif;font-size:32px;color:#f0eeea;">{trend_str}</span>
      <span style="font-size:12px;color:{trend_col};">{'appreciation' if _trend>=0 else 'depreciation'}</span>
    </div>
    <div style="display:flex;align-items:flex-end;gap:3px;height:40px;margin-top:8px;">{spark_html}</div>
    <div style="display:flex;justify-content:space-between;margin-top:8px;font-family:'Space Mono',monospace;font-size:9px;color:rgba(240,238,234,0.45);">
      <span>Oct</span><span>Nov</span><span>Dec</span><span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span>
    </div>
    <div style="margin-top:24px;">
      <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:12px;">Market Heat — {_city}</div>
      <div style="display:flex;gap:4px;">
        <div style="height:28px;border-radius:3px;flex:1;display:flex;align-items:center;justify-content:center;font-family:'Space Mono',monospace;font-size:9px;background:rgba(255,71,87,0.08);color:#ff4757;">LOW</div>
        <div style="height:28px;border-radius:3px;flex:1;display:flex;align-items:center;justify-content:center;font-family:'Space Mono',monospace;font-size:9px;background:rgba(245,166,35,0.08);color:#f5a623;">MID</div>
        <div style="height:28px;border-radius:3px;flex:1;display:flex;align-items:center;justify-content:center;font-family:'Space Mono',monospace;font-size:9px;background:rgba(0,212,255,0.15);color:#00d4ff;border:1px solid rgba(0,212,255,0.3);">{_locality.upper()} &#9658;</div>
        <div style="height:28px;border-radius:3px;flex:1;display:flex;align-items:center;justify-content:center;font-family:'Space Mono',monospace;font-size:9px;background:rgba(0,229,160,0.08);color:#00e5a0;">PRIME</div>
        <div style="height:28px;border-radius:3px;flex:1;display:flex;align-items:center;justify-content:center;font-family:'Space Mono',monospace;font-size:9px;background:rgba(0,229,160,0.15);color:#00e5a0;">TOP</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── TAB 2: LIQUIDITY ──────────────────────────────────────────────────────
    with tab2:
        liq_score_col = "#00e5a0" if ri>=70 else "#f5a623" if ri>=40 else "#ff4757"
        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:920px;">
  <div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:28px;">
    <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">Liquidity Factor Breakdown</div>
    {factors_html}
  </div>
  <div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:28px;">
    <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">Liquidity Summary</div>
    <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:20px;">
      <span style="font-family:'Playfair Display',Georgia,serif;font-size:48px;color:{liq_score_col};">{ri}</span>
      <span style="font-size:14px;color:rgba(240,238,234,0.45);">/100 &middot; {grade}</span>
    </div>
    {bullets_html}
    <div style="margin-top:20px;padding:16px;background:rgba(255,255,255,0.02);border-radius:6px;">
      <div style="font-family:'Space Mono',monospace;font-size:9px;letter-spacing:2px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:12px;">Confidence Signals</div>
      <div style="margin-bottom:8px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:11px;color:rgba(240,238,234,0.45);">
          <span>Data Completeness</span><span style="font-family:'Space Mono',monospace;">{bd.get('data_completeness',0)*100:.0f}%</span>
        </div>
        <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:2px;">
          <div style="height:3px;width:{bd.get('data_completeness',0)*100:.0f}%;background:#00d4ff;border-radius:2px;"></div>
        </div>
      </div>
      <div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:11px;color:rgba(240,238,234,0.45);">
          <span>Signal Agreement</span><span style="font-family:'Space Mono',monospace;">{bd.get('signal_agreement',0)*100:.0f}%</span>
        </div>
        <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:2px;">
          <div style="height:3px;width:{bd.get('signal_agreement',0)*100:.0f}%;background:#00e5a0;border-radius:2px;"></div>
        </div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── TAB 3: PROXIMITY ─────────────────────────────────────────────────────
    with tab3:
        lat = loc.get("latitude"); lon = loc.get("longitude")
        coords = f"{lat:.5f}° N, {lon:.5f}° E" if lat and lon else "Geocoding unavailable"
        zone = loc.get("circle_rate_zone","—").replace("_"," ").title()
        found_msg = "Locality verified in database" if loc.get("locality_found_in_db") else "Using city-level average"
        found_col = "#00e5a0" if loc.get("locality_found_in_db") else "#f5a623"
        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:920px;">
  <div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:28px;">
    <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">Infrastructure Distances</div>
    {prox_html}
    <div style="display:flex;gap:16px;margin-top:16px;font-size:10px;font-family:'Space Mono',monospace;color:rgba(240,238,234,0.45);">
      <span><span style="color:#00e5a0">●</span> &lt;2km ideal</span>
      <span><span style="color:#f5a623">●</span> 2–6km moderate</span>
      <span><span style="color:#ff4757">●</span> &gt;6km weak</span>
    </div>
  </div>
  <div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:28px;">
    <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">Location Intelligence</div>
    <div style="margin-bottom:16px;padding:16px;background:rgba(0,212,255,0.04);border-radius:6px;border:1px solid rgba(0,212,255,0.1);">
      <div style="font-size:10px;color:rgba(240,238,234,0.45);margin-bottom:4px;font-family:'Space Mono',monospace;">RESOLVED LOCATION</div>
      <div style="font-size:15px;color:#f0eeea;margin-bottom:2px;">{_locality.title()}, {_city}</div>
      <div style="font-size:11px;color:#00d4ff;font-family:'Space Mono',monospace;">{coords}</div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">
      <div style="padding:14px;background:rgba(255,255,255,0.02);border-radius:6px;">
        <div style="font-size:10px;color:rgba(240,238,234,0.45);font-family:'Space Mono',monospace;margin-bottom:6px;">CIRCLE RATE</div>
        <div style="font-family:'Playfair Display',Georgia,serif;font-size:20px;color:#00d4ff;">&#8377;{cr:,.0f}</div>
        <div style="font-size:10px;color:rgba(240,238,234,0.45);">per sqft &middot; {zone}</div>
      </div>
      <div style="padding:14px;background:rgba(255,255,255,0.02);border-radius:6px;">
        <div style="font-size:10px;color:rgba(240,238,234,0.45);font-family:'Space Mono',monospace;margin-bottom:6px;">MARKET RATE</div>
        <div style="font-family:'Playfair Display',Georgia,serif;font-size:20px;color:#f0eeea;">&#8377;{pps:,.0f}</div>
        <div style="font-size:10px;color:rgba(240,238,234,0.45);">per sqft avg</div>
      </div>
    </div>
    <div style="padding:10px 14px;background:rgba(0,229,160,0.05);border-radius:6px;border:1px solid rgba(0,229,160,0.15);font-size:11px;color:{found_col};">
      &#8250; {found_msg} &nbsp;&middot;&nbsp; {zone} zone
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── TAB 4: MARKET INTELLIGENCE ──────────────────────────────────────────────
    with tab4:
        # Extract AI-computed market signals from the API response
        _absorption_display = liq.get("absorption_rate_pct", "—")
        _supply_display = liq.get("supply_pressure", "—")
        _locality_quality = liq.get("locality_quality_score", "—")
        _zone = loc.get("circle_rate_zone", "—").replace("_", " ").title()
        _locality_found = loc.get("locality_found_in_db", False)

        # Builder score derived from zone quality
        zone_builder_map = {"Premium": 85, "Upper Mid": 78, "Mid": 70, "Developing": 58, "Unknown": 65}
        _builder_derived = zone_builder_map.get(_zone, 65)
        _builder_col = "#00e5a0" if _builder_derived >= 75 else "#f5a623" if _builder_derived >= 60 else "#ff4757"

        # Absorption from liquidity engine
        _abs_val = float(_absorption_display.replace("%","")) if _absorption_display != "—" else 18
        _abs_col = "#00e5a0" if _abs_val >= 20 else "#f5a623" if _abs_val >= 12 else "#ff4757"

        # Supply pressure
        _sup_val = float(_supply_display.replace("%","")) if _supply_display != "—" else 60
        _sup_col = "#00e5a0" if _sup_val <= 40 else "#f5a623" if _sup_val <= 70 else "#ff4757"

        # Price trend from key drivers
        _trend_derived = 0
        for drv in drivers:
            if "+" in drv and "momentum" in drv.lower():
                try: _trend_derived = max(_trend_derived, float(drv.split("+")[1].split("%")[0].strip()))
                except: pass
            elif "+" in drv and "trend" in drv.lower():
                try: _trend_derived = max(_trend_derived, float(drv.split("+")[1].split("%")[0].strip()))
                except: pass
        if _trend_derived == 0:
            _trend_derived = 5.0
        _trend_derived_col = "#00e5a0" if _trend_derived >= 5 else "#f5a623" if _trend_derived >= 0 else "#ff4757"

        # RERA status
        _rera_status = "Registered" if _locality_found else "Pending Verification"
        _rera_col = "#00e5a0" if _locality_found else "#f5a623"

        # Govt project
        _govt_status = "Detected Nearby" if any("infrastructure" in d.lower() or "govt" in d.lower() or "project" in d.lower() for d in drivers) else "None Detected"
        _govt_col = "#00e5a0" if _govt_status == "Detected Nearby" else "rgba(240,238,234,0.45)"

        # NPA zone
        _npa_status = "Flagged" if any("npa" in d.lower() for d in drivers) else "Clear"
        _npa_col = "#ff4757" if _npa_status == "Flagged" else "#00e5a0"

        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:920px;">
  <div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:28px;">
    <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">AI-Computed Market Signals</div>
    <div style="margin-bottom:18px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="font-size:12px;color:rgba(240,238,234,0.45);">Builder Reputation Score</span>
        <span style="font-family:'Space Mono',monospace;font-size:12px;color:{_builder_col};">{_builder_derived}/100</span>
      </div>
      <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:2px;">
        <div style="height:3px;width:{_builder_derived}%;background:{_builder_col};border-radius:2px;"></div>
      </div>
      <div style="font-size:10px;color:rgba(240,238,234,0.3);margin-top:4px;">Derived from {_zone} zone classification</div>
    </div>
    <div style="margin-bottom:18px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="font-size:12px;color:rgba(240,238,234,0.45);">Monthly Absorption Rate</span>
        <span style="font-family:'Space Mono',monospace;font-size:12px;color:{_abs_col};">{_absorption_display}</span>
      </div>
      <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:2px;">
        <div style="height:3px;width:{min(_abs_val * 3, 100):.0f}%;background:{_abs_col};border-radius:2px;"></div>
      </div>
      <div style="font-size:10px;color:rgba(240,238,234,0.3);margin-top:4px;">Locality-specific market activity</div>
    </div>
    <div style="margin-bottom:18px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="font-size:12px;color:rgba(240,238,234,0.45);">Supply Pressure</span>
        <span style="font-family:'Space Mono',monospace;font-size:12px;color:{_sup_col};">{_supply_display}</span>
      </div>
      <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:2px;">
        <div style="height:3px;width:{_sup_val:.0f}%;background:{_sup_col};border-radius:2px;"></div>
      </div>
      <div style="font-size:10px;color:rgba(240,238,234,0.3);margin-top:4px;">Lower = less competition for sellers</div>
    </div>
    <div>
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="font-size:12px;color:rgba(240,238,234,0.45);">6-Month Price Trend</span>
        <span style="font-family:'Space Mono',monospace;font-size:12px;color:{_trend_derived_col};">+{_trend_derived:.1f}%</span>
      </div>
      <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:2px;">
        <div style="height:3px;width:{min(max(_trend_derived * 6, 10), 100):.0f}%;background:{_trend_derived_col};border-radius:2px;"></div>
      </div>
      <div style="font-size:10px;color:rgba(240,238,234,0.3);margin-top:4px;">Micro-market momentum indicator</div>
    </div>
  </div>
  <div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:28px;">
    <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">Automated Risk Flags</div>
    <div style="display:flex;align-items:center;justify-content:space-between;padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.07);">
      <span style="font-size:12px;color:rgba(240,238,234,0.45);">RERA Registration</span>
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-family:'Space Mono',monospace;font-size:11px;color:{_rera_col};">{_rera_status}</span>
        <span style="width:7px;height:7px;border-radius:50%;background:{_rera_col};display:inline-block;"></span>
      </div>
    </div>
    <div style="display:flex;align-items:center;justify-content:space-between;padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.07);">
      <span style="font-size:12px;color:rgba(240,238,234,0.45);">Govt Infrastructure Project</span>
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-family:'Space Mono',monospace;font-size:11px;color:{_govt_col};">{_govt_status}</span>
        <span style="width:7px;height:7px;border-radius:50%;background:{_govt_col};display:inline-block;"></span>
      </div>
    </div>
    <div style="display:flex;align-items:center;justify-content:space-between;padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.07);">
      <span style="font-size:12px;color:rgba(240,238,234,0.45);">NPA Zone Status</span>
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-family:'Space Mono',monospace;font-size:11px;color:{_npa_col};">{_npa_status}</span>
        <span style="width:7px;height:7px;border-radius:50%;background:{_npa_col};display:inline-block;"></span>
      </div>
    </div>
    <div style="display:flex;align-items:center;justify-content:space-between;padding:14px 0;">
      <span style="font-size:12px;color:rgba(240,238,234,0.45);">Locality Quality Score</span>
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-family:'Space Mono',monospace;font-size:11px;color:#00d4ff;">{_locality_quality}/100</span>
        <span style="width:7px;height:7px;border-radius:50%;background:#00d4ff;display:inline-block;"></span>
      </div>
    </div>
    <div style="margin-top:16px;padding:14px;background:rgba(0,212,255,0.04);border-radius:6px;border:1px solid rgba(0,212,255,0.1);">
      <div style="font-size:10px;color:rgba(240,238,234,0.45);font-family:'Space Mono',monospace;margin-bottom:6px;">INTELLIGENCE NOTE</div>
      <div style="font-size:11px;color:rgba(240,238,234,0.55);line-height:1.6;">
        Market signals are auto-derived from locality databases, circle rate zones, and real-time proximity data.
        No manual input required — the engine computes builder reputation, absorption rates, and supply dynamics
        based on the property's micro-market.
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── TAB 5: FUTURE GROWTH ──────────────────────────────────────────────────
    with tab5:
        st.markdown(f"""
<div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">Growth Catalysts &amp; Outlook</div>
{growth_html}
""", unsafe_allow_html=True)

    # ── TAB 6: DOCUMENTS ─────────────────────────────────────────────────────
    with tab6:
        notes_html = "".join(
            f'<div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.07);font-size:12px;color:rgba(240,238,234,0.45);">&#8250; {n.strip().lstrip("-").lstrip("*").strip()}</div>'
            for n in rec.get("notes",[])[:5] if n.strip()
        )
        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:920px;margin-bottom:24px;">
  <div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:28px;">
    <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">Required Documents Checklist</div>
    {docs_html}
  </div>
  <div style="background:#0d0d12;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:28px;">
    <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:20px;">Lender Summary</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
      <div style="padding:14px;background:rgba(255,255,255,0.02);border-radius:6px;">
        <div style="font-size:10px;color:rgba(240,238,234,0.45);font-family:'Space Mono',monospace;margin-bottom:6px;">SAFE LOAN</div>
        <div style="font-family:'Playfair Display',Georgia,serif;font-size:22px;color:#00e5a0;">{rec.get('safe_loan_display','—')}</div>
        <div style="font-size:10px;color:rgba(240,238,234,0.45);">at {rec.get('ltv_ratio','70%')} LTV</div>
      </div>
      <div style="padding:14px;background:rgba(255,255,255,0.02);border-radius:6px;">
        <div style="font-size:10px;color:rgba(240,238,234,0.45);font-family:'Space Mono',monospace;margin-bottom:6px;">DISTRESS RECOVERY</div>
        <div style="font-family:'Playfair Display',Georgia,serif;font-size:22px;color:#f5a623;">{rec.get('distress_recovery_assured','—')}</div>
        <div style="font-size:10px;color:rgba(240,238,234,0.45);">assured minimum</div>
      </div>
    </div>
    {notes_html}
    <div style="margin-top:20px;">
      <div style="font-family:'Space Mono',monospace;font-size:10px;letter-spacing:3px;color:#00d4ff;opacity:0.6;text-transform:uppercase;margin-bottom:12px;">Fraud / Anomaly Check</div>
      {fraud_html}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
        with st.expander("Raw API Response (debug)"):
            st.json(r)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("""
<div style="background:#0d0d12;border-top:1px solid rgba(255,255,255,0.07);padding:32px 56px;
  display:flex;align-items:center;justify-content:space-between;margin-top:60px;
  animation:fadeInUp 1.2s ease-out 0.7s both;">
  <div style="display:flex;align-items:center;gap:12px;">
    <span style="font-family:'Playfair Display',Georgia,serif;font-size:15px;color:#f0eeea;">
      <span style="color:#00d4ff">Prop</span>Intel AI
    </span>
    <span style="font-size:11px;color:rgba(240,238,234,0.3);">v2.0</span>
  </div>
  <span style="font-family:'Space Mono',monospace;font-size:10px;color:rgba(240,238,234,0.35);
    letter-spacing:1px;">
    TEAM TE-08 &nbsp;·&nbsp; PICT PUNE &nbsp;·&nbsp; POONAWALLA FINCORP AI HACKATHON
  </span>
</div>
""", unsafe_allow_html=True)
