# Source Data Validation

The original assignment files were recovered after the public portfolio repository had already been assembled.

## Recovered source files

- `drugs.csv`
  - 114 candidate projects
  - therapeutic area
  - time-to-market
  - expected net present value (eNPV)
  - current-year development cost

- `drugs_cov.csv`
  - 114 × 114 covariance matrix
  - symmetric in the recovered file
  - positive definite in local numerical validation

- `drug.ipynb`
  - original starter / template notebook
  - contains the data-loading setup, therapeutic-area budgets, 3% risk-free rate, covariance loading, and placeholder sections for model variables, constraints, objective, and output

## Independent local validation

The original CSVs were used locally to check that the public portfolio results correspond to the recovered source data.

### Q1 — Therapeutic-area risk-neutral model

Independent local mixed-integer re-solve reproduced:

- selected projects: **46**
- development spend: **$874.48M**
- unused budget: **$125.52M**
- project eNPV: **$2,301.32M**
- risk-free return: **$3.7656M**
- total expected portfolio value: **$2,305.0856M**
- portfolio variance: **20,076,423.45**
- portfolio standard deviation: **$4,480.6722M**
- 95% VaR: **-$5,065.6202M**

These reproduce the submitted headline figures to rounding.

### Q3 — Company-wide budget model

Independent local mixed-integer re-solve reproduced:

- selected projects: **53**
- development spend: **$986.95M**
- unused budget: **$13.05M**
- project eNPV: **$2,466.21M**
- risk-free return: **$0.3915M**
- total expected portfolio value: **$2,466.6015M**
- portfolio standard deviation: **$4,742.2596M**

These also reproduce the submitted headline figures to rounding.

## Q2 and Q4

The source submission contains the original Gurobi code and outputs for the variance-constrained and 95% VaR models. The public repository preserves those formulations and source-reported outputs. They can be rerun locally with the recovered source files and a valid Gurobi installation / license.

## Public-repository policy

The recovered assignment PDF states that the publication may not be reproduced, stored, used in a spreadsheet, or transmitted without permission from George Washington University. For that reason:

- the course case PDF is not redistributed;
- the starter notebook is not redistributed;
- the raw `drugs.csv` and `drugs_cov.csv` source files are not committed publicly;
- the repository instead contains independently written portfolio code, derived results, figures, and documentation.
