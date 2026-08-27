import numpy as np
import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum
from common import load_drug_data, load_covariance, THERAPEUTIC_AREA_BUDGETS


def solve_q2(data_dir=None, variance_cap=None, minimize_variance=False, output_flag=0):
    df, projects = load_drug_data(data_dir)
    cov = load_covariance(data_dir)
    budgets = THERAPEUTIC_AREA_BUDGETS

    m = Model("zinca_q2_variance")
    m.Params.OutputFlag = output_flag

    x = m.addVars(projects, vtype=GRB.BINARY, name="x")
    U = m.addVars(budgets.keys(), lb=0.0, vtype=GRB.CONTINUOUS, name="U")

    for ta, B in budgets.items():
        area_projects = df.loc[df["TA"] == ta, "Project"].tolist()
        m.addConstr(
            quicksum(
                df.loc[df["Project"] == j, "Cost"].iloc[0] * x[j]
                for j in area_projects
            ) + U[ta] == B,
            name=f"budget_balance_{ta}",
        )

    N = quicksum(x[j] for j in projects)
    m.addConstr(
        quicksum(x[j] for j in projects
                 if int(df.loc[df["Project"] == j, "Time_to_market"].iloc[0]) == 1)
        >= 0.15 * N
    )
    m.addConstr(
        quicksum(x[j] for j in projects
                 if int(df.loc[df["Project"] == j, "Time_to_market"].iloc[0]) in [2, 3])
        >= 0.20 * N
    )
    m.addConstr(
        quicksum(x[j] for j in projects
                 if int(df.loc[df["Project"] == j, "Time_to_market"].iloc[0]) in [4, 5])
        >= 0.25 * N
    )

    var_expr = quicksum(
        cov.loc[i, j] * x[i] * x[j]
        for i in projects for j in projects
    )

    if variance_cap is not None:
        m.addQConstr(var_expr <= variance_cap, name="variance_cap")

    if minimize_variance:
        m.setObjective(var_expr, GRB.MINIMIZE)
    else:
        m.setObjective(
            quicksum(df.loc[df["Project"] == j, "eNPV"].iloc[0] * x[j]
                     for j in projects)
            + 0.03 * quicksum(U[ta] for ta in budgets),
            GRB.MAXIMIZE,
        )

    m.optimize()

    selected = [j for j in projects if x[j].X > 0.5]
    spend = float(df.loc[df["Project"].isin(selected), "Cost"].sum())
    project_enpv = float(df.loc[df["Project"].isin(selected), "eNPV"].sum())
    unused = float(sum(U[ta].X for ta in budgets))
    variance = sum(
        cov.loc[i, j]
        * (1 if i in selected else 0)
        * (1 if j in selected else 0)
        for i in projects for j in projects
    )

    return {
        "model": m,
        "selected": selected,
        "n_selected": len(selected),
        "spend": spend,
        "unused": unused,
        "project_enpv": project_enpv,
        "risk_free_return": 0.03 * unused,
        "total_value": project_enpv + 0.03 * unused,
        "variance": variance,
        "stdev": variance ** 0.5,
    }


def build_frontier(data_dir=None, n_points=20):
    risk_neutral = solve_q2(data_dir)
    caps = np.linspace(0, risk_neutral["variance"], n_points)

    sd, value = [], []
    for cap in caps:
        sol = solve_q2(data_dir, variance_cap=cap)
        sd.append(sol["stdev"])
        value.append(sol["total_value"])
    return sd, value


if __name__ == "__main__":
    rep = solve_q2(variance_cap=20_000_000)
    print(rep)

    sd, value = build_frontier()
    plt.plot(sd, value, marker="o")
    plt.xlabel("Standard deviation of portfolio value")
    plt.ylabel("Total expected portfolio value")
    plt.title("Efficient Frontier (Q2)")
    plt.grid(True)
    plt.show()
