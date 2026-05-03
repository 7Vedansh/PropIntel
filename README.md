# PropIntel AI

**Collateral Intelligence Engine for NBFC Lending**

An AI-powered system that transforms property collateral assessment from a 10-day manual process into a 2-second intelligent decision. Built for Indian NBFCs and lending institutions.

---

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

## System Architecture

```
                          PropIntel AI Architecture
                          ========================

  +----------+         +----------------+         +-------------------+
  |  Loan    |  HTTP   |   FastAPI      |  Call   |   Intelligence    |
  |  Officer | ------> |   Backend      | ------> |   Engines          |
  +----------+         |   (api/)       |         |                   |
                       +----------------+         |  +-------------+ |
  +----------+         |                |         |  | Valuation   | |
  | Streamlit| <------ |  /assess       | <------ |  | (GB Model)  | |
  | Dashboard|  JSON   |  endpoint      |  results|  +-------------+ |
  +----------+         |                |         |  | Liquidity   | |
                       |  Geocoder      |         |  | (10-factor) | |
                       |  Proximity      |         |  +-------------+ |
                       |  Circle Rate DB |         |  | Fraud       | |
                       +----------------+         |  | (9 rules)   | |
                                                   |  +-------------+ |
                                                   |  | Confidence  | |
                                                   |  | (3-signal)  | |
                                                   |  +-------------+ |
                                                   +-------------------+
```

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

## UI Overview

The Streamlit dashboard provides a premium dark-themed interface:

1. **Input Section** - Address, BHK, area, age, floor, ownership, and lift status. Market signals are auto-computed by the intelligence engine.
2. **Decision Banner** - Clear Approve / Review / Reject with safe loan amount and LTV ratio.
3. **Metric Cards** - Market Value, Resale Index, Time to Sell, and Confidence Score.
4. **Risk Pills** - Fraud risk, legal risk, supply pressure, and NPA zone status at a glance.
5. **Tabbed Details** - Valuation breakdown, liquidity factors, proximity distances, market intelligence (auto-computed builder score, absorption rate, supply pressure, price trend), growth catalysts, and document checklist.
6. **PDF Export** - Download a formatted two-page lender assessment report.

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

## Model Performance

| Model | MAPE | RMSE | R2 |
|---|---|---|---|
| Circle Rate Baseline | 10.4% | 1761 | 0.95 |
| Linear Regression | 4.6% | 772 | 0.99 |
| Random Forest | 8.2% | 1448 | 0.97 |
| **Gradient Boosting (selected)** | **7.1%** | **1326** | **0.97** |

Gradient Boosting was selected for its balance of accuracy and stability on financial data, avoiding overfitting risks present in the linear model.

---

## API Reference

### `POST /assess`

Full property assessment with all intelligence layers.

**Request body** (simplified - market signals are auto-derived):

```json
{
  "address": "Survey No 45, Baner Road",
  "locality": "baner",
  "city": "Pune",
  "bhk": 2,
  "carpet_area_sqft": 1200,
  "age_years": 8,
  "floor_number": 7,
  "total_floors": 14,
  "ownership_type": "freehold",
  "has_lift": true
}
```

**Response** includes: valuation, liquidity, confidence, fraud flags, proximity data, key drivers, and lender recommendation.

### `GET /health`

Health check with model status and API version.

### `GET /market/{pincode}`

Market data lookup by pincode (absorption rate, demand level, comparable count).

### `GET /docs`

Interactive Swagger documentation.

---

## Future Improvements

- **Real-time APIs** - Integrate live property listing feeds for dynamic price trends
- **Enhanced ML Models** - XGBoost/LightGBM with hyperparameter tuning on larger datasets
- **Production Deployment** - Docker Compose with Redis caching, rate limiting, and CI/CD
- **Multi-city Expansion** - Extend circle rate database and locality intelligence to Tier-2 cities
- **Time-series Forecasting** - LSTM/Prophet models for price trend prediction
- **Document OCR** - Automated RERA and encumbrance certificate verification
- **Audit Trail** - Database-backed assessment history for regulatory compliance

---

## Author

**Vedansh** - [GitHub](https://github.com/7Vedansh)

Team Arjuna
