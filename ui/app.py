"""
PropIntel AI - Streamlit Frontend
Complete UI for property collateral valuation system
"""

import streamlit as st
import requests
import json

# ══════════════════════════════════════
# PAGE CONFIG & CSS
# ══════════════════════════════════════

st.set_page_config(
    page_title="PropIntel AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }
.main .block-container { padding-top: 1.5rem; max-width: 1200px; }

.card {
    background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 1.2rem; margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.banner-approve {
    background: linear-gradient(135deg, #059669, #10B981); color: white;
    padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
}
.banner-review {
    background: linear-gradient(135deg, #D97706, #F59E0B); color: white;
    padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
}
.banner-reject {
    background: linear-gradient(135deg, #DC2626, #EF4444); color: white;
    padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
}
.banner-approve h2, .banner-review h2, .banner-reject h2 {
    margin: 0; font-size: 1.6rem; font-weight: 800;
}
.banner-approve p, .banner-review p, .banner-reject p {
    margin: 0.3rem 0 0 0; font-size: 1rem; opacity: 0.95;
}
.zone-premium { background: #F59E0B; color: #000; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.zone-upper_mid { background: #3B82F6; color: #fff; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.zone-mid { background: #10B981; color: #fff; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.zone-developing { background: #9CA3AF; color: #fff; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.zone-default { background: #6B7280; color: #fff; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }

.severity-high { color: #EF4444; font-weight: 700; }
.severity-medium { color: #F59E0B; font-weight: 700; }
.severity-low { color: #3B82F6; font-weight: 700; }

.metric-card {
    text-align: center; background: #F9FAFB; border: 1px solid #E5E7EB;
    border-radius: 10px; padding: 1rem; margin: 0.3rem 0;
}
.metric-card .value { font-size: 1.5rem; font-weight: 800; color: #1E3A8A; }
.metric-card .label { font-size: 0.8rem; color: #6B7280; margin-top: 0.2rem; }

[data-testid="stSidebar"] { background: #0F172A; }
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebar"] .stButton > button {
    width: 100%; background: #1E3A8A; color: white; border: none;
    border-radius: 8px; padding: 0.5rem; font-weight: 600;
    margin-bottom: 0.3rem; transition: background 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover { background: #2563EB; }

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1E3A8A, #2563EB); color: white;
    border: none; border-radius: 10px; padding: 0.75rem; font-size: 1.1rem;
    font-weight: 700; width: 100%;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════
# SAMPLE PROPERTIES
# ══════════════════════════════════════

SAMPLE_PROPERTIES = {
    "Baner 2BHK": {
        "address": "Survey No 45, Baner Road",
        "locality": "baner", "city": "Pune",
        "property_subtype": "Apartment",
        "bhk": 2, "carpet_area_sqft": 1200,
        "age_years": 8, "floor_number": 7,
        "total_floors": 14, "has_lift": True,
        "ownership_type": "Freehold",
        "construction_status": "Ready",
        "has_rera": True, "builder_score": 78,
        "govt_project_nearby": True, "npa_zone": False,
        "absorption_rate": 0.23,
        "supply_demand_ratio": 0.85,
        "price_trend_6m": 7.5
    },
    "Wagholi 3BHK Old": {
        "address": "Near Wagholi Chowk",
        "locality": "wagholi", "city": "Pune",
        "property_subtype": "Apartment",
        "bhk": 3, "carpet_area_sqft": 1450,
        "age_years": 18, "floor_number": 2,
        "total_floors": 5, "has_lift": False,
        "ownership_type": "Freehold",
        "construction_status": "Ready",
        "has_rera": False, "builder_score": 48,
        "govt_project_nearby": False, "npa_zone": True,
        "absorption_rate": 0.09,
        "supply_demand_ratio": 1.9,
        "price_trend_6m": -2.0
    },
    "Fraud Case": {
        "address": "Plot 12, Kothrud",
        "locality": "kothrud", "city": "Pune",
        "property_subtype": "Apartment",
        "bhk": 2, "carpet_area_sqft": 4800,
        "age_years": 3, "floor_number": 1,
        "total_floors": 4, "has_lift": False,
        "ownership_type": "Disputed",
        "construction_status": "Ready",
        "has_rera": False, "builder_score": 42,
        "govt_project_nearby": False, "npa_zone": True,
        "absorption_rate": 0.12,
        "supply_demand_ratio": 1.5,
        "price_trend_6m": 1.0
    }
}

# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════

with st.sidebar:
    st.markdown("## 🏠 PropIntel AI")
    st.caption("AI-Powered Property Collateral Valuation")
    st.divider()

    # Quick Fill
    st.markdown("### ⚡ Quick Fill Demo")
    for name in SAMPLE_PROPERTIES:
        if st.button(name, key=f"sample_{name}"):
            st.session_state["selected_sample"] = name

    st.divider()

    # API Status
    st.markdown("### 🔌 API Status")
    try:
        health = requests.get(f"{API_URL}/health", timeout=3).json()
        st.success(f"✅ API Connected (v{health.get('api_version', '?')})")
    except Exception:
        st.error("❌ API Offline — run `uvicorn api.main:app --reload`")

    st.divider()

    with st.expander("ℹ️ How It Works"):
        st.markdown("""
1. **Geocode** — Address → lat/long via OpenStreetMap
2. **Proximity** — Real distances to metro, hospital, school, IT park
3. **Circle Rate** — Government statutory floor price lookup
4. **Valuation** — ML model predicts market & distress value
5. **Decision** — Fraud detection + liquidity + confidence → APPROVE / REVIEW / REJECT
        """)

# ══════════════════════════════════════
# LOAD SAMPLE INTO SESSION STATE
# ══════════════════════════════════════

s = SAMPLE_PROPERTIES.get(st.session_state.get("selected_sample", ""), {})

# ══════════════════════════════════════
# MAIN FORM
# ══════════════════════════════════════

st.markdown("# 🏠 PropIntel AI — Property Assessment")
st.caption("AI-Powered Collateral Valuation & Liquidity Intelligence for Indian NBFCs")

with st.form("assessment_form"):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("#### 📍 Location")
        address = st.text_input("Address", value=s.get("address", ""), placeholder="e.g. Survey No 45, Baner Road")
        locality = st.text_input("Locality", value=s.get("locality", ""), placeholder="e.g. Baner")
        city = st.selectbox("City", ["Pune", "Mumbai", "Bangalore", "Hyderabad", "Chennai"],
                            index=["Pune", "Mumbai", "Bangalore", "Hyderabad", "Chennai"].index(s.get("city", "Pune")))
        pincode = st.text_input("Pincode (optional)", value="")

    with c2:
        st.markdown("#### 🏗️ Property")
        subtypes = ["Apartment", "Villa", "Independent House"]
        property_subtype = st.selectbox("Type", subtypes,
                                        index=subtypes.index(s.get("property_subtype", "Apartment")))
        bhk = st.selectbox("BHK", [1, 2, 3, 4], index=[1,2,3,4].index(s.get("bhk", 2)))
        carpet_area_sqft = st.number_input("Carpet Area (sqft)", 200, 8000, value=s.get("carpet_area_sqft", 1000))
        age_years = st.slider("Age (years)", 0, 40, value=s.get("age_years", 5))
        floor_number = st.number_input("Floor Number", 0, 50, value=s.get("floor_number", 3))
        total_floors = st.number_input("Total Floors", 1, 60, value=s.get("total_floors", 10))
        has_lift = st.checkbox("Has Lift", value=s.get("has_lift", True))

    with c3:
        st.markdown("#### 📋 Ownership & Builder")
        own_types = ["Freehold", "Leasehold", "Disputed"]
        ownership_type = st.selectbox("Ownership", own_types,
                                      index=own_types.index(s.get("ownership_type", "Freehold")))
        construction_status = st.selectbox("Status", ["Ready", "Under Construction"],
                                           index=["Ready", "Under Construction"].index(s.get("construction_status", "Ready")))
        has_rera = st.checkbox("RERA Registered", value=s.get("has_rera", True))
        if ownership_type == "Leasehold":
            lease_years = st.number_input("Lease Years Remaining", 1, 99, value=50)
        builder_score = st.slider("Builder Score", 40, 95, value=s.get("builder_score", 70))
        govt_project_nearby = st.checkbox("Govt Project Nearby", value=s.get("govt_project_nearby", False))
        npa_zone = st.checkbox("NPA Zone", value=s.get("npa_zone", False))

    with c4:
        st.markdown("#### 📊 Market Signals")
        st.caption("Leave defaults if unsure — system uses locality averages")
        absorption_rate = st.slider("Absorption Rate", 0.03, 0.40, value=s.get("absorption_rate", 0.18),
                                    help="% of listings sold per month in this area")
        supply_demand_ratio = st.slider("Supply/Demand Ratio", 0.3, 2.5, value=s.get("supply_demand_ratio", 1.0))
        price_trend_6m = st.slider("6-Month Price Trend (%)", -10.0, 15.0, value=float(s.get("price_trend_6m", 5.0)),
                                   help="% price change in locality last 6 months")

    submitted = st.form_submit_button("🔍 Assess Property Collateral", type="primary", use_container_width=True)

# ══════════════════════════════════════
# API CALL & RESULTS
# ══════════════════════════════════════

if submitted:
    if not address or not locality:
        st.error("Please fill in Address and Locality.")
        st.stop()

    payload = {
        "address": address, "locality": locality, "city": city,
        "bhk": bhk, "carpet_area_sqft": carpet_area_sqft,
        "age_years": age_years, "floor_number": floor_number,
        "total_floors": total_floors,
        "property_type": property_subtype.lower().replace(" ", "_"),
        "ownership_type": ownership_type.lower(),
        "has_rera": 1 if has_rera else 0,
        "has_lift": has_lift,
        "builder_score": builder_score,
        "govt_project_nearby": 1 if govt_project_nearby else 0,
        "npa_zone": 1 if npa_zone else 0,
        "absorption_rate": absorption_rate,
        "supply_demand_ratio": supply_demand_ratio,
        "price_trend_6m": price_trend_6m
    }

    with st.spinner("🔄 Analyzing property across 6 intelligence layers..."):
        try:
            resp = requests.post(f"{API_URL}/assess", json=payload, timeout=30)
        except requests.exceptions.ConnectionError:
            st.error("🔌 API server not running. Start it with: `uvicorn api.main:app --reload`")
            st.stop()

    if resp.status_code == 422:
        st.error(f"Validation Error: {resp.json().get('detail', resp.text)}")
        st.stop()
    elif resp.status_code != 200:
        st.error(f"Analysis failed (HTTP {resp.status_code}). Check server logs.")
        st.stop()

    result = resp.json()

    # ── Unpack ──
    val = result["valuation"]
    liq = result["liquidity"]
    conf = result["confidence"]
    fraud = result["fraud_flags"]
    loc = result["location_resolved"]
    prox = result["proximity_data"]
    rec = result["lender_recommendation"]
    drivers = result.get("key_drivers", [])
    doc_ver = result.get("document_verification", {})

    # ═══════════════════════════════
    # A: DECISION BANNER
    # ═══════════════════════════════
    decision = rec["decision"]
    banner_cls = {"APPROVE": "banner-approve", "REVIEW": "banner-review", "REJECT": "banner-reject"}[decision]
    banner_icon = {"APPROVE": "✅ APPROVED FOR LENDING", "REVIEW": "⚠️ MANUAL REVIEW REQUIRED", "REJECT": "❌ DO NOT PROCEED"}[decision]

    st.markdown(f"""
    <div class="{banner_cls}">
        <h2>{banner_icon}</h2>
        <p><strong>Safe Loan Amount:</strong> {rec['safe_loan_display']} &nbsp;|&nbsp;
        <strong>LTV:</strong> {rec['ltv_ratio']} &nbsp;|&nbsp;
        <strong>Confidence:</strong> {conf['percentage']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════════════════════════
    # B: FOUR KEY METRICS
    # ═══════════════════════════════
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Market Value", val["market_value_display"])
    m2.metric("📈 Resale Index", f"{liq['resale_index']}/100", delta=liq["grade"])
    m3.metric("⏱️ Time to Sell", liq["time_to_sell_display"])
    m4.metric("🎯 Confidence", conf["percentage"], delta=conf["label"])

    st.divider()

    # ═══════════════════════════════
    # C: LOCATION INTELLIGENCE
    # ═══════════════════════════════
    st.subheader("📍 Location Intelligence")
    lc1, lc2 = st.columns(2)

    with lc1:
        zone = loc.get("circle_rate_zone", "default")
        zone_cls = f"zone-{zone}" if zone in ["premium","upper_mid","mid","developing"] else "zone-default"
        found_msg = "✓ Exact locality match" if loc.get("locality_found_in_db") else "⚠ Using city average"

        st.markdown(f"""<div class="card">
        <h4>{locality.title()} <span class="{zone_cls}">{zone.replace('_',' ').title()}</span></h4>
        <p style="color:#6B7280;font-size:0.85rem">{found_msg}</p>
        </div>""", unsafe_allow_html=True)

        cc1, cc2 = st.columns(2)
        cc1.markdown(f"""<div class="metric-card"><div class="label">Circle Rate</div><div class="value">₹{loc.get('circle_rate_sqft',0):,.0f}/sqft</div></div>""", unsafe_allow_html=True)
        cc2.markdown(f"""<div class="metric-card"><div class="label">Market Rate</div><div class="value">₹{val.get('price_per_sqft',0):,.0f}/sqft</div></div>""", unsafe_allow_html=True)

    with lc2:
        def dist_signal(dist, thresholds):
            if dist is None: return "—", "⚪"
            g, y = thresholds
            if dist < g: return f"{dist:.1f} km", "🟢"
            if dist < y: return f"{dist:.1f} km", "🟡"
            return f"{dist:.1f} km", "🔴"

        amenities = [
            ("🚇 Metro", prox.get("distance_to_metro_km"), (2, 5)),
            ("🛣️ Highway", prox.get("distance_to_highway_km"), (2, 5)),
            ("🏥 Hospital", prox.get("distance_to_hospital_km"), (1, 3)),
            ("🏫 School", prox.get("distance_to_school_km"), (1, 2)),
            ("🛍️ Mall", prox.get("distance_to_mall_km"), (3, 6)),
            ("💼 IT Park", prox.get("distance_to_it_park_km"), (3, 8)),
        ]
        rows = "".join(f"<tr><td>{a}</td><td>{dist_signal(d,t)[0]}</td><td>{dist_signal(d,t)[1]}</td></tr>" for a, d, t in amenities)
        st.markdown(f"""<div class="card"><table width="100%"><tr><th>Amenity</th><th>Distance</th><th>Signal</th></tr>{rows}</table></div>""", unsafe_allow_html=True)

    if not loc.get("locality_found_in_db"):
        st.warning("Locality not found in database. Using city-level averages. Results may be less precise.")

    st.divider()

    # ═══════════════════════════════
    # D: VALUATION BREAKDOWN
    # ═══════════════════════════════
    st.subheader("💰 How We Arrived At This Value")

    st.info(f"**Circle Rate:** ₹{loc.get('circle_rate_sqft',0):,.0f}/sqft (government statutory minimum)")

    if drivers:
        for d in drivers:
            if d.startswith("+"):
                st.success(f"↑ {d}")
            elif d.startswith("-"):
                st.error(f"↓ {d}")
            else:
                st.info(d)

    st.info(f"**Final Market Rate:** ₹{val.get('price_per_sqft',0):,.0f}/sqft × {carpet_area_sqft} sqft")

    vc1, vc2 = st.columns(2)
    with vc1:
        st.markdown(f"""<div class="card" style="border-left: 4px solid #10B981;">
        <h4 style="color:#059669;">Market Value</h4>
        <p style="font-size:1.3rem;font-weight:700;">{val['market_value_display']}</p>
        </div>""", unsafe_allow_html=True)
    with vc2:
        st.markdown(f"""<div class="card" style="border-left: 4px solid #F59E0B;">
        <h4 style="color:#D97706;">Distress Value</h4>
        <p style="font-size:1.3rem;font-weight:700;">{val['distress_value_display']}</p>
        <p style="color:#6B7280;font-size:0.8rem;">Forced sale within 90 days</p>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ═══════════════════════════════
    # E: LIQUIDITY ANALYSIS
    # ═══════════════════════════════
    st.subheader("🔄 Liquidity Analysis")
    lq1, lq2 = st.columns(2)

    with lq1:
        ri = liq["resale_index"]
        grade_color = {"HIGH": "#10B981", "MEDIUM": "#F59E0B", "LOW": "#EF4444"}.get(liq["grade"], "#6B7280")
        st.markdown(f"**Resale Index:** <span style='color:{grade_color};font-weight:700;'>{ri}/100 ({liq['grade']})</span>", unsafe_allow_html=True)
        st.progress(min(ri / 100, 1.0))
        st.metric("Time to Sell", liq["time_to_sell_display"])
        st.metric("Absorption Rate", liq.get("absorption_rate_pct", "—"))
        st.metric("Supply Pressure", liq.get("supply_pressure", "—"))

    with lq2:
        st.markdown("**Factor Breakdown**")
        for factor in liq.get("factor_breakdown", []):
            fc1, fc2 = st.columns([3, 1])
            fc1.caption(f"{factor['factor']} ({factor['weight']})")
            fc2.caption(f"{factor['score']}/100")
            st.progress(min(factor["score"] / 100, 1.0))

    liq_drivers = liq.get("liquidity_drivers", [])
    if liq_drivers:
        st.markdown("**Liquidity Drivers:**")
        for ld in liq_drivers:
            st.markdown(f"- {ld}")

    st.divider()

    # ═══════════════════════════════
    # F: FRAUD & DOCUMENT RISK
    # ═══════════════════════════════
    st.subheader("🛡️ Fraud Detection & Document Risk")
    fr1, fr2 = st.columns(2)

    with fr1:
        st.markdown("**Fraud Detection**")
        if not fraud:
            st.success("✅ No fraud indicators detected")
        else:
            for flag in fraud:
                sev = flag.get("severity", "LOW")
                badge = {"HIGH": "🔴 HIGH", "MEDIUM": "🟡 MEDIUM", "LOW": "🔵 LOW"}.get(sev, sev)
                st.markdown(f"""<div class="card">
                <span class="severity-{sev.lower()}">{badge}</span> — <strong>{flag.get('code','')}</strong><br>
                {flag.get('message','')}<br>
                <em>{flag.get('recommendation','')}</em>
                </div>""", unsafe_allow_html=True)

    with fr2:
        st.markdown("**Document Verification**")
        st.info(f"Status: {doc_ver.get('status', 'Pending')} — {doc_ver.get('message', '')}")

        st.markdown("**Required Documents Checklist:**")
        docs = ["Sale Deed / Agreement", "Encumbrance Certificate", "Property Tax Receipt",
                "RERA Certificate", "Builder NOC", "Approved Building Plan"]
        for doc in docs:
            st.checkbox(doc, value=False, key=f"doc_{doc}")
        st.caption("Check off documents as collected")

    st.divider()

    # ═══════════════════════════════
    # G: LENDER RECOMMENDATION
    # ═══════════════════════════════
    st.subheader("🏦 Lender's Decision Summary")

    rc1, rc2, rc3 = st.columns(3)
    dec_color = {"APPROVE": "#10B981", "REVIEW": "#F59E0B", "REJECT": "#EF4444"}.get(decision, "#6B7280")
    rc1.markdown(f"""<div class="metric-card"><div class="label">Safe Loan Amount</div><div class="value" style="color:{dec_color}">{rec['safe_loan_display']}</div></div>""", unsafe_allow_html=True)
    rc2.markdown(f"""<div class="metric-card"><div class="label">LTV Ratio</div><div class="value">{rec['ltv_ratio']}</div></div>""", unsafe_allow_html=True)
    rc3.markdown(f"""<div class="metric-card"><div class="label">Risk Level</div><div class="value" style="color:{dec_color}">{rec['risk_level']}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Notes for Loan Officer:**")
    for note in rec.get("notes", []):
        st.markdown(f"- {note}")

    with st.expander("🔧 View Raw API Response (for developers)"):
        st.json(result)

    # ═══════════════════════════════
    # FOOTER
    # ═══════════════════════════════
    st.divider()
    st.caption("PropIntel AI v2.0 | Team TE-08, PICT Pune | Problem Statement 4A | TenzorX by Poonawalla Fincorp")
