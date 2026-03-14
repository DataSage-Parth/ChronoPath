# 🔒 Ethics & Privacy Checklist

## ✅ DO

1. **Aggregate data only** — All model training uses publicly available, aggregated survey data. No individual records are identifiable.
2. **Synthetic examples** — All demo inputs/outputs shown in docs, tests, and UI use synthetic (fabricated) data. Never display a real person's survey response.
3. **Client-side by default** — User inputs (slider values, scenario configurations) remain in the browser. The backend receives them only for the duration of a prediction request and does NOT persist them.
4. **Stateless API** — The backend processes requests and returns results. No user inputs, predictions, or sessions are logged to disk or database by default.
5. **Export ownership** — Users can export their scenario as a JSON file. The file is generated client-side and never touches the server. The export includes a `"generated_by": "ai-life-simulator"` field and a `"disclaimer"` field.
6. **Bias transparency** — Display a visible disclaimer in the UI: *"Predictions are based on aggregated survey data that skews towards tech workers in Western countries. Results may not generalize to all demographics, industries, or regions."*
7. **Confidence communication** — Always show prediction intervals / percentile bands, never a single deterministic number without context.
8. **Model card** — Maintain a model card (docs/MODEL_CARD.md) documenting training data, known biases, performance metrics, and intended use.
9. **Accessible design** — Meet WCAG 2.1 AA standards: proper contrast ratios, keyboard navigation, ARIA labels on all interactive elements, screen-reader-friendly chart descriptions.
10. **Open source** — Full code and training scripts are open-source. Anyone can audit the models and data pipeline.

---

## ❌ DON'T

1. **Don't store PII** — Never collect names, emails, IP addresses, or any personally identifiable information. No analytics cookies without explicit consent.
2. **Don't present predictions as facts** — Always frame outputs as "hypothetical scenarios based on statistical models," not "your future income WILL be $X."
3. **Don't use protected attributes as features** — Do NOT include race, gender, religion, sexual orientation, or disability status as model inputs, even if available in source datasets. These introduce discriminatory patterns.
4. **Don't claim individual accuracy** — The models predict *population-level trends*. Individual outcomes depend on countless unmeasured factors.
5. **Don't scrape without permission** — Only use datasets with explicit public/open licenses (CC-BY, Open Data, etc.). If Glassdoor data is scraped, use only Kaggle-hosted versions with appropriate licenses.
6. **Don't automate life decisions** — The tool is for exploration and education, not for making hiring, lending, or policy decisions. Include a footer: *"This tool is for educational purposes only."*
7. **Don't retain chat logs** — The AI Career Coach processes prompts in-memory. Don't log user questions or generated advice to persistent storage.
8. **Don't expose raw model weights** — While the code is open-source, don't serve downloadable model files without documenting their limitations and intended use.

---

## 🔐 Data Flow & Privacy Architecture

```
┌──────────────┐     HTTPS (TLS 1.3)     ┌──────────────┐
│   Browser    │ ───────────────────────▶ │   FastAPI    │
│              │                          │   Backend    │
│ • Inputs     │ ◀─────────────────────── │              │
│ • Results    │     JSON response        │ • Stateless  │
│ • Export     │     (no logging)         │ • No DB      │
│   (local)    │                          │ • No PII     │
└──────────────┘                          └──────────────┘
       │                                         │
       │ JSON export                             │ reads
       ▼                                         ▼
  User's device                          models/*.joblib
  (never uploaded)                       (pre-trained, static)
```

## 📋 Pre-Launch Checklist

- [ ] All example data in docs/tests is synthetic
- [ ] Bias disclaimer is visible on the main UI page
- [ ] No `console.log` or server log captures user inputs in production
- [ ] `/advice` endpoint does not persist conversation history
- [ ] Export JSON includes disclaimer field
- [ ] Model card is up-to-date with latest training metrics
- [ ] CORS is restricted to known frontend origins in production
- [ ] Rate limiting is enabled on all endpoints
- [ ] HTTPS is enforced; no HTTP fallback
- [ ] Accessibility audit passes WCAG 2.1 AA
