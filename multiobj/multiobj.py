#
# SAFE, copyright 2019 moshe sipper, www.moshesipper.com
#
# Multiobjective optimization
#

from math import sqrt, sin, cos, exp, pi
from random import uniform, random, randint
from scipy.spatial import distance

import general as gl;

ndim = 30
func_name = 'ZDT1'

def set_func_name(name):
    global func_name
    func_name = name

def f1(x): 
    if func_name == 'ZDT1' or func_name == 'ZDT2' or func_name == 'ZDT3' or func_name == 'ZDT4':
        return x[0]
    elif func_name == 'ZDT6':
        return 1 - exp(-4*x[0])*((sin(6*pi*x[0]))**6)

def g(x):
    if func_name == 'ZDT1' or func_name == 'ZDT2' or func_name == 'ZDT3':
        return 1 + 9/(ndim-1)*sum([x[i] for i in range(1,len(x))])
    elif func_name == 'ZDT4':
        return 1 + 10*(ndim-1) + sum([x[i]**2 - 10*cos(4*pi*x[i]) for i in range(1,len(x))])
    elif func_name == 'ZDT6':
        return 1 + 9*((sum([x[i] for i in range(1,len(x))]))**0.25)
       
def f2(x): 
    if func_name == 'ZDT1' or func_name == 'ZDT4':
        return (1 - sqrt(x[0]/g(x))) # g(x) * 
    elif func_name == 'ZDT2':
        return (1 - (x[0]/g(x))**2) # g(x) * 
    elif func_name == 'ZDT3':
        return (1 - sqrt(x[0]/g(x)) - x[0]/g(x)*sin(10*pi*x[0])) # g(x) * 
    elif func_name == 'ZDT6':
        return 1 - (f1(x)/g(x))**2

def init_solution_pop(solution_pop_size): # initialize population of solutions
    if func_name != 'ZDT4':
        return [ [uniform(0, 1) for j in range(0,ndim)] for i in range(solution_pop_size) ]
    else:
        return [ [uniform(0, 1)] +  [uniform(-5, 5) for j in range(1,ndim)] for i in range(solution_pop_size) ]

def init_objective_pop(): # initialize population of objective functions    
    return [ [uniform(0, 1) for j in range(gl.NUM_OBJECTIVE_PARAMS)] for i in range(gl.OBJECTIVE_POP_SIZE) ]

def solution_mutation(ind, *args):
    if (random() > gl.SOLUTION_PROB_MUTATION):
        return(ind) # no mutation 
    else: # perform mutation 
        gene = randint(0, ndim-1)
        if func_name != 'ZDT4':
            ind[gene] = uniform(0, 1)
        else:
            if gene == 0: ind[gene] = uniform(0, 1)
            else: ind[gene] = uniform(-5, 5)
        return(ind) 

def objective_mutation(ind):
    if (random() > gl.OBJECTIVE_PROB_MUTATION):
        return(ind) # no mutation 
    else: # perform mutation 
        gene = randint(0, gl.NUM_OBJECTIVE_PARAMS-1)
        ind[gene] = uniform(0, 1)
        return(ind)    

def dominates(p1, p2):
    if ( ( f1(p1) < f1(p2) ) and ( f2(p1) <= f2(p2) ) ) or\
       ( ( f2(p1) < f2(p2) ) and ( f1(p1) <= f1(p2) ) ):
        return True
    else:  
        return False
              
def num_dominating_solutions(point, pop):
    nd = 0
    for j in range(len(pop)):
        if dominates(pop[j], point): nd += 1
    return nd                       

def add_to_pareto_front(point, pareto_front):
    added = False
    pareto_front = [pareto_front[i] for i in range(len(pareto_front)) if not dominates(point, pareto_front[i])]
    if num_dominating_solutions(point, pareto_front) == 0 and point not in pareto_front:
        pareto_front.append(point)
        added = True
    return pareto_front, added

def safe_fitness(ind, objFunc):
    s = sum(objFunc)
    return objFunc[0]/s*f1(ind) + objFunc[1]/s*f2(ind)

def novelty_metric_solutions(i, archive_sol, f1f2):
    dists = [] # find nearest neighbors of i
    val = f1f2[i]
    for j in range(gl.SOLUTION_POP_SIZE): 
        if j != i:
            dists.append(distance.euclidean(val, f1f2[j]))
    for j in range(len(archive_sol)):
        dists.append(distance.euclidean(val, archive_sol[j][0]))
    dists = sorted(dists) 
    avg_nn = sum(dists[:gl.KNN])/gl.KNN # average distance to nearest neighbors
    archive = gl.add_to_archive(archive_sol, val, avg_nn)
    return avg_nn, archive  

