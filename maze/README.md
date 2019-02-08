The maze experiments described in M. Sipper, J. H. Moore, and R. J. Urbanowicz, "Solution and fitness evolution (SAFE): Coevolving solutions and their objective functions", in Genetic Programming - 22nd European Conference, EuroGP 2019, L. Sekanina et al. Eds, 2019.

* safe.py: the main evolutionary algorithm
* general.py: additional general functions, also used in experiments other than robot
* robot.py: the robot simulator

To run: 
1. set parameters in general.py (NUM_EXPERIMENTS, GENERATIONS, etc.)
2. run safe.py directly, or from command line: safe [StandardEA/Novelty/SAFE/Random] RobotMaze [maze1/maze2]

There are 2 maze files in folder 'mazes':  maze1.txt, maze2.txt

The result file of the evolutionary run will be placed in the 'results' folder. For example, one experiment using maze1 might generate the following output:
```
    gen,best_dist,best_sol,best_obj
    43,2.0,"[0.8551481579500111,-0.9332774090573333,-0.11563879500160379,-0.24246406808598064,-0.7294920250170724,-0.7785401932192244,-0.3266954075442574,0.841564173423937,0.9637883597920414,0.9191537390177535,-0.16024844744982314,-0.8911765558396127,-0.7338655700137233,-0.4610089333613969,-0.24926925465405003,0.5816104285712513]","[0.48863509963359775,0.5113649003664023]"

    no. success: 1
    success gens mean: 43 (0.0)
    result mean: 2.0 (0.0)
    all gens mean: 43 (0.0)
```    
    
 Generation 43 found best solution with distance 2 from target. 
 Best solution (p vector) is:
 
 `p = [0.8551481579500111,-0.9332774090573333,-0.11563879500160379,-0.24246406808598064,-0.7294920250170724,-0.7785401932192244,-0.3266954075442574,0.841564173423937,0.9637883597920414,0.9191537390177535,-0.16024844744982314,-0.8911765558396127,-0.7338655700137233,-0.4610089333613969,-0.24926925465405003,0.5816104285712513]`
 
 and the best objective-function pair is `[0.48863509963359775,0.5113649003664023]`
 
 To obtain an image of the robot's path, run the following:
 ```
   maze, start, target = read_maze('maze1')
   p=[0.8551481579500111,-0.9332774090573333,-0.11563879500160379,-0.24246406808598064,-0.7294920250170724,-0.7785401932192244,-0.3266954075442574,0.841564173423937,0.9637883597920414,0.9191537390177535,-0.16024844744982314,-0.8911765558396127,-0.7338655700137233,-0.4610089333613969,-0.24926925465405003,0.5816104285712513]
   robot_move(maze, start, target, p, draw_walk=True)
```

This will create a file in folder 'mazes' called 'maze-path.png'

Inline-style: 
![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "maze-path")
