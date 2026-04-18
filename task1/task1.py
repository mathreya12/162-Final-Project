from amplpy import AMPL

def main():
    ampl = AMPL()
    ampl.read("task1.mod")
    ampl.read_data("../project.dat")
    ampl.set_option("solver", "highs")
    ampl.solve()

    print("Task 1 Results") 
    print(f"Total Activation Cost: ${ampl.get_objective('TotalCost').value()}k")
    
    y = ampl.get_variable("y")
    x = ampl.get_variable("x")
    
    for i, instance in y.instances():
        if instance.value() > 0.5:
            assigned = [j for (idx_i, j), inst in x.instances() if idx_i == i[0] and inst.value() > 0.5]
            print(f"Venue {i} active: hosting {', '.join(assigned)}")

if __name__ == "__main__":
    main()