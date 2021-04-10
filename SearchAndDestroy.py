import numpy as np
import itertools
import random
import pprint
import copy
import time
# import visualizer as vis

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
    return grid

#Similar to generate map except returns the (x,y) coordinate of the target
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

#Searches the square. Follows the grid's probability of failing if the target is there
#Target's existence determined by if the grid probability is negative
def check_square(grid, x, y):
    rand = random.uniform(0,1)
    if grid[x][y] < 0 and rand >= abs(grid[x][y]):
        return True
    return False

#Debugging function. Ensures that our probability is correctly calculated
#Sums the probability grid to make sure that it is equal to 1
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

#Follows the formula listed in the report
#Updates all cells since we failed at x,y
def update_belief(grid, belief, x,y):
    p = abs(grid[x][y])
    max_x, max_y = (0, 0)
    denom = 1 - belief[x][y]*(1-p)

    for i in range(50):
        for j in range(50):
            if (x,y) == (i,j): #Handle the search square separately
                continue
            belief[i][j] = belief[i][j]/denom

            #Keep track of next square to search
            if belief[i][j] > belief[max_x][max_y]:
                max_x, max_y = i, j
            elif belief[i][j] == belief[max_x][max_y]:
                max_dist = abs(max_x - x) + abs(max_y -y)
                curr_dist = abs(i -x) + abs(j - y)
                if curr_dist < max_dist:
                    max_x, max_y = i, j

    #Handle search square
    belief[x][y] = p*belief[x][y]/(denom)
    if belief[x][y] >= belief[max_x][max_y]:
        max_x, max_y = x, y
    check_belief_array(belief)

    #return next seach square
    return max_x, max_y


def agent_one(grid):
    #initialize belief and starting point
    #Belief represents probability of containing target
    path = []
    belief = [[1/2500.]*50 for i in range(50)]
    x, y = random.randint(0, 49), random.randint(0, 49)
    
    found_target = False
    score = 0
    while not found_target:
        #vis.display_landscape(grid, x, y)
        score +=1
        path.append((x,y))

        #Search the square
        if check_square(grid, x, y):
            found_target = True
        else:
            #On failure, update our belief in every sqaure
            x_prime, y_prime = update_belief(grid, belief, x, y)
            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
    
    print("Agent 1: " + str(score))
    return score

#Initialize array that contains probability of FINDING the target
def initialize_prob_array(grid):
    prob = []
    for i in range(50):
        prob.append([])
        for j in range(50):
            prob[i].append((1-abs(grid[i][j])) * 1/2500.)
    return prob

#Update prob of FINDING the target given the prob of CONTAINING the target
#Simply multiples current belief by the false negative rate
def update_prob(grid, prob, belief, x, y):
    max_x, max_y = (0,0)
    for i in range(50):
        for j in range(50):
            p = abs(grid[i][j])
            prob[i][j] = (1-p)*belief[i][j]

            #Keep track of highest prob
            if prob[i][j] > prob[max_x][max_y]:
                max_x, max_y = i, j
            elif prob[i][j] == prob[max_x][max_y]:
                max_dist = abs(max_x - x) + abs(max_y - y)
                curr_dist = abs(i - x) + abs(j  -y)
                if curr_dist < max_dist:
                    max_x, max_y = i, j

    #Return highest prob square
    return max_x, max_y


def agent_two(grid):
    #Belief represents probability of CONTAINING the target
    #Prob represents probability of FINDING the target
    path = []
    belief = [[1/2500.]*50 for i in range(50)]
    prob = initialize_prob_array(grid) 
    x, y = random.randint(0, 49), random.randint(0,49)
    
    found_target = False
    score = 0
    while not found_target:
        #vis.display_landscape(grid, x, y)
        score +=1
        path.append((x,y))
        
        #Search Square
        if check_square(grid, x,y):
            found_target = True
        else:
            #On fail, update belief & Prob. Use prob to determine next square
            update_belief(grid, belief, x, y)
            x_prime, y_prime = update_prob(grid, prob, belief, x, y)
            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
    
    print("Agent 2: " + str(score))
    return score

def agent_improved(grid):
    #Everything here follows same logic as Agent 2 except for failure portion
    #Belief represents probability of CONTAINING the target
    #Prob represents probability of FINDING the target
    path = []
    belief = [[1/2500.]*50 for i in range(50)]
    prob = initialize_prob_array(grid)
    unvisited = []
    for i in range(50):
        for j in range(50):
            unvisited.append((i,j))
    unvisited = set(unvisited)
    x, y = random.randint(0, 49), random.randint(0,49)
    
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
            ### FAILURE PORTION
            #Update all beliefs and probs
            unvisited.discard((x,y))
            update_belief(grid, belief, x, y)
            update_prob(grid, prob, belief, x, y)

            #Pick the highest NEARBY prob to search next
            x_prime, y_prime = highest_nearby_prob(x,y,prob)
            if(len(unvisited) == 0 and not printed):
                printed = True
                print("Visited everything when score = " + str(score))
            
            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
    
    print("Agent Improved: " + str(score))
    return score

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

#Moves the target 1 manhattan unit away from current location
#Uniform random decision making
def update_grid(grid, X, Y):
    deltas = [(1,0), (-1, 0), (0, 1), (0, -1)]
    neighbors = list((X + d[0], Y + d[1]) for d in deltas)
    properNeighbors = list(filter(lambda x: (0<=x[0]< 50 and 0<=x[1]<50), neighbors))

    neighbor_move = random.randint(0, len(properNeighbors)-1)
    newTargX, newTargY = properNeighbors[neighbor_move]

    grid[X][Y] = abs(grid[X][Y])
    grid[newTargX][newTargY] = -1* grid[newTargX][newTargY]

    return newTargX, newTargY

#Sums the belief of all squares that are within 5 units of searched square
def sum_beliefs(belief, x, y, man_five):
    total_belief = 0
    for i in man_five:
        total_belief += belief[i[0]][i[1]]
    return total_belief

#If the search is within 5 manhattan units of the target
#   Return 1 if the square's location is within 5, 0 otherwise
#Otherwise, flip this value
#
#Used for the numerator in the moving probability formula given in the report
def man_five_belief_num(i, j, man_five_neighbors, man_five):
    if (i, j) in man_five_neighbors:
        return 1 if man_five else 0
    else:
        return 0 if man_five else 1


def bonus_agent_one(grid, targX, targY):
    #Belief represents the probability of CONTAINING the target
    belief = [[1/2500.]*50 for i in range(50)]
    x, y = random.randint(0, 49), random.randint(0, 49)
    found_target = False
    score = 0
    count = 0
    while not found_target:
        # vis.display_landscape(grid, x, y)
        score+=1
        
        #Get a list of all the neighbors that are within 5 units
        man_five = False
        man_five_neighbors = manhattan_five_neighbors(grid, x, y)
        if (targX,targY) in man_five_neighbors:
            #Tell agent that the target is within Manhattan 5 units
            man_five = True
        
        #Tell the agent the result of the search
        if check_square(grid, x, y):
            found_target = True
        else:
            if((x,y) == (targX, targY)):
                count += 1
                print(count)
            # On fail, update our beliefs like normal
            update_belief(grid, belief, x, y)
            #Utilize our new piece of information to update our beliefs
            x_prime, y_prime = utilize_man(grid, belief, x, y, man_five, man_five_neighbors)
            #Propogate our belief now that the target has moved
            belief = propagate_probabilities(belief)
            #Get the best probability of CONTAINING for our next search
            x_prime, y_prime = get_random_best(belief, x, y, belief[x_prime][y_prime], abs(x_prime-x) + abs(y_prime - y))

            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
        
        #Propogate the target if our search failed
        if not found_target:
            targX, targY = update_grid(grid, targX, targY)
            if not check_belief_array(belief):
                print("bad")

    print("Agent 1: " + str(score))
    print("Missed Targets: " + str(count))
    return score

#Calculate all beliefs depending on whether the target is within 5 units of the search
def utilize_man(grid, belief, x, y, man_five, man_five_neighbors):
    p = abs(grid[x][y])

    #Denominator of formula in section 6 of the report
    man_five_denom = sum_beliefs(belief, x, y, man_five_neighbors)
    #Take complement of it if we are not within 5 of target 
    if not man_five:
        man_five_denom = 1- man_five_denom
    max_x, max_y = (0, 0)
    
    for i in range(50):
        for j in range(50):
            if (i,j) == (x, y): # calculate the searched square separately
                continue

            #Calculate the second term of the numerator
            man_five_num = man_five_belief_num(i,j, man_five_neighbors, man_five)
            #Update our belief
            belief[i][j] = belief[i][j]*man_five_num/(man_five_denom)

            #Keep track of the highest belief
            if belief[i][j] > belief[max_x][max_y]:
                max_x, max_y = i, j
            elif belief[i][j] == belief[max_x][max_y]:
                max_dist = abs(max_x - x) + abs(max_y -y)
                curr_dist = abs(i -x) + abs(j - y)
                if curr_dist < max_dist:
                    max_x, max_y = i, j

    #Finish calculating the searched square
    man_five_num = man_five_belief_num(x, y, man_five_neighbors, man_five)
    belief[x][y] = belief[x][y]*man_five_num/(man_five_denom)
    if belief[x][y] >= belief[max_x][max_y]:
        max_x, max_y = x, y
 
    #Return square with highest prob
    return max_x, max_y

#Sum all the probabilities of the target moving into our current square
#Therefore, we need to look at all the adjacent neighbors.
def propagate_probabilities(belief):
    new_belief = [[0]*50 for i in range(50)]
    deltas = [(1,0), (-1, 0), (0, 1), (0, -1)]
    for X in range(50):
        for Y in range(50):
            neighbors = list((X + d[0], Y + d[1]) for d in deltas)
            properNeighbors = list(filter(lambda x: (0<=x[0]< 50 and 0<=x[1]<50), neighbors))
            uni_belief = belief[X][Y]/len(properNeighbors)

            #Update our neighobrs probability since its equiprobable to move into any of these neighbors
            for neighbor in properNeighbors:
                new_belief[neighbor[0]][neighbor[1]] += uni_belief
    return new_belief

#Get list of all neighbors within 5 manhattan units
def manhattan_five_neighbors(grid, targX, targY):
    neighbors = list(itertools.product(range(targX-5, targX+6), range(targY-5, targY+6)))
    properNeighbors = list(filter(lambda x: (0<=x[0]< 50 and 0<=x[1]< 50 and (abs(x[0]-targX) + abs(x[1]-targY)) < 6), neighbors))
    return properNeighbors

def bonus_agent_two(grid, targX, targY):
    #Belief represents probability of CONTAINING the target
    #Prob represents probability of FINDING the target

    belief = [[1/2500.]*50 for i in range(50)]
    prob = initialize_prob_array(grid)
    x, y = random.randint(0, 49), random.randint(0, 49)
    found_target = False
    score = 0
    count = 0
    while not found_target:
        #vis.display_landscape(grid, x, y)

        #Same logic as agent 1 until failure
        score+=1
        man_five = False
        man_five_neighbors = manhattan_five_neighbors(grid, x, y)
        if (targX,targY) in man_five_neighbors:
            man_five = True
        if check_square(grid, x, y):
            found_target = True
        else:
            #FAILURE PORTION
            if((x,y) == (targX, targY)):
                count += 1
            
            #Update beliefs like normal
            update_belief(grid, belief, x, y)
            #Utilize the new information
            utilize_man(grid, belief, x, y, man_five, man_five_neighbors)
            #Propogate our belief
            belief = propagate_probabilities(belief)
            #Select the best prob of FINDING the target
            x_prime, y_prime = update_prob(grid, prob, belief, x, y)

            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime

        #Propogate the target if we can't find it
        if not found_target:
            targX, targY = update_grid(grid, targX, targY)
            
            if not check_belief_array(belief):
                print("bad")
    print("Agent 2: " + str(score))
    print("Missed Targets: " + str(count))
    #print(count)
    return score

def bonus_agent_improved(grid, targX, targY):
    #Follows same logic as Agnet 2 until FAILURE
    #Belief represents probability of CONTAINING the target
    #Prob represents probability of FINDING the target
    belief = [[1/2500.]*50 for i in range(50)]
    prob = initialize_prob_array(grid)
    x, y = random.randint(0, 49), random.randint(0, 49)
    found_target = False
    score = 0
    count = 0
    unvisited = []
    for i in range(50):
        for j in range(50):
            unvisited.append((i,j))
    unvisited = set(unvisited)
    printed = False


    while not found_target:
        # vis.display_landscape(grid, x, y)
        score +=1
        man_five = False
        man_five_neighbors = manhattan_five_neighbors(grid, x, y)
        if (targX,targY) in man_five_neighbors:
            man_five = True
        if check_square(grid, x,y):
            found_target = True
        else:
            #FAILURE
            if((x,y) == (targX, targY)):
                count += 1
                print(count)
            unvisited.discard((x,y))
            
            #Same as previous two agents
            update_belief(grid, belief, x, y)
            x_prime, y_prime = utilize_man(grid, belief, x, y, man_five, man_five_neighbors)
            belief = propagate_probabilities(belief)
            #If we aren't in man5, then pick the highest nearby probability
            x_prime, y_prime = highest_nearby_prob_adv(x,y, belief)
            #If we are within man5, then pick the highest prob of finding the target
            if(man_five):
                x_prime, y_prime = update_prob(grid, prob, belief, x, y)
            
            score += abs(x_prime - x) + abs(y_prime - y)
            x, y = x_prime, y_prime
        
        #Propogate our target
        if not found_target:
            targX, targY = update_grid(grid, targX, targY)

    print("Agent Improved: " + str(score))
    print("Missed Targets: " + str(count))
    return score

#Get the best probability, randomly selecting the equidistant and equiprobable ones
def get_random_best(mat, x, y, minProb, minDist):
    eqlist = []
    maxProb = 0
    maxX = 0
    maxY = 0
    for i in range(50):
        for j in range(50):
            if(mat[i][j] > maxProb):
                eqlist = []
                eqlist.append((i,j))
                maxProb = mat[i][j]
                maxX = i
                maxY = j
            elif(mat[i][j] == maxProb and abs(maxX-x) + abs(maxY-y) > abs(x-i) + abs(y-j)):
                eqlist = []
                eqlist.append((i,j))
                maxX = i
                maxY = j
            elif(mat[i][j] == maxProb and abs(maxX-x) + abs(maxY-y) == abs(x-i) + abs(y-j)):
                eqlist.append((i,j))
                
    return eqlist[0] if len(eqlist) == 1 else eqlist[random.randint(0, len(eqlist)-1)]

def highest_nearby_prob_adv(x,y,belief):
    #Depending on which belief is passed in, will return highest adjacent probability
    #Probability of finding the agent OR probability of containing the agent
    max = 0
    dist = 0
    eqlist = []
    neighbors = list(itertools.product(range(targX-10, targX+11), range(targY-10, targY+11)))
    properNeighbors = list(filter(lambda x: (0<=x[0]< 50 and 0<=x[1]< 50 and (abs(x[0]-targX) + abs(x[1]-targY)) <= 10), neighbors))
    for i,j in properNeighbors:
        if(belief[i][j] > max) or (belief[i][j] == max and dist > abs(i-x)+abs(y-j)):
            max = belief[i][j]
            dist = abs(i-x) + abs(j-y)
            eqlist = []
            eqlist.append((i,j))
        elif belief[i][j] == max and dist == abs(i-x)+abs(y-j):
            eqlist.append((i,j))
    
    item = eqlist[0] if len(eqlist) == 1 else eqlist[random.randint(0, len(eqlist)-1)]
    #print(belief[item[0]][item[1]])
    return item


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
score1 = 0
score2 = 0
score3 = 0
trials = 10

for iterative in range(trials):
    print(str(iterative))
    grid, targX, targY = generate_advanced_maze()
    score1 += bonus_agent_one(grid, targX, targY)
    score2 += bonus_agent_two(grid, targX, targY)
    score3 += bonus_agent_improved(grid, targX, targY)

print("Avg Agent 1 Score: " + str(score1/10))
print("Avg Agent 2 Score: " + str(score2/10))
print("Avg Agent Improved Score: " + str(score3/10))

# score_bonus = bonus_agent_improved(grid, targX, targY)