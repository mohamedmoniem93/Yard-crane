"""
Created on Tue Oct 15 10:52:33 2019
@author: Mohamed Abdel Moniem
"""

# Yard crane scheduling

from gurobipy import *

NUMBER_OF_BLOCKS = 6
ROWS = 3
COLS = 2


def place_blocks():
    #    """
    #    Places blocks on the given rows and columns
    #    :return: grid as a map of
    #    """
    if ROWS * COLS < NUMBER_OF_BLOCKS:
        raise Exception("Blocks more than grid")

    if ROWS * COLS > NUMBER_OF_BLOCKS:
        raise Exception("Blocks less than grid")

    # Maps between block number and position block: (x, y)
    grid = {}
    positions = [(row, col) for row in range(1, ROWS + 1) for col in range(1, COLS + 1)]
    index = 1
    for position in positions:
        grid[index] = position
        index += 1

    return grid


if __name__ == "__main__":
    place_blocks()


# initiate the model
m = Model()

# Modeldata

TB = 6
yr = 50
TC = 6
yt = 150
NC = 25

sourceblock = [i for i in range(1, NUMBER_OF_BLOCKS + 1)]
destblock = [i for i in range(1, NUMBER_OF_BLOCKS + 1)]
craneid = [i for i in range(1, NC + 1)]
shifts = [1]


# import random
#
# Random = []
# for i in range(NUMBER_OF_BLOCKS):
#    x = random.randint(0, 2)
#    Random.append(x)
## print(Random)
# IT = []
# for i in range(1, NUMBER_OF_BLOCKS + 1):
#    for j in range(1, 2):
#        IT.append(tuple([i, j]))
## print(IT)
# H = dict(zip(IT, Random))
# print("H=", H)
#
# import random
#
# Random = []
# for i in range(NUMBER_OF_BLOCKS):
#    x = random.randint(0, 2)
#    Random.append(x)
## print(Random)
# IT = []
# for i in range(1, NUMBER_OF_BLOCKS + 1):
#    for j in range(1, 2):
#        IT.append(tuple([i, j]))
## print(IT)
# b = dict(zip(IT, Random))
# print("b=", b)

H = {(1, 1): 2, (2, 1): 0, (3, 1): 0, (4, 1): 0, (5, 1): 2, (6, 1): 0}
b = {(1, 1): 1, (2, 1): 2, (3, 1): 2, (4, 1): 0, (5, 1): 1, (6, 1): 1}

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
for p in craneid:
    for i in sourceblock:
        for j in destblock:
            for t in shifts:
                x[i, j, t] = m.addVar(
                    vtype=GRB.BINARY, name="x[%s,%s,%s,%s]" % (p, i, j, t)
                )

m.update()
# Constraints

# total number of yard cranes moving from block i to block j at each time period t are no more than one

for t in shifts:
    for i in sourceblock:
        cont_1 = m.addConstr(
            quicksum(x[p, i, j, t] for p in craneid for j in destblock) <= 2
        )
##
###the number of yard cranes moving from block j to block i are no more than two
##
for t in shifts:
    for j in destblock:
        cont_2 = m.addConstr(quicksum(x[p, i, j, t] for p in craneid) <= 2)
#
# total number of yard cranes moving from block j to block i for each time period t are not less than the required number of yard cranes that needs to be delivered to block i
#
for t in shifts:
    for j in sourceblock:
        cont_3 = m.addConstr(
            (H[j, t] - b[j, t])
            <= quicksum(x[p, i, j, t] for p in craneid for i in sourceblock)
        )

# ensures no yard cranes moves from block ⅈ to any block j at each time period t if it’s number of required yard cranes are less than the number of yard cranes already available at the block.
for t in shifts:
    for j in destblock:
        if b[j, t] <= H[j, t]:
            cont_5 = m.addConstr(
                quicksum(x[p, j, i, t] for p in craneid for i in sourceblock) == 0
            )

# ensures the total number of yard cranes remaining at block j remains satisfactory after some YC(s) left block j to all blocks at each time period t.
for t in shifts:
    for j in destblock:
        cont_6 = m.addConstr(
            abs(b[j, t] - H[j, t]) >= quicksum(x[p, j, i, t] for i in sourceblock)
        )

# ensures that the number of yard cranes moving along a row of blocks are non-negativity.
for p in craneid:
    for t in shifts:
        for i in sourceblock:
            for j in destblock:
                cont_6 = m.addConstr(x[p, i, j, t] >= 0)

# objective function
m.setObjective(
    quicksum(
        x[p, i, j, t] * y[i, j] * 0.0085
        for p in craneid
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
    #    (x[2, 1, 1], 1)
    # ]
    # Output
    # [
    #    [2, 1, 1, 1]
    # ]
    optimum_y = []
    for opt_x in optimum_x:
        cur_y = []
        for char in opt_x[0]:
            if char.isdigit():
                cur_y.append(int(char))
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


opt_x = get_optimum_x()
opt_y = get_optimum_y(opt_x)
total_y = get_total_y(opt_y)

print(f"Total Y: {total_y}")
