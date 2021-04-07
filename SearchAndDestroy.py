import numpy as np
import itertools
import random
import pprint
import copy
import time
#import visualizer as vis

#negative probability square is the one with the target, so always use abs(prob)
def generate_map():
    grid = []
    terrainProbs = [.1, .3, .7, .9]
    targX, targY = random.randint(0, 49), random.randint(0, 49)
    for i in range(50):
        grid.append([])
        for j in range(50):
            terrain = random.randint(0, 3)
            grid[i].append(terrainProbs[terrain])
            if i == targX and j == targY:
                grid[i][j] = -terrainProbs[terrain]
    #print(targX, targY)
    return grid

def check_square(grid, x, y):
    rand = random.uniform(0,1)
    if grid[x][y] < 0 and rand >= abs(grid[x][y]):
        return True
    return False

def check_belief_array(belief):
    total = 0
    for i in range(50):
        for j in range(50):
            total +=belief[i][j]
    total = round(total, 6)
    if total != 1:
        print(total)
        return False
    return True

def update_belief(grid, belief, x,y):
    p = abs(grid[x][y])
    max_x, max_y = (0, 0)
    denom = 1 - belief[x][y]*(1-p)
    for i in range(50):
        for j in range(50):
            if (x,y) == (i,j):
                continue
            belief[i][j] = belief[i][j]/denom
            if belief[i][j] > belief[max_x][max_y]:
                max_x, max_y = i, j
            elif belief[i][j] == belief[max_x][max_y]:
                max_dist = abs(max_x - x) + abs(max_y -y)
                curr_dist = abs(i -x) + abs(j - y)
                if curr_dist < max_dist:
                    max_x, max_y = i, j
    belief[x][y] = p*belief[x][y]/(denom)
    if belief[x][y] >= belief[max_x][max_y]:
        max_x, max_y = x, y
    check_belief_array(belief)
    return max_x, max_y

def agent_one(grid):
    path = []
    belief = [[1/2500.]*50 for i in range(50)]
    x, y = random.randint(0, 49), random.randint(0, 49)
    #print("Start: " + str((x,y)))
    found_target = False
    score = 0
    while not found_target:
        #vis.display_landscape(grid, x, y)
        score +=1
        path.append((x,y))
        if check_square(grid, x, y):
            found_target = True
        else:
            x_prime, y_prime = update_belief(grid, belief, x, y)
            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
    #print(x,y)
    print("Agent 1: " + str(score))
    return score
    #print(path)

def initialize_prob_array(grid):
    prob = []
    for i in range(50):
        prob.append([])
        for j in range(50):
            prob[i].append((1-abs(grid[i][j])) * 1/2500.)
    return prob

def update_prob(grid, prob, belief, x, y):
    max_x, max_y = (0,0)
    for i in range(50):
        for j in range(50):
            p = abs(grid[i][j])
            prob[i][j] = (1-p)*belief[i][j]
            if prob[i][j] > prob[max_x][max_y]:
                max_x, max_y = i, j
            elif prob[i][j] == prob[max_x][max_y]:
                max_dist = abs(max_x - x) + abs(max_y - y)
                curr_dist = abs(i - x) + abs(j  -y)
                if curr_dist < max_dist:
                    max_x, max_y = i, j
    return max_x, max_y


def agent_two(grid):
    path = []
    belief = [[1/2500.]*50 for i in range(50)]
    prob = initialize_prob_array(grid) 
    x, y = random.randint(0, 49), random.randint(0,49)
    #print("Start: " + str((x,y)))
    found_target = False
    score = 0
    while not found_target:
        #vis.display_landscape(grid, x, y)
        score +=1
        path.append((x,y))
        if check_square(grid, x,y):
            found_target = True
        else:
            update_belief(grid, belief, x, y)
            x_prime, y_prime = update_prob(grid, prob, belief, x, y)
            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
    #print(x,y)
    print("Agent 2: " + str(score))
    return score
    #print(path)

def agent_improved(grid):
    path = []
    belief = [[1/2500.]*50 for i in range(50)]
    prob = initialize_prob_array(grid)
    unvisited = []
    for i in range(50):
        for j in range(50):
            unvisited.append((i,j))
    unvisited = set(unvisited)

    x, y = random.randint(0, 49), random.randint(0,49)
    #print("Start: " + str((x,y)))
    found_target = False
    printed = False
    score = 0
    while not found_target:
        #vis.display_landscape(grid, x, y)
        score +=1
        path.append((x,y))
        if check_square(grid, x,y):
            found_target = True
        else:
            unvisited.discard((x,y))
            update_belief(grid, belief, x, y)
            update_prob(grid, prob, belief, x, y)
            x_prime, y_prime = highest_nearby_prob(x,y,prob) #if (len(unvisited) > 0) else highest_nearby_prob(x,y,belief)
            if(len(unvisited) == 0 and not printed):
                printed = True
                print("Visited everything when score = " + str(score))
            
            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
    #print(x,y)
    print("Agent Improved: " + str(score))
    return score
    #print(path)

def highest_nearby_prob(x,y,belief):
    #Depending on which belief is passed in, will return highest adjacent probability
    #Probability of finding the agent OR probability of containing the agent
    max_x = 0
    max_y = 0
    max = 0
    for i in range(x-1,x+2):
        for j in range(y-1,y+2):
            if(i < 0 or i >=50 or j < 0 or j >= 50):
                continue
            if(belief[i][j] > max):
                max = belief[i][j]
                max_x = i
                max_y = j
    
    return max_x, max_y

score1 = 0
score2 = 0
score3 = 0
score4 = 0
score5 = 0
score6 = 0
trials = 10

for iterative in range(trials):
    grid = generate_map()
    print(str(iterative))
    if(iterative < 10):
        score1 += agent_one(grid)
        score2 += agent_two(grid)
        score3 += agent_improved(grid)
    elif (iterative < 20):
        score3 += agent_one(grid)
        score4 += agent_two(grid)
    else:
        score5 += agent_one(grid)
        score6 += agent_two(grid)

print("Trial 1")
print("Avg Agent 1 Score: " + str(score1/10))
print("Avg Agent 2 Score: " + str(score2/10))
print("Avg Agent Improved Score: " + str(score3/10))
# print("Trial 2")
# print("Avg Agent 1 Score: " + str(score3/10))
# print("Avg Agent 2 Score: " + str(score4/10))
# print("Trial 3")
# print("Avg Agent 1 Score: " + str(score5/10))
# print("Avg Agent 2 Score: " + str(score6/10))