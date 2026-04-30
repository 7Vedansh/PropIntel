# PropIntel AI 🏠
> AI-Powered Collateral Valuation & Liquidity Engine for Indian NBFCs

## Problem It Solves
When an Indian NBFC issues a property-backed loan, determining the true market value of the collateral is a slow, manual, and expensive process. Lenders rely on manual valuators who take 7-10 days, use outdated government circle rates, and provide no actionable insights into how quickly the property could be liquidated in a distress scenario. Furthermore, lenders are constantly exposed to fraudulent applications involving size manipulation or fake documents.

**PropIntel AI** transforms this process. By ingesting basic property data (location, size, age, configuration), the engine instantly computes an accurate market valuation, predicts the exact liquidity (time-to-sell), detects anomalous data points flagging potential fraud, and provides a lender confidence score. What used to take 10 days and ₹10,000 per property now takes less than 2 seconds, empowering loan officers to make immediate, safe, data-driven decisions.

## How It Works
```text
[ Loan Officer ] -> Enters property details via UI
       │
       ▼
[ Streamlit App ] -> Submits JSON payload to API
       │
       ▼
[ FastAPI Backend ]
       │
       ├──► 1. Valuation Engine   -> Predicts Market & Distress Value (Random Forest / GBM)
       ├──► 2. Liquidity Engine   -> Computes Resale Index & Time-to-Sell
       ├──► 3. Fraud Engine       -> Runs rule-based anomaly detection
       └──► 4. Confidence Engine  -> Evaluates data completeness & signal agreement
       │
       ▼
[ Final Assessment ] -> Loan Recommendation, LTV rules, and Risk Level returned
```

## Features
- **Accurate Market Valuation:** ML-based estimation using synthetic Indian real estate data.
- **Liquidity Intelligence:** Estimates the exact number of days to sell and provides a resale index.
- **Automated Fraud Detection:** Rule-based checks for size anomalies, floor mismatches, and price manipulation.
- **Confidence Scoring:** Tells the lender exactly how reliable the prediction is.
- **Interactive Dashboard:** Beautiful, premium Streamlit UI for immediate loan officer usage.

## Tech Stack
- **Backend:** FastAPI, Pydantic, Uvicorn
- **Frontend:** Streamlit
- **Machine Learning:** Scikit-Learn, Pandas, NumPy, Joblib
- **Data:** Synthetic data generation pipeline mimicking top Indian cities.

## Installation & Running

1. **Clone the repository**
```bash
git clone https://github.com/7Vedansh/PropIntel.git
cd PropIntel
```

2. **Set up the environment**
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

3. **Generate Synthetic Data**
```bash
python data/generate_data.py
```
*(This will generate a 500-row synthetic dataset and inject required fraud cases).*

4. **Train the ML Model**
```bash
python train.py
```
*(This will output the performance of 3 models and save the best Gradient Boosting model to the `models/` directory).*

5. **Start the API Server**
```bash
uvicorn api.main:app --reload --port 8000
```

6. **Launch the Streamlit UI**
Open a new terminal window, activate the venv, and run:
```bash
streamlit run chatbot/app.py
```

## API Documentation
Once the API server is running, navigate to `http://127.0.0.1:8000/docs` to view the interactive Swagger documentation.

**Example Request to `/assess`**:
```json
{
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
}
```

## Model Performance
| Model                        |  MAPE  |   RMSE   |  R²   |
|------------------------------|--------|----------|-------|
| Circle Rate Baseline         |  10.4% |     1761 |  0.95 |
| Linear Regression            |   4.6% |      772 |  0.99 |
| Random Forest                |   8.2% |     1448 |  0.97 |
| **Gradient Boosting (BEST)** | **7.1%** |  **1326** | **0.97** |

*Note: Model chosen based on real-world stability requirements for financial data.*

## Project Structure
```text
PropIntel/
├── api/
│   ├── __init__.py
│   └── main.py                   # FastAPI backend
├── chatbot/
│   └── app.py                    # Streamlit UI
├── data/
│   ├── generate_data.py          # Synthetic dataset generator
│   └── synthetic_properties.csv  # Generated dataset (500 rows)
├── engine/
│   ├── __init__.py
│   ├── confidence.py             # Confidence score calculator
│   ├── fraud.py                  # Fraud detection rules
│   ├── liquidity.py              # Liquidity scoring engine
│   └── valuation.py              # ML valuation model inference
├── models/
│   ├── __init__.py
│   ├── feature_names.pkl         # Saved feature list
│   └── valuation_model.pkl       # Saved trained model
├── notebooks/
│   └── model_training.ipynb      # Model training & validation notebook
├── README.md
├── requirements.txt
└── train.py                      # Training script
```

## Team
**Team TE-08, PICT Pune**
Problem Statement 4A
Built for Poonawalla Fincorp AI Hackathon
