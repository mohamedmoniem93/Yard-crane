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

def run(ROWS, COLS, NUMBER_OF_SHIFTS):
    """
    RUN THE WHOLE MODEL GIVEN THE ROWS, COLS AND NUMBER OF SHIFTS
    Returns total y, objective value
    """
    with open('Results.txt', 'w') as f:
        print ("Start Solution\n", file=f)
        print ("____________________________________________________________________________________", file=f)
        
        NUMBER_OF_BLOCKS = ROWS * COLS
        sourceblock = [i for i in range(1, NUMBER_OF_BLOCKS + 1)]
        destblock = [i for i in range(1, NUMBER_OF_BLOCKS + 1)]
        shifts = [i for i in range(1, NUMBER_OF_SHIFTS + 1)]
    
        # START
        H = {}
        b = {}
        total_y = 0
        objective_value = 0
        b = create_b(NUMBER_OF_BLOCKS)
        H = create_h(shifts, NUMBER_OF_BLOCKS)
#        H = create_h_given_workload(shifts, NUMBER_OF_BLOCKS)
        
        with open('H_values_before.csv', 'w') as fh:    
            print("block, shift, required cranes, designation", file=fh)
            for key, value in H.items():
                print(f"{key[0]}, {key[1]}, {value[0]}, {value[1]}", file=fh)
        
        I = place_blocks(ROWS, COLS, NUMBER_OF_BLOCKS)
        J = place_blocks(ROWS, COLS, NUMBER_OF_BLOCKS)
        y = {}
        calculate_distance_matrix(I, J, y)
        
        for shift in shifts:
        
            curr_y = 0
            sparecranes_distance = 0
            ready_for_model, penalty = input_ready(NUMBER_OF_BLOCKS, b, H, shift)
            if not ready_for_model:
                print(f"Spare cranes are needed with the following distribution: {penalty}", file=f)
                # Update b with added cranes
                sub_penalty_cranes_from_h(H, penalty, shift)
                # Add penalty distance to y
                curr_y += calculate_penalty_distance(penalty)        
                sparecranes_distance=curr_y
                print(f"Added penalty of {curr_y} to the total distance", file=f)
        
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
                    x[i, j, shift] * y[i, j] * 0.02 for i in sourceblock for j in destblock
                ),
                GRB.MINIMIZE,
            )
        
    #       m.write("mod.lp")
            m.optimize()
            objective_value += m.getObjective().getValue() + 2*sparecranes_distance*0.02
            m.printAttr("x", "x*")
    #        print(f"h={H}")
    #        print(f"b={b}")
        
            # OUTPUT
            opt_x = get_optimum_x(m)
            opt_y = get_optimum_y(opt_x)
            curr_y += get_total_y(opt_y, y)
            total_y += curr_y
        
            # UPDATE B for next shift
            update_b_values(b, opt_y, shift)
        
            print(f"Y for current shift: {shift} equals = {curr_y}", file=f)
    #        print(f"SHIFT={shift}, Updated b,\n {b}")
    #        print(f"h={H}")
            print(f"energy consumption for current shift ={m.getObjective().getValue() + sparecranes_distance*0.02}", file=f)
            
            print("End shift", file=f)
            print("--------------------------------", file=f)
            
#        print (f"distance_matrix= {y}", file=f)
        print(f"Total Y: {total_y}", file=f)
        print(f"total energy consumption: {objective_value}", file=f)
        print(f"H_after={H}", file=f)
        print(f"b={b}", file=f)
    with open('H_values_after.csv', 'w') as fh:    
        print("block, shift, required cranes, designation", file=fh)
        for key, value in H.items():
            print(f"{key[0]}, {key[1]}, {value[0]}, {value[1]}", file=fh)
    with open('b_values.csv', 'w') as fb:   
        print("block, shift, available cranes", file=fb)
        for key, value in b.items():
            print(f"{key[0]}, {key[1]}, {value}", file=fb)
    return total_y
   
if __name__ == "__main__":
    # Row, cols, shifts
    run(4, 5, 3)