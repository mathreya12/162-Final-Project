import os
import sys
from contextlib import contextmanager

from amplpy import AMPL


MODEL_PATH = "../task4/task4.mod"
DATA_PATH  = "../project.dat"


@contextmanager
def _silent_stdout():
    # amplpy's solver output is written at the C level, so Python's
    # contextlib.redirect_stdout can't catch it. Redirect the fd instead.
    sys.stdout.flush()
    saved = os.dup(sys.stdout.fileno())
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, sys.stdout.fileno())
        yield
    finally:
        sys.stdout.flush()
        os.dup2(saved, sys.stdout.fileno())
        os.close(devnull)
        os.close(saved)

SCENARIOS = [
    ("Baseline (Task 4)",          10, 1.0),
    ("S1: profit $5 / ticket",      5, 1.0),
    ("S2: profit $15 / ticket",    15, 1.0),
    ("S3: demand -10%",            10, 0.9),
]


def _make_ampl(ticket_profit, demand_scale):
    ampl = AMPL()
    ampl.read(MODEL_PATH)
    ampl.read_data(DATA_PATH)
    ampl.get_parameter("ticket_profit").set(ticket_profit)
    ampl.get_parameter("demand_scale").set(demand_scale)
    ampl.set_option("solver", "highs")
    ampl.set_option("solver_msg", 0)
    return ampl


def solve_scenario(label, ticket_profit, demand_scale):
    ampl = _make_ampl(ticket_profit, demand_scale)
    with _silent_stdout():
        ampl.solve()
    net    = ampl.get_objective("NetCost").value()
    y      = dict(ampl.get_variable("y").get_values().to_dict())
    x      = dict(ampl.get_variable("x").get_values().to_dict())
    h      = dict(ampl.get_variable("h").get_values().to_dict())
    b2     = dict(ampl.get_variable("b2").get_values().to_dict())
    b3     = dict(ampl.get_variable("b3").get_values().to_dict())
    Tvals  = dict(ampl.get_variable("T").get_values().to_dict())
    venues = list(ampl.get_set("VENUES").members())
    costs  = {v: ampl.get_parameter("cost")[v] for v in venues}
    fixed_cost = sum(costs[v] * round(y[v]) for v in venues)
    bus_fixed  = 20 * (sum(round(v) for v in b2.values()) + sum(round(v) for v in b3.values()))
    tickets    = sum(Tvals.values())
    revenue    = ticket_profit * tickets
    return dict(label=label, ticket_profit=ticket_profit, demand_scale=demand_scale,
                net=net, y=y, x=x, h=h, b2=b2, b3=b3, T=Tvals,
                fixed_cost=fixed_cost, bus_fixed=bus_fixed,
                tickets=tickets, revenue=revenue)


def evaluate_plan(plan, ticket_profit, demand_scale):
    # Fix integer decisions from `plan`; let only T / flow / ticket LP re-optimize.
    ampl = _make_ampl(ticket_profit, demand_scale)
    for k, v in plan["y"].items():
        ampl.get_variable("y")[k].fix(round(v))
    for k, v in plan["x"].items():
        ampl.get_variable("x")[k].fix(round(v))
    for k, v in plan["h"].items():
        ampl.get_variable("h")[k].fix(round(v))
    for k, v in plan["b2"].items():
        ampl.get_variable("b2")[k].fix(round(v))
    for k, v in plan["b3"].items():
        ampl.get_variable("b3")[k].fix(round(v))
    with _silent_stdout():
        ampl.solve()
    if ampl.get_value("solve_result") != "solved":
        return None
    net     = ampl.get_objective("NetCost").value()
    tickets = sum(ampl.get_variable("T").get_values().to_dict().values())
    return net, tickets


def _fmt_plan(p):
    venues_open = sorted(v for v, val in p["y"].items() if val > 0.5)
    nets2  = [f"{a}-{b}"     for (a, b),     val in p["b2"].items() if val > 0.5]
    nets3  = [f"{a}-{b}-{c}" for (a, b, c),  val in p["b3"].items() if val > 0.5]
    return venues_open, nets2, nets3


def main():
    plans = []
    for label, pr, ds in SCENARIOS:
        print("=" * 68)
        print(f"Solving: {label}  (profit=${pr}/ticket, demand_scale={ds})")
        print("=" * 68)
        p = solve_scenario(label, pr, ds)
        plans.append(p)
        venues_open, nets2, nets3 = _fmt_plan(p)
        print(f"  Net cost         : ${p['net']:>10.2f}k")
        print(f"  Venue fixed cost : ${p['fixed_cost']:>10.2f}k")
        print(f"  Bus fixed cost   : ${p['bus_fixed']:>10.2f}k")
        print(f"  Tickets sold     : {p['tickets']:>10.2f}k")
        print(f"  Ticket revenue   : ${p['revenue']:>10.2f}k")
        print(f"  Venues opened    : {', '.join(venues_open)}")
        print(f"  2-venue networks : {', '.join(nets2) if nets2 else '(none)'}")
        print(f"  3-venue networks : {', '.join(nets3) if nets3 else '(none)'}")
        print()

    print("=" * 68)
    print("Cross-evaluation (each plan re-scored under each scenario)")
    print("  rows = plan source, cols = evaluation scenario")
    print("=" * 68)
    label_col = "Plan vs. Scenario"
    header = f"{label_col:28s}" + "".join(f"{s[0][:18]:>20s}" for s in SCENARIOS)
    print(header)
    for src in plans:
        row = [src["label"]]
        for (_, pr, ds) in SCENARIOS:
            res = evaluate_plan(src, pr, ds)
            row.append("INF" if res is None else f"${res[0]:+.1f}k")
        print(f"{row[0]:28s}" + "".join(f"{cell:>20s}" for cell in row[1:]))

    print()
    print("Sub-optimality gap vs. each scenario's own optimum:")
    print("=" * 68)
    optimal_by_scen = [p["net"] for p in plans]
    print(header)
    for src in plans:
        row = [src["label"]]
        for j, (_, pr, ds) in enumerate(SCENARIOS):
            res = evaluate_plan(src, pr, ds)
            gap = res[0] - optimal_by_scen[j] if res else float("inf")
            row.append(f"{gap:+.1f}k")
        print(f"{row[0]:28s}" + "".join(f"{cell:>20s}" for cell in row[1:]))


if __name__ == "__main__":
    main()
