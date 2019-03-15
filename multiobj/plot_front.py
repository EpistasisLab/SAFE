#
# SAFE, copyright 2019 moshe sipper, www.moshesipper.com
#
# plot Pareto front

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from math import sqrt, sin, exp, pi
from scipy.spatial import distance
from decimal import Decimal

import f1f2  # contains func_name, f1, and f2

gx = 1 # opt of ZDT at g(x) = 1   
def f1_opt(x): 
    if func_name == 'ZDT1' or func_name == 'ZDT2' or func_name == 'ZDT3' or func_name == 'ZDT4':
        return x[0]
    elif func_name == 'ZDT6':
        return 1 - exp(-4*x[0])*(sin(6*pi*x[0]))**6
def f2_opt(x): 
    if func_name == 'ZDT1' or func_name == 'ZDT4':
        return (1 - sqrt(x[0]/gx)) # g(x) * 
    elif func_name == 'ZDT2':
        return (1 - (x[0]/gx)**2) # g(x) * 
    elif func_name == 'ZDT3':
        return (1 - sqrt(x[0]/gx) - x[0]/gx*sin(10*pi*x[0])) # g(x) *  
    elif func_name == 'ZDT6':
        return 1 - (f1_opt(x)/gx)**2

def dominates(p1, p2):
    if ( ( p1[0] < p2[0] ) and ( p1[1] <= p2[1] ) ) or\
       ( ( p1[1] < p2[1] ) and ( p1[0] <= p2[0] ) ):
        return True
    else:  
        return False
              
def num_dominating_solutions(point, pop):
    nd = 0
    for j in range(len(pop)):
        if dominates(pop[j], point): nd += 1
    return nd  

def compute_igd(true_front, non_dom): # inverted generational distance
    igd = 0;
    T = len(true_front)
    for i in range(T):
        igd += min([distance.euclidean(true_front[i],non_dom[j]) for j in range(len(non_dom))])
    igd /= T
    return igd   

def true_front(fname):    
    global func_name
    func_name = fname
    xx = [[x/1000] for x in range(0,1001,1)] 
    f1f2 = [ [f1_opt(x), f2_opt(x)] for x in xx ]
    f1f2 = [f1f2[i] for i in range(len(f1f2)) if num_dominating_solutions(f1f2[i], f1f2) == 0]
    return f1f2

def main():
    f1f2 = true_front(func_name)
    print("\nsize true front:",len(f1f2))
    print("igd: ", '%.2E' % Decimal(compute_igd(f1f2, [ [a,b] for a,b in zip(f1,f2)])))
    
    f1_o = [f1f2[i][0] for i in range(len(f1f2))]
    f2_o = [f1f2[i][1] for i in range(len(f1f2))]
    
    
    plt.figure(figsize=(10,10))
    plt.tick_params(labelsize=20)
    plt.xlabel('f1', fontsize=35)
    plt.ylabel('f2', fontsize=35)
    plt.title(func_name, fontsize=35)
    safe_patch = mpatches.Patch(color='pink',  linewidth=4, label='SAFE')
    true_patch = mpatches.Patch(color='black', linewidth=4, label='True front')
    plt.legend(handles=[safe_patch,true_patch],fontsize=30)
    #plt.legend(fontsize=30)
    plt.plot(f1, f2, color='pink', linestyle='None', marker='.',markersize=20, label='SAFE') 
    plt.plot(f1_o, f2_o, color='black', linestyle='None', marker='.',markersize=4, label='True front') 
    #plt.scatter(f1_o, f2_o, color='black', linestyle='-', marker='.', label='True front') 
    plt.show()

if __name__== "__main__":
  main()