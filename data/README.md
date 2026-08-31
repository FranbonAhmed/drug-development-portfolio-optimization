# Data Setup

The original assignment uses two source files:

```text
data/
├── drugs.csv
└── drugs_cov.csv
```

These files were recovered after the public portfolio was created and were used **locally** to validate the portfolio implementation. They are intentionally **not committed to this public repository**.

## Why the raw source files are not public

The accompanying course case states that the publication may not be reproduced, stored, used in a spreadsheet, or transmitted without permission from George Washington University. To avoid redistributing course materials or assignment data, this repository publishes the independently written modeling code, derived results, charts, and portfolio documentation instead.

The repository `.gitignore` excludes `data/*.csv` so the source files are less likely to be committed accidentally.

## `drugs.csv`

The recovered file has:

- **4 rows × 115 columns** including the `Project` descriptor column;
- **114 candidate projects** numbered 1 through 114;
- rows for:
  - `TA`
  - `Time-to-market`
  - `eNPV`
  - `Cost this Year`

The portfolio scripts reshape this wide-format input into one row per candidate project.

## `drugs_cov.csv`

The recovered covariance file is a **114 × 114** matrix whose row and column labels correspond to project IDs 1 through 114.

Local validation confirmed that the recovered covariance matrix is symmetric and positive definite.

## Rerunning locally

If you are authorized to use the original course files, rename / copy them locally as:

```text
data/drugs.csv
data/drugs_cov.csv
```

Accepted alternate filenames in the scripts are also:

- `drugs(1).csv`
- `drugs_cov(1).csv`

Then run the notebooks in numerical order with a valid Gurobi installation and license.

The raw source files themselves should remain local unless redistribution permission is confirmed.
