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
    
    print("\nVenue Revenue Contribution:")
    total_revenue = 0

    t_values = t.get_values().to_dict() 
    y_values = y.get_values().to_dict()

    for venue in ampl.get_set("VENUES"):
        if y_values[venue] > 0.5:
            v_rev = sum(t_values[venue, sport] * 10 for sport in ampl.get_set("SPORTS"))
            total_revenue += v_rev
            print(f"Venue {venue}: Generated ${v_rev}k in ticket sales")
            
    print(f"\nTotal Ticket Revenue: ${total_revenue}k")

if __name__ == "__main__":
    main()