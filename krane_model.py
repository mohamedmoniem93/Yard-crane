#!/usr/bin/python3.7

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 10:52:33 2019

@author: Mohamed Abdel Moniem
"""

# Yard crane scheduling
import random
from gurobipy import *
from constraints import *


# CONSTANTS / INPUTS
NUMBER_OF_BLOCKS = 10
ROWS = 5
COLS = 2

sourceblock = [i for i in range(1, NUMBER_OF_BLOCKS + 1)]
destblock = [i for i in range(1, NUMBER_OF_BLOCKS + 1)]
NUMBER_OF_SHIFTS = 3
shifts = [i for i in range(1, NUMBER_OF_SHIFTS + 1)]

TB = 6
yr = 50
TC = 6
yt = 150


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


def update_b_values(b, optimum_y, last_shift):
    """
    Takes in co-ordinates of x and values of cranes and update b array
    :param b: b dictionary
    :param optimum_y: [
    #     i , j , t (shift), quantity
    #    [2, 1, 1, 1],
    #    [20, 1, 1, 1],
    # ]
    :return: Nothing, it changes b internally
    """
    # Create entries for the next shift
    new_shift_dictionary = {}
    for key, value in b.items():
        src_block, solution_shift = key[0], key[1]
        if solution_shift == last_shift:
            new_shift_dictionary[(src_block, last_shift + 1)] = value

    # Get the optimum solution for the last shift and update the values
    for op_y in optimum_y:
        src_block, d_block, quantity = op_y[0], op_y[1], op_y[3]
        # Take from the src block and add it to the d_block
        new_shift_dictionary[(src_block, last_shift + 1)] -= quantity
        new_shift_dictionary[(d_block, last_shift + 1)] += quantity

    b.update(new_shift_dictionary)


def calculate_distance_matrix(I, J, y):
    """
    Takes in I, J arrays and calculate the distance matrix out of it
    :param I: Source blocks
    :param J: Destination blocks
    :param y: Distance matrix as dictionary
    :return: Nothing, it changes y value
    """
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


# START
H = {}
b = {}
total_y = 0
for shift in shifts:

    # initiate the model
    m = Model()

    if shift == 1:
        b = create_B()
        H = create_H()

    I = place_blocks()
    J = place_blocks()

    y = {}
    calculate_distance_matrix(I, J, y)
    m.update()

    # Decision variables
    x = {}
    for i in sourceblock:
        for j in destblock:
            x[i, j, shift] = m.addVar(
                lb=0.0, ub=2.0, vtype=GRB.INTEGER, name="x[%s,%s,%s]" % (i, j, shift)
            )

    # CONSTRAINTS
    m.update()
    first_constraint(sourceblock, m, destblock, shift, x)
    second_constraint(sourceblock, m, destblock, shift, x)
    third_constraint(sourceblock, m, destblock, shift, b, H, x)
    fifth_constraint(sourceblock, m, destblock, shift, b, H, x)
    sixth_constraint(sourceblock, m, destblock, shift, b, H, x)
    seventh_constraint(sourceblock, m, destblock, shift, x)

    # objective function
    m.setObjective(
        quicksum(
            x[i, j, shift] * y[i, j] * 0.0085 for i in sourceblock for j in destblock
        ),
        GRB.MINIMIZE,
    )

    m.write("mod.lp")
    m.optimize()
    m.printAttr("x", "x*")

    opt_x = get_optimum_x()
    opt_y = get_optimum_y(opt_x)

    curr_y = get_total_y(opt_y)
    print(f"Y for current shift: {shift} equals = {curr_y}")
    total_y += curr_y

    # print(f"b before update \n{b}")
    update_b_values(b, opt_y, shift)
    print(f"SHIFT={shift}, Updated b,\n {b}")


print(f"Total Y: {total_y}")
