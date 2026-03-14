# 🤖 AI Career Coach — Sample Q&A & Prompt Templates

## Prompt System Design

### System Prompt (sent to LLM as `system` role)

```
You are an AI Career Coach inside the "ChronoPath" app.
You give actionable, measurable, encouraging advice based on data.

RULES:
- Be specific: give numbers, timelines, and measurable steps.
- Prioritize: rank suggestions by estimated impact (highest first).
- Be honest: if the data shows trade-offs, state them.
- Stay positive: frame advice as opportunities, not criticisms.
- Keep it concise: 3-5 action items max.
- Never fabricate statistics — use the model predictions provided.
```

### User Prompt Template (injected per request)

```
### Current inputs
- Age: {age}
- Education: {education_level} (0-5 scale)
- Experience: {years_experience} years
- Study: {study_hours_per_day} hrs/day
- Work: {work_hours_per_week} hrs/week
- Savings rate: {savings_rate_pct}%
- Exercise: {exercise_days_per_week} days/week
- Networking: {networking_hours_per_week} hrs/week

### Model predictions
- Predicted income: ${predicted_income}/year
- Predicted happiness: {predicted_happiness}/10
- Stress probability: {stress_probability}%

### Top factors driving income (from SHAP explainability)
1. {shap_factor_1}
2. {shap_factor_2}
3. {shap_factor_3}

### User's question
{user_question}

Please respond with:
1. A direct answer (2-3 sentences)
2. 3-5 prioritized action items with: what to change, by how much, estimated impact
```

---

## 8 Sample Q&A Pairs

### Q1: "I want to double my income in 5 years — what should I improve?"

**Context**: User with Bachelor's, 3 years experience, $65K income, 1 hr/day study, 2 hrs/week networking.

**Coach response**:

> Your best path to doubling income involves three high-impact changes, based on the model's top predictors. Education and study time are your biggest levers — they compound over 5 years.

**Action items**:
| Priority | Action | Change | Estimated Impact |
|---|---|---|---|
| 1 | Pursue a Master's degree or advanced certifications | Education 3 → 4 | +18-25% income over 3 years |
| 2 | Increase daily study/learning time | 1 → 3 hrs/day | +12-15% income via learning_rate boost |
| 3 | Increase professional networking | 2 → 6 hrs/week | +8-10% income via career_score |
| 4 | Target larger companies | company_size 0 → 2 | +10-15% immediate salary jump |
| 5 | Negotiate remote flexibility | remote_pct 0 → 50 | Opens access to higher-paying markets |

---

### Q2: "I'm burned out — how do I reduce stress without losing income?"

**Context**: User working 60 hrs/week, 1 day exercise, $120K income, stress probability 72%.

**Coach response**:

> Your stress probability is 72%, with work hours and low exercise being the primary drivers. The good news: reducing work hours by 15% while adding exercise actually has a *neutral* income impact because health_score improves productivity and career longevity.

**Action items**:
| Priority | Action | Change | Estimated Impact |
|---|---|---|---|
| 1 | Reduce work hours gradually | 60 → 45 hrs/week | -15% stress probability, ~neutral income |
| 2 | Exercise more regularly | 1 → 4 days/week | +0.8 happiness, -12% stress probability |
| 3 | Set boundaries: no email after 7 PM | Qualitative change | Improved recovery, sustainable performance |
| 4 | Increase savings rate as buffer | 10% → 25% | Financial security reduces anxiety |

---

### Q3: "Is a PhD worth it financially?"

**Context**: User with Master's, data science, $110K, age 28.

**Coach response**:

> Based on the model, a PhD (education_level 4→5) adds approximately +8-12% income over 10 years for data science roles. However, you'd forgo 4-6 years of full-time salary ~$110K/year. The break-even point is around year 12-15 post-PhD. If your goal is purely financial, advanced certifications + experience would outperform a PhD.

**Action items**:
| Priority | Action | Change | Estimated Impact |
|---|---|---|---|
| 1 | Stay at Master's + specialize | Focus study on ML systems or MLOps | +15-20% income in 3 years |
| 2 | Consider PhD only if research-motivated | Education 4 → 5 (5-year investment) | +8-12% long-term, negative short-term |
| 3 | Get industry certifications instead | AWS ML Specialty, GCP Professional | +7-10% income, 3-month investment |

---

### Q4: "I save almost nothing — how bad is that for my future?"

**Context**: User with savings_rate_pct = 2%, $85K income.

**Coach response**:

> A 2% savings rate puts you in the bottom 10% of financial_discipline scores, which correlates with higher stress and lower long-term income trajectory. The model shows that increasing savings to 20% has a compounding effect on income trajectory because financial stability enables bolder career moves.

**Action items**:
| Priority | Action | Change | Estimated Impact |
|---|---|---|---|
| 1 | Set up automatic transfers: 15% of paycheck | 2% → 15% savings | +5% income trajectory, -8% stress |
| 2 | Build 3-month emergency fund | ~$21K target | Enables job switching without desperation |
| 3 | Target 20% within 6 months | 15% → 20% | Enters optimal financial_discipline range |
| 4 | Invest savings in index funds | After emergency fund | Compound growth accelerates trajectory |

---

### Q5: "Should I go remote or return to office?"

**Context**: User at remote_pct = 100, considering return to office.

**Coach response**:

> The model shows remote work has a small positive effect on happiness (+0.3) and near-neutral effect on income. However, networking_hours_per_week is a top-3 SHAP factor for income, and in-office time naturally increases networking. A hybrid approach (50%) captures both benefits.

**Action items**:
| Priority | Action | Change | Estimated Impact |
|---|---|---|---|
| 1 | Try hybrid (50%) for 3 months | remote_pct 100 → 50 | +3-5% income from networking |
| 2 | If staying remote, increase intentional networking | 2 → 6 hrs/week | Compensates for remote isolation |
| 3 | Use commute savings for study time | reallocate 1 hr/day | +5% career_score |

---

### Q6: "What's the single highest-impact change I can make right now?"

**Context**: Generic default inputs.

**Coach response**:

> Based on SHAP values for your profile, **study_hours_per_day** has the highest impact on your predicted income. Increasing it from 2 to 4 hours/day would boost your learning_rate from 0.63 to 0.86 and is estimated to increase income by 10-15% over 3 years.

**Single action**: Increase daily study to 4 hours, focused on high-value skills (currently ML/AI for data science roles).

---

### Q7: "I'm 45 and worried about career decline — should I pivot?"

**Context**: User age 45, 20 years experience, backend engineering.

**Coach response**:

> The model shows years_experience continues to positively impact income up to ~25 years, after which it plateaus. At 45 with 20 years experience, you're in a strong position. The key is to keep learning_rate high — the model penalizes stagnation more than age.

**Action items**:
| Priority | Action | Change | Estimated Impact |
|---|---|---|---|
| 1 | Increase study time to learn adjacent technologies | 1 → 2.5 hrs/day | Maintains career_score growth |
| 2 | Shift toward architecture/leadership roles | Qualitative | Higher salary ceiling |
| 3 | Increase networking with hiring managers | 2 → 5 hrs/week | Opens staff/principal engineer paths |

---

### Q8: "How do I balance everything without sacrificing happiness?"

**Context**: User optimizing for income at expense of happiness (60 hrs/work, 0 exercise, high study).

**Coach response**:

> Your model shows a classic trade-off: high career_score (82) but low health_score (15) and happiness (4.2/10). The data suggests diminishing returns on income past 50 work hours — the happiness cost outweighs marginal income gains. A rebalanced profile would sacrifice ~5% income but gain +2.5 happiness points.

**Action items**:
| Priority | Action | Change | Estimated Impact |
|---|---|---|---|
| 1 | Reduce work to 45 hrs/week | 60 → 45 hrs | -5% income, +1.2 happiness |
| 2 | Add exercise 4 days/week | 0 → 4 days | +0.8 happiness, -10% stress |
| 3 | Keep study at 2 hrs (don't add more) | Maintain 2 hrs | Efficient learning_rate without burnout |
| 4 | Allocate saved time to social/networking | +3 hrs/week | +0.5 happiness, +career opportunities |
