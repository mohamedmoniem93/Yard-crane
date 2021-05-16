#!/usr/bin/python3.7

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 10:52:33 2019

@author: Mohamed Abdel Moniem
"""

# Yard crane scheduling
from gurobipy import *
from constraints import *
from input_generator import *
from output_generators import *


# CONSTANTS / INPUTS
NUMBER_OF_BLOCKS = 6
ROWS = 3
COLS = 2

sourceblock = [i for i in range(1, NUMBER_OF_BLOCKS + 1)]
destblock = [i for i in range(1, NUMBER_OF_BLOCKS + 1)]
NUMBER_OF_SHIFTS = 2
shifts = [i for i in range(1, NUMBER_OF_SHIFTS + 1)]


# START
H = {}
b = {}
total_y = 0
b = create_b(NUMBER_OF_BLOCKS)
H = create_h(shifts, NUMBER_OF_BLOCKS)

I = place_blocks(ROWS, COLS, NUMBER_OF_BLOCKS)
J = place_blocks(ROWS, COLS, NUMBER_OF_BLOCKS)
y = {}
calculate_distance_matrix(I, J, y)

for shift in shifts:

    curr_y = 0
    ready_for_model, penalty = input_ready(NUMBER_OF_BLOCKS, b, H, shift)
    if not ready_for_model:
        print(f"Spare cranes are needed with the following distribution: {penalty}")
        # Update b with added cranes
        sub_penalty_cranes_from_h(H, penalty, shift)
        # Add penalty distance to y
        curr_y += calculate_penalty_distance(penalty)
        print(f"Added penalty of {curr_y} to the total distance")

    # initiate the model
    m = Model()

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

    # m.write("mod.lp")
    m.optimize()
    m.printAttr("x", "x*")
    print(f"h={H}")
    print(f"b={b}")

    # OUTPUT
    opt_x = get_optimum_x(m)
    opt_y = get_optimum_y(opt_x)
    curr_y += get_total_y(opt_y, y)
    total_y += curr_y

    # UPDATE B for next shift
    update_b_values(b, opt_y, shift)

    print(f"Y for current shift: {shift} equals = {curr_y}")
    print(f"SHIFT={shift}, Updated b,\n {b}")
    print(f"h={H}")


print(f"Total Y: {total_y}")
