from amplpy import AMPL


def solve(ticket_profit=10, bus_cost=20, demand_scale=1.0, label="Task 4"):
    ampl = AMPL()
    ampl.read("task4.mod")
    ampl.read_data("../project.dat")
    ampl.get_parameter("ticket_profit").set(ticket_profit)
    ampl.get_parameter("bus_cost").set(bus_cost)
    ampl.get_parameter("demand_scale").set(demand_scale)
    ampl.set_option("solver", "highs")
    ampl.solve()

    net_cost = ampl.get_objective("NetCost").value()
    y  = ampl.get_variable("y").get_values().to_dict()
    x  = ampl.get_variable("x").get_values().to_dict()
    h  = ampl.get_variable("h").get_values().to_dict()
    T  = ampl.get_variable("T").get_values().to_dict()
    b2 = ampl.get_variable("b2").get_values().to_dict()
    b3 = ampl.get_variable("b3").get_values().to_dict()
    f  = ampl.get_variable("f").get_values().to_dict()

    t_max = int(ampl.get_parameter("T_MAX").value())
    venues = list(ampl.get_set("VENUES").members())
    sports = list(ampl.get_set("SPORTS").members())

    print(f"\n{label}")
    print(f"  profit=${ticket_profit}/ticket, bus_cost=${bus_cost}k, demand_scale={demand_scale}")
    print(f"Net cost: ${net_cost:.2f}k")

    fixed_cost = sum(ampl.get_parameter("cost")[v] * y.get(v, 0) for v in venues)
    bus_fixed  = bus_cost * (sum(b2.values()) + sum(b3.values()))
    revenue    = ticket_profit * sum(T.values())
    print(f"  Venue fixed cost : ${fixed_cost:.2f}k")
    print(f"  Bus fixed cost   : ${bus_fixed:.2f}k")
    print(f"  Ticket revenue   : ${revenue:.2f}k "
          f"(tickets = {sum(T.values()):.2f}k)")

    print("\nVenues opened:")
    for v in venues:
        if y.get(v, 0) > 0.5:
            print(f"  {v}  cost ${ampl.get_parameter('cost')[v]:.0f}k, "
                  f"cap {ampl.get_parameter('capacity')[v]:.0f}k, "
                  f"kappa {int(ampl.get_parameter('max_sports')[v])}")

    print("\nWeekly schedule:")
    for t in range(1, t_max + 1):
        print(f"  Week {t}:")
        for v in venues:
            assigned = [s for s in sports
                        if (v, s, t) in x and x[(v, s, t)] > 0.5]
            if assigned:
                tix = T.get((v, t), 0)
                print(f"    {v}: {', '.join(assigned)}  ({tix:.2f}k tickets)")

    print("\nSport schedule:")
    for s in sports:
        wk = next((t for t in range(1, t_max + 1)
                   if h.get((s, t), 0) > 0.5), None)
        vs = [v for v in venues if (v, s, wk) in x and x[(v, s, wk)] > 0.5]
        print(f"  {s}: week {wk}  @ {', '.join(vs)}")

    print("\nBus networks:")
    any_bus = False
    for (p, q), val in b2.items():
        if val > 0.5:
            any_bus = True
            print(f"  2-venue: {p} <-> {q}")
    for (p, q, r), val in b3.items():
        if val > 0.5:
            any_bus = True
            print(f"  3-venue: {p} <-> {q} <-> {r}")
    if not any_bus:
        print("  (none)")

    print("\nBus flow (src -> dst, week, tickets k):")
    any_flow = False
    for (i, k, t), val in f.items():
        if val > 1e-6:
            any_flow = True
            print(f"  {i} -> {k}  wk {t}:  {val:.2f}k")
    if not any_flow:
        print("  (none)")

    return {
        "net_cost": net_cost,
        "fixed_cost": fixed_cost,
        "bus_fixed": bus_fixed,
        "revenue": revenue,
        "tickets": sum(T.values()),
        "y": y, "x": x, "T": T, "b2": b2, "b3": b3, "f": f,
    }


if __name__ == "__main__":
    solve()
