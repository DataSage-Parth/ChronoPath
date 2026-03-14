# 🎓 Portfolio & Demo Guide

## Elevator Pitch

> ChronoPath lets anyone preview the financial and emotional trajectory of their life decisions using machine learning and Monte Carlo simulation. Tweak your education, savings rate, and work habits with intuitive sliders, and instantly see probabilistic income curves, happiness scores, and stress forecasts — plus an AI coach that tells you exactly which changes would have the biggest impact. It's the "What-If Machine" for your career and life, grounded in real-world survey data.

---

## README Hero Section

```markdown
# 🧬 ChronoPath
### Preview your future. Change your present.

Tweak life decisions → see probabilistic outcomes → get AI coaching.

[Live Demo](https://your-deployment-url.com) · [Video Walkthrough](https://youtube.com/watch?v=xxx)

![screenshot](docs/assets/demo_screenshot.png)
```

---

## GIF / Video Idea

**30-second screen recording** showing:
1. User adjusts "Study Hours" slider from 0 → 4 hrs/day (1 sec)
2. Clicks "Run Simulation" → loading animation (2 sec)
3. Income curve renders with shaded percentile bands growing (3 sec)
4. Quick stats update: income jumps from $68K → $92K median at year 10
5. Scrolls to AI Career Coach, types "What else should I change?"
6. Coach responds with 3 action items + estimated impacts

**File**: `docs/assets/demo.gif` (create with ScreenToGif or RecordIt)

---

## Three Demo Scripts for Recruiters

Each script takes < 2 minutes to run and showcases a different capability.

### Demo 1: "The Power of Education" (shows ML prediction)

```bash
# Start backend
cd backend && uvicorn app.main:app --port 8000 &

# Predict trajectory for a high-school graduate vs. Master's degree holder
curl -s -X POST http://localhost:8000/predict/trajectory \
  -H "Content-Type: application/json" \
  -d '{"age":25,"education_level":1,"years_experience":3,"study_hours_per_day":1,"work_hours_per_week":40,"savings_rate_pct":10,"exercise_days_per_week":2,"networking_hours_per_week":2,"remote_work_pct":50,"job_category":"backend","company_size":1,"country":"USA"}' \
  | python -m json.tool

# Same person with Master's degree + 3 hrs study/day
curl -s -X POST http://localhost:8000/predict/trajectory \
  -H "Content-Type: application/json" \
  -d '{"age":25,"education_level":4,"years_experience":3,"study_hours_per_day":3,"work_hours_per_week":40,"savings_rate_pct":10,"exercise_days_per_week":2,"networking_hours_per_week":2,"remote_work_pct":50,"job_category":"backend","company_size":1,"country":"USA"}' \
  | python -m json.tool
```

### Demo 2: "10,000 Futures" (shows Monte Carlo simulation)

```bash
curl -s -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{"inputs":{"age":28,"education_level":3,"years_experience":5,"study_hours_per_day":2,"work_hours_per_week":45,"savings_rate_pct":20,"exercise_days_per_week":3,"networking_hours_per_week":4,"remote_work_pct":100,"job_category":"data_science","company_size":2,"country":"USA"},"n_simulations":10000,"years_horizon":20,"random_seed":42}' \
  | python -c "import sys,json; d=json.load(sys.stdin); print(f'Year 10 median income: \${d[\"income\"][\"percentiles\"][\"50\"][9]:,.0f}'); print(f'Year 10 range (5th-95th): \${d[\"income\"][\"percentiles\"][\"5\"][9]:,.0f} – \${d[\"income\"][\"percentiles\"][\"95\"][9]:,.0f}')"
```

### Demo 3: "AI Career Coach" (shows LLM-powered advice)

```bash
curl -s -X POST http://localhost:8000/advice \
  -H "Content-Type: application/json" \
  -d '{"inputs":{"age":28,"education_level":3,"years_experience":5,"study_hours_per_day":2,"work_hours_per_week":45,"savings_rate_pct":20,"exercise_days_per_week":3,"networking_hours_per_week":4,"remote_work_pct":100,"job_category":"data_science","company_size":2,"country":"USA"},"question":"I want to double my income in 5 years. What should I change?"}' \
  | python -m json.tool
```

---

## What to Highlight on Your Resume/Portfolio

1. **End-to-end ML pipeline**: data → features → models → API → frontend
2. **Production patterns**: Pydantic schemas, model registry, CORS, error handling
3. **Statistical rigor**: Monte Carlo simulation with explicit seeds, grouped cross-validation
4. **Explainability**: SHAP integration with user-facing feature contribution display
5. **Software engineering**: pytest, CI/CD, Docker, type-safe API client
6. **Product thinking**: user-friendly sliders, responsive design, ethical considerations

---

## Sample JSON Exchanges

### /predict/trajectory — Full Request & Response

**Request**:
```json
{
  "age": 28,
  "education_level": 3,
  "years_experience": 5,
  "study_hours_per_day": 2.0,
  "work_hours_per_week": 45.0,
  "savings_rate_pct": 20.0,
  "exercise_days_per_week": 3,
  "networking_hours_per_week": 4.0,
  "remote_work_pct": 100,
  "job_category": "data_science",
  "company_size": 2,
  "country": "USA"
}
```

**Response**:
```json
{
  "predicted_income": 95420.50,
  "predicted_happiness": 6.82,
  "predicted_stress_probability": 0.3847,
  "confidence_intervals": {
    "income": {
      "lower_95": 75420.50,
      "upper_95": 115420.50
    },
    "happiness": {
      "lower_95": 5.22,
      "upper_95": 8.42
    }
  },
  "feature_importances": {
    "career_score": 0.1823,
    "country_income_tier": 0.1456,
    "education_level": 0.1234,
    "years_experience_norm": 0.1102,
    "learning_rate": 0.0987,
    "job_category_encoded": 0.0876,
    "financial_discipline": 0.0654,
    "work_hours_per_week_norm": 0.0543
  }
}
```

### /simulate — Full Request & Response (truncated)

**Request**:
```json
{
  "inputs": {
    "age": 28,
    "education_level": 3,
    "years_experience": 5,
    "study_hours_per_day": 2.0,
    "work_hours_per_week": 45.0,
    "savings_rate_pct": 20.0,
    "exercise_days_per_week": 3,
    "networking_hours_per_week": 4.0,
    "remote_work_pct": 100,
    "job_category": "data_science",
    "company_size": 2,
    "country": "USA"
  },
  "n_simulations": 10000,
  "years_horizon": 10,
  "random_seed": 42
}
```

**Response** (years 1–3 shown, truncated):
```json
{
  "years": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  "income": {
    "percentiles": {
      "5":  [82145, 78230, 74921, 72100, 69800, 68200, 67100, 66500, 66200, 66000],
      "25": [90234, 89100, 88500, 88700, 89200, 90100, 91500, 93200, 95100, 97200],
      "50": [98500, 101200, 104100, 107300, 110800, 114600, 118700, 123100, 127800, 132800],
      "75": [107800, 114300, 121500, 129400, 138100, 147500, 157800, 169000, 181200, 194500],
      "95": [125600, 140200, 157800, 178500, 202300, 229800, 261200, 297500, 339000, 386800]
    },
    "sample_trajectories": [
      [96200, 99800, 101300, 108200, 112500, 118900, 123400, 131200, 139800, 148200],
      [100100, 94500, 97200, 103400, 109800, 106200, 112400, 119300, 126800, 133400],
      [93800, 102100, 108900, 112600, 119400, 128200, 137800, 142500, 155200, 168900]
    ]
  },
  "happiness": {
    "percentiles": {
      "5":  [4.8, 4.7, 4.6, 4.5, 4.5, 4.4, 4.4, 4.3, 4.3, 4.3],
      "50": [6.8, 6.9, 6.9, 7.0, 7.0, 7.0, 7.1, 7.1, 7.1, 7.1],
      "95": [8.8, 8.9, 9.0, 9.1, 9.1, 9.2, 9.2, 9.2, 9.3, 9.3]
    },
    "sample_trajectories": []
  },
  "stress": {
    "percentiles": {
      "5":  [0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24],
      "50": [0.38, 0.39, 0.40, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47],
      "95": [0.62, 0.63, 0.65, 0.67, 0.69, 0.71, 0.73, 0.75, 0.77, 0.79]
    },
    "sample_trajectories": []
  },
  "config": {
    "n_simulations": 10000,
    "random_seed": 42,
    "noise_model": "gaussian_residual"
  }
}
```

> **Note**: The percentile values above are illustrative/synthetic examples.
> Actual values will vary based on trained model weights.
