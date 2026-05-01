"""
PropIntel AI - Streamlit UI
Interactive chatbot interface for property assessment
"""

import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PropIntel AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .warning-badge {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .danger-badge {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:8000"

# Helper Functions
def call_api(endpoint, data=None):
    """Call FastAPI backend"""
    try:
        if data:
            response = requests.post(f"{API_URL}{endpoint}", json=data)
        else:
            response = requests.get(f"{API_URL}{endpoint}")
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Please ensure the FastAPI server is running on port 8000."
    except Exception as e:
        return None, f"Error: {str(e)}"

def get_sample_properties():
    """Get sample property configurations"""
    return {
        "Sample 1: High Liquidity (Baner, Pune)": {
            "locality": "Baner",
            "city": "Pune",
            "bhk": 2,
            "sqft": 1200,
            "age_years": 8,
            "floor": 7,
            "total_floors": 14,
            "metro_distance_km": 1.2,
            "it_park_distance_km": 3.5,
            "school_distance_km": 0.8,
            "hospital_distance_km": 1.5,
            "circle_rate_sqft": 8200,
            "absorption_rate": 0.22,
            "builder_score": 78,
            "govt_project_nearby": 1,
            "npa_zone": 0,
            "supply_demand_ratio": 0.85,
            "price_trend_6m": 6.5
        },
        "Sample 2: Low Liquidity (Remote)": {
            "locality": "Outskirts Area",
            "city": "Hyderabad",
            "bhk": 3,
            "sqft": 1800,
            "age_years": 22,
            "floor": 3,
            "total_floors": 5,
            "metro_distance_km": 12.5,
            "it_park_distance_km": 18.0,
            "school_distance_km": 4.5,
            "hospital_distance_km": 5.2,
            "circle_rate_sqft": 5500,
            "absorption_rate": 0.06,
            "builder_score": 52,
            "govt_project_nearby": 0,
            "npa_zone": 1,
            "supply_demand_ratio": 1.8,
            "price_trend_6m": -2.5
        },
        "Sample 3: Fraud Alert (Size Anomaly)": {
            "locality": "Koramangala",
            "city": "Bangalore",
            "bhk": 2,
            "sqft": 4200,  # Anomaly: Too large for 2BHK
            "age_years": 5,
            "floor": 8,
            "total_floors": 15,
            "metro_distance_km": 0.8,
            "it_park_distance_km": 2.0,
            "school_distance_km": 0.5,
            "hospital_distance_km": 1.0,
            "circle_rate_sqft": 12000,
            "absorption_rate": 0.28,
            "builder_score": 85,
            "govt_project_nearby": 1,
            "npa_zone": 0,
            "supply_demand_ratio": 0.65,
            "price_trend_6m": 9.5
        }
    }

# Header
st.markdown('<p class="main-header">🏠 PropIntel AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Collateral Valuation & Liquidity Intelligence Engine</p>', unsafe_allow_html=True)
st.caption("From property data → lending-grade intelligence | Built for NBFCs")

st.divider()

# Sidebar
with st.sidebar:
    st.header("📋 About PropIntel AI")
    st.markdown("""
    PropIntel AI provides **instant, intelligent property assessment** for lending decisions.
    
    **What we deliver:**
    - 🎯 Accurate market valuation
    - 🔄 Liquidity & resale analysis
    - ⚠️ Fraud detection
    - 📊 Confidence scoring
    - 🏦 Lending recommendations
    """)
    
    st.divider()
    
    st.header("📖 How to Use")
    st.markdown("""
    1. **Fill property details** in the form
    2. **Click "Assess Property"**
    3. **Review intelligence report**
    
    Or try a **sample property** below ⬇️
    """)
    
    # Sample properties
    samples = get_sample_properties()
    selected_sample = st.selectbox("Load Sample Property", ["None"] + list(samples.keys()))
    
    if selected_sample != "None":
        if st.button("Load Sample"):
            st.session_state.sample_data = samples[selected_sample]
            st.success("Sample loaded! Check the form.")
    
    st.divider()
    
    # API Status
    health, error = call_api("/health")
    if health:
        st.success("✅ API Online")
    else:
        st.error("❌ API Offline")
        if error:
            st.caption(error)

# Main Form
st.header("🏢 Property Assessment Form")

with st.form("property_form"):
    col1, col2, col3 = st.columns(3)
    
    # Get sample data if loaded
    sample = st.session_state.get('sample_data', {})
    
    # Column 1: Property Details
    with col1:
        st.subheader("Property Details")
        
        locality = st.text_input(
            "Locality/Area",
            value=sample.get('locality', ''),
            help="e.g., Baner, Koramangala"
        )
        
        city = st.selectbox(
            "City",
            options=["Pune", "Mumbai", "Bangalore", "Hyderabad", "Chennai"],
            index=["Pune", "Mumbai", "Bangalore", "Hyderabad", "Chennai"].index(sample.get('city', 'Pune'))
        )
        
        bhk = st.selectbox(
            "BHK Configuration",
            options=[1, 2, 3, 4],
            index=[1, 2, 3, 4].index(sample.get('bhk', 2))
        )
        
        property_type = st.selectbox(
            "Property Type",
            options=["apartment", "villa", "independent_house"],
            index=0
        )
        
        sqft = st.number_input(
            "Carpet Area (sqft)",
            min_value=100.0,
            max_value=10000.0,
            value=float(sample.get('sqft', 1200)),
            step=50.0,
            help="Total carpet area in square feet"
        )
        
        age_years = st.slider(
            "Property Age (years)",
            min_value=0,
            max_value=50,
            value=int(sample.get('age_years', 8)),
            help="How old is the property?"
        )
        
        floor = st.number_input(
            "Floor Number",
            min_value=0,
            max_value=60,
            value=int(sample.get('floor', 7)),
            help="Which floor is the property on?"
        )
        
        total_floors = st.number_input(
            "Total Floors in Building",
            min_value=1,
            max_value=60,
            value=int(sample.get('total_floors', 14)),
            help="Total number of floors"
        )
    
    # Column 2: Location Intelligence
    with col2:
        st.subheader("Location Intelligence")
        
        metro_distance_km = st.slider(
            "Metro Distance (km)",
            min_value=0.2,
            max_value=15.0,
            value=float(sample.get('metro_distance_km', 1.2)),
            step=0.1,
            help="Distance to nearest metro station"
        )
        
        it_park_distance_km = st.slider(
            "IT Park Distance (km)",
            min_value=0.5,
            max_value=20.0,
            value=float(sample.get('it_park_distance_km', 3.5)),
            step=0.5,
            help="Distance to nearest IT/employment hub"
        )
        
        school_distance_km = st.slider(
            "School Distance (km)",
            min_value=0.1,
            max_value=8.0,
            value=float(sample.get('school_distance_km', 0.8)),
            step=0.1,
            help="Distance to nearest school"
        )
        
        hospital_distance_km = st.slider(
            "Hospital Distance (km)",
            min_value=0.2,
            max_value=8.0,
            value=float(sample.get('hospital_distance_km', 1.5)),
            step=0.1,
            help="Distance to nearest hospital"
        )
        
        govt_project_nearby = st.checkbox(
            "Government Project Nearby",
            value=bool(sample.get('govt_project_nearby', 0)),
            help="Is there an announced metro/highway/infrastructure project?"
        )
    
    # Column 3: Market Signals
    with col3:
        st.subheader("Market Signals")
        
        # City-based circle rate hints
        circle_rate_hints = {
            "Mumbai": "12,000 - 35,000",
            "Pune": "6,000 - 15,000",
            "Bangalore": "8,000 - 20,000",
            "Hyderabad": "5,000 - 14,000",
            "Chennai": "6,000 - 16,000"
        }
        
        circle_rate_sqft = st.number_input(
            f"Circle Rate (Rs. /sqft) - {city}: {circle_rate_hints.get(city, '5,000 - 20,000')}",
            min_value=1000.0,
            max_value=100000.0,
            value=float(sample.get('circle_rate_sqft', 8200)),
            step=100.0,
            help="Government circle rate for this area"
        )
        
        absorption_rate = st.slider(
            "Absorption Rate",
            min_value=0.01,
            max_value=0.50,
            value=float(sample.get('absorption_rate', 0.22)),
            step=0.01,
            help="% of listings sold per month (e.g., 0.22 = 22%)"
        )
        
        builder_score = st.slider(
            "Builder RERA Score",
            min_value=0,
            max_value=100,
            value=int(sample.get('builder_score', 78)),
            help="Builder reputation score (0-100)"
        )
        
        supply_demand_ratio = st.slider(
            "Supply/Demand Ratio",
            min_value=0.1,
            max_value=3.0,
            value=float(sample.get('supply_demand_ratio', 0.85)),
            step=0.05,
            help="<1 = demand exceeds supply, >1 = oversupply"
        )
        
        price_trend_6m = st.slider(
            "6-Month Price Trend (%)",
            min_value=-15.0,
            max_value=20.0,
            value=float(sample.get('price_trend_6m', 6.5)),
            step=0.5,
            help="Price change in last 6 months"
        )
        
        npa_zone = st.checkbox(
            "High NPA Zone",
            value=bool(sample.get('npa_zone', 0)),
            help="Is this locality flagged as high NPA zone?"
        )
    
    # Submit button
    submitted = st.form_submit_button("🔍 Assess Property", use_container_width=True, type="primary")

# Process submission
if submitted:
    # Prepare data
    property_data = {
        "locality": locality,
        "city": city,
        "bhk": bhk,
        "sqft": sqft,
        "age_years": age_years,
        "floor": floor,
        "total_floors": total_floors,
        "property_type": property_type,
        "furnishing": "semi",
        "parking": 1,
        "metro_distance_km": metro_distance_km,
        "it_park_distance_km": it_park_distance_km,
        "school_distance_km": school_distance_km,
        "hospital_distance_km": hospital_distance_km,
        "circle_rate_sqft": circle_rate_sqft,
        "absorption_rate": absorption_rate,
        "builder_score": builder_score,
        "govt_project_nearby": 1 if govt_project_nearby else 0,
        "npa_zone": 1 if npa_zone else 0,
        "supply_demand_ratio": supply_demand_ratio,
        "price_trend_6m": price_trend_6m
    }
    
    # Call API
    with st.spinner("🔄 Analyzing property..."):
        result, error = call_api("/assess", property_data)
    
    if error:
        st.error(f"❌ {error}")
    else:
        # Display results
        st.success("✅ Assessment Complete!")
        
        # Fraud Alerts (show first if present)
        if result['fraud_flags']:
            high_severity = [f for f in result['fraud_flags'] if f['severity'] == 'HIGH']
            if high_severity:
                st.error("🚨 HIGH SEVERITY FRAUD FLAGS DETECTED")
                for flag in high_severity:
                    st.warning(f"**{flag['code']}**: {flag['message']}")
        
        st.divider()
        
        # Top Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Market Value",
                result['valuation']['market_value_display'],
                help="Estimated market value range"
            )
        
        with col2:
            st.metric(
                "Distress Value",
                result['valuation']['distress_value_display'],
                delta="-10 to -18%",
                delta_color="inverse",
                help="Value in forced sale scenario"
            )
        
        with col3:
            liquidity_delta = f"{result['liquidity']['grade']}"
            st.metric(
                "Resale Index",
                f"{result['liquidity']['resale_index']}/100",
                delta=liquidity_delta,
                help="Liquidity score"
            )
        
        with col4:
            st.metric(
                "Time to Sell",
                result['liquidity']['time_to_sell_display'],
                help="Expected resale timeframe"
            )
        
        # Second Row Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            conf_color = "🟢" if result['confidence']['label'] == "HIGH" else "🟡" if result['confidence']['label'] == "MEDIUM" else "🔴"
            st.metric(
                "Confidence Score",
                result['confidence']['percentage'],
                delta=f"{conf_color} {result['confidence']['label']}",
                help="Assessment reliability"
            )
        
        with col2:
            st.metric(
                "Loan Recommendation",
                result['lender_recommendation']['safe_loan_display'],
                delta="70% LTV",
                help="Safe lending amount"
            )
        
        with col3:
            decision = result['lender_recommendation']['decision']
            if decision == "APPROVE":
                badge_html = '<span class="success-badge">✅ APPROVE</span>'
            elif decision == "REVIEW":
                badge_html = '<span class="warning-badge">⚠️ REVIEW</span>'
            else:
                badge_html = '<span class="danger-badge">❌ REJECT</span>'
            
            st.metric(
                "Decision",
                "",
                help="Lending decision"
            )
            st.markdown(badge_html, unsafe_allow_html=True)
        
        st.divider()
        
        # Detailed Sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Key Drivers",
            "🔄 Liquidity Analysis",
            "🎯 Confidence Breakdown",
            "⚠️ Fraud Detection",
            "🏦 Lender's Report"
        ])
        
        with tab1:
            st.subheader("Key Value Drivers")
            if result['key_drivers']:
                for driver in result['key_drivers']:
                    if driver.startswith('+'):
                        st.success(driver)
                    elif driver.startswith('-'):
                        st.warning(driver)
                    else:
                        st.info(driver)
            else:
                st.info("No significant drivers identified")
        
        with tab2:
            st.subheader("Liquidity Analysis")
            
            # Progress bar for resale index
            st.write("**Resale Index:**")
            st.progress(result['liquidity']['resale_index'] / 100)
            st.caption(f"{result['liquidity']['resale_index']}/100 - {result['liquidity']['grade']} liquidity")
            
            st.write(f"**Time to Sell:** {result['liquidity']['time_to_sell_display']}")
            st.write(f"**Absorption Rate:** {result['liquidity']['absorption_rate_pct']} monthly")
            
            st.write("**Liquidity Drivers:**")
            for driver in result['liquidity']['liquidity_drivers']:
                st.write(f"• {driver}")
        
        with tab3:
            st.subheader("Confidence Breakdown")
            
            breakdown = result['confidence']['breakdown']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Data Completeness", f"{breakdown['data_completeness']*100:.0f}%")
                st.progress(breakdown['data_completeness'])
            
            with col2:
                st.metric("Signal Agreement", f"{breakdown['signal_agreement']*100:.0f}%")
                st.progress(breakdown['signal_agreement'])
            
            with col3:
                st.metric("Anomaly Score", f"{breakdown['anomaly_score']*100:.0f}%")
                st.progress(breakdown['anomaly_score'])
            
            st.info(f"**Interpretation:** {result['confidence']['interpretation']}")
            
            if result['confidence']['concerns']:
                st.write("**Concerns:**")
                for concern in result['confidence']['concerns']:
                    st.write(f"• {concern}")
        
        with tab4:
            st.subheader("Fraud Detection Results")
            
            if not result['fraud_flags']:
                st.success("✅ No fraud flags detected. Property data appears consistent.")
            else:
                st.warning(f"⚠️ {len(result['fraud_flags'])} anomaly flag(s) detected")
                
                for flag in result['fraud_flags']:
                    severity_color = {
                        'HIGH': '🔴',
                        'MEDIUM': '🟡',
                        'LOW': '🟢'
                    }
                    
                    with st.expander(f"{severity_color.get(flag['severity'], '⚪')} {flag['code']} ({flag['severity']} Severity)"):
                        st.write(f"**Message:** {flag['message']}")
                        st.write(f"**Recommendation:** {flag['recommendation']}")
        
        with tab5:
            st.subheader("Lender's Report")
            
            rec = result['lender_recommendation']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Safe Loan Amount", rec['safe_loan_display'], help="70% LTV on minimum market value")
                st.metric("LTV Ratio", rec['ltv_ratio'])
            
            with col2:
                st.metric("Distress Recovery", rec['distress_recovery_assured'])
                st.metric("Risk Level", rec['risk_level'])
            
            st.write("**Decision Notes:**")
            for note in rec['notes']:
                st.write(f"• {note}")
            
            # Raw JSON
            with st.expander("📄 View Raw API Response"):
                st.json(result)

# Footer
st.divider()
st.caption("PropIntel AI v1.0 | Team TE-08, PICT Pune | Problem Statement 4A")
st.caption("Built for Poonawalla Fincorp AI Hackathon | Powered by Gradient Boosting ML")