<p align="center">
  <h1 align="center">⏳ ChronoPath</h1>
  <p align="center"><strong>Explore how your decisions shape your future.</strong></p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-14-black?logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/XGBoost-ML-blue?logo=xgboost" alt="XGBoost" />
  <img src="https://img.shields.io/badge/Monte%20Carlo-10K%20sims-purple" alt="Monte Carlo" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT" />
</p>

---

ChronoPath is an AI-powered life-decision simulator. Tweak your education, work habits, savings rate, and lifestyle — and instantly see probabilistic trajectories for **income**, **happiness**, and **stress** over the next 20 years.

> **Not a crystal ball** — ChronoPath generates data-grounded "what-if" scenarios with confidence bands using ensemble ML models and Monte Carlo simulation.

<!-- Add your demo GIF or screenshot here -->
<!-- ![ChronoPath Demo](docs/assets/demo.gif) -->

---

## Features

| Feature | Description |
|---|---|
| **Decision Inputs** | 15 life variables across 4 groups: Personal, Career, Lifestyle, Financial |
| **Income Forecasting** | XGBoost-predicted income curve with Monte Carlo percentile bands |
| **Scenario Comparison** | Compare two life paths (A/B) side-by-side on one chart |
| **AI Insight** | Natural-language explanation of what your results mean |
| **Goal Mode** | Set a target income + age, get strategy recommendations |
| **Life Timeline** | Narrative milestones ("Age 30 → salary crosses $120K") |
| **Impact Analysis** | SHAP-based ranking of which decisions influence income most |
| **Country Context** | Regional salary benchmarks, growth outlook, opportunity index |
| **Quick Presets** | One-click profiles: Career Focus, Health Focus, Wealth, Balanced |
| **Currency Switching** | USD / INR with locale-aware formatting |
| **Model Transparency** | Plain-English explanation of how predictions work |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Sliders  │  │ Presets  │  │ GoalMode │  │ Compare  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       └──────────────┴─────────────┴─────────────┘       │
│                        │ POST /simulate                   │
├────────────────────────┼─────────────────────────────────┤
│                    BACKEND (FastAPI)                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Pydantic │→ │ Feature Eng. │→ │ ML Models         │  │
│  │ Schemas  │  │ (21 features)│  │ XGB + GBR + LogReg│  │
│  └──────────┘  └──────────────┘  └────────┬──────────┘  │
│                                          │              │
│                               ┌──────────▼──────────┐   │
│                               │ Monte Carlo Engine  │   │
│                               │ (10,000 simulations)│   │
│                               └─────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

---

## ML Pipeline

**3 models trained on 21 engineered features:**

| Model | Algorithm | Target | Key Metric |
|---|---|---|---|
| Income | XGBoost Regressor | Annual income (USD) | RMSE ~$14K |
| Happiness | Gradient Boosting | Score (0–10) | RMSE ~0.73 |
| Stress | Logistic Regression (Platt-calibrated) | Binary (high/low) | AUC 0.97 |

**Feature engineering pipeline:**

```
Raw inputs (15)
  → Constraint enforcement (experience ≤ age − 18)
  → Categorical encoding (7 industries, 7 countries)
  → Min-max normalization (12 continuous features)
  → Derived features (6): career_score, financial_discipline,
    health_score, learning_rate, wellbeing_score, entrepreneurial_drive
  → Final vector: 21 features
```

**Monte Carlo simulation:**
- 10,000 stochastic trajectories per run
- Gaussian noise calibrated from model RMSE
- Growth rates adjusted by skill, education, industry, side projects
- Outputs: 5th / 25th / 50th / 75th / 95th percentile bands

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14 · React 18 · Tailwind CSS · Plotly.js |
| **Backend** | FastAPI · Python 3.11 · Pydantic v2 |
| **ML** | scikit-learn · XGBoost · SHAP |
| **Simulation** | NumPy Monte Carlo |
| **DevOps** | Docker · docker-compose |
| **Testing** | pytest (19 tests) |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/train_models.py     # Train models (~30s)
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # → http://localhost:3000
```

### Docker (full stack)
```bash
cp .env.example .env
docker-compose up --build   # → http://localhost:3000
```

---

## Deployment

| Service | Platform | Notes |
|---|---|---|
| Frontend | **Vercel** | Connect repo, set `NEXT_PUBLIC_API_URL` env var |
| Backend | **Render** or **Railway** | Use `backend/Dockerfile`, set `CORS_ORIGINS` |

```bash
# Backend env vars for production:
CORS_ORIGINS=["https://your-app.vercel.app"]
DEBUG=false
```

---

## Project Structure

```
chronopath/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + CORS + lifespan
│   │   ├── models.py               # Pydantic schemas (15 inputs)
│   │   ├── core/config.py          # Environment settings
│   │   ├── ml/
│   │   │   ├── feature_engineering.py  # 21-feature pipeline
│   │   │   ├── monte_carlo.py          # 10K-sim engine
│   │   │   └── model_loader.py         # Model registry
│   │   └── routers/                # /predict, /simulate, /explain, /advice
│   ├── scripts/train_models.py     # Training pipeline
│   ├── models/                     # Saved .joblib artifacts
│   └── Dockerfile
├── frontend/
│   ├── src/components/
│   │   ├── SimulatorApp.tsx        # Main app (presets, scenarios, inputs)
│   │   ├── IncomeCurve.tsx         # Plotly chart (A/B overlay)
│   │   ├── AIInsight.tsx           # Natural-language insights
│   │   ├── GoalMode.tsx            # Target income strategy
│   │   ├── LifeTimeline.tsx        # Narrative milestones
│   │   ├── SensitivityAnalysis.tsx # SHAP impact bars
│   │   ├── CountryContext.tsx      # Regional economic data
│   │   ├── ModelTransparency.tsx   # "How it works" panel
│   │   └── DecisionSlider.tsx      # Accessible range input
│   ├── src/lib/api.ts              # Typed API client
│   └── Dockerfile
├── docs/
│   ├── DATASETS.md                 # Data source mapping
│   ├── ETHICS.md                   # Privacy & bias checklist
│   └── ROADMAP.md                  # Release phases
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Ethics & Privacy

- **No PII stored** — all inputs stay client-side
- **Synthetic training data** — no real individuals' data
- **Bias disclosure** — models trained on tech-heavy, Western-centric surveys
- **User agency** — predictions are hypothetical scenarios, not guarantees

See [docs/ETHICS.md](docs/ETHICS.md) for the full checklist.

---

## License

MIT © 2026
