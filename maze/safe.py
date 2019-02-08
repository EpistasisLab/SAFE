#
# SAFE, copyright 2018 moshe sipper, www.moshesipper.com
#
# Search algorithms: 'StandardEA', 'Novelty', 'SAFE', 'Random'
# Problem to solve: 'RobotMaze'

from random import seed
from copy import deepcopy 
from pathlib import Path # correctly use folders -- '/' or '\' -- on both Windows and Linux 
from sys import maxsize, argv, exit 
from statistics import mean, pstdev

import general as gl;

import robot as mod_robot;
modname= mod_robot;
    
def search_algorithm(run_num, algo, problem_type, *args): 
    # algo: 'StandardEA' / 'Novelty' / 'SAFE' / 'Random' 
    # problem_type: 'RobotMaze' 
    # args = (maze, start, target) 
        
    if problem_type == 'RobotMaze':
        maze, start, target = args[0], args[1], args[2]
    else: exit("error: unknown problem type") 
   
    global modname;
    generations = gl.GENERATIONS
    solution_pop_size = gl.SOLUTION_POP_SIZE
    if algo == 'Random': # random search, draw pop X gens random individuals
        solution_pop_size = solution_pop_size * generations
        generations = 1
        algo = 'StandardEA'

    solution_pop = modname.init_solution_pop(solution_pop_size)
    solution_fitnesses = [0] * solution_pop_size # fitness values of solution pop
    best_dist = maxsize # best distance to objective
    best_str = ""

    if algo == 'SAFE':
        objective_pop = modname.init_objective_pop()
        objective_fitnesses = [0] * gl.OBJECTIVE_POP_SIZE # fitness values of objective pop
        objective_best = 0 # best fitness of objective-function population

    archive_sol, archive_obj = [], [] # archives for novelty metric, solutions / obj funcs

    for gen in range(generations):   
        gl.myprint(gen)
        nextgen_solution_pop = [] # solution population of next gen
        nextgen_objective_pop = [] # objective-func population of next gen (SAFE)
        end_pos = [] # robot end positions
        novelty_scores = [] # novelty score of each individual
        
        for i in range(solution_pop_size):           
            if problem_type == 'RobotMaze':
                end_pos.append(modname.robot_move(maze, start, target, solution_pop[i]))
        
        if algo == 'Novelty' or algo == 'SAFE' or algo == 'StandardEA': # compute novelty metric
            for i in range(solution_pop_size):
                if problem_type == 'RobotMaze':
                    avg_nn, archive_sol = modname.novelty_metric_solutions(i, archive_sol, end_pos)
                else: exit("error: unknown problem type") 
                novelty_scores.append(avg_nn)

        #gl.myprint(novelty_scores_g)
        #gl.myprint(novelty_scores_p)

        for i in range(solution_pop_size): # compute fitness            
            if algo == 'StandardEA':
                if problem_type == 'RobotMaze':
                    solution_fitnesses[i] = modname.standard_fitness(end_pos[i], target) 
                                           #modname.safe_fitness(i, novelty_scores, [0.5,0.5], target, end_pos)
            elif algo == 'Novelty':             
                solution_fitnesses[i] = novelty_scores[i] # minus: turn maximization into minimization  
            elif algo == 'SAFE': 
                solution_fitnesses[i] = 0
                best_obj_index = 0
                for j in range(gl.OBJECTIVE_POP_SIZE):
                    if problem_type == 'RobotMaze':
                        fitness = modname.safe_fitness(i, novelty_scores, objective_pop[j], target, end_pos)
                    else: exit("error: unknown problem type")  
                    if fitness > solution_fitnesses[i]: 
                        solution_fitnesses[i] = fitness
                        best_obj_index = j
            else:
                exit("algo error: no such algo")

            if problem_type == 'RobotMaze':
                distance_to_goal = modname.distance_to_goal(end_pos[i], target) 
            else: exit("error: unknown problem type")     

            if (distance_to_goal < best_dist):       
                best_dist = distance_to_goal
                solution_best = deepcopy(solution_pop[i])
                best_str = str(gen) + "," + str(best_dist) + ",\"[" + ",".join([str(solution_best[i]) for i in range(len(solution_best))]) + "]\""                    
                if algo == 'SAFE':
                    objective_best = deepcopy(objective_pop[best_obj_index])
                    s = sum(objective_best)
                    best_str += ",\"[" + ",".join([str(objective_best[i]/s) for i in range(len(objective_best))]) + "]\"\n"
                else: best_str += "\n"    
                gl.myprint(best_str)

        if problem_type == 'RobotMaze' and best_dist <= modname.ROBO_DIST_SUCCESS: break # robot made it to goal
            
        sol_sort = sorted(solution_fitnesses, reverse=True)
        for i in range(gl.ELITISM):        
            nextgen_solution_pop.append(deepcopy(solution_pop[solution_fitnesses.index(sol_sort[i])]))
        
        for i in range(int(solution_pop_size/2) - int(gl.ELITISM/2)): #select-xo-mutate 
            parent1 = gl.selection(solution_pop, solution_fitnesses)
            parent2 = gl.selection(solution_pop, solution_fitnesses)
            child1, child2 = gl.single_point_crossover(parent1, parent2)
            nextgen_solution_pop.append(modname.solution_mutation(child1, *args))
            nextgen_solution_pop.append(modname.solution_mutation(child2, *args))

        
        if algo == 'SAFE': # evolve population of objective functions
            for i in range(gl.OBJECTIVE_POP_SIZE):
                avg_nn, archive_obj = gl.novelty_metric_genotypic(i, archive_obj, objective_pop)
                objective_fitnesses[i] = avg_nn

            obj_sort = sorted(objective_fitnesses, reverse=True) 
            for i in range(gl.ELITISM): 
                nextgen_objective_pop.append(deepcopy(objective_pop[objective_fitnesses.index(obj_sort[i])]))
            
            for i in range(int(gl.OBJECTIVE_POP_SIZE/2)- int(gl.ELITISM/2)): #select-xo-mutate 
                parent1 = gl.selection(objective_pop, objective_fitnesses)
                parent2 = gl.selection(objective_pop, objective_fitnesses)
                child1, child2 = gl.single_point_crossover(parent1, parent2)
                nextgen_objective_pop.append(modname.objective_mutation(child1))
                nextgen_objective_pop.append(modname.objective_mutation(child2))        
            
            objective_pop  = nextgen_objective_pop
    
        solution_pop = nextgen_solution_pop
        
    return best_str, best_dist, gen


# main    
def main():
# command line: safe [StandardEA/Novelty/SAFE/Random] RobotMaze [maze1/maze2] 
    
    global modname;
    seed() # initialize internal state of random number generator
    algo, problem_type, mazefile = 'SAFE', 'RobotMaze', 'maze1' # 'maze2'

    if len(argv) > 1: 
        algo = argv[1]
        problem_type = argv[2]
        if problem_type == 'RobotMaze': 
            mazefile = argv[3]
        else: exit("error: unknown problem_type")    
            
    if problem_type == 'RobotMaze':
        gl.myprint(algo, problem_type, mazefile)
        fn = mazefile
        modname = mod_robot;

    rnd = gl.rand_str(6)
    fname = "results/" + algo + "_" + fn + "_" + rnd + ".csv"
    gl.myprint(fname[8:-4])
    
    with open(Path(fname),'w') as f: 
        header = "gen,best_dist,best_sol"
        if algo == 'SAFE': header += ",best_obj\n"
        else: header += "\n"
        f.write(header)
    if problem_type=='RobotMaze':
        maze, start, target = modname.read_maze(mazefile)
 
    if problem_type=='RobotMaze': args = (maze, start, target)

    best_of_runs = [] 
    all_gens = []
    success_gens = []
    num_success = 0    
    for i in range(gl.NUM_EXPERIMENTS):
        gl.myprint("experiment",i+1)
        best_str, best_dist, gen = search_algorithm(i+1, algo, problem_type, *args) 
        best_of_runs.append(best_dist)
        all_gens.append(gen)
        if problem_type == 'RobotMaze' and best_dist <= modname.ROBO_DIST_SUCCESS:            
            num_success += 1
            success_gens.append(gen)
        with open(Path(fname),'a') as f: 
            f.write(best_str)
                            
    with open(Path(fname),'a') as f:
        f.write("\n")
        if problem_type == 'RobotMaze': 
            f.write("no. success: " + str(num_success))
            f.write("\n")
            if num_success > 0:
                f.write("success gens mean: " + str(round(mean(success_gens),1)) + " ("+ str(round(pstdev(success_gens),1)) + ")")
                f.write("\n")
        f.write("result mean: " + str(round(mean(best_of_runs),2)) + " ("+ str(round(pstdev(best_of_runs),2)) + ")")
        f.write("\n")
        f.write("all gens mean: " + str(round(mean(all_gens),1)) + " ("+ str(round(pstdev(all_gens),1)) + ")")
        f.write("\n")

if __name__== "__main__":
  main()
  