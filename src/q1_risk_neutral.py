from gurobipy import Model, GRB, quicksum
from common import load_drug_data, THERAPEUTIC_AREA_BUDGETS


def solve_q1(data_dir=None, output_flag=1):
    df, projects = load_drug_data(data_dir)
    budgets = THERAPEUTIC_AREA_BUDGETS

    m = Model("zinca_q1_risk_neutral")
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
        quicksum(
            x[j] for j in projects
            if int(df.loc[df["Project"] == j, "Time_to_market"].iloc[0]) == 1
        ) >= 0.15 * N,
        name="pipeline_1_year",
    )
    m.addConstr(
        quicksum(
            x[j] for j in projects
            if int(df.loc[df["Project"] == j, "Time_to_market"].iloc[0]) in [2, 3]
        ) >= 0.20 * N,
        name="pipeline_2_3_years",
    )
    m.addConstr(
        quicksum(
            x[j] for j in projects
            if int(df.loc[df["Project"] == j, "Time_to_market"].iloc[0]) in [4, 5]
        ) >= 0.25 * N,
        name="pipeline_4_5_years",
    )

    m.setObjective(
        quicksum(
            df.loc[df["Project"] == j, "eNPV"].iloc[0] * x[j]
            for j in projects
        ) + 0.03 * quicksum(U[ta] for ta in budgets),
        GRB.MAXIMIZE,
    )

    m.optimize()

    selected = [j for j in projects if x[j].X > 0.5]
    total_spend = float(df.loc[df["Project"].isin(selected), "Cost"].sum())
    unused = float(sum(U[ta].X for ta in budgets))
    project_enpv = float(df.loc[df["Project"].isin(selected), "eNPV"].sum())
    risk_free_return = 0.03 * unused

    return {
        "model": m,
        "df": df,
        "selected": selected,
        "n_selected": len(selected),
        "spend": total_spend,
        "unused": unused,
        "project_enpv": project_enpv,
        "risk_free_return": risk_free_return,
        "total_value": project_enpv + risk_free_return,
        "unused_by_area": {ta: U[ta].X for ta in budgets},
    }


if __name__ == "__main__":
    result = solve_q1()
    for k in ["n_selected","spend","unused","project_enpv","risk_free_return","total_value"]:
        print(k, result[k])
    print("Selected projects:", result["selected"])
