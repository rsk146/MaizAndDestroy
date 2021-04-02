import numpy as np
import itertools
import random
import pprint
import copy

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
    print(targX, targY)
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
    for i in range(50):
        for j in range(50):
            if (x,y) == (i,j):
                continue
            denom = 1 - belief[x][y]*(1-p)
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
    print("Start: " + str((x,y)))
    found_target = False
    score = 0
    while not found_target:
        score +=1
        path.append((x,y))
        if check_square(grid, x, y):
            found_target = True
        else:
            x_prime, y_prime = update_belief(grid, belief, x, y)
            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
    print(x,y)
    print(score)
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
    print("Start: " + str((x,y)))
    found_target = False
    score = 0
    while not found_target:
        score +=1
        path.append((x,y))
        if check_square(grid, x,y):
            found_target = True
        else:
            update_belief(grid, belief, x, y)
            x_prime, y_prime = update_prob(grid, prob, belief, x, y)
            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
    print(x,y)
    print(score)
    #print(path)
#agent_one(generate_map())
#agent_two(generate_map())