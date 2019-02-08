#
# SAFE, copyright 2018 moshe sipper, www.moshesipper.com
#
# Maze navigation
#
# note about maze coordinates: (y,x) | y == rows (up-down), x == columns (left-right) | top left: (0,0), bottom right: (height-1, width-1)
#

from PIL import Image
from pathlib import Path
from math import fabs
from random import uniform, random, randint;
import general as gl;

NUM_ROBOT_PARAMS = 16
ROBOT_STEPS = 300 
ROBO_DIST_SUCCESS = 2 # distance to goal for run to be successful


def read_maze(mazefile):
# maze is text file of size height x width: 0 -- empty cell, 1 -- wall or boundary, 2 -- start, 3 -- target        
    with open('mazes/' + mazefile + '.txt') as f:
        temp = f.read().splitlines()
    height, width = len(temp), len(temp[0])
    maze = [[int(temp[i][j]) for j in range(width)] for i in range(height)]
    for i in range(height):
        for j in range(width):
            if maze[i][j] == 2: start = (i,j)
            elif maze[i][j] == 3: target = (i,j)
    return maze, start, target

def maze_size(maze):
    return len(maze), len(maze[0]) # height, width

def draw_maze(maze, mazefile):
    height, width = maze_size(maze)
    big_maze = []
    for i in range(height):
        l=maze[i]
        big_maze.append([x for p in zip(l,l,l,l) for x in p])
        big_maze.append([x for p in zip(l,l,l,l) for x in p])
        big_maze.append([x for p in zip(l,l,l,l) for x in p])
        big_maze.append([x for p in zip(l,l,l,l) for x in p])
    pixels = [p for line in big_maze for p in line]
    image = Image.new('P', (4*width, 4*height))
    image.putpalette([
        255,255,255,# index 0 is white
        0, 0, 0,    # index 1 is black
        0, 0, 255,  # index 2 is blue
        255,0,0,    # index 3 is red 
        0, 255, 0,  # index 4 is green
    ])
    image.putdata(pixels)
    image.save(Path('mazes/' + mazefile + '.png'), "PNG")
    
def dist(a, b): 
    # distance between 2 points in maze
    return fabs(a[0]-b[0]) + fabs(a[1]-b[1])
    
def look_up(maze, pos):# look upward and return: distance to obstacle/wall, goal found?
    height, width = maze_size(maze)
    y,x = pos
    goal_up = 0
    dist = 0
    hit_obs = False
    y -= 1
    while y>=0:
        if maze[y][x]==3: goal_up = height
        if not hit_obs and maze[y][x]==1: 
            dist += 1
            hit_obs = True
        elif not hit_obs:
            dist += 1
        y -= 1
    return dist, goal_up
    
def look_down(maze, pos):# look downward and return: distance to obstacle/wall, goal found?
    height, width = maze_size(maze)
    y,x = pos
    goal_down = 0
    dist = 0
    hit_obs = False
    y += 1
    while y<height:
        if maze[y][x]==3: goal_down = height
        if not hit_obs and maze[y][x]==1: 
            dist += 1
            hit_obs = True
        elif not hit_obs:
            dist += 1
        y += 1
    return dist, goal_down

def look_left(maze, pos):# look left and return: distance to obstacle/wall, goal found?
    height, width = maze_size(maze)
    y,x = pos
    goal_left = 0
    dist = 0
    hit_obs = False
    x -= 1
    while x>=0:
        if maze[y][x]==3: goal_left = width
        if not hit_obs and maze[y][x]==1: 
            dist += 1
            hit_obs = True
        elif not hit_obs:
            dist += 1
        x -= 1
    return dist, goal_left

def look_right(maze, pos):# look right and return: distance to obstacle/wall, goal found?
    height, width = maze_size(maze)
    y,x = pos
    goal_right = 0
    dist = 0
    hit_obs = False
    x += 1
    while x<width:
        if maze[y][x]==3: goal_right = width
        if not hit_obs and maze[y][x]==1: 
            dist += 1
            hit_obs = True
        elif not hit_obs:
            dist += 1
        x += 1
    return dist, goal_right

def pie_slice(maze, pos, target): # check which pie slice goal is in
    height, width = maze_size(maze)
    goal_right, goal_left, goal_up, goal_down = 0,0,0,0
    y,x = pos
    y_t,x_t = target
    if y_t>y: goal_down = height 
    else: goal_up = height
    if x_t>x: goal_right = width
    else: goal_left = width
    return goal_right, goal_left, goal_up, goal_down

def dist_to_obstacles(maze, pos): # dist to obstacles in 4 directions
    dist_right, goal_right = look_right(maze,pos)
    dist_left, goal_left = look_left(maze,pos)
    dist_up, goal_up = look_up(maze,pos)
    dist_down, goal_down = look_down(maze,pos)
    return dist_right, dist_left, dist_up, dist_down

def dist_to_walls(maze, pos): # dist to walls in 4 directions
    height, width = maze_size(maze)
    y,x = pos
    w_right = width - x
    w_left = x
    w_up = y
    w_down = height - y
    return w_right, w_left, w_up, w_down 

def robot_move(maze, start, target, p, draw_walk=False): # p: the 8 parameters of the robot controller
    height, width = maze_size(maze)
    pos = start
    for i in range(ROBOT_STEPS):
        dist_right, goal_right = look_right(maze, pos)
        dist_left,  goal_left  = look_left(maze, pos)
        dist_up,    goal_up    = look_up(maze, pos)
        dist_down,  goal_down  = look_down(maze, pos)
        goal_right, goal_left, goal_up, goal_down = pie_slice(maze, pos,target)
        h = p[0]*dist_right + p[1]*goal_right + p[2]*dist_left + p[3]*goal_left +\
            p[4]*dist_down + p[5]*goal_down + p[6]*dist_up + p[7]*goal_up
        v = p[8]*dist_right + p[9]*goal_right + p[10]*dist_left + p[11]*goal_left +\
            p[12]*dist_down + p[13]*goal_down + p[14]*dist_up + p[15]*goal_up
        y,x = pos
        l_y, l_x = y,x-1 # left
        r_y, r_x = y,x+1 # right
        if h>=0 and x<width-1 and maze[r_y][r_x]!=1 : pos = (r_y,r_x)
        elif h<0 and x>0 and maze[l_y][l_x]!=1: pos = (l_y,l_x)
        y,x = pos
        u_y, u_x = y-1,x # up
        d_y, d_x = y+1,x # down
        if v>=0 and y<height-1 and maze[d_y][d_x]!=1: pos = (d_y,d_x)
        elif v<0 and y>0 and maze[u_y][u_x]!=1: pos = (u_y,u_x)
        if draw_walk: 
            if maze[pos[0]][pos[1]]!=2 and maze[pos[0]][pos[1]]!=3: # not start or target
                maze[pos[0]][pos[1]] = 4
    if draw_walk: draw_maze(maze,'maze-path')
    return pos
            

def init_solution_pop(solution_pop_size): # initialize population of solutions
    return [ [uniform(-1, 1) for j in range(NUM_ROBOT_PARAMS)] for i in range(solution_pop_size) ]

def init_objective_pop(): # initialize population of objective functions    
    return [ [uniform(0, 1) for j in range(gl.NUM_OBJECTIVE_PARAMS)] for i in range(gl.OBJECTIVE_POP_SIZE) ]
            
def solution_mutation(ind, *args):
    if (random() > gl.SOLUTION_PROB_MUTATION):
        return(ind) # no mutation 
    else: # perform mutation 
        gene = randint(0, NUM_ROBOT_PARAMS-1)
        ind[gene] = uniform(-1, 1)
        return(ind) 

def objective_mutation(ind):
    if (random() > gl.OBJECTIVE_PROB_MUTATION):
        return(ind) # no mutation 
    else: # perform mutation 
        gene = randint(0, gl.NUM_OBJECTIVE_PARAMS-1)
        ind[gene] = uniform(0, 1)
        return(ind)           
            
def novelty_metric_solutions(i, archive, end_pos):
    dists = [] # find nearest neighbors of i
    pos = end_pos[i]
    for j in range(gl.SOLUTION_POP_SIZE): 
        if j != i:
            dists.append(dist(pos, end_pos[j]))
    for j in range(len(archive)):
        dists.append(dist(pos, archive[j][0]))
    dists = sorted(dists) 
    avg_nn = sum(dists[:gl.KNN])/gl.KNN # average distance to nearest neighbors
    archive = gl.add_to_archive(archive, pos, avg_nn)
    return avg_nn, archive 
    
def novelty_metric_objectives(i, archive, obj_vals):
    dists = [] # find nearest neighbors of i
    val = obj_vals[i]
    for j in range(gl.OBJECTIVE_POP_SIZE): 
        if j != i:
            dists.append(fabs(val - obj_vals[j]))
    for j in range(len(archive)):
        dists.append(fabs(val - archive[j][0]))
    dists = sorted(dists) 
    avg_nn = sum(dists[:gl.KNN])/gl.KNN # average distance to nearest neighbors
    archive = gl.add_to_archive(archive, val, avg_nn)
    return avg_nn, archive 

def standard_fitness(pos, target):
    return 1/dist(pos, target)   

def safe_fitness(i, novelty_scores, objFunc, target, end_pos):
    goal = standard_fitness(end_pos[i], target)
    nov = novelty_scores[i]
    return objFunc[0]*goal + objFunc[1]*nov     

def distance_to_goal(pos, target):
    return dist(pos, target) 
    
    
    