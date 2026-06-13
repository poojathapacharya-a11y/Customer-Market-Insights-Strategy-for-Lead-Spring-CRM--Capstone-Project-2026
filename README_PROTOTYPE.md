# Lead Spring CRM MDSS Prototype

This folder contains the working prototype for the assessment.

## Files

- `complete_project_dataset.xlsx` - combined project workbook with lead data, marketing benchmarks, ad pricing models, and recommendations.
- `prototype_logic.py` - Python rule logic for lead scoring and recommendation data preparation.
- `dashboard_data.js` - generated dashboard dataset used by the browser prototype.
- `mdss_dashboard.html` - interactive dashboard prototype.
- `serve_dashboard.mjs` - small local server for running the dashboard.

## Run The Dashboard

From this folder, run:

```bash
node serve_dashboard.mjs
```

Then open:

```text
http://127.0.0.1:4173/
```

## What The Prototype Does

- Loads real WBA business lead profiles.
- Uses real ad-pricing benchmark data for Meta Ads, Google Ads, and TikTok Ads.
- Scores each lead using CRM need, digital readiness, package fit, source data, and channel suitability.
- Recommends a realistic platform mix and monthly ad budget.
- Generates a suggested follow-up message for Lead Spring CRM.

## Python Logic

If Python is available, run:

```bash
python prototype_logic.py
```

This regenerates `dashboard_data.js` from the CSV datasets.
