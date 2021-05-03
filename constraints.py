from gurobipy import *


def first_constraint(sourceblock, m, destblock, shift, x):
    """
    total number of yard cranes moving from block i to block j at each time period t are no more than one
    :param shift: Current shift number
    """
    for i in sourceblock:
        m.addConstr(quicksum(x[i, j, shift] for j in destblock) <= 2)


def second_constraint(sourceblock, m, destblock, shift, x):
    """
    the number of yard cranes moving from block j to block i are no more than two
    :param shift: Current shift number
    """
    for j in destblock:
        m.addConstr(quicksum(x[i, j, shift] for i in sourceblock) <= 2)


def third_constraint(sourceblock, m, destblock, shift, b, H, x):
    """
    total number of yard cranes moving from block j to block i for each time period t are not less than the required number of yard cranes that needs to be delivered to block i
    :param shift: Current shift number
    """
    for j in sourceblock:
        m.addConstr(
            (H[j, shift] - b[j, shift]) <= quicksum(x[i, j, shift] for i in sourceblock)
        )


def fifth_constraint(sourceblock, m, destblock, shift, b, H, x):
    """
    ensures no yard cranes moves from block ⅈ to any block j at each time period t if it’s number of required yard cranes are less than the number of yard cranes already available at the block.
    :param shift: Current shift number
    """
    for j in destblock:
        if b[j, shift] <= H[j, shift]:
            m.addConstr(quicksum(x[j, i, shift] for i in sourceblock) == 0)


def sixth_constraint(sourceblock, m, destblock, shift, b, H, x):
    """
    ensures the total number of yard cranes remaining at block j remains satisfactory after some YC(s) left block j to all blocks at each time period t.
    :param shift: Current shift number
    """
    for j in destblock:
        m.addConstr(
            abs(b[j, shift] - H[j, shift])
            >= quicksum(x[j, i, shift] for i in sourceblock)
        )


def seventh_constraint(sourceblock, m, destblock, shift, x):
    """
    ensures that the number of yard cranes moving along a row of blocks are non-negativity.
    :param shift: Current shift number
    """
    for i in sourceblock:
        for j in destblock:
            m.addConstr(x[i, j, shift] >= 0)
