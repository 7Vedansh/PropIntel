# PropIntel AI

**Collateral Intelligence Engine for NBFC Lending**

An AI-powered system that transforms property collateral assessment from a 10-day manual process into a 2-second intelligent decision. Built for Indian NBFCs and lending institutions.
<hr>
<h2 align="center"> Languages & Frameworks & Tools</h2>
<br>
<p align="center">
<code><img title="Python" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"></code>
<code><img title="Machine Learning" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scikitlearn/scikitlearn-original.svg"></code>
<code><img title="TensorFlow" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tensorflow/tensorflow-original.svg"></code>
<code><img title="NumPy" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg"></code>
<code><img title="Pandas" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg"></code>
<code><img title="Scikit-Learn" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scikitlearn/scikitlearn-original.svg"></code>
<code><img title="FastAPI" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg"></code>
<code><img title="Uvicorn" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"></code>
<code><img title="Pydantic" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"></code>
<code><img title="Streamlit" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/streamlit/streamlit-original.svg"></code>
<code><img title="Docker" height="35" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg"></code>
<code><img title="OpenStreetMap" height="35" src="https://upload.wikimedia.org/wikipedia/commons/b/b0/Openstreetmap_logo.svg"></code>
<code><img title="Joblib" height="35" src="https://img.icons8.com/color/48/artificial-intelligence.png"></code>

</p>
<hr>
## Overview

### The Problem

When an NBFC issues a property-backed loan, determining the true market value of collateral is slow, manual, and expensive. Lenders rely on physical valuators who take 7-10 days, use outdated government circle rates, and provide no insight into how quickly the property could be liquidated in distress. Fraudulent applications with size manipulation or fake documents further expose lenders to risk.

### The Solution

PropIntel AI ingests basic property data (address, size, age, configuration) and instantly computes:

- Accurate market and distress valuations
- Liquidity prediction (time-to-sell and resale index)
- Fraud and anomaly detection
- Lender confidence scoring
- Approve / Review / Reject decision output

What took 10 days and manual effort now takes under 2 seconds.

---

## Key Features

| Feature | Description |
|---|---|
| **AI Property Valuation** | Gradient Boosting model predicts market and distress values using circle rates, proximity, and property attributes |
| **Liquidity Intelligence** | 10-factor engine computes resale index (0-100), time-to-sell, and supply pressure metrics |
| **Fraud Detection** | Rule-based anomaly detection flags size manipulation, floor mismatches, price-circle rate divergence, and NPA zone conflicts |
| **Proximity Intelligence** | Real geocoding (Nominatim + Overpass API) computes distances to metro, hospitals, schools, IT parks, and highways |
| **Decision Engine** | Combines valuation, liquidity, confidence, and fraud signals into a clear Approve / Review / Reject recommendation |
| **Explainable Outputs** | Every prediction includes key value drivers, confidence breakdown, and risk flags |
| **PDF Report Generation** | Two-page print-ready lender assessment report with all metrics and disclaimers |

---

---
## Installation and Setup

```bash
# Clone the repository
git clone https://github.com/7Vedansh/PropIntel.git
cd PropIntel

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Generate synthetic training data
python data/generate_data.py

# Train the valuation model
python train.py

# Start the FastAPI backend
uvicorn api.main:app --reload --port 8000

# In a new terminal, start the Streamlit dashboard
streamlit run app/main.py
```

The API documentation is available at `http://localhost:8000/docs` once the backend is running.

---


## System Architecture


<img width="1672" height="941" alt="adc8ceeb-b166-4a9f-95ac-bdae329e3aac" src="https://github.com/user-attachments/assets/0f9008cd-1a15-46ef-bf08-37aac4cd7700" />




---

## Workflow

```
Step 1: User enters property address + basic details
            |
Step 2: Address geocoded to lat/long (5-strategy fallback)
            |
Step 3: Proximity distances computed (Overpass -> Nominatim -> Fallback)
            |
Step 4: Circle rate looked up from government database
            |
Step 5: Feature engineering assembles all inputs
            |
Step 6: Valuation model predicts market + distress value
            |
Step 7: Liquidity engine computes resale index + time-to-sell
            |
Step 8: Fraud engine runs 9 anomaly detection rules
            |
Step 9: Confidence engine scores data quality + signal agreement
            |
Step 10: Decision engine generates Approve/Review/Reject + safe loan amount
```

---

## Project Structure

```
PropIntel/
├── api/                          # FastAPI backend
│   ├── __init__.py
│   └── main.py                   # REST API endpoints + decision logic
│
├── app/                          # Streamlit frontend
│   ├── main.py                   # Premium dashboard UI
│   └── components/
│       └── python_report.py      # PDF report generator
│
├── engine/                       # Core intelligence engines
│   ├── __init__.py
│   ├── valuation.py              # ML valuation (Gradient Boosting)
│   ├── liquidity_v2.py          # 10-factor liquidity scoring
│   ├── fraud.py                  # 9-rule anomaly detection
│   ├── confidence.py             # 3-signal confidence scoring
│   ├── geocoder.py               # 5-strategy address geocoding
│   └── proximity.py              # Overpass + Nominatim distance engine
│
├── data/                         # Data layer
│   ├── circle_rate_db.py         # Government circle rate database
│   ├── generate_data.py          # Synthetic data generator (500 rows)
│   └── synthetic_properties.csv  # Generated training dataset
│
├── models/                       # Trained model artifacts
│   ├── __init__.py
│   ├── valuation_model.pkl       # Serialized Gradient Boosting model
│   ├── feature_names.pkl         # Model feature list
│   └── model_metadata.pkl        # Training metadata
│
├── notebooks/
│   └── model_training.ipynb      # Jupyter training + validation notebook
│
├── train.py                      # Model training pipeline
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container configuration
└── README.md
```



---
## Business Impact

| Metric | Before | After |
|---|---|---|
| Assessment time | 7-10 days | < 2 seconds |
| Cost per assessment | ~10,000 INR | Near zero (marginal compute) |
| Fraud detection | Manual spot-checks | Automated 9-rule engine |
| Liquidity insight | None | Resale index + time-to-sell |
| Decision consistency | Varies by valuator | Standardized AI output |
| Scalability | Limited by manpower | Unlimited concurrent assessments |

## Input Property Details
<img width="1921" height="972" alt="image" src="https://github.com/user-attachments/assets/b9da085f-4cd9-40e7-94cf-7e79c61ede19" />
## Report Generated
<img width="1921" height="878" alt="image" src="https://github.com/user-attachments/assets/356a05c6-a1f4-4274-b6fb-8150a7592c1b" />
## Valuation Analysis
<img width="1449" height="611" alt="image" src="https://github.com/user-attachments/assets/37c718fe-ca55-4427-a792-a09da5a8161e" />
## Liquidity Analysis
<img width="1226" height="636" alt="image" src="https://github.com/user-attachments/assets/b773bc34-5495-4006-b5ff-aaa71f1f2974" />
## Proximity Analysis
<img width="1217" height="675" alt="image" src="https://github.com/user-attachments/assets/f769340b-19c2-47b3-aa0e-b16c27a2e897" />
## Market Intelligence Analysis
<img width="1188" height="679" alt="image" src="https://github.com/user-attachments/assets/e988b447-f1ec-4c8c-bdee-b284bf2d17de" />

## Author

**Vedansh & Ameya** - [GitHub](https://github.com/7Vedansh)

Team Arjuna
