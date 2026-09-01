"""Independent validation of the Zinca portfolio results.

This script intentionally uses SciPy/HiGHS rather than Gurobi for the two
linear mixed-integer models (Q1 and Q3). Its purpose is to verify that the
headline portfolio results are reproducible from authorized local copies of
`drugs.csv` and `drugs_cov.csv`.

The original course data are not distributed with the public repository.
Place authorized copies in `data/` before running this script.
"""

from pathlib import Path
import hashlib
import math
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DRUGS = DATA_DIR / "drugs.csv"
COV = DATA_DIR / "drugs_cov.csv"

BUDGETS = {
    "Oncology": 100.0,
    "Cardiovascular": 200.0,
    "Respiratory and dermatology": 150.0,
    "Transplantation": 100.0,
    "Rheumatology and hormone therapy": 300.0,
    "Central nervous system": 100.0,
    "Ophtalmics": 50.0,
}

Q2_SELECTED = [
    3,4,6,7,13,17,18,20,21,22,24,25,27,28,29,30,39,40,42,43,44,47,
    48,50,57,58,62,66,69,72,76,77,78,86,91,98,99,101,102,104,105,106,
    109,110,111,112,
]


def load_data():
    if not DRUGS.exists() or not COV.exists():
        raise FileNotFoundError(
            "Place authorized copies of drugs.csv and drugs_cov.csv in data/."
        )

    raw = pd.read_csv(DRUGS)
    data = raw.set_index("Project")
    projects = [str(i) for i in range(1, 115)]
    ta = data.loc["TA", projects]
    ttm = data.loc["Time-to-market", projects].astype(int)
    enpv = data.loc["eNPV", projects].astype(float)
    cost = data.loc["Cost this Year", projects].astype(float)

    cov = pd.read_csv(COV, index_col=0)
    cov.index = cov.index.map(str)
    cov.columns = cov.columns.map(str)
    cov = cov.loc[projects, projects].astype(float)
    return raw, projects, ta, ttm, enpv, cost, cov


def portfolio_metrics(selected, projects, ttm, enpv, cost, cov):
    selected = [str(i) for i in selected]
    spend = float(cost[selected].sum())
    unused = 1000.0 - spend
    project_enpv = float(enpv[selected].sum())
    risk_free = 0.03 * unused
    total_value = project_enpv + risk_free

    x = np.array([1.0 if j in selected else 0.0 for j in projects])
    variance = float(x @ cov.values @ x)
    stdev = math.sqrt(variance)
    var95 = total_value - 1.645 * stdev

    return {
        "n_selected": len(selected),
        "spend_m": spend,
        "unused_m": unused,
        "project_enpv_m": project_enpv,
        "risk_free_return_m": risk_free,
        "total_expected_value_m": total_value,
        "variance": variance,
        "stdev_m": stdev,
        "var95_m": var95,
        "pipeline_1yr": int((ttm[selected] == 1).sum()),
        "pipeline_2_3yr": int(ttm[selected].isin([2, 3]).sum()),
        "pipeline_4_5yr": int(ttm[selected].isin([4, 5]).sum()),
    }


def solve_linear_model(companywide, projects, ta, ttm, enpv, cost):
    objective = -(enpv.values - 0.03 * cost.values)
    A, lb, ub = [], [], []

    if companywide:
        A.append(cost.values)
        lb.append(-np.inf)
        ub.append(1000.0)
    else:
        for area, budget in BUDGETS.items():
            A.append(np.where(ta.values == area, cost.values, 0.0))
            lb.append(-np.inf)
            ub.append(budget)

    for years, pct in [([1], 0.15), ([2, 3], 0.20), ([4, 5], 0.25)]:
        indicator = np.isin(ttm.values, years).astype(float)
        A.append(pct * np.ones(114) - indicator)
        lb.append(-np.inf)
        ub.append(0.0)

    result = milp(
        objective,
        integrality=np.ones(114),
        bounds=Bounds(np.zeros(114), np.ones(114)),
        constraints=LinearConstraint(np.asarray(A), np.asarray(lb), np.asarray(ub)),
    )
    if not result.success:
        raise RuntimeError(result.message)
    return [int(projects[i]) for i, value in enumerate(result.x) if value > 0.5]


def main():
    raw, projects, ta, ttm, enpv, cost, cov = load_data()

    symmetry_error = float(np.max(np.abs(cov.values - cov.values.T)))
    min_eigenvalue = float(np.linalg.eigvalsh(cov.values).min())
    np.linalg.cholesky(cov.values)

    print("SOURCE DATA")
    print("drugs.csv shape:", raw.shape)
    print("drugs_cov.csv shape:", cov.shape)
    print("drugs.csv SHA256:", hashlib.sha256(DRUGS.read_bytes()).hexdigest())
    print("drugs_cov.csv SHA256:", hashlib.sha256(COV.read_bytes()).hexdigest())
    print("max covariance symmetry error:", symmetry_error)
    print("minimum covariance eigenvalue:", min_eigenvalue)

    q1_selected = solve_linear_model(False, projects, ta, ttm, enpv, cost)
    q3_selected = solve_linear_model(True, projects, ta, ttm, enpv, cost)

    q1 = portfolio_metrics(q1_selected, projects, ttm, enpv, cost, cov)
    q2 = portfolio_metrics(Q2_SELECTED, projects, ttm, enpv, cost, cov)
    q3 = portfolio_metrics(q3_selected, projects, ttm, enpv, cost, cov)

    rows = [
        {"model": "Q1 independently solved", **q1},
        {"model": "Q2 source portfolio recomputed", **q2},
        {"model": "Q3 independently solved", **q3},
        {
            "model": "Q4 all-cash extreme",
            "n_selected": 0,
            "spend_m": 0.0,
            "unused_m": 1000.0,
            "project_enpv_m": 0.0,
            "risk_free_return_m": 30.0,
            "total_expected_value_m": 30.0,
            "variance": 0.0,
            "stdev_m": 0.0,
            "var95_m": 30.0,
            "pipeline_1yr": 0,
            "pipeline_2_3yr": 0,
            "pipeline_4_5yr": 0,
        },
    ]
    table = pd.DataFrame(rows)
    print("\nVALIDATED RESULTS")
    print(table.to_string(index=False))

    print("\nQ2 variance cap check:", q2["variance"] <= 20_000_000 + 1e-6)
    print("Q1 95% VaR:", q1["var95_m"])
    print("Q4 all-cash 95% VaR: 30.0")


if __name__ == "__main__":
    main()
