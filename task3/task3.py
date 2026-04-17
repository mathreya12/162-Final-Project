from amplpy import AMPL

def main():
    ampl = AMPL()
    ampl.read("task3.mod")
    ampl.read_data("../project.dat")
    ampl.set_option("solver", "highs")
    ampl.solve()

    print(f"Task 3 Results")
    print(f"Net Optimized Cost: ${ampl.get_objective('NetCost').value()}k")
    
    y = ampl.get_variable("y")
    t = ampl.get_variable("T")
    
    total_revenue = 0
    print("\nVenue Revenue Contribution:")
    for i, instance in y.instances():
        if instance.value() > 0.5:
            v_rev = sum(inst.value() * 10 for (idx_i, j), inst in t.instances() if idx_i == i)
            total_revenue += v_rev
            print(f"Venue {i}: Generated ${v_rev}k in ticket sales")
            
    print(f"\nTotal Ticket Revenue: ${total_revenue}k")

if __name__ == "__main__":
    main()