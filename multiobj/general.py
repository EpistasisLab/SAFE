#
# SAFE, copyright 2019 moshe sipper, www.moshesipper.com
#
# General definitions and functions

from string import ascii_uppercase
from random import choices, randint, random
from socket import gethostname
from copy import deepcopy 
from scipy.spatial import distance
from os import environ

# evolution
NUM_EXPERIMENTS = 1
GENERATIONS = 500#3000
SOLUTION_POP_SIZE = 200#500
TOURNAMENT_SIZE = 5
ELITISM = 2 # num elite individuals to copy to next gen, must be even
XO_RATE = 0.8
SOLUTION_PROB_MUTATION = 0.4
OBJECTIVE_GAP = 5 # evolve objective functions every nth generation

# novelty search
KNN = 15 # k nearest neighbors
ARCHIVE_SIZE = 1000

# SAFE
OBJECTIVE_POP_SIZE = 50#150
OBJECTIVE_PROB_MUTATION = 0.4
NUM_OBJECTIVE_PARAMS = 2


#utils
def rand_str(N): # return random string of length N, with upper-case characters 
    return ''.join(choices(ascii_uppercase, k=N))

def running_on_cluster():
    return "lambda" in gethostname()

def running_in_spyder():
    return any('SPYDER' in name for name in environ)    

def myprint(*args, **kwargs):
    if not running_on_cluster(): print(*args, **kwargs)

def progress_indicator(x):
    c = '/' if x%2==0 else '\\'
    myprint('\x08' + c, end="", flush=True)

# general evolutionary functions:
def selection(population, fitnesses, maximum=True): # select one individual using tournament selection
    tournament = [randint(0, len(population)-1) for i in range(TOURNAMENT_SIZE)] # select tournament contenders
    tournament_fitnesses = [fitnesses[tournament[i]] for i in range(TOURNAMENT_SIZE)]
    if maximum:
        return deepcopy(population[tournament[tournament_fitnesses.index(max(tournament_fitnesses))]]) 
    else:
        return deepcopy(population[tournament[tournament_fitnesses.index(min(tournament_fitnesses))]]) 

def single_point_crossover(parent1, parent2): 
    # single-point xo between two genomes (lists), assume both equal in size   
    if (random() < XO_RATE):
        xo_point = randint(1, len(parent1)-1)
        return(parent1[:xo_point]+parent2[xo_point:], parent2[:xo_point]+parent1[xo_point:])
    else:
        return(deepcopy(parent1), deepcopy(parent2))

# novelty search:
def add_to_archive(archive, point, avg_nn): # add point to archive if it is greater than minimum
    # archive is maintained sorted by avg_nn: [(point1, avg_nn1),  (point2, avg_nn2),... ]

    def insert(archive):
        i=0
        while i < len(archive):
            if avg_nn < archive[i][1]: break
            else: i += 1
        archive = archive[:i] + [(point, avg_nn)] + archive[i:]
        return archive

    if len(archive) == 0:    
        archive.append((point, avg_nn)) 
    elif len(archive) < ARCHIVE_SIZE:
        archive = insert(archive)
    else: # archive is full
        if avg_nn > archive[0][1]: # greater than minimum
            del archive[0]
            archive = insert(archive)
    return archive        

def novelty_metric_genotypic(i, archive, population):
    dists = [] # find nearest neighbors of i
    for j in range(len(population)): 
        if j != i:
            dists.append(distance.euclidean(population[i], population[j]))
    for j in range(len(archive)):
        dists.append(distance.euclidean(population[i], archive[j][0]))
    dists = sorted(dists) 
    avg_nn = sum(dists[:KNN])/KNN # average distance to nearest neighbors
    archive = add_to_archive(archive, population[i], avg_nn)
    return avg_nn, archive