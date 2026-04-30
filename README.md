# PropIntel AI 🏠

> **AI‑Powered Property Collateral Valuation & Liquidity Intelligence Engine** for Indian NBFCs and housing finance lenders.

## Overview
PropIntel AI provides rapid, data‑driven insights for property‑backed loans:
1. **Accurate market valuation** – ML model trained on synthetic Indian property data.
2. **Liquidity scoring** – predicts how quickly the property can be sold under distress.
3. **Fraud detection** – rule‑based checks for suspicious property details.
4. **Confidence scoring** – reliability metric with key driver explanations.

All results are returned via a clean FastAPI backend and an interactive Streamlit dashboard, turning days‑long manual appraisal into minutes.

## Quick Start
```bash
# Clone the repo
git clone <https://github.com/7Vedansh/PropIntel.git>
cd propintel

# Setup environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Generate synthetic dataset (optional, file shipped)
python data/generate_data.py

# Train the valuation model
python train.py

# Start the API server
uvicorn api.main:app --reload   # http://127.0.0.1:8000

# Launch the UI
streamlit run chatbot/app.py   # http://127.0.0.1:8501
```

## Project Structure
```
propintel/
├─ data/
│  ├─ generate_data.py          # Synthetic dataset generator
│  └─ synthetic_properties.csv  # 500‑row sample dataset
├─ engine/
│  ├─ __init__.py
│  ├─ valuation.py              # Valuation model inference
│  ├─ liquidity.py              # Liquidity scoring logic
│  ├─ fraud.py                  # Fraud detection rules
│  └─ confidence.py             # Confidence score calculator
├─ api/
│  ├─ __init__.py
│  └─ main.py                   # FastAPI endpoints
├─ chatbot/
│  └─ app.py                    # Streamlit UI
├─ notebooks/
│  └─ model_training.ipynb      # Model training & validation notebook
├─ models/
│  └─ valuation_model.pkl       # Trained model artifact
├─ train.py                      # Training script
├─ requirements.txt
└─ README.md
```

## License
MIT – Feel free to adapt and extend.
