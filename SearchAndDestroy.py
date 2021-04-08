import numpy as np
import itertools
import random
import pprint
import copy
import time
import visualizer as vis

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

def generate_advanced_maze():
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
    return grid, targX, targY

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

def update_grid(grid, X, Y):
    deltas = [(1,0), (-1, 0), (0, 1), (0, -1)]
    neighbors = list((X + d[0], Y + d[1]) for d in deltas)
    properNeighbors = list(filter(lambda x: (0<=x[0]< 50 and 0<=x[1]<50), neighbors))
    neighbor_move = random.randint(0, len(properNeighbors)-1)
    newTargX, newTargY = properNeighbors[neighbor_move]
    grid[X][Y] = abs(grid[X][Y])
    grid[newTargX][newTargY] = -1* grid[newTargX][newTargY]
    return newTargX, newTargY

def update_belief_advanced(grid, belief, x, y, man_five, man_five_neighbors):
    #old_belief = copy.deepcopy(belief)
    p = abs(grid[x][y])
    denom_one= 1 - belief[x][y]*(1-p)
    man_five_denom = sum_beliefs(belief, x, y, man_five_neighbors)
    if not man_five:
        man_five_denom = 1- man_five_denom
    max_x, max_y = (0, 0)
    for i in range(50):
        for j in range(50):
            if (i,j) == (x, y):
                continue
            man_five_num = man_five_belief_num(i,j, man_five_neighbors, man_five)
            belief[i][j] = belief[i][j]*man_five_num/(denom_one * man_five_denom)
            if belief[i][j] > belief[max_x][max_y]:
                max_x, max_y = i, j
            elif belief[i][j] == belief[max_x][max_y]:
                max_dist = abs(max_x - x) + abs(max_y -y)
                curr_dist = abs(i -x) + abs(j - y)
                if curr_dist < max_dist:
                    max_x, max_y = i, j
    man_five_num = man_five_belief_num(x, y, man_five_neighbors, man_five)
    belief[x][y] = p*belief[x][y]*man_five_num/(denom_one*man_five_denom)
    if belief[x][y] >= belief[max_x][max_y]:
        max_x, max_y = x, y
    check_belief_array(belief)
    return max_x, max_y

def sum_beliefs(belief, x, y, man_five):
    total_belief = 0
    for i in man_five:
        total_belief += belief[i[0]][i[1]]
    return total_belief

def man_five_belief_num(i, j, man_five_neighbors, man_five):
    if (i, j) in man_five_neighbors:
        return 1 if man_five else 0
    else:
        return 0 if man_five else 1

#change man five condition to check man5 around x,y and then pass that into update belief advaned for efficiency
def bonus_agent_one(grid, targX, targY):
    belief = [[1/2500.]*50 for i in range(50)]
    x, y = random.randint(0, 49), random.randint(0, 49)
    found_target = False
    score = 0
    while not found_target:
        vis.display_landscape(grid, x, y)
        score+=1
        man_five = False
        man_five_neighbors = manhattan_five_neighbors(grid, x, y)
        if (targX,targY) in man_five_neighbors:
            man_five = True
        if check_square(grid, x, y):
            found_target = True
        else:
            # x_prime, y_prime = update_belief_advanced(grid, belief, x, y, man_five, man_five_neighbors)
            update_belief(grid, belief, x, y)
            x_prime, y_prime = utilize_man(grid, belief, x, y, man_five, man_five_neighbors)
            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
        if not found_target:
            targX, targY = update_grid(grid, targX, targY)
            belief = propagate_probabilities(belief)
    print("Agent 1: " + str(score))
    return score

def utilize_man(grid, belief, x, y, man_five, man_five_neighbors):
    #old_belief = copy.deepcopy(belief)
    p = abs(grid[x][y])
    man_five_denom = sum_beliefs(belief, x, y, man_five_neighbors)
    if not man_five:
        man_five_denom = 1- man_five_denom
    max_x, max_y = (0, 0)
    for i in range(50):
        for j in range(50):
            if (i,j) == (x, y):
                continue
            man_five_num = man_five_belief_num(i,j, man_five_neighbors, man_five)
            belief[i][j] = belief[i][j]*man_five_num/(man_five_denom)
            if belief[i][j] > belief[max_x][max_y]:
                max_x, max_y = i, j
            elif belief[i][j] == belief[max_x][max_y]:
                max_dist = abs(max_x - x) + abs(max_y -y)
                curr_dist = abs(i -x) + abs(j - y)
                if curr_dist < max_dist:
                    max_x, max_y = i, j
    man_five_num = man_five_belief_num(x, y, man_five_neighbors, man_five)
    belief[x][y] = belief[x][y]*man_five_num/(man_five_denom)
    if belief[x][y] >= belief[max_x][max_y]:
        max_x, max_y = x, y
    if check_belief_array(belief):
        print("good")
    return max_x, max_y

def propagate_probabilities(belief):
    new_belief = [[0]*50 for i in range(50)]
    deltas = [(1,0), (-1, 0), (0, 1), (0, -1)]
    for X in range(50):
        for Y in range(50):
            neighbors = list((X + d[0], Y + d[1]) for d in deltas)
            properNeighbors = list(filter(lambda x: (0<=x[0]< 50 and 0<=x[1]<50), neighbors))
            uni_belief = belief[X][Y]/len(properNeighbors)
            for neighbor in properNeighbors:
                new_belief[neighbor[0]][neighbor[1]] += uni_belief
    return new_belief

def manhattan_five_neighbors(grid, targX, targY):
    neighbors = list(itertools.product(range(targX-5, targX+6), range(targY-5, targY+6)))
    properNeighbors = list(filter(lambda x: (0<=x[0]< 50 and 0<=x[1]< 50 and (abs(x[0]-targX) + abs(x[1]-targY)) < 6), neighbors))
    return properNeighbors



# score1 = 0
# score2 = 0
# score3 = 0
# score4 = 0
# score5 = 0
# score6 = 0
# trials = 10

# for iterative in range(trials):
#     print(str(iterative))
#     grid = generate_map()
#     if(iterative < 10):
#         score1 += agent_one(grid)
#         score2 += agent_two(grid)
#         score3 += agent_improved(grid)
#     elif (iterative < 20):
#         score3 += agent_one(grid)
#         score4 += agent_two(grid)
#     else:
#         score5 += agent_one(grid)
#         score6 += agent_two(grid)

# print("Trial 1")
# print("Avg Agent 1 Score: " + str(score1/10))
# print("Avg Agent 2 Score: " + str(score2/10))
# print("Avg Agent Improved Score: " + str(score3/10))
# # print("Trial 2")
# # print("Avg Agent 1 Score: " + str(score3/10))
# # print("Avg Agent 2 Score: " + str(score4/10))
# # print("Trial 3")
# # print("Avg Agent 1 Score: " + str(score5/10))
# # print("Avg Agent 2 Score: " + str(score6/10))

grid, targX, targY = generate_advanced_maze()
score_bonus = bonus_agent_one(grid, targX, targY)