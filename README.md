# Olympic Venue Optimization (AMPL)

This project uses Mixed-Integer Programming (MIP) to optimize venue selection and sports scheduling for a regional Olympic event.

## Project Structure
* `project.dat`: Shared data file containing venue costs, capacities, and sport demands.
* `task1.mod/.py`: Basic venue selection (Cost Minimization).
* `task2.mod/.py`: Multi-week scheduling with session requirements.
* `task3.mod/.py`: Revenue optimization (Net Cost Minimization).

## How to Run
1. Ensure you have the `amplpy` library installed: `pip install amplpy`
2. Run any task: `python3 task1.py`