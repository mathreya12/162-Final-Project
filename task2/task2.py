from amplpy import AMPL

def main():
    ampl = AMPL()
    ampl.read("task2.mod")
    ampl.read_data("../project.dat")
    ampl.set_option("solver", "highs")
    ampl.solve()

    print(f"Task 2 Results")
    print(f"Total Multi-Week Cost: ${ampl.get_objective('TotalCost').value()}k")
    
    s = ampl.get_variable("s")
    for j in ampl.get_set("SPORTS"):
        venues = [i for (i, idx_j), inst in s.instances() if idx_j == j and inst.value() > 0.5]
        print(f"Sport {j} sessions at: {', '.join(venues)}")

if __name__ == "__main__":
    main()