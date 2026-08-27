# Data Setup

This repository expects the same two source files used in the submitted project:

```text
data/
├── drugs.csv
└── drugs_cov.csv
```

Accepted alternate filenames in the scripts:

- `drugs(1).csv`
- `drugs_cov(1).csv`

## `drugs.csv`

The source code expects a wide-format file where:

- the first column is named `Project`;
- project columns are numbered `1` through `114`;
- rows include:
  - `TA`
  - `Time-to-market`
  - `eNPV`
  - `Cost this Year`

The portfolio scripts reshape this file into one row per candidate project.

## `drugs_cov.csv`

The covariance file is read with the first column as the index and is expected to contain a 114 x 114 covariance matrix whose row and column labels correspond to project IDs `1` through `114`.

## Why the raw data are not included

The uploaded submission report contains code and output but not the underlying CSV files. The repository therefore preserves the source-reported results while keeping the executable code ready for the original data files.
