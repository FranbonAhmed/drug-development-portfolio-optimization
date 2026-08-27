import numpy as np
import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum
from common import load_drug_data, load_covariance, THERAPEUTIC_AREA_BUDGETS


def _add_pipeline_constraints(m, x, df, projects):
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


def solve_q4(data_dir=None, var_floor=None, maximize_var=False, output_flag=0):
    df, projects = load_drug_data(data_dir)
    cov = load_covariance(data_dir)
    budgets = THERAPEUTIC_AREA_BUDGETS

    # Source formulation uses a Cholesky-based norm representation.
    L = np.linalg.cholesky(cov.loc[projects, projects].values)

    m = Model("zinca_q4_var")
    m.Params.OutputFlag = output_flag

    x = m.addVars(projects, vtype=GRB.BINARY, name="x")
    U = m.addVars(budgets.keys(), lb=0.0, vtype=GRB.CONTINUOUS, name="U")
    h = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="h")
    tau = m.addVars(range(len(projects)), lb=-GRB.INFINITY,
                    vtype=GRB.CONTINUOUS, name="tau")

    for ta, B in budgets.items():
        area_projects = df.loc[df["TA"] == ta, "Project"].tolist()
        m.addConstr(
            quicksum(
                df.loc[df["Project"] == j, "Cost"].iloc[0] * x[j]
                for j in area_projects
            ) + U[ta] == B
        )

    _add_pipeline_constraints(m, x, df, projects)

    mu_total = (
        quicksum(df.loc[df["Project"] == j, "eNPV"].iloc[0] * x[j]
                 for j in projects)
        + 0.03 * quicksum(U[ta] for ta in budgets)
    )

    for k in range(len(projects)):
        m.addConstr(
            tau[k] == quicksum(
                float(L[i, k]) * x[projects[i]]
                for i in range(len(projects))
            )
        )

    m.addQConstr(
        quicksum(tau[k] * tau[k] for k in range(len(projects))) <= h * h,
        name="soc_norm",
    )

    if var_floor is not None:
        m.addConstr(mu_total - 1.645 * h >= var_floor, name="var_floor")

    if maximize_var:
        m.setObjective(mu_total - 1.645 * h, GRB.MAXIMIZE)
    else:
        m.setObjective(mu_total, GRB.MAXIMIZE)

    m.optimize()

    selected = [j for j in projects if x[j].X > 0.5]
    spend = float(df.loc[df["Project"].isin(selected), "Cost"].sum())
    unused = float(sum(U[ta].X for ta in budgets))
    total_value = float(df.loc[df["Project"].isin(selected), "eNPV"].sum()) + 0.03 * unused

    return {
        "model": m,
        "selected": selected,
        "n_selected": len(selected),
        "spend": spend,
        "unused": unused,
        "total_value": total_value,
        "h": h.X,
        "var95": total_value - 1.645 * h.X,
    }


def build_var_frontier(data_dir=None, risk_neutral_var95=-5065.62, n_points=15):
    safest = solve_q4(data_dir, maximize_var=True)
    floors = np.linspace(risk_neutral_var95, safest["var95"], n_points)

    var95, value = [], []
    for floor in floors:
        sol = solve_q4(data_dir, var_floor=floor)
        var95.append(sol["var95"])
        value.append(sol["total_value"])
    return var95, value


if __name__ == "__main__":
    safest = solve_q4(maximize_var=True)
    print("Maximum-VaR portfolio:", safest)

    no_loss = solve_q4(var_floor=0.0)
    print("Best portfolio with VaR >= 0:", no_loss)

    x, y = build_var_frontier()
    plt.plot(x, y, marker="o")
    plt.xlabel("95% VaR of portfolio value ($M)")
    plt.ylabel("Total expected portfolio value ($M)")
    plt.title("Efficient Frontier: Expected Value vs 95% VaR")
    plt.grid(True)
    plt.show()
