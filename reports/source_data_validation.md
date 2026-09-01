# Source Data Validation

The original assignment files were recovered after the public portfolio repository had already been assembled. They were used locally to validate the public portfolio implementation without redistributing the copyrighted course materials or raw assignment data.

## Recovered source files

- `drugs.csv`
  - 114 candidate drug-development projects
  - therapeutic area
  - time-to-market
  - expected net present value (eNPV)
  - current-year development cost

- `drugs_cov.csv`
  - 114 × 114 covariance matrix
  - symmetric in the recovered file
  - positive definite in local numerical validation
  - Cholesky factorization succeeds

- `drug.ipynb`
  - original starter / template notebook
  - contains the data-loading setup, therapeutic-area budgets, 3% risk-free rate, covariance loading, and placeholders for model variables, constraints, objective, and output

## Source-file fingerprints

The validation notebook records SHA-256 fingerprints so the exact locally validated inputs can be identified without publishing them:

- `drugs.csv`: `375850d89cadcffd03e8f084270bc7469c90fb2edce9068def248353a31d5c15`
- `drugs_cov.csv`: `fbd2a5badc620ac6dda74bfe7b3591e6ae3bde85875b31bdd8a1ad172ffa885e`

## Independent validation method

The public portfolio keeps **Gurobi** as the primary modeling implementation because that is the optimization environment used in the source assignment.

For additional reproducibility, Q1 and Q3 were independently re-solved with **SciPy/HiGHS mixed-integer optimization**, using the same source data and constraints. Q2 portfolio metrics and Q4 risk calculations were independently recomputed from the recovered project data and covariance matrix.

This gives the repository a second validation path instead of relying only on copied solver output.

## Q1 — Therapeutic-area risk-neutral model

Independent mixed-integer re-solve reproduced the exact selected project set and the submitted headline figures:

- selected projects: **46**
- development spend: **$874.48M**
- unused budget: **$125.52M**
- project eNPV: **$2,301.32M**
- risk-free return: **$3.7656M**
- total expected portfolio value: **$2,305.0856M**
- portfolio variance: **20,076,423.45**
- portfolio standard deviation: **$4,480.6722M**
- 95% VaR: **-$5,065.6202M**
- pipeline mix: **7 / 19 / 20** projects across the 1-year, 2–3-year, and 4–5-year buckets

## Q2 — Variance-constrained representative portfolio

The source-selected 46-project portfolio at variance cap `20,000,000` was recomputed directly from the recovered inputs:

- development spend: **$873.43M**
- unused budget: **$126.57M**
- project eNPV: **$2,299.47M**
- risk-free return: **$3.7971M**
- total expected portfolio value: **$2,303.2671M**
- recomputed variance: **19,986,424.85**
- portfolio standard deviation: **$4,470.6179M**
- 95% VaR: **-$5,050.8994M**

The recomputed variance is below the **20,000,000** cap.

## Q3 — Company-wide budget model

Independent mixed-integer re-solve reproduced the exact selected project set and submitted headline figures:

- selected projects: **53**
- development spend: **$986.95M**
- unused budget: **$13.05M**
- project eNPV: **$2,466.21M**
- risk-free return: **$0.3915M**
- total expected portfolio value: **$2,466.6015M**
- portfolio variance: **22,489,025.76**
- portfolio standard deviation: **$4,742.2596M**
- 95% VaR from the same covariance data: **-$5,334.4155M**

## Q4 — Extreme-risk checks

Using the recovered covariance matrix, the Q1 risk-neutral benchmark reproduces:

- total expected value: **$2,305.0856M**
- standard deviation: **$4,480.6722M**
- 95% VaR: **-$5,065.6202M**

The source maximum-VaR / minimum-risk solution is the all-cash portfolio:

- selected drug projects: **0**
- expected value: **$30.00M**
- standard deviation: **$0.00M**
- 95% VaR: **$30.00M**

The full Q4 Gurobi formulation remains in the public source code for authorized local reruns.

## Repository validation artifacts

- `notebooks/00_source_data_validation.ipynb` — executed independent validation notebook
- `src/independent_validation.py` — reusable command-line validation script
- `results/independent_validation.csv` — consolidated validation results

## Public-repository policy

The recovered assignment PDF states that the publication may not be reproduced, stored, used in a spreadsheet, or transmitted without permission from George Washington University. For that reason:

- the original course case PDF is not redistributed;
- the starter notebook is not redistributed;
- the raw `drugs.csv` and `drugs_cov.csv` source files are not committed publicly;
- the repository instead contains independently written portfolio code, derived results, figures, and documentation.
