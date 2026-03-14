# 🗺️ Feature Roadmap

## Phase 1 — MVP (Weeks 1–3)

**Goal**: Single-page app with income prediction and Monte Carlo visualization.

- [x] Data pipeline: download + clean SO Developer Survey + Kaggle salary data
- [x] Feature engineering: education_level, years_experience, study_hours, savings_rate
- [x] Train XGBoost income model with hyperparameter tuning
- [x] Monte Carlo simulation function (N=10,000, percentile bands)
- [x] FastAPI endpoints: `/predict/trajectory`, `/simulate`
- [x] React frontend: input sliders + Plotly income curve with shaded bands
- [x] Basic README and project structure
- [ ] Deploy to a free tier (Railway / Render)

---

## Phase 2 — Multi-Metric Dashboard (Weeks 4–6)

**Goal**: Add happiness and stress models, scenario comparison, and explainability.

- [ ] Integrate World Happiness Report + OECD data
- [ ] Train GradientBoosting happiness model (target: 0–10 score)
- [ ] Train calibrated LogisticRegression stress model (probability of high-stress)
- [ ] `/explain` endpoint returning SHAP feature contributions
- [ ] Happiness gauge component (animated radial chart)
- [ ] Stress meter component (traffic-light bar)
- [ ] Scenario Compare UI: side-by-side two configurations
- [ ] SHAP waterfall plot rendered in frontend
- [ ] Integration tests for all endpoints

---

## Phase 3 — AI Career Coach (Weeks 7–9)

**Goal**: In-app chatbot that gives personalized, SHAP-informed advice.

- [ ] `/advice` endpoint with LLM prompt template
- [ ] Career Coach chat UI component
- [ ] Prompt engineering: inject user inputs + top-3 SHAP features + predictions
- [ ] 8 curated Q/A examples for fine-tuning / few-shot
- [ ] Rate limiting and content filtering on `/advice`
- [ ] Export scenario as JSON (client-side)

---

## Phase 4 — Scale & Polish (Weeks 10+)

**Goal**: Production hardening, multi-country, community features.

- [ ] Multi-country support: user selects country → models adjust for local data
- [ ] Community benchmarks: opt-in anonymized percentile ("you're in the top 20% for your cohort")
- [ ] Timeline animation: play/scrub through years 1–30
- [ ] Mobile-responsive layout optimization
- [ ] Internationalization (i18n) for 5 languages
- [ ] A/B test different model configurations
- [ ] User feedback loop: "Was this prediction helpful?" → model retraining signal
