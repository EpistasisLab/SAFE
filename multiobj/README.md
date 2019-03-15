The evolutionary multiobjective experiments described in M. Sipper, J. H. Moore, and R. J. Urbanowicz, "Solution and Fitness Evolution (SAFE): A Study of Multiobjective Problems", in _Proceedings of 2019 IEEE Congress On Evolutionary Computation_, 2019.

* `safe.py`: the main evolutionary algorithm
* `general.py`: additional general functions, also used in experiments other than robot
* `multiobj.py`: the multiobjective code
* `plot_front.py`: plotting the evolved Pareto fronts
* `f1f2.py`: function name (e.g., 'ZDT1') and evolved f1 and f2 fronts (used by `plot_front.py`)

To run: 
1. set parameters in general.py (GENERATIONS, SOLUTION_POP_SIZE, OBJECTIVE_POP_SIZE, etc.)    
2. run safe.py directly, or from command line: `python safe.py [algorithm] MultiObj [func_name]`    

At the end of a run the `results` folder will contain a csv file and a text file, e.g.:   
`SAFE_MultiObj_ZDT1_PDBTCC.csv`   
`SAFE_MultiObj_ZDT1_PDBTCC.csv`   

The csv contains a summary of the results. The txt file contains the fronts found and their _igd_ values.

To plot an evolved Pareto front simply copy front values from the txt file -- `f1` and `f2` lists -- into `plot_front.py` and in that file also set `func_name` to the correct problem, e.g., 'ZDT1'. Then run `plot_front.py`.
