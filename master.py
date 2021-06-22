# -*- coding: utf-8 -*-

from krane_model import run
from visualize import draw_graph

# CONSTANTS / INPUTS
ROWS = 2
COLS = 3
NUMBER_OF_SHIFTS = 5

number_of_blocks = [(row * col) for row in range(1, ROWS) for col in range(1,COLS)]
y_array = []
x_array = []
for row in range(1, ROWS):
    for cols in range(1, COLS):
        y, x = run(row, cols, NUMBER_OF_SHIFTS)
        y_array.append(y)
        x_array.append(x)

draw_graph(number_of_blocks, y_array)

draw_graph(number_of_blocks, x_array)

