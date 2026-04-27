# Olympic Venue Optimization (AMPL)

This project uses Mixed-Integer Programming (MIP) to optimize venue selection and sports scheduling for a regional Olympic event.

## Project Structure
* `project.dat`: Shared data file containing venue costs, capacities, and sport demands.
* `task1/task1.mod`, `task1.py`: Basic venue selection (Cost Minimization).
* `task2/task2.mod`, `task2.py`: Multi-week scheduling with session requirements.
* `task3/task3.mod`, `task3.py`: Revenue optimization (Net Cost Minimization).
* `task4/task4.mod`, `task4.py`: Adds explicit weekly scheduling, 2- and 3-venue bus networks ($20k each), bus-induced ticket flow between venues active in the same week, and the same-week-per-sport rule.
* `task5/task5.py`: Sensitivity analysis on Task 4. Re-solves under profit = $5, profit = $15, and demand = 90% of nominal, then cross-evaluates each plan under every other scenario's parameters. Re-uses `task4/task4.mod`.

## How to Run
1. Install `amplpy` and the HiGHS solver:
   ```
   pip install amplpy
   python3 -m amplpy.modules install highs
   ```
2. Run any task from its own directory, since the scripts use relative paths:
   ```
   cd task1 && python3 task1.py
   cd ../task2 && python3 task2.py
   cd ../task3 && python3 task3.py
   cd ../task4 && python3 task4.py
   cd ../task5 && python3 task5.py
   ```

## Results Summary
| Task | Objective | Result |
|------|-----------|--------|
| 1 | Min venue fixed cost | $2,350k, 7 venues |
| 2 | + multi-session scheduling | $2,850k, 8 venues |
| 3 | − $10 per ticket revenue | $250k net, 260k tickets |
| 4 | + weekly schedule, bus networks | −$28.7k net, 291.87k tickets, 2 bus networks |
| 5 | Sensitivity to profit and demand | Venue set insensitive; 3rd bus network appears at $15/ticket |

Task 4 and Task 5 share the same `.mod` file (`task4/task4.mod`). All tunable parameters (`ticket_profit`, `bus_cost`, `demand_scale`) have defaults in the model and can be overridden from Python via `ampl.get_parameter(...).set(...)`.
