#
#
# SAFE, copyright 2019 moshe sipper, www.moshesipper.com
#
# cmd line: python safe.py [algorithm] MultiObj [func_name] 
#
# Search algorithms: 'StandardEA', 'Novelty', 'SAFE', 'Random'
# Problem to solve: 'MultiObj'

from enum import Enum
Algorithm = Enum('Algorithms', 'StandardEA  Novelty  SAFE  Random') # Search algorithms
Problem = Enum('Problem', 'RobotMaze  MultiObj') # Problems to solve, use only MultiObj here

# if not using command line init to:
algo         = Algorithm.SAFE
problem      = Problem.MultiObj
func_name    = 'ZDT1' # for Problem.MultiObj 
RESULTS_FOLDER = 'results/'

from random import seed
from copy import deepcopy 
from pathlib import Path # correctly use folders -- '/' or '\' -- on both Windows and Linux 
from sys import maxsize, argv, exit 
from statistics import mean, pstdev

from plot_front import compute_igd, true_front
import general as gl
import multiobj as mod_multiobj
modname = mod_multiobj
    
def search_algorithm(run_num, algo, problem, *args):         
    if problem != Problem.MultiObj: exit("error: unknown problem type") 
   
    global modname
    generations = gl.GENERATIONS
    solution_pop_size = gl.SOLUTION_POP_SIZE
    if algo == Algorithm.Random: # random search, draw pop*gens random individuals
        solution_pop_size = solution_pop_size * generations
        generations = 1
        algo = Algorithm.StandardEA

    solution_pop = modname.init_solution_pop(solution_pop_size)
    solution_fitnesses = [0] * solution_pop_size # fitness values of solution pop
    best_dist = maxsize # best distance to objective
    best_str = ""
    best_f1, best_f2 = maxsize, maxsize # for MultiObj

    if algo == Algorithm.SAFE:
        objective_pop = modname.init_objective_pop()
        objective_fitnesses = [0] * gl.OBJECTIVE_POP_SIZE # fitness values of objective pop
        objective_best = 0 # best fitness of objective-function population

    archive_obj = [] # archive for novelty metric of objective funcs
    pareto_front = [] # for multiobjective

    for gen in range(generations):   
        gl.myprint("gen", gen)
        if problem == Problem.MultiObj: gl.myprint("PF len: ", len(pareto_front))
        
        nextgen_solution_pop = [] # solution population of next gen
        nextgen_objective_pop = [] # objective-func population of next gen (when algo == 'SAFE')
        num_dom = [] # number of dominating solutions for multiobj
        novelty_scores = [] # novelty score of each individual
        f1f2 = [] # for MultiObj
        
        for i in range(solution_pop_size):           
            if problem == Problem.MultiObj:
                v = [modname.f1(solution_pop[i]), modname.f2(solution_pop[i])]                
                f1f2.append(v)
                if v[0] < best_f1: best_f1 = v[0]
                if v[1] < best_f2: best_f2 = v[1]
        
        if algo == Algorithm.Novelty or algo == Algorithm.SAFE or algo == Algorithm.StandardEA: 
            for i in range(solution_pop_size): # compute novelty metric of solutions
                avg_nn = 0 # not used for MultiObj problem, used for other problems, so just set to 0

        for i in range(solution_pop_size): # compute fitness            
            if algo == Algorithm.StandardEA:
                exit("Standard EA not implemented for MultiObj")
                #if problem == Problem.MultiObj:    
                #    solution_fitnesses[i] = gl.SOLUTION_POP_SIZE - num_dom[i]
            elif algo == Algorithm.Novelty:
                solution_fitnesses[i] = novelty_scores[i] 
            elif algo == Algorithm.SAFE: 
                solution_fitnesses[i] = 0
                best_obj_index = 0
                for j in range(gl.OBJECTIVE_POP_SIZE):
                    if problem == Problem.MultiObj:
                        ff = modname.safe_fitness(solution_pop[i], objective_pop[j])
                        if ff != 0: fitness = 1/ff
                        else: fitness = maxsize
                    if fitness > solution_fitnesses[i]: 
                        solution_fitnesses[i] = fitness
                        best_obj_index = j

            if problem == Problem.MultiObj: # update pareto front
                    nd = modname.num_dominating_solutions(solution_pop[i], solution_pop)
                    num_dom.append(nd)
                    if nd == 0: 
                        pareto_front, added = modname.add_to_pareto_front(solution_pop[i], pareto_front)
                        
            if problem == Problem.MultiObj:
                distance_to_goal = 1/(1+len(pareto_front))

            if (distance_to_goal < best_dist):       
                best_dist = distance_to_goal
                solution_best = deepcopy(solution_pop[i])
                best_str = str(gen) + "," + str(best_dist) + ",\"[" + ",".join([str(solution_best[i]) for i in range(len(solution_best))]) + "]\""                    
                if algo == Algorithm.SAFE:
                    objective_best = deepcopy(objective_pop[best_obj_index])
                    s = sum(objective_best)
                    best_str += ",\"[" + ",".join([str(objective_best[i]/s) for i in range(len(objective_best))]) + "]\"\n"
                else: best_str += "\n"    
                gl.myprint(best_str)
   
        sol_sort = sorted(solution_fitnesses, reverse=True)
        for i in range(gl.ELITISM):        
            nextgen_solution_pop.append(deepcopy(solution_pop[solution_fitnesses.index(sol_sort[i])]))
        
        for i in range(int(solution_pop_size/2) - int(gl.ELITISM/2)): #select-xo-mutate 
            parent1 = gl.selection(solution_pop, solution_fitnesses)
            parent2 = gl.selection(solution_pop, solution_fitnesses)
            child1, child2 = gl.single_point_crossover(parent1, parent2)
            nextgen_solution_pop.append(modname.solution_mutation(child1, *args))
            nextgen_solution_pop.append(modname.solution_mutation(child2, *args))
        
        if algo == Algorithm.SAFE and (gen % gl.OBJECTIVE_GAP == 0): 
            gl.myprint("evolving objective functions at gen", gen)
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
        
    return best_str, best_dist, gen, pareto_front, solution_best

# main    
def main():    
    global modname, algo, problem, func_name
    seed() # init internal state of random number generator
    gl.myprint("-------------------------------------")
    
    if len(argv) > 1: 
        algo = Algorithm[argv[1]]
        problem = Problem[argv[2]]
        if problem == Problem.MultiObj:   
            func_name = argv[3]
        else: exit("error: unknown problem")   
                
    if problem == Problem.MultiObj:     
        gl.myprint(algo.name, problem.name, func_name)
        modname = mod_multiobj
        fn = 'MultiObj' + "_" + func_name
        modname.set_func_name(func_name)

    rnd = gl.rand_str(6)
    fname = RESULTS_FOLDER + algo.name + "_" + fn + "_" + rnd + ".csv"
    gl.myprint(fname[8:-4])
    
    if problem == Problem.MultiObj:
        pareto_fname = RESULTS_FOLDER + str(algo) + "_" + "front_" + fn + "_" + rnd + ".txt"

    with open(Path(fname),'w') as f: 
        header = "gen,best_dist,best_sol"
        if algo == Algorithm.SAFE: header += ",best_obj\n"
        else: header += "\n"
        f.write(header)
 
    if problem == Problem.MultiObj: args = []

    best_of_runs = [] 
    all_gens = []
    gl.myprint("-------------------------------------")
    for i in range(gl.NUM_EXPERIMENTS):
        gl.myprint("experiment",i+1)
        best_str, best_dist, gen, pareto_front, solution_best =\
            search_algorithm(i+1, algo, problem, *args) 
        best_of_runs.append(best_dist)
        all_gens.append(gen)
        with open(Path(fname),'a') as f: 
            f.write(best_str)
        if problem == Problem.MultiObj:
            front_f1 = [modname.f1(pareto_front[i]) for i in range(len(pareto_front))]
            front_f2 = [modname.f2(pareto_front[i]) for i in range(len(pareto_front))]
            with open(Path(pareto_fname),'a') as f:
                print("experiment ", i+1, file=f)
                print("f1=",front_f1, end="\n", file=f)
                print("f2=",front_f2, end="\n", file=f)
                print("front=",pareto_front, end="\n", file=f)
                f1f2 = true_front(func_name)
                print("size true front:",len(f1f2), end="\n", file=f)
                print("igd: ", compute_igd(f1f2, [ [a,b] for a,b in zip(front_f1,front_f2)]), end="\n\n", file=f)
                            
    with open(Path(fname),'a') as f:
        f.write("\n")
        f.write("result mean: " + str(round(mean(best_of_runs),2)) + " ("+ str(round(pstdev(best_of_runs),2)) + ")")
        f.write("\n")
        f.write("all gens mean: " + str(round(mean(all_gens),1)) + " ("+ str(round(pstdev(all_gens),1)) + ")")
        f.write("\n")

if __name__== "__main__":
  main()
  