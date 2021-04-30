#!/usr/bin/python3.7

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 10:52:33 2019

@author: Mohamed Abdel Moniem
"""

# Yard crane scheduling
import random
from gurobipy import *

NUMBER_OF_BLOCKS = 10
ROWS = 5
COLS = 2


def place_blocks():
    """
    Places blocks on the given rows and columns
    :return: grid as a map of
    """
    if ROWS * COLS < NUMBER_OF_BLOCKS:
        raise Exception("Blocks more than grid")

    # Maps between block number and position block: (x, y)
    grid = {}
    positions = [(row, col) for row in range(1, ROWS + 1) for col in range(1, COLS + 1)]
    index = 1
    for position in positions:
        grid[index] = position
        index += 1

    return grid


# initiate the model
m = Model()

# Modeldata

TB = 6
yr = 50
TC = 6
yt = 150

sourceblock = [i for i in range(1, NUMBER_OF_BLOCKS + 1)]
destblock = [i for i in range(1, NUMBER_OF_BLOCKS + 1)]
NUMBER_OF_SHIFTS = 1
shifts = [i for i in range(1, NUMBER_OF_SHIFTS + 1)]


def create_H():
    """
    Create a dictionary keys= (block#, shift#): random between (0-2)
    :returns H (# H= {(1, 1): 2, (2, 1): 0, (3, 1): 0, (4, 1): 0, (5, 1): 2, (6, 1): 0})
    """
    h = {}
    for t in shifts:
        for block in range(1, NUMBER_OF_BLOCKS + 1):
            h[(block, t)] = random.randint(0, 2)
    return h


def create_B():
    """
    Create a dictionary keys= (block#, shift#): random between (0-2)
    This is done for the first shift only, after that B is updated from the solution
    :returns B (# b= {(1, 1): 1, (2, 1): 2, (3, 1): 2, (4, 1): 0, (5, 1): 1, (6, 1): 1})
    """
    b = {}
    t = 1
    for block in range(1, NUMBER_OF_BLOCKS + 1):
        b[(block, t)] = random.randint(0, 2)
    return b


H = create_H()
b = create_B()

I = place_blocks()
J = place_blocks()

y = {}
# same rows and adj columns
for k1, v1 in I.items():
    for k2, v2 in J.items():
        if v1[0] == v2[0] and abs(v1[1] - v2[1]) == 1:
            y1 = abs(v1[1] - v2[1]) * 210
            y[(k1, k2)] = y1
        # same columns and diff rows
        elif v1[1] == v2[1] and v1[0] != v2[0]:
            y5 = abs(v1[0] - v2[0]) * 46 + (2 * yt)
            y[(k1, k2)] = y5
        # diff rows and adj columns
        elif v1[0] != v2[0] and abs(v1[1] - v2[1]) == 1:
            y2 = abs(v1[1] - v2[1]) * 210 + abs(v1[0] - v2[0]) * 46 + (2 * yt)
            y[(k1, k2)] = y2
        elif k1 == k2:
            y[(k1, k2)] = 10000000
        else:
            y3 = (
                abs(v1[1] - v2[1]) * 210
                + abs(v1[0] - 1)
                + abs(v2[0] - 1) * 46
                + (2 * yr)
                + (4 * yt)
            )
            y[(k1, k2)] = y3

print("y[i,j]=", y)

m.update()

# Decision variables
x = {}
for i in sourceblock:
    for j in destblock:
        for t in shifts:
            x[i, j, t] = m.addVar(
                lb=0.0, ub=2.0, vtype=GRB.INTEGER, name="x[%s,%s,%s]" % (i, j, t)
            )

m.update()
# Constraints


def first_constraint(shift):
    """
    total number of yard cranes moving from block i to block j at each time period t are no more than one
    :param shift: Current shift number
    """
    for i in sourceblock:
        m.addConstr(quicksum(x[i, j, shift] for j in destblock) <= 2)


def second_constraint(shift):
    """
    the number of yard cranes moving from block j to block i are no more than two
    :param shift: Current shift number
    """
    for j in destblock:
        m.addConstr(quicksum(x[i, j, shift] for i in sourceblock) <= 2)


def third_constraint(shift):
    """
    total number of yard cranes moving from block j to block i for each time period t are not less than the required number of yard cranes that needs to be delivered to block i
    :param shift: Current shift number
    """
    for j in sourceblock:
        m.addConstr(
            (H[j, shift] - b[j, shift]) <= quicksum(x[i, j, t] for i in sourceblock)
        )


def fifth_constraint(shift):
    """
    ensures no yard cranes moves from block ⅈ to any block j at each time period t if it’s number of required yard cranes are less than the number of yard cranes already available at the block.
    :param shift: Current shift number
    """
    for j in destblock:
        if b[j, shift] <= H[j, shift]:
            m.addConstr(quicksum(x[j, i, shift] for i in sourceblock) == 0)


def sixth_constraint(shift):
    """
    ensures the total number of yard cranes remaining at block j remains satisfactory after some YC(s) left block j to all blocks at each time period t.
    :param shift: Current shift number
    """
    for j in destblock:
        m.addConstr(
            abs(b[j, shift] - H[j, shift]) >= quicksum(x[j, i, shift] for i in sourceblock)
        )


def seventh_constraint(shift):
    """
    ensures that the number of yard cranes moving along a row of blocks are non-negativity.
    :param shift: Current shift number
    """
    for i in sourceblock:
        for j in destblock:
            m.addConstr(x[i, j, shift] >= 0)

# objective function
m.setObjective(
    quicksum(
        x[i, j, t] * y[i, j] * 0.0085
        for i in sourceblock
        for j in destblock
        for t in shifts
    ),
    GRB.MINIMIZE,
)

# print(quicksum(x[i,j,t] * y[i,j] for i in sourceblock for j in destblock for t in shifts)

m.write("mod.lp")
# m.computeIIS()
# m.write('modi.ilp')
m.optimize()
m.printAttr("x", "x*")


def get_optimum_x():
    # Get all x that have a value
    optimum_x = []
    for x in m.getVars():
        if x.x > 0:
            x_y_var = (x.Varname, x.x)
            optimum_x.append(x_y_var)
    return optimum_x


def get_optimum_y(optimum_x):
    # Only get numbers out of var name
    # input
    # [
    #    (x[2, 1, 1], 1),
    #    (x[20, 1, 1], 1),
    # ]
    # Output
    # [
    #    [2, 1, 1, 1],
    #    [20, 1, 1, 1],
    # ]
    optimum_y = []
    for opt_x in optimum_x:
        cur_y = []
        for str in opt_x[0].split(","):
            cur_number = ""
            for char in str:
                if char.isdigit():
                    cur_number += char
            cur_y.append(int(cur_number))
        cur_y.append(opt_x[1])
        optimum_y.append(cur_y)
    return optimum_y


def get_total_y(optimum_y):
    # calculate total y
    total_y = 0
    for opt_y in optimum_y:
        i = opt_y[0]
        j = opt_y[1]
        quantity = opt_y[3]
        total_y += y[(i, j)] * quantity
    return total_y


def update_b_values(optimum_y):
    """
    Takes in co-ordinates of x and values of cranes and update b array

    :param optimum_y: [
    #     i , j , t (shift), quantity
    #    [2, 1, 1, 1],
    #    [20, 1, 1, 1],
    # ]
    :return: New b array
    """


opt_x = get_optimum_x()
opt_y = get_optimum_y(opt_x)
print(opt_y)
total_y = get_total_y(opt_y)

# print(f"Distance Matrix: \n {y}")
print(f"Total Y: {total_y}")

