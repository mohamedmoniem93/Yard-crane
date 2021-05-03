import random


def place_blocks(ROWS, COLS, NUMBER_OF_BLOCKS):
    """
    :param: ROWS: Rows of the grid
    :param COLS: columns of the grid
    :param NUMBER_OF_BLOCKS: total number of blocks
    Places blocks on the given rows and columns
    :return: grid as a map of
    """
    if ROWS * COLS != NUMBER_OF_BLOCKS:
        raise Exception("Blocks more or less than grid")

    # Maps between block number and position block: (x, y)
    grid = {}
    positions = [(row, col) for row in range(1, ROWS + 1) for col in range(1, COLS + 1)]
    index = 1
    for position in positions:
        grid[index] = position
        index += 1

    return grid


def create_h(shifts, NUMBER_OF_BLOCKS):
    """
    Create a dictionary keys= (block#, shift#): random between (0-2)
    :returns H (# H= {(1, 1): 2, (2, 1): 0, (3, 1): 0, (4, 1): 0, (5, 1): 2, (6, 1): 0})
    """
    h = {}
    for t in shifts:
        for block in range(1, NUMBER_OF_BLOCKS + 1):
            h[(block, t)] = random.randint(0, 2)
    return h


def create_b(NUMBER_OF_BLOCKS):
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


def calculate_distance_matrix(I, J, y):
    """
    Takes in I, J arrays and calculate the distance matrix out of it
    :param I: Source blocks
    :param J: Destination blocks
    :param y: Distance matrix as dictionary
    :return: Nothing, it changes y value
    """
    yr = 50
    yt = 150
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
