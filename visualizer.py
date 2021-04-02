import pygame
import sys
from enum import Enum

import copy

WHITE = (255, 255, 255) #Flat
L_GREEN = (154,205,50) #hilly
GREEN = (34,139,34) #forested
KHAKI = (189,183,107) #cave
RED = (255, 0, 0) #target
BLACK = (0,0,0) #current 

pygame.init()
size = [800,800]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("MineSweeper")
clock = pygame.time.Clock()
dim = 50
height, width, margin = (800/dim-4, 800/dim -4, 4)

def display_landscape(grid, x, y):
    #check if exiting the visualization, then exit the program
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
    #loop over all maze entries and set the color appropriately based on the enum value in the maze
    for row in range(dim):
            for column in range(dim):
                color = WHITE
                if grid[row][column] < 0: 
                    color = RED
                if grid[row][column] == .1:
                    color = WHITE
                elif grid[row][column] == .3:
                    color = L_GREEN
                elif grid[row][column] == .7:
                    color = GREEN
                elif grid[row][column] == .9:
                    color = KHAKI
                if (row, column) == (x,y):
                    color = BLACK
                #draw this square on the visualization with the appropriate color
                pygame.draw.rect(screen, color, [(margin + width) * column + margin,
                                                (margin+ height) * row + margin,
                                                width, height])
    #fps for updating the maze visually
    clock.tick(60)
    #update display
    pygame.display.update()
    pygame.display.flip()
    return