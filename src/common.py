from pathlib import Path
import pandas as pd


def locate_file(data_dir: Path, names):
    """Return the first existing file from a list of allowed names."""
    for name in names:
        path = data_dir / name
        if path.exists():
            return path
    raise FileNotFoundError(
        f"None of these files were found in {data_dir}: {', '.join(names)}"
    )


def load_drug_data(data_dir=None):
    """
    Load the wide-format drug project file used by the source assignment.

    Expected rows in the first column named 'Project':
      - TA
      - Time-to-market
      - eNPV
      - Cost this Year

    Project columns are numbered 1..114.
    """
    if data_dir is None:
        data_dir = Path(__file__).resolve().parents[1] / "data"
    else:
        data_dir = Path(data_dir)

    drugs_file = locate_file(data_dir, ["drugs.csv", "drugs(1).csv"])
    raw = pd.read_csv(drugs_file)

    projects = [str(i) for i in range(1, 115)]
    rows = []
    for j in projects:
        rows.append({
            "Project": j,
            "TA": raw.loc[raw["Project"] == "TA", j].values[0],
            "Time_to_market": int(
                raw.loc[raw["Project"] == "Time-to-market", j].values[0]
            ),
            "eNPV": float(raw.loc[raw["Project"] == "eNPV", j].values[0]),
            "Cost": float(raw.loc[raw["Project"] == "Cost this Year", j].values[0]),
        })

    return pd.DataFrame(rows), projects


def load_covariance(data_dir=None):
    """Load and normalize the project covariance matrix."""
    if data_dir is None:
        data_dir = Path(__file__).resolve().parents[1] / "data"
    else:
        data_dir = Path(data_dir)

    cov_file = locate_file(data_dir, ["drugs_cov.csv", "drugs_cov(1).csv"])
    cov = pd.read_csv(cov_file, index_col=0)
    cov.index = cov.index.map(str)
    cov.columns = cov.columns.map(str)
    return cov


THERAPEUTIC_AREA_BUDGETS = {
    "Oncology": 100.0,
    "Cardiovascular": 200.0,
    "Respiratory and dermatology": 150.0,
    "Transplantation": 100.0,
    "Rheumatology and hormone therapy": 300.0,
    "Central nervous system": 100.0,
    "Ophtalmics": 50.0,
}
