# 📊 Datasets — Sources & Field Mapping

## 1. Stack Overflow Developer Survey (Annual)
- **URL**: https://survey.stackoverflow.co/ (download section)
- **Format**: CSV, ~70k–90k rows/year
- **Fields extracted**:

| Raw Field | Maps To | Notes |
|---|---|---|
| `EdLevel` | `education_level` (ordinal 0–5) | Encode: "Less than secondary" → 0, "Secondary" → 1, "Bachelor's" → 3, "Master's" → 4, "PhD" → 5. **VERIFY** exact category names on download. |
| `YearsCodePro` | `years_experience` (int) | Clean: remove "Less than 1 year" → 0, "More than 50" → 50 |
| `ConvertedCompYearly` | `annual_income_usd` (float) | Target variable for income model. Drop nulls and outliers > $1M |
| `WorkWeekHrs` | `work_hours_per_week` (float) | Impute median if null |
| `Age` | `age` (int) | **VERIFY**: field name varies by year |
| `Country` | `country` (categorical) | Used for grouping in cross-validation |
| `LearnHowToCode` | `self_taught_flag` (bool) | **VERIFY**: may not exist in all years |

---

## 2. World Happiness Report
- **URL**: https://worldhappiness.report/data/ (download "Data for Table 2.1")
- **Format**: CSV/XLS, ~150 rows × ~10 years
- **Fields extracted**:

| Raw Field | Maps To | Notes |
|---|---|---|
| `Life Ladder` | `happiness_score` (float 0–10) | Target variable for happiness model |
| `Log GDP per capita` | `log_gdp` (float) | Feature; convert to per-capita income proxy |
| `Social support` | `social_support_score` (float 0–1) | Maps to networking_hours influence |
| `Healthy life expectancy at birth` | `health_life_expectancy` (float) | Maps to exercise proxying |
| `Freedom to make life choices` | `autonomy_score` (float 0–1) | Proxy for career flexibility |
| `Generosity` | `generosity_score` (float) | Optional; low predictive power — **VERIFY** |
| `Perceptions of corruption` | `corruption_score` (float) | Control variable, country-level |

---

## 3. OECD Better Life Index
- **URL**: https://stats.oecd.org/ → search "Better Life Index"
- **Alt URL**: https://www.oecdbetterlifeindex.org/
- **Format**: CSV export from interactive tool
- **Fields extracted**:

| Raw Field | Maps To | Notes |
|---|---|---|
| `Household net adjusted disposable income` | `oecd_income` (float) | Cross-validates income model |
| `Educational attainment` | `oecd_education` (float %) | Complements SO survey education |
| `Employees working very long hours` | `overwork_rate` (float %) | Used in stress model |
| `Life satisfaction` | `oecd_life_satisfaction` (float 0–10) | Cross-validates happiness |
| `Self-reported health` | `oecd_health` (float %) | Supports health_score feature |
| `Time devoted to leisure and personal care` | `leisure_hours` (float hrs/day) | Stress inverse proxy |

---

## 4. Kaggle — Data Science / ML Salary Datasets
- **Search query**: `"data science salaries 2024"` on https://kaggle.com/datasets/
- **Recommended dataset**: "Data Science Salaries 2024" by Hummaam Qaasim (or latest equivalent)
- **Format**: CSV, ~10k–30k rows
- **Fields extracted**:

| Raw Field | Maps To | Notes |
|---|---|---|
| `salary_in_usd` | `annual_income_usd` (float) | Merge with SO survey on role + experience |
| `experience_level` | `experience_tier` (ordinal) | EN=0, MI=1, SE=2, EX=3 |
| `employment_type` | `employment_type` (cat) | FT, PT, CT, FL |
| `remote_ratio` | `remote_pct` (int: 0, 50, 100) | Feature for stress/happiness |
| `company_size` | `company_size` (ordinal) | S=0, M=1, L=2 |
| `job_title` | `job_category` (cat) | Group into ~10 categories — **VERIFY** grouping |

---

## 5. WHO Global Health Observatory
- **URL**: https://www.who.int/data/gho → Indicators
- **Search terms**: `"insufficient physical activity"`, `"life expectancy at birth"`, `"mental health"`
- **Format**: CSV download per indicator
- **Fields extracted**:

| Raw Field | Maps To | Notes |
|---|---|---|
| `Prevalence of insufficient physical activity` | `inactivity_rate` (float %) | Country-level; inverse proxy for exercise |
| `Healthy life expectancy (HALE)` | `healthy_years` (float) | Target for long-range health impact |
| `Suicide mortality rate` | `mental_health_risk` (float) | Stress model covariate. **Handle sensitively.** |
| `Alcohol, total per capita consumption` | `alcohol_consumption` (float L/yr) | Optional stress/health covariate |

---

## 6. Glassdoor Salary Data (via Kaggle)
- **Search query**: `"glassdoor salary"` on https://kaggle.com/datasets/
- **Recommended**: "Data Analyst Jobs" by Picklesueat or "Glassdoor Job Reviews"
- **Format**: CSV, ~1k–10k rows
- **Fields extracted**:

| Raw Field | Maps To | Notes |
|---|---|---|
| `Salary Estimate` | `salary_range_low`, `salary_range_high` (float) | Parse "$55K-$90K" → (55000, 90000). Use midpoint. |
| `Rating` | `company_rating` (float 1–5) | Happiness/stress covariate |
| `Sector` | `industry` (categorical) | Merge on job_category |
| `Size` | `company_size_employees` (ordinal) | Map "1001–5000" → ordinal. **VERIFY** exact strings. |
| `Job Title` | `job_role` (cat) | Cross-reference with SO survey |

---

## Joining Strategy

```
Primary key: (country, education_level, years_experience, job_category)

1. SO Survey (individual-level) — anchor dataset
2. LEFT JOIN Kaggle Salary on (experience_tier, job_category) — enrich salary coverage
3. LEFT JOIN WHR + OECD on (country, year) — country-level happiness/stress context
4. LEFT JOIN WHO on (country) — health context

Final merged dataset shape: ~50k–80k rows × ~30 features
```

> **⚠️ NOTE**: Country-level datasets (WHR, OECD, WHO) are aggregated. When joining
> to individual-level data (SO Survey), the country-level features will repeat for
> all individuals in that country. This is acceptable for modeling but must be noted
> in interpretation — individual variation within a country is NOT captured by these
> features.
